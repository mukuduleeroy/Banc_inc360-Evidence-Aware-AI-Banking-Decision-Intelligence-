# Phase 6 safe deployment guide

No dataset or code was deployed during Phase 6. Written BancABC approval is required before provisioning competition data outside the competition context. Section 11 restrictions apply even when fields appear synthetic. A private repository alone does not authorize redistribution or make an app's visitors private.

## Configuration contract

Settings may be shell environment variables or **top-level** Streamlit secrets. Environment values take precedence; `.env` files are not loaded automatically. No credential is committed. `.streamlit/secrets.example.toml` is documentation, while real secrets files are ignored.

| Setting | Meaning |
| --- | --- |
| DATA_MODE | LOCAL (backward-compatible default), DEPLOYED (permission-gated artifact), DEMO (explicit synthetic only) |
| BANCINC_RUNTIME | LOCAL or CLOUD; DEPLOYED defaults to CLOUD; set CLOUD explicitly for public DEMO |
| BANCINC_FEATURES_PATH | CSV path relative to repository ROOT; LOCAL also accepts existing absolute local paths; CLOUD rejects absolute paths, parent traversal and symlink escape |
| DATA_SHA256 | Required DEPLOYED pin of reviewed CSV bytes, independently configured from the manifest |
| DATA_VERSION | Required DEPLOYED match to adjacent manifest dataset_version |
| DATA_RELEASE_APPROVAL_REFERENCE | Actual reviewed written approval reference covering artifact, host, audience and purpose; not an authorization service |
| DATA_ACCESS_SCOPE | PRIVATE_HOST or PUBLIC_APPROVED; assertion only, never implements authentication |
| BANCINC_ALIAS_KEY_HEX | DEPLOYED private stable 32-byte key encoded as 64 hex characters; existing conflicting key blocks instead of rotating aliases |
| BANCINC_AUDIT_DB | Repository-relative CLOUD SQLite path; defaults outputs/cloud_review.sqlite3. LOCAL preserves BANCINC_AUDIT_DB/default outputs/review_audit.sqlite3 |

DEPLOYED loading checks exact feature columns, SHA-256, dataset_version, builder/event/schema/source provenance, manifest population, invalid/quarantined records and a manifest-replacement race before exposing the index. The existing index computes all counts and decisions through the unchanged engine. Neither expected row counts nor outcomes are hardcoded. Data/manifest/key/policy cache invalidation remains content based. Version and expected-hash checks execute on each import before cached-index reuse.

LOCAL retains schema validation and fail-closed per-record/lineage controls. A missing artifact now stops the real-data flow with DATASET_UNAVAILABLE; it never silently activates demo. The sidebar still permits deliberate synthetic selection. Explicit DATA_MODE=DEMO requires no competition artifact and displays no real-data portfolio metrics.

## Local startup

From the relocated repository:

```sh
cd /Users/user/Documents/BancInc360_Final
export DATA_MODE=LOCAL
export BANCINC_RUNTIME=LOCAL
export BANCINC_FEATURES_PATH=outputs/customer_features.csv
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8505
```

This workstation path is only a local terminal example; no cloud setting should contain it. To reuse a particular local audit database, export its existing repository-relative BANCINC_AUDIT_DB. No reset is required. Use Ctrl+C to stop. Backups remain available via `scripts/audit_admin.py backup --db <local-db> --out <new-private-backup>`; never copy just a live SQLite main file while WAL is active.

## Safe public Community Cloud mode now

Repository: `mukuduleeroy/Banc_inc360-Evidence-Aware-AI-Banking-Decision-Intelligence-`; intended branch `main`; entry point `app.py`. Verify these in the owner's app settings before applying any code update; the deployed exact commit was not available from public inspection. Review the Phase 6 changes before pushing. Do not force-add any CSV, manifest of restricted customer material, source ZIP, key, review DB or generated screenshots/evidence.

Set these top-level secrets in the owner's Streamlit settings:

```toml
DATA_MODE = "DEMO"
BANCINC_RUNTIME = "CLOUD"
BANCINC_AUDIT_DB = "outputs/cloud_review.sqlite3"
```

This intentionally remains synthetic-only. It fixes the misleading implicit fallback behavior when code is deployed but cannot provide authorized real-data parity by itself. Requirements and current architecture remain unchanged; use a tested Python/package environment compatible with requirements/lock and rerun acceptance after a runtime change.

## Approved private real-data hosting, after permission

Recommended: bank-approved private machine/container/VM with actual access restrictions, private encrypted artifact storage and a private mounted directory at `<repository>/private_data/`. Data retrieval/provisioning occurs through the bank's approved operational process, not a new public download endpoint. No object-store credentials, fetch client or public artifact was added. Streamlit secrets cannot materialize a missing CSV merely by naming it. Community Cloud source-only deployment will still need an authorized provisioning mechanism; this phase does not assert one exists.

Only after written approval, prepare a separate release copy of the validated feature CSV and its adjacent `customer_features.manifest.json`; add a reviewed dataset_version to that release manifest without altering canonical local inputs. Retain its schema/builder/event definition, source/feature SHA, cutoff and population validation. Pin that exact release version and SHA. Dataset size is small enough for a file artifact but public Git distribution remains prohibited absent explicit written permission. Prefer private mounted delivery over committing it, even after approved hosting.

```toml
DATA_MODE = "DEPLOYED"
BANCINC_RUNTIME = "CLOUD"
BANCINC_FEATURES_PATH = "private_data/customer_features.csv"
DATA_SHA256 = "<approved exact 64-character lowercase SHA-256>"
DATA_VERSION = "<approved version matching release manifest dataset_version>"
DATA_RELEASE_APPROVAL_REFERENCE = "<reviewed written approval reference>"
DATA_ACCESS_SCOPE = "PRIVATE_HOST"
BANCINC_ALIAS_KEY_HEX = "<private stable 64-character hex key>"
BANCINC_AUDIT_DB = "outputs/cloud_review.sqlite3"
```

The placeholders are not usable credentials or permission. PRIVATE_HOST requires real host access restrictions; this setting supplies none. PUBLIC_APPROVED is accepted only for a release/audience actually authorized for public access, not as a workaround. No such approval was verified here. Do not transfer the local alias key without authorization; a new approved deployment can use its own stable secret, producing different aliases while preserving counts. Cross-environment alias equality requires the same key and authorized handling of it.

If deploying on an approved private host with genuinely retained storage, the filesystem/backup guarantee must be verified independently. CLOUD UI remains conservative and labels SQLite ephemeral. It is unsuitable as a production or multi-tenant audit service. Events may disappear on cloud redeploy; demo actor selection is unverified; no financial approval or communication is performed.

## Acceptance after the authorized deployment

1. Confirm configured commit/entry point and runtime mode. Missing/invalid configuration must error explicitly, never show fake portfolio counts.
2. Verify artifact SHA and dataset_version privately against the approved release; inspect the live provenance view.
3. Independently recompute all-customer engine counts, comparing with authorized local evidence. Current reference is 50,000 / 2,052 / 20 / 47,928; do not code these as outputs.
4. Check all nine pages, alias selection, six-gate Passport, supported queue, Pending KYC simulation/reset and real-vs-simulation labels.
5. Inspect UI tables for raw identifiers/source fields and avoid personal information in reasons. Do not expose raw files/download endpoints.
6. Confirm the EPHEMERAL CLOUD warning, fresh database initialization and no assertion of production identity or restart durability.
7. Record live screenshots and outcomes privately. Cloud parity remains unverified until this is completed; local emulation does not substitute for it.

Local reproduction: `.venv/bin/python scripts/verify_deployment_parity.py --out outputs/phase6/parity-new`; choose a new directory. It only makes an ignored local copy and isolated database; its test approval marker is explicitly NOT a release authorization. Run `.venv/bin/python -m pytest -v -ra --junitxml=outputs/phase6/tests.xml` for regression.
