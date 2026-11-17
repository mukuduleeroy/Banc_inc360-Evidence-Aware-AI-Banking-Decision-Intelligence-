"""SQLite audit foundation. Append-only application history is not tamper-proof storage."""
from contextlib import contextmanager
from datetime import datetime,timezone
from pathlib import Path
import os,sqlite3,hashlib

SCHEMA_VERSION=1
DEMO_REVIEWERS=(('DEMO-RM-01','Demo reviewer 1'),('DEMO-RM-02','Demo reviewer 2'),('DEMO-AUDIT-01','Demo auditor'))

class AuditError(ValueError):
    def __init__(self,code,message):super().__init__(message);self.code=code

def utc_now():return datetime.now(timezone.utc).isoformat(timespec='microseconds')

DDL=[
'''CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_utc TEXT NOT NULL, ddl_hash TEXT NOT NULL)''',
'''CREATE TABLE reviewers(reviewer_id TEXT PRIMARY KEY, display_name TEXT NOT NULL, attribution_kind TEXT NOT NULL CHECK(attribution_kind='DEMO_UNVERIFIED'), created_utc TEXT NOT NULL)''',
'''CREATE TABLE datasets(dataset_version_id TEXT PRIMARY KEY, dataset_hash TEXT NOT NULL, manifest_hash TEXT NOT NULL, source_hash TEXT, cutoff TEXT NOT NULL, recorded_utc TEXT NOT NULL, UNIQUE(dataset_hash,manifest_hash))''',
'''CREATE TABLE policies(policy_hash TEXT PRIMARY KEY, policy_version TEXT NOT NULL, method TEXT NOT NULL CHECK(method='deterministic_rules'), recorded_utc TEXT NOT NULL)''',
'''CREATE TABLE passport_snapshots(snapshot_id TEXT PRIMARY KEY, customer_ref TEXT NOT NULL, dataset_version_id TEXT NOT NULL REFERENCES datasets(dataset_version_id), dataset_hash TEXT NOT NULL, manifest_hash TEXT NOT NULL, policy_hash TEXT NOT NULL REFERENCES policies(policy_hash), policy_version TEXT NOT NULL, outcome TEXT NOT NULL CHECK(outcome IN ('SUPPORTED','CAUTION','ABSTAIN')), context_kind TEXT NOT NULL CHECK(context_kind='REAL'), normalized_json TEXT NOT NULL, snapshot_hash TEXT NOT NULL, decision_hash TEXT NOT NULL, snapshot_utc TEXT NOT NULL)''',
'''CREATE TABLE review_cases(case_id TEXT PRIMARY KEY, customer_ref TEXT NOT NULL UNIQUE, state TEXT NOT NULL CHECK(state IN ('OPEN','INVESTIGATION_REQUIRED','DEFERRED','REJECTED','APPROVED_LOCAL')), revision INTEGER NOT NULL CHECK(revision>=0), current_snapshot_id TEXT NOT NULL REFERENCES passport_snapshots(snapshot_id), dataset_version_id TEXT NOT NULL REFERENCES datasets(dataset_version_id), dataset_hash TEXT NOT NULL, manifest_hash TEXT NOT NULL, policy_hash TEXT NOT NULL REFERENCES policies(policy_hash), policy_version TEXT NOT NULL, decision_hash TEXT NOT NULL, last_action TEXT, last_reviewer_id TEXT REFERENCES reviewers(reviewer_id), latest_event_id TEXT REFERENCES review_events(event_id) DEFERRABLE INITIALLY DEFERRED, created_utc TEXT NOT NULL, updated_utc TEXT NOT NULL)''',
'''CREATE TABLE review_events(event_sequence INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE, case_id TEXT NOT NULL REFERENCES review_cases(case_id), case_revision INTEGER NOT NULL, customer_ref TEXT NOT NULL, action TEXT NOT NULL CHECK(action IN ('OPEN','REFRESH','APPROVE','DEFER','REJECT')), reason TEXT NOT NULL CHECK(length(trim(reason)) BETWEEN 1 AND 2000), reviewer_id TEXT NOT NULL REFERENCES reviewers(reviewer_id), event_utc TEXT NOT NULL, dataset_hash TEXT NOT NULL, manifest_hash TEXT NOT NULL, policy_hash TEXT NOT NULL REFERENCES policies(policy_hash), policy_version TEXT NOT NULL, snapshot_id TEXT NOT NULL REFERENCES passport_snapshots(snapshot_id), request_id TEXT NOT NULL UNIQUE, request_hash TEXT NOT NULL, UNIQUE(case_id,case_revision))''',
'''CREATE TABLE evidence_references(reference_id TEXT PRIMARY KEY, snapshot_id TEXT NOT NULL REFERENCES passport_snapshots(snapshot_id), reference_level TEXT NOT NULL CHECK(reference_level='FEATURE_LEVEL'), feature_name TEXT NOT NULL, customer_ref TEXT NOT NULL, artifact_hash TEXT NOT NULL, source_hash TEXT, cutoff TEXT, temporal_kind TEXT NOT NULL CHECK(temporal_kind IN ('HISTORICAL','CURRENT_SNAPSHOT')), derivation TEXT NOT NULL, source_event_reference TEXT CHECK(source_event_reference IS NULL), UNIQUE(snapshot_id,feature_name))''',
'''CREATE INDEX events_case_timeline ON review_events(case_id,event_sequence)''',
'''CREATE INDEX events_customer_time ON review_events(customer_ref,event_utc)''',
'''CREATE INDEX snapshots_customer ON passport_snapshots(customer_ref,snapshot_utc)''',
'''CREATE INDEX cases_state ON review_cases(state,updated_utc)''',
'''CREATE INDEX evidence_snapshot ON evidence_references(snapshot_id)''',
'''CREATE TRIGGER event_snapshot_matches BEFORE INSERT ON review_events BEGIN
SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM passport_snapshots s WHERE s.snapshot_id=NEW.snapshot_id AND s.customer_ref=NEW.customer_ref AND s.dataset_hash=NEW.dataset_hash AND s.manifest_hash=NEW.manifest_hash AND s.policy_hash=NEW.policy_hash AND s.policy_version=NEW.policy_version AND s.context_kind='REAL') THEN RAISE(ABORT,'EVENT_SNAPSHOT_MISMATCH') END;
SELECT CASE WHEN NEW.action='APPROVE' AND NOT EXISTS(SELECT 1 FROM passport_snapshots s WHERE s.snapshot_id=NEW.snapshot_id AND s.outcome='SUPPORTED') THEN RAISE(ABORT,'APPROVAL_REQUIRES_SUPPORTED') END;
END''',
'''CREATE TRIGGER case_update_requires_event BEFORE UPDATE ON review_cases BEGIN
SELECT CASE WHEN NEW.case_id!=OLD.case_id OR NEW.customer_ref!=OLD.customer_ref THEN RAISE(ABORT,'CASE_IDENTITY_IS_IMMUTABLE') END;
SELECT CASE WHEN NOT ((NEW.last_action='APPROVE' AND NEW.state='APPROVED_LOCAL') OR (NEW.last_action='DEFER' AND NEW.state='DEFERRED') OR (NEW.last_action='REJECT' AND NEW.state='REJECTED') OR (NEW.last_action IN ('OPEN','REFRESH') AND NEW.state IN ('OPEN','INVESTIGATION_REQUIRED'))) THEN RAISE(ABORT,'INVALID_CASE_TRANSITION') END;
SELECT CASE WHEN NEW.revision!=OLD.revision+1 OR NOT EXISTS(SELECT 1 FROM review_events e WHERE e.event_id=NEW.latest_event_id AND e.case_id=OLD.case_id AND e.case_revision=NEW.revision AND e.snapshot_id=NEW.current_snapshot_id AND e.customer_ref=NEW.customer_ref AND e.dataset_hash=NEW.dataset_hash AND e.manifest_hash=NEW.manifest_hash AND e.policy_hash=NEW.policy_hash AND e.policy_version=NEW.policy_version AND e.action=NEW.last_action AND e.reviewer_id=NEW.last_reviewer_id) THEN RAISE(ABORT,'CASE_UPDATE_REQUIRES_NEW_EVENT') END;
END''',
'''CREATE TRIGGER cases_no_delete BEFORE DELETE ON review_cases BEGIN SELECT RAISE(ABORT,'AUDIT_HISTORY_IS_APPEND_ONLY'); END''',
]
for table in ('review_events','passport_snapshots','evidence_references','reviewers','datasets','policies','schema_migrations'):
    for operation in ('UPDATE','DELETE'):
        DDL.append(f"CREATE TRIGGER {table}_no_{operation.lower()} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT,'AUDIT_HISTORY_IS_APPEND_ONLY'); END")

SCHEMA_DDL_HASH=hashlib.sha256('\n'.join(DDL).encode()).hexdigest()

class AuditStore:
    def __init__(self,path):
        if str(path)==':memory:':raise AuditError('DURABLE_PATH_REQUIRED','A file-backed database path is required for durable audit.')
        self.path=Path(path).expanduser()
        self.initialize()

    @contextmanager
    def connection(self):
        con=sqlite3.connect(str(self.path),timeout=5,isolation_level=None)
        con.row_factory=sqlite3.Row
        try:
            con.execute('PRAGMA foreign_keys=ON')
            con.execute('PRAGMA busy_timeout=5000')
            yield con
        finally:con.close()

    @contextmanager
    def transaction(self):
        with self.connection() as con:
            con.execute('BEGIN IMMEDIATE')
            try:
                yield con
                con.commit()
            except BaseException:
                con.rollback();raise

    def initialize(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        try:
            fd=os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
        except FileExistsError:pass
        if os.name=='posix':os.chmod(self.path,0o600)
        try:
            with self.connection() as con:
                version=con.execute('PRAGMA user_version').fetchone()[0]
                if version not in (0,SCHEMA_VERSION):raise AuditError('UNSUPPORTED_SCHEMA_VERSION','Audit database schema is unsupported; back up and review migrations before use.')
                if version==0:
                    with self.transaction() as tx:
                        # Recheck under the writer lock for concurrent first initialization.
                        if tx.execute('PRAGMA user_version').fetchone()[0]==0:
                            existing=tx.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
                            if existing:raise AuditError('UNRECOGNIZED_DATABASE','Unversioned existing tables will not be modified.')
                            for statement in DDL:tx.execute(statement)
                            now=utc_now()
                            tx.executemany('INSERT INTO reviewers VALUES(?,?,?,?)',[(i,n,'DEMO_UNVERIFIED',now) for i,n in DEMO_REVIEWERS])
                            tx.execute('INSERT INTO schema_migrations VALUES(?,?,?)',(SCHEMA_VERSION,now,SCHEMA_DDL_HASH))
                            tx.execute('PRAGMA user_version=1')
                required={'review_cases','review_events','passport_snapshots','evidence_references','datasets','policies','reviewers','schema_migrations'}
                actual={r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if not required<=actual:raise AuditError('INCOMPLETE_SCHEMA','Audit database schema is incomplete; do not record reviews.')
                columns={r[1] for r in con.execute('PRAGMA table_info(schema_migrations)')}
                if 'ddl_hash' not in columns:raise AuditError('SCHEMA_INTEGRITY_FAILURE','Schema migration fingerprint is missing; back up and review the database.')
                recorded=con.execute('SELECT ddl_hash FROM schema_migrations WHERE version=?',(SCHEMA_VERSION,)).fetchone()
                if not recorded or recorded[0]!=SCHEMA_DDL_HASH:raise AuditError('SCHEMA_INTEGRITY_FAILURE','Schema definition changed without an explicit versioned migration.')
                con.execute('PRAGMA journal_mode=WAL')
        except sqlite3.Error:
            raise AuditError('AUDIT_DATABASE_UNAVAILABLE','Audit storage could not be initialized. No review success is recorded.') from None

    def reviewers(self):
        with self.connection() as con:return [dict(r) for r in con.execute('SELECT reviewer_id,display_name,attribution_kind FROM reviewers ORDER BY reviewer_id')]

    def case(self,case_id):
        with self.connection() as con:
            row=con.execute('SELECT * FROM review_cases WHERE case_id=?',(case_id,)).fetchone()
            return dict(row) if row else None

    def case_for_customer(self,alias):
        with self.connection() as con:
            row=con.execute('SELECT * FROM review_cases WHERE customer_ref=?',(alias,)).fetchone()
            return dict(row) if row else None

    def cases(self):
        with self.connection() as con:return [dict(r) for r in con.execute('SELECT * FROM review_cases ORDER BY updated_utc DESC,case_id')]

    def timeline(self,case_id=None):
        with self.connection() as con:
            sql='SELECT e.*,r.display_name AS reviewer_display_name FROM review_events e JOIN reviewers r USING(reviewer_id)'
            rows=con.execute(sql+' WHERE e.case_id=? ORDER BY e.event_sequence',(case_id,)) if case_id else con.execute(sql+' ORDER BY e.event_sequence')
            return [dict(r) for r in rows]

    def snapshot(self,snapshot_id):
        import json,hashlib
        with self.connection() as con:
            row=con.execute('SELECT * FROM passport_snapshots WHERE snapshot_id=?',(snapshot_id,)).fetchone()
            if not row:raise AuditError('SNAPSHOT_NOT_FOUND','Passport snapshot is unavailable.')
            row=dict(row)
            if hashlib.sha256(row['normalized_json'].encode()).hexdigest()!=row['snapshot_hash']:
                raise AuditError('SNAPSHOT_INTEGRITY_FAILURE','Stored passport content does not match its fingerprint.')
            row['payload']=json.loads(row['normalized_json'])
            row['evidence_references']=[dict(r) for r in con.execute('SELECT * FROM evidence_references WHERE snapshot_id=? ORDER BY feature_name',(snapshot_id,))]
            return row

    def backup(self,destination):
        destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
        try:fd=os.open(destination,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
        except FileExistsError:raise AuditError('BACKUP_EXISTS','Backup destination already exists; choose a new file.') from None
        target=sqlite3.connect(str(destination))
        try:
            with self.connection() as source:source.backup(target)
        finally:target.close()
        return destination

    def summary(self):
        with self.connection() as con:
            return {'schema_version':con.execute('PRAGMA user_version').fetchone()[0],'cases':con.execute('SELECT count(*) FROM review_cases').fetchone()[0],'events':con.execute('SELECT count(*) FROM review_events').fetchone()[0],'snapshots':con.execute('SELECT count(*) FROM passport_snapshots').fetchone()[0],'evidence_references':con.execute('SELECT count(*) FROM evidence_references').fetchone()[0]}
