# Phase 7 design system

Canonical implementation: `design_system.py`. These are original BancABC-inspired **student prototype** working colors, not official or verified bank brand tokens. The UI explicitly says it is independent and not operated by BancABC.

## Tokens

| Role | Value |
| --- | --- |
| Primary banking blue | #1D3B6E |
| Secondary/navy | #10283F |
| Muted burgundy accent | #A85959 |
| Application background | #F4F7FB |
| Card surface | #FFFFFF |
| Primary text | #182B3B |
| Muted reading text | #526676 |
| Border | #DFE6ED |
| Sidebar secondary text | #BDCDDD |
| SUPPORTED chart/accent | #16877C |
| CAUTION chart/accent | #D39B35 |
| ABSTAIN chart/accent | #8292A3 |
| Error accent | #C64747 |

The proposed muted #687A89 was darkened for small text. Status fill/accent colors are not assumed safe for ordinary white text. Badges use paired accessible foreground/background tokens: supported #0D635B/#E9F5F2; caution #78500B/#FFF5DF; abstain #43566A/#EDF1F5; error #9C2929/#FCEEEE. Ten token foreground/background pairs have automated normal-text contrast checks of at least 4.5:1. This checks those pairs, not every native element or complete WCAG conformance.

Spacing scale: 4, 8, 12, 16, 24, 32, 48 px. Surface radius approximately 8–12 px. Subtle surface shadow only on KPI cards. Burgundy is reserved for identity/focus/change emphasis; semantic statuses retain their own palette.

## Typography

Offline stack: `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif`. Inter is preferred only if available on the user's machine; no font is downloaded. The inspected machine lacks a local Inter install. Bundled native icon fonts remain untouched.

Type scale: responsive page title 1.75–2.125rem; section title 1.35rem; KPI 2rem; body 1rem; captions .875rem; status .8125rem. Financial/statistical numerals use tabular figures. CSS sets reading text, captions, headings and controls consistently; chart text uses the same fallback family. Theme values in `.streamlit/config.toml` and the original SVG palette are generated from these tokens; a test checks theme/token agreement.

## Component rules

- Shared identity: original wordmark, independent-student disclaimer and explicit data-mode badge. No official-bank-operated or compliance claim.
- Native sidebar/navigation: retained, with wrapped labels, active blue surface and burgundy accent. Current cutoff and data/policy fingerprint snippets remain visible. Demo reviewer context is labeled unverified.
- KPI cards: existing native st.metric values/labels and wrapping containers; first population card is primary blue, status cards use semantic top borders. Counts come from the existing index, never constants. The Overview summarizes existing historical engagement, relationship activity and savings-gap evidence.
- Charts: original aggregates, high-contrast labels, actual customer-count annotations, semantic outcome labels and tooltips. Chart-data expanders remain. Value labels do not change source measurements. Long axes may shorten visually; full text remains available in data tables/tooltips.
- Passport: six responsive cards read existing gate strings/status/reasons/codes. PASS and CAUTION retain their names. Engine ABSTAIN is displayed as **BLOCK · ABSTAIN**, not converted to another engine outcome. PENDING is only a presentation mapping if supplied; no new engine state is generated. G6 PASS still means a required human-control rule passed, not completed bank authorization. Original gate table remains unchanged.
- Replay: unchanged baseline/result metrics, explicit transition, changed-field comparison and changed-gate table. Baseline is left; simulated values are right and tinted. On small screens the comparison stacks in that same order. Modified values are always labeled SIMULATED, non-actionable.
- Tables/forms: native components retained with consistent borders, minimum-height buttons, wrapping labels and focus rings. No controls or provenance warnings are hidden for style.

## Responsiveness and safety

The native Streamlit wrapping layout is retained. Gate grid has two columns on desktop and one below 900px; evidence comparisons stack below 600px. Header content clears the fixed Streamlit toolbar. Buttons wrap and primary layouts stay within viewport bounds. Wide data tables can scroll internally; their columns are not removed to force a narrow screenshot.

Keyboard focus uses a visible burgundy outline, with reduced-motion preference support. Status words and reason text communicate meaning beyond color. Raw strings interpolated into custom gate/replay HTML are escaped. No JavaScript, external CSS/fonts, banking API or new dependency is introduced. Content-based data/policy cache invalidation, review controls and audit persistence remain the existing implementation.
