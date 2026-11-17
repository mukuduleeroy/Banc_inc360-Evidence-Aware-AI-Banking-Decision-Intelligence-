# Phase 5 measured performance and reliability

Measured locally on 2026-11-16, existing macOS arm64 Python 3.9.6 environment, 50,000 customer rows. These are small local measurements, not an SLA, load test or browser network latency guarantee.

| Operation | Median seconds | Samples |
| --- | ---: | ---: |
| Feature CSV read | 0.057335 | 1 |
| Cold validated decision-index build | 7.268861 | 1 |
| Cached validated index load | 0.006315 | 5 |
| First Overview AppTest, after index is warm | 2.157544 | 1 |
| Warm Overview AppTest rerun | 0.277720 | 3 |
| Queue filter computation | 0.006088 | 10 |
| Queue page computation | 0.005438 | 10 |
| Queue filter AppTest rerun | 0.084268 | 3 |
| Queue page AppTest rerun | 0.084962 | 3 |
| Customer passport computation | 0.000217 | 10 |
| Customer 360 AppTest render | 0.088523 | 3 |
| Fresh case open and snapshot | 0.031275 | 1 |
| Current-evidence revalidation and review write | 0.029624 | 1 |
| Cold server spawn to healthy HTTP endpoint | 0.477298 | 1 |
| Server restart to healthy HTTP endpoint | 0.628650 | 1 |

Cold server health does not mean the initial browser page is fully rendered. CSV read timing is a separate pandas read, and the cold index measurement includes its own read/validation/evaluation; these overlapping measurements must not be summed as independent pipeline stages. AppTest measurements run after warming the index; the first overview also initializes descriptive aggregates. AppTest times exclude browser paint/network. Queue and customer computation timings are distinct from their UI reruns. Review timings include actual local SQLite commits and source revalidation, using temporary databases.

The existing content-aware cache is effective: the cold index takes about 7.27s, while a same-process validated cached load is about 6ms. Warm UI reruns are below .30s in this sample. No application bottleneck requiring a code rewrite was demonstrated, so engine, cache, analytics and data builder were preserved. The evaluation CLI avoids unavailable physical-core discovery and keeps fitting numerically single-threaded; this is an experiment runtime setting, not a change to banking logic.

Commands: `.venv/bin/python scripts/measure_phase5.py`; `.venv/bin/python scripts/accept_phase5.py --out outputs/phase5/acceptance-new`. The latter requires existing local Chrome and Node plus permission to bind localhost; it creates an unused acceptance directory and cleans up only its own processes. Existing presentation records are never reset by measurements.

Raw samples: `outputs/phase5/performance.json`; server startup measurements and restart evidence: `outputs/phase5/acceptance_verified/acceptance.json`. All nine pages rendered without application exceptions; replay/reset and committed review persistence passed. No new app dependency or caching redesign was introduced.
