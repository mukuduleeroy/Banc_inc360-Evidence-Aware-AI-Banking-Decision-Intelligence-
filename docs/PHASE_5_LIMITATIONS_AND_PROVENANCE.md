# Phase 5 limitations and provenance

## Preserved authority

The application still uses the existing six-gate deterministic rules. Canonical 50,000-row CSV SHA-256: `a66035aade8bf2aa7be0bb4f50481211391ffe9473bce8b3afc60b9400498993`. Source ZIP fingerprint: `4a7919a7a98f8340d2d7589ec8cfdbe352742686df97cb6e8d6bd58d93fd4e1b`. Current policy: `fb55bf63040711dd15f03005cd298472743899c186e59315396422a0d970f1ae`. The final preservation report compares all eight protected Phase 4 artifacts, alias-key hash and existing audit summaries. No experimental model is imported by the engine, eligibility index or review service.

## What the evaluation establishes

Point-in-time reconstruction and observed 90-day inactivity labels are reproducible from the available extract. It does not establish account closure, future real-world churn, calibrated probabilities, product interest, uplift, fairness, affordability or profitability. Eligibility is at least two prior-180-day events; customers outside it are not scored in the experiment. Current portfolio outcomes still cover all 50,000 customers under the engine's distinct thresholds.

All holdout customers also occur in training at an earlier cutoff. No random row split is used, but this is not unseen-customer generalization. January prevalence 19.44% versus July 59.33% indicates substantial shift. Fixed 20/21 total transaction rows and repeated deterministic-looking patterns limit trust in predictive scores outside this competition dataset. Event timestamps are available, ingestion timestamps/timezone are not. Future coverage is observed, not independently certified complete.

The original setup request and submission evidence document contain reported concept metrics. Their original executable training run is unavailable. Recency reproduces at stated rounding. The new explicit five-feature, scaled logistic experiment differs materially; its result must not replace the old claim without explaining the changed/unavailable original specification. AP and trapezoidal PR area are separately labeled. Bootstrap intervals are conditional on frozen predictions in one extract; they are not production uncertainty guarantees.

## Historical and snapshot separation

Only recency, qualifying counts, absolute volume and deposit-event history enter evaluated predictors. Current customer/account/KYC status, holdings, account breadth, service issues, income, balances and last-transaction snapshots are excluded. Their effective dates remain unknown. They are current suitability inputs in the rules, never reconstructed historical facts.

## Evidence and audit boundaries

Raw source transaction IDs exist, but the application's canonical feature artifact has no verified event-to-feature mapping. Audit evidence remains FEATURE_LEVEL, with derivations, cutoff and hashes; no transaction-level replay or invented event IDs. Historical evaluation aggregation is not an implemented transaction drilldown in the app.

SQLite append-only triggers and snapshot hashes protect application workflow integrity; they are not tamper-proof against the database owner. Storage is unencrypted and no retention enforcement or production access control is implemented. Explicit demo reviewer identifiers are unverified attribution, not authentication. Free-text reasons can contain accidental PII and require care. Stable keyed aliases are pseudonyms; preserve and restrict the private key and backups.

No live banking APIs, automatic outreach, credit/insurance approvals or regulatory compliance claims. No customer communications were sent during acceptance. Absence of an external action integration plus explicit false authorization/outreach flags supports this scope; it is not a general malware/network security certification.

## Package and sharing boundary

All datasets, SQLite/WAL/SHM, keys, wheels and generated evidence remain ignored under outputs. The presentation package excludes raw source/customer tables, databases, individual prediction exports and keys. Screenshots contain aliases and permitted derived values; review them before any external sharing. No automatic publishing or Git commit was performed.

Runtime environment remains Python 3.9.6/Streamlit 1.50.0. Optional evaluation versions are pinned separately; the app's dependency contract is preserved. Future production work needs a supported runtime refresh, bank-reviewed timestamped input and transaction semantics, source lineage, external validation, authenticated access, approved retention and independently protected audit storage.
