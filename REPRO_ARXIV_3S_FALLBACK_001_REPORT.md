# REPRO_ARXIV_3S_FALLBACK_001

Date: 2026-09-09  
Query: `RealScholarQuery_0` only  
Status: **FAIL — stopped during Expand depth 0 after sustained HTTP 429 responses**

## Patch scope

Only the arXiv title fallback in `utils.py` was changed:

- all threads share one condition-based global request-start limiter;
- adjacent HTTP request starts must be at least three seconds apart;
- initial attempts and retries use the same limiter;
- each unique title has at most three total attempts: one initial request plus two retries;
- `ReadTimeout` and temporary `requests` connection errors are retried within that limit;
- HTTP 429 applies a six-second global cooldown, or the server's longer `Retry-After` value when present;
- timeout, retry, cooldown, minimum-spacing, and one-second-window statistics are recorded;
- patch marker: `REPRO_ARXIV_3S_FALLBACK_001`.

The existing local exact-title resolver remained unchanged. Crawler, Selector, prompts, checkpoints, generated-query count, expand depth, test sample, dtype, and attention backend were not changed.

## Pre-run verification

- A mocked two-thread test injected one `ReadTimeout` and one HTTP 429. Four resulting initial/retry starts had a minimum spacing of 3.000083 seconds and at most one start in every one-second window.
- Mock result: `http_requests=4`, `timeouts=1`, `http_429=1`, `retries=2`, `global_cooldowns=1`, `MOCK_LIMITER_TEST=PASS`.
- The temporary input contained exactly `RealScholarQuery_0`; the original 50-row dataset SHA-256 remained `b3b570411ce2399ce4ea145ba9b2d3d0048b248030edeeb44ba95a7e9dc575c2`.
- Only physical A100 GPUs 1 and 2 were exposed to the process.

## Inference outcome

Search completed successfully with five Serper calls and 34 search paper nodes. During Expand depth 0, arXiv returned 14 HTTP 200 responses and then entered a sustained rejection state. Progress snapshots showed:

```text
requests=17  HTTP_200=14  HTTP_429=3   timeouts=0
requests=22  HTTP_200=14  HTTP_429=7   timeouts=1
requests=27  HTTP_200=14  HTTP_429=11  timeouts=1
requests=31  HTTP_200=14  HTTP_429=15  timeouts=1
requests=36  HTTP_200=14  HTTP_429=18  timeouts=2
```

HTTP 200 never increased after reaching 14, while HTTP 429 rose continuously. The run was interrupted under the user's stop condition instead of allowing all queued titles to consume their retry limits.

The interruption snapshot contains 39 started requests: 14 completed with HTTP 200, 20 with HTTP 429, 3 with timeout, and 2 were still in flight when statistics were serialized. Thus HTTP 429 was 54.05% of the 37 completed requests. Non-daemon worker threads were then terminated, so a small number of post-snapshot in-flight attempts are not represented in the report counters.

## Requested metrics

```text
LOCAL_TITLE_LOOKUPS=640 (partial)
LOCAL_TITLE_HITS=471 (partial)
LOCAL_TITLE_HIT_RATE=73.59% (partial)
LOCAL_TITLE_MISSES=168 (partial)
LOCAL_TITLE_AMBIGUOUS=1 (partial)
ARXIV_FALLBACKS=169 (partial)
ARXIV_REQUESTS=39 started at interruption snapshot
HTTP_200=14
HTTP_429=20
TIMEOUTS=3
RETRIES=23
GLOBAL_COOLDOWNS=20
FINAL_LOOKUP_FAILURES=8 confirmed at snapshot; many lookups remained queued/in-flight
MIN_REQUEST_START_SPACING=3.00007198 seconds
MAX_REQUESTS_IN_ANY_1S_WINDOW=1
SEARCH_NODES=34
EXPAND_NODES=N/A (Expand depth 0 did not complete)
CRAWLER_GT_FOUND=N/A
FINAL_GT_FOUND=N/A
FINAL_PRECISION=N/A
FINAL_RECALL=N/A
FINAL_F1=N/A
LATENCY=286.828 seconds to controlled interruption
PEAK_GPU_MEMORY=physical GPU 1: 16322 MiB; physical GPU 2: 19938 MiB
SERPER_CALLS=5
OUTPUT_PATH=NONE (final tree was not serialized)
```

`FINAL_LOOKUP_FAILURES=8` is only the number finalized before interruption. It must not be interpreted as the expected final count: 169 fallback calls had been submitted, only 39 HTTP attempts had started, and many titles were still waiting or retrying.

## Assessment

- **Was the three-second global limiter effective?** Yes. Minimum observed spacing was 3.000072 seconds and every one-second window contained at most one request start. Retries could not bypass it.
- **Were 429 responses basically eliminated?** No. They became sustained after 14 successful HTTP responses and reached 20/37 completed requests at interruption.
- **Were timeouts acceptable after limited retry?** Not established. Three timeouts occurred and retry accounting worked, but the run could not complete because 429 dominated.
- **Was any GT definitively missed because of network fallback failure?** Cannot be determined from an incomplete Expand layer. No final paper tree or final ranking exists. None of the eight finalized failure titles proves a network-caused GT miss; unfinished lookups may include relevant papers.
- **Ready for a five-query pilot?** No. The single query did not complete under the stop condition, and the arXiv HTML endpoint remained unstable despite correctly enforced pacing and limited retries.

## Artifacts

- Partial smoke report: `/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-3s-fallback-001/smoke_report.json`
- Run log: `/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-3s-fallback-001/run.log`
- Patch-before status/diff: `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_ARXIV_3S_FALLBACK_001/before.status`, `before.diff`
- Patch-after status/diff: `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_ARXIV_3S_FALLBACK_001/after.status`, `after.diff`
- Mock limiter test: `/mnt/nvme3/chenyi/tmp/pasa-smoke/test_arxiv_3s_limiter.py`
- Single-query runner: `/mnt/nvme3/chenyi/tmp/pasa-smoke/smoke_runner_arxiv_3s.py`
