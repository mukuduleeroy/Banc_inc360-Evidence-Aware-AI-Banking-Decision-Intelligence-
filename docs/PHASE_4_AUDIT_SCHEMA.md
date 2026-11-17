# Phase 4 audit schema and operations

Implementation: `audit_store.py`; Python standard-library sqlite3 (locally SQLite 3.54.0). Default database `outputs/review_audit.sqlite3`; override with exported `BANCINC_AUDIT_DB`. `.env` files are not auto-loaded. File-backed storage is required; `:memory:` is rejected.

## Schema version 1

| Table | Keys and persisted content |
| --- | --- |
| `schema_migrations` | version PK, applied_utc, DDL hash |
| `reviewers` | reviewer_id PK, display_name, DEMO_UNVERIFIED attribution_kind, created_utc |
| `datasets` | dataset_version_id PK; feature and manifest SHA-256 pair UNIQUE; source_hash, cutoff, recorded_utc |
| `policies` | policy_hash PK; policy_version, deterministic_rules method, recorded_utc |
| `passport_snapshots` | snapshot_id PK; alias, dataset_version_id FK, data/manifest/policy hashes, policy_version, outcome, REAL context, normalized_json, snapshot_hash, decision_hash, snapshot_utc |
| `review_cases` | case_id PK; customer_ref UNIQUE; state, revision; current_snapshot_id/dataset_version_id/policy_hash FKs; fingerprints, decision_hash; last_action/reviewer/latest_event FKs; created/updated UTC |
| `review_events` | event_sequence autoincrement PK; event_id UNIQUE; case_id FK, case_revision, alias, action, reason, reviewer FK, event_utc, data/manifest/policy hashes/version, snapshot FK, request_id UNIQUE, request_hash; UNIQUE(case_id,case_revision) |
| `evidence_references` | reference_id PK; snapshot FK, FEATURE_LEVEL, feature_name, alias, artifact/source hashes, temporal_kind, cutoff, derivation; source_event_reference constrained NULL; UNIQUE(snapshot_id,feature_name) |

Exact column definitions, CHECK constraints and trigger SQL live in the versioned `DDL` list in `audit_store.py`. Case states: OPEN, INVESTIGATION_REQUIRED, APPROVED_LOCAL, DEFERRED, REJECTED. STALE is a derived UI/service condition, not a rewrite of the historical state. Events: OPEN, REFRESH, APPROVE, DEFER, REJECT.

Initialization migrates an empty version-0 database to version 1 atomically and seeds three fixed demonstration reviewers. Reopening is idempotent. Unknown nonempty unversioned databases, incomplete schema, future versions and a mismatching release DDL hash are rejected. No historical migration is guessed. Future changes require an explicit versioned migration and tests; do not edit released v1 DDL in place.

## Integrity and concurrency

Each connection enables foreign keys, busy timeout 5,000ms; WAL is enabled. Writes use BEGIN IMMEDIATE with commit/rollback and parameterized values. Case latest-event FK is deferred to transaction commit. Immutable-table UPDATE/DELETE triggers cover events, snapshots, references, reviewer/dataset/policy metadata and migration rows. Case deletion is blocked; updates require a matching new event and revision increment, with action/state correspondence. APPROVE event snapshots must be real and SUPPORTED.

Indexes cover case event sequence, customer/event time, customer snapshots, state/update time and snapshot evidence lookup. Request tokens provide idempotent identical submissions; conflicting reuse is rejected. Expected revision and inspected snapshot prevent concurrent lost updates. Revalidation occurs before writes and again before commit; failure rolls back all related rows.

Snapshots persist aliases, six statuses/reason codes, limited evidence summaries, method/policy and dataset provenance. Raw records, credentials, raw transaction/customer identifiers and arbitrary behavioural explanation text are excluded. Required free-text reviewer reasons are retained, so operators must avoid entering personal data. Snapshot SHA-256 is checked on retrieval; it is not an external signature or owner-resistant tamper seal.

## Backup, recovery and reset

Databases and SQLite sidecars are ignored by Git. The database and backup are created with POSIX mode 0600. Restrict the containing directory and OS account too; SQLite is not encrypted here. Never commit real data, screenshots, alias keys, databases or backups.

```sh
.venv/bin/python scripts/audit_admin.py status --db outputs/review_audit.sqlite3
.venv/bin/python scripts/audit_admin.py backup --db outputs/review_audit.sqlite3 --out /private/tmp/bancinc-audit-backup.sqlite3
```

Use a previously unused backup path: overwrite is refused. The helper uses SQLite's online backup API, which includes committed WAL data consistently. Copying only the main file of an active WAL database is unsafe. Preserve source feature+manifest versions, policy/code version and the private `outputs/.presentation_alias_key` separately with equally restricted access; losing/rotating the key changes alias mapping and may disconnect cases from the current population.

For recovery, stop the target application, validate a backup using the status helper, copy it to a new private path and start with `BANCINC_AUDIT_DB` pointing there. Do not overwrite the original. For a clean demonstration, stop that preview and choose a new unused database path; keep the old database/backup intact. There is no application history delete/reset command. Set retention and secure archival rules before wider use. The demonstration databases in `outputs/phase4/` are separate from the default database.
