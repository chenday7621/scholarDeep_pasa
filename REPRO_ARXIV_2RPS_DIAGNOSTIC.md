# PaSa arXiv Fallback 2 RPS Diagnostic

Date: 2026-09-09  
Scope: network-only diagnostic using 60 real Q0 local-miss citation titles. No model was loaded and no inference was run.

## Method

- Source titles: the saved `failed_titles` from `/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-resolver-001/smoke_report.json`.
- Requests used the same arXiv title-search endpoint and query parameters as PaSa.
- Eight worker threads shared one process-wide limiter.
- The limiter serialized request starts and enforced at least 0.5 seconds between starts. The first request could start immediately; every subsequent request queued, so there was no startup burst.
- Each diagnostic item made one HTTP attempt. Retries were deliberately not added after persistent 429 responses appeared; no PaSa source patch was applied.
- `MAX_1S_REQUESTS` uses half-open sliding windows `[t, t+1s)` over every recorded request start.

## Result

```text
TEST_REQUESTS=60
ACTUAL_AVG_RPS=1.997939
MIN_REQUEST_SPACING=0.500507s
MAX_1S_REQUESTS=2
HTTP_200=14
HTTP_429=46
TIMEOUTS=0
OTHER_HTTP=0
REQUEST_ERRORS=0
RATE_LIMIT_WORKING=PASS
HTTP_429_RATE=76.67%
```

All request-window checks passed. The first 14 requests returned HTTP 200, covering start offsets 0.000378–6.507096 seconds. The first HTTP 429 occurred at 7.007614 seconds. Every remaining request, sequences 14–59, returned HTTP 429. This is sustained rate limiting rather than a small number of transient responses.

## Decision

The global 2 RPS limiter works, but 429 responses did not basically disappear. The user-defined stop condition therefore applies:

```text
PASA_FALLBACK_PATCH_APPLIED=NO
REALSCHOLARQUERY_0_RERUN=NO
MODEL_LOADED=NO
```

The existing `REPRO_LOCAL_RESOLVER_001` source remains unchanged by this diagnostic. Applying the tested 2 RPS limiter would make request spacing deterministic, but this result does not support running inference because 46/60 requests were rejected.

## Artifacts

- Per-request timestamps and outcomes: `/mnt/nvme3/chenyi/tmp/pasa-rate-limit-2rps/requests.jsonl`
- Machine-readable summary: `/mnt/nvme3/chenyi/tmp/pasa-rate-limit-2rps/summary.json`
- Console log: `/mnt/nvme3/chenyi/tmp/pasa-rate-limit-2rps/diagnose.log`
- Standalone diagnostic script: `/mnt/nvme3/chenyi/tmp/pasa-rate-limit-2rps/diagnose.py`
