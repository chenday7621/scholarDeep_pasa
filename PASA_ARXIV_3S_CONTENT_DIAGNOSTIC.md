# PaSa arXiv Search 3-Second Diagnostic

Date: 2026-09-09  
Scope: independent network diagnostic only. No model was loaded, no RealScholarQuery inference was run, and no PaSa fallback source was modified.

## Preconditions

- The previous arXiv rate-limit activity was allowed to cool for about one hour.
- The recovery probe used the real Q0 local-miss title `Self-instruct: Aligning language models with self-generated instructions`.
- Probe result: HTTP 200, normal arXiv search template, three paper result nodes, latency 3.669241 seconds.
- The first formal request started more than three seconds after the recovery probe began.

The content check required HTTP 200, the normal arXiv Search HTML structure, and at least one `li.arxiv-result` paper entry with a parsed title. Empty but otherwise normal search pages are reported separately and are not counted as `CONTENT_VALID_200`.

## Test method

- Source: real citation titles from Q0 `REPRO_LOCAL_RESOLVER_001` local misses.
- Planned titles: 30 distinct titles.
- Execution: one thread, strictly serial, no retry.
- Minimum interval between request starts: three seconds.
- Early-stop rule: stop after three consecutive HTTP 429 responses.
- Each request records UTC timestamp, title, HTTP status, latency, timeout/error type, normal-page flag, result count, and content-valid flag.

## Result

The run stopped at request 21 after requests 19–21 returned three consecutive HTTP 429 responses.

```text
TEST_REQUESTS=21
PLANNED_REQUESTS=30
DIFFERENT_TITLES=21
REQUEST_INTERVAL=3 seconds
MIN_REQUEST_START_SPACING=3.000085 seconds
MAX_1S_REQUESTS=1
HTTP_200=15
HTTP_429=3
TIMEOUTS=3
REQUEST_ERRORS=0
FIRST_429_AT=request 19 (+69.487296 seconds)
NORMAL_SEARCH_PAGE_200=15
CONTENT_VALID_200=3
HTTP_200_NO_PAPER_RESULTS=12
THREE_SECOND_RATE_STABLE=NO
```

The three content-valid formal responses were:

- Request 11, `On the opportunities and risks of foundation models`: one result.
- Request 13, `Coresets and sketches`: four results.
- Request 15, `Open llm leaderboard`: five results.

The three timeouts occurred on requests 1, 3, and 9. All 15 HTTP 200 responses used the normal arXiv search-page structure; 12 displayed the normal no-results message rather than paper entries. HTTP 429 responses had no valid search content.

## Conclusion

The observed 429 responses cannot be attributed to a startup burst or a violation of the requested rate: request starts were at least 3.000085 seconds apart, and every one-second sliding window contained at most one start. Nevertheless, the endpoint began sustained rejection at formal request 19 and the test stopped after three consecutive 429 responses.

`THREE_SECOND_RATE_STABLE=NO`. A three-second interval alone is not sufficient for the current arXiv Search HTML endpoint and network path. This diagnostic makes no change to `REPRO_LOCAL_RESOLVER_001` or PaSa fallback behavior.

## Artifacts

- Recovery probe: `/mnt/nvme3/chenyi/tmp/pasa-3s-content-diagnostic/preflight.json`
- Per-request records: `/mnt/nvme3/chenyi/tmp/pasa-3s-content-diagnostic/requests.jsonl`
- Machine-readable summary: `/mnt/nvme3/chenyi/tmp/pasa-3s-content-diagnostic/summary.json`
- Run log: `/mnt/nvme3/chenyi/tmp/pasa-3s-content-diagnostic/run.log`
- Diagnostic script: `/mnt/nvme3/chenyi/tmp/pasa-3s-content-diagnostic/run.py`
