# Phase 7 visual audit

Audit date: 2026-11-18, Africa/Harare. This phase refines the existing nine-view Streamlit application; it does not rebuild the interface or change banking logic. Baseline: **291 tests passed in 65.41s** before visual edits. The local feature artifact remains 50,000 records; its rule outcomes are checked again in final preservation evidence.

## Evidence inspected before refinement

Inspected `.streamlit/config.toml`, `app.py`, `ui_shell.py`, `ui_components.py`, all render functions/routes in `ui_views.py` and `views/`, and existing Phase 3/6 visual reports and screenshot sets. The Phase 6 Executive Overview screenshot was visually inspected. Current metric, chart, table, filter, gate and replay implementations were read before edits. Existing browser evidence already covered nine desktop pages and a 768px overview; that did not establish 390px usability or a complete four-width visual regression.

## Findings and response

| Existing weakness | Consequence | Refinement |
| --- | --- | --- |
| Equal-weight outlined KPIs, mostly teal chart accents | Weak first-screen hierarchy | Banking-blue identity, primary population card, semantic status borders, consistent white surfaces |
| Theme and chart colors repeated in Python, TOML and SVG | Styling can drift | Canonical design_system.py tokens; generated theme/SVG values and token-consistency test |
| Broad titles/captions without a complete type/focus system | Uneven reading hierarchy | System font stack with tabular numerals, shared type scale, explicit caption contrast, visible keyboard focus |
| No prominent independent-student identity | Possible confusion about ownership | Header/sidebar explicitly identify an independent student hackathon prototype, not operated by BancABC |
| Mode/data/policy context distributed unevenly | Hard to explain evidence status during a demo | LOCAL/DEPLOYED/DEMO identity badge; cutoff and data/policy fingerprints in shared sidebar; unverified reviewer context |
| Passport gate table is horizontally dense | Six-gate reasoning is slower to scan | Six escaped engine-derived cards with status, reason and code, retaining original table and data |
| Replay changes mostly expressed by a table and final metrics | Changes are less obvious | Explicit outcome-transition banner and labeled left-baseline/right-simulation evidence comparison |
| Small or very imbalanced bars | Tiny CAUTION category is difficult to read | Actual count labels alongside bars; unchanged accessible chart-data tables |
| Long sidebar labels and header padding | Truncation/overlap at some layouts | Wrapped navigation labels, header clearance and bounded mobile layouts |

## Inspection-driven corrections

The first actual refined screenshot revealed custom identity content underneath Streamlit's fixed header. Main content padding was corrected before final validation. Browser DOM inspection also showed native navigation labels were spans, so their wrapping selector was corrected without using generated Emotion class names. Caption and heading selectors were scoped to the main/sidebar surfaces; chart rendering now uses the explicit local palette rather than an overriding Streamlit chart theme. These are visual corrections, not permission or navigation changes.

## Boundaries

The proposed colors are student design choices, not verified official BancABC tokens. The existing original Banc-Inc360 SVG was recolored; no bank logo, proprietary asset or proprietary font was copied. Inter is not installed in the inspected local font folders; the application prefers it if locally available and falls back to operating-system fonts. No external font request or dependency was added.

Competition data remains private. All screenshots use aliases and permitted derived presentation values, remain under ignored outputs, and require review before external sharing. This audit/refinement is not accessibility, security, regulatory or bank endorsement certification. Desktop/tablet/mobile results and exact final tests are recorded separately in PHASE_7_VISUAL_VALIDATION.md.
