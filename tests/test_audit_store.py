"""SQLite foundation using isolated local test databases only."""
import sqlite3
from pathlib import Path
import pytest
from audit_store import AuditStore,AuditError,SCHEMA_VERSION


def test_initialization_version_foreign_keys_permissions_and_repeat(tmp_path):
    path=tmp_path/'audit.sqlite3';store=AuditStore(path)
    assert store.summary()==dict(schema_version=1,cases=0,events=0,snapshots=0,evidence_references=0)
    assert len(store.reviewers())==3
    with store.connection() as con:
        assert con.execute('PRAGMA foreign_keys').fetchone()[0]==1
        assert con.execute('PRAGMA user_version').fetchone()[0]==SCHEMA_VERSION
        assert con.execute('PRAGMA journal_mode').fetchone()[0]=='wal'
    assert path.stat().st_mode & 0o777 == 0o600
    assert AuditStore(path).summary()==store.summary()

@pytest.mark.parametrize('version',[2,99])
def test_future_schema_rejected_without_migration(tmp_path,version):
    path=tmp_path/'future.sqlite3';AuditStore(path)
    with sqlite3.connect(path) as con:con.execute('PRAGMA user_version='+str(version))
    with pytest.raises(AuditError,match='unsupported'):AuditStore(path)
    with sqlite3.connect(path) as con:assert con.execute('PRAGMA user_version').fetchone()[0]==version


def test_unknown_unversioned_database_not_modified(tmp_path):
    path=tmp_path/'unknown.sqlite3'
    with sqlite3.connect(path) as con:con.execute('CREATE TABLE valuable(value TEXT)');con.execute('INSERT INTO valuable VALUES(?)',('preserve',))
    with pytest.raises(AuditError) as exc:AuditStore(path)
    assert exc.value.code=='UNRECOGNIZED_DATABASE'
    with sqlite3.connect(path) as con:assert con.execute('SELECT value FROM valuable').fetchone()[0]=='preserve'


def test_schema_change_requires_explicit_migration(tmp_path,monkeypatch):
    import audit_store
    path=tmp_path/'audit.sqlite3';AuditStore(path)
    monkeypatch.setattr(audit_store,'SCHEMA_DDL_HASH','changed')
    with pytest.raises(AuditError) as exc:AuditStore(path)
    assert exc.value.code=='SCHEMA_INTEGRITY_FAILURE'


def test_transaction_rollback_and_foreign_key_failure(tmp_path):
    store=AuditStore(tmp_path/'audit.sqlite3')
    with pytest.raises(RuntimeError):
        with store.transaction() as con:
            con.execute('INSERT INTO policies VALUES(?,?,?,?)',('hash','version','deterministic_rules','time'))
            raise RuntimeError('Controlled rollback')
    with store.connection() as con:assert con.execute('SELECT count(*) FROM policies').fetchone()[0]==0
    with pytest.raises(sqlite3.IntegrityError):
        with store.transaction() as con:con.execute('INSERT INTO evidence_references VALUES(?,?,?,?,?,?,?,?,?,?,?)',('ref','missing','FEATURE_LEVEL','field','alias','hash',None,None,'HISTORICAL','description',None))


def test_metadata_and_reviewer_rows_append_only(tmp_path):
    store=AuditStore(tmp_path/'audit.sqlite3')
    for sql in ["UPDATE reviewers SET display_name='changed'","DELETE FROM reviewers","DELETE FROM schema_migrations"]:
        with pytest.raises(sqlite3.IntegrityError,match='APPEND_ONLY'):
            with store.transaction() as con:con.execute(sql)


def test_consistent_backup_and_no_overwrite(tmp_path):
    store=AuditStore(tmp_path/'audit.sqlite3');dest=tmp_path/'backup.sqlite3'
    store.backup(dest)
    assert AuditStore(dest).summary()==store.summary()
    assert dest.stat().st_mode & 0o777 == 0o600
    with pytest.raises(AuditError) as exc:store.backup(dest)
    assert exc.value.code=='BACKUP_EXISTS'


def test_memory_database_not_presented_as_durable():
    with pytest.raises(AuditError) as exc:AuditStore(':memory:')
    assert exc.value.code=='DURABLE_PATH_REQUIRED'
