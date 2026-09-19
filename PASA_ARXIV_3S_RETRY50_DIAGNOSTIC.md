# PaSa arXiv Search 3-Second Retry-50 Diagnostic

Date: 2026-09-09  
Scope: independent network diagnostic only. No model or RealScholarQuery inference was run, and no PaSa fallback source was modified.

## Protocol

- The test reused the same 30 distinct real Q0 local-miss titles as the preceding 3-second diagnostic.
- A recovery probe first used `Self-instruct: Aligning language models with self-generated instructions` and returned HTTP 200, a normal arXiv Search page, and three paper results.
- All initial requests and any HTTP 429 retries shared one serial schedule with at least three seconds between request starts.
- An HTTP 429 would retry the same title up to 50 additional times. Timeouts and other errors were not retried because the requested retry condition was specifically HTTP 429.
- The test would stop if all 50 retries for one title still returned 429.

## Result

All 30 different titles were attempted. This run produced no HTTP 429, so the retry branch was not exercised.

```text
TEST_REQUESTS=30
DISTINCT_TITLES=30
REQUEST_INTERVAL=3 seconds
MIN_REQUEST_START_SPACING=3.000149 seconds
ACTUAL_AVG_START_RPS=0.273294
MAX_1S_REQUESTS=1
HTTP_200=21
HTTP_429=0
TIMEOUTS=9
REQUEST_ERRORS=0
FIRST_429_AT=NONE
RETRY_REQUESTS=0
RETRY_HTTP_200=0
RETRY_HTTP_429=0
CONTENT_VALID_200=5
NORMAL_SEARCH_PAGE_200=21
HTTP_200_NO_PAPER_RESULTS=16
STOPPED_AFTER_50_RETRIES=NO
THREE_SECOND_RATE_429_FREE_THIS_RUN=YES
OVERALL_REQUEST_SUCCESS_STABLE=NO
```

The last request began at +106.112751 seconds and completed at approximately +111.202781 seconds. All 21 HTTP 200 responses used the normal arXiv Search HTML structure. Five contained paper results and 16 were normal no-results pages. Nine requests ended with `ReadTimeout`; no timeout was counted as HTTP 200 or HTTP 429.

## Interpretation

This repeat is 429-free under a strict three-second schedule, unlike the preceding run, which reached three consecutive 429 responses at requests 19–21. The result shows that three-second pacing can complete 30 titles without 429 after a suitable cooldown, but it does not establish long-run stability because:

- the retry behavior was not observable when no 429 occurred;
- 9/30 requests timed out;
- two otherwise equivalent runs produced different 429 outcomes.

Therefore the narrow result is `THREE_SECOND_RATE_429_FREE_THIS_RUN=YES`; end-to-end fallback reliability remains unproven. No source patch or model run follows from this diagnostic.

## Artifacts

- Recovery probe: `/mnt/nvme3/chenyi/tmp/pasa-3s-retry50-diagnostic/preflight.json`
- Per-request records: `/mnt/nvme3/chenyi/tmp/pasa-3s-retry50-diagnostic/requests.jsonl`
- Machine-readable summary: `/mnt/nvme3/chenyi/tmp/pasa-3s-retry50-diagnostic/summary.json`
- Run log: `/mnt/nvme3/chenyi/tmp/pasa-3s-retry50-diagnostic/run.log`
- Diagnostic script: `/mnt/nvme3/chenyi/tmp/pasa-3s-retry50-diagnostic/run.py`
