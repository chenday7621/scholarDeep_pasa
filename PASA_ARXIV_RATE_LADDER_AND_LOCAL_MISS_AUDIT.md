# PaSa arXiv Rate Ladder and Local Miss Audit

Date: 2026-09-09  
Scope: network-only arXiv Search HTML diagnostics followed by an offline audit of the existing Q0 local-title misses. No model was loaded, no RealScholarQuery inference was run, and no PaSa source, prompt, checkpoint, or dataset was modified.

## Rate ladder method

- Titles came from the saved Q0 `REPRO_LOCAL_RESOLVER_001` real local-miss list.
- Each tier used a different slice of titles and made serial requests to the same arXiv title-search HTML endpoint used by PaSa.
- A separate recovery probe had to return HTTP 200 before a tier could start. Recovery probes are not included in tier request counts.
- Request starts were separated by at least the target interval. There was no startup burst and no retry traffic.
- A tier stopped immediately after three consecutive HTTP 429 responses.
- `MAX_1S_REQUESTS` uses a half-open sliding window `[t, t + 1 second)` over request-start timestamps.

## Rate ladder result

| Test rate | Requests made | HTTP 200 | HTTP 429 | Timeouts | Other request errors | First 429 | Max starts in any 1s window | Minimum spacing |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| 1 request / 1 second | 25/30 | 18 | 3 | 2 | 2 SSL errors | request 23, +63.630s | 1 | 1.000059s |
| 1 request / 2 seconds | 17/30 | 14 | 3 | 0 | 0 | request 15, +41.406s | 1 | 2.000061s |
| 1 request / 3 seconds | 17/30 | 14 | 3 | 0 | 0 | request 15, +47.884s | 1 | 3.000137s |

All three limiters behaved correctly. All three tiers nevertheless reached three consecutive 429 responses and stopped early. The 2-second and 3-second tiers both returned exactly 14 successful formal requests before the first 429. Including the successful recovery probe, each recovery period allowed 15 observed HTTP 200 responses before sustained 429 began.

The first 3-second recovery probe, made about 167 seconds after the preceding tier's last 429, still returned 429. After a longer no-request cooldown, a later probe returned 200 and the tier was allowed to begin. This supports a cumulative quota/cooldown interpretation rather than an instantaneous-RPS-only limit. It does not establish the server's exact quota algorithm.

```text
TEST_RATE=1 request / 1 second
REQUESTS=25
HTTP_200=18
HTTP_429=3
TIMEOUTS=2
FIRST_429_AT=request 23 (+63.630s)
MAX_1S_REQUESTS=1

TEST_RATE=1 request / 2 seconds
REQUESTS=17
HTTP_200=14
HTTP_429=3
TIMEOUTS=0
FIRST_429_AT=request 15 (+41.406s)
MAX_1S_REQUESTS=1

TEST_RATE=1 request / 3 seconds
REQUESTS=17
HTTP_200=14
HTTP_429=3
TIMEOUTS=0
FIRST_429_AT=request 15 (+47.884s)
MAX_1S_REQUESTS=1
```

`STABLE_RATE=NONE_OF_TESTED_RATES`

## Q0 LOCAL_TITLE_MISS composition

The saved Q0 run contains 329 local-miss calls representing 224 unique fallback cache keys after excluding its two separately counted ambiguous lookups.

The old instrumentation stored aggregate counters and unique final-failure titles rather than every repeated call. The output tree reconstructs 274 calls exactly. Cache-key reconciliation identifies another 24 titles that must each occur at least once. The remaining 31 calls are known repeats, but their titles cannot be assigned uniquely from saved artifacts and are therefore classified as `OTHER`.

Classification uses only local `id2paper.json`, `cs_paper_2nd.zip`, the saved Q0 output, and citation text. Local similarity checks were used for audit only; no fuzzy matching was added to PaSa.

| Category | Calls | Percentage | Unique known keys | Examples |
|---|---:|---:|---:|---|
| `NOT_IN_LOCAL_DB` | 113 | 34.35% | 87 | `Mamba: Linear-time sequence modeling with selective state spaces`; `Gemini: A family of highly capable multimodal models`; `Self-RAG: Learning to retrieve, generate, and critique through self-reflection` |
| `TITLE_VARIANT` | 42 | 12.77% | 33 | `ReAct...` versus local `\model...`; `Self-Instruct...` versus local `ACL 2023 Self-Instruct...`; `D2 Pruning...` versus local `𝔻² Pruning...`; Unicode `k` versus mathematical `𝑘` |
| `DIRTY_OR_INCOMPLETE` | 8 | 2.43% | 8 | `B`; `Borgeaud, A`; long author strings stored as titles; malformed `ZeRO-Offload` bibliography text |
| `NON_ARXIV` | 135 | 41.03% | 96 | `Common Crawl - commoncrawl.org`; `OpenAI: Introducing ChatGPT`; GitHub/model-card URLs; legal cases; legacy non-arXiv publications |
| `OTHER` | 31 | 9.42% | — | Repeated calls whose exact cache key was not serialized |
| **Total** | **329** | **100.00%** | **224** | |

The first four call counts are confirmed lower bounds; any of the 31 unresolved repeat calls could belong to them. The complete unique-key classification is 87 not in the local DB, 33 title variants, 8 dirty/incomplete citations, and 96 non-arXiv references.

## Conclusion and next step

```text
STABLE_RATE=NONE_OF_TESTED_RATES
LOCAL_MISS_TOTAL=329
NOT_IN_LOCAL_DB=113 (34.35%)
TITLE_VARIANT=42 (12.77%)
DIRTY_OR_INCOMPLETE=8 (2.43%)
NON_ARXIV=135 (41.03%)
OTHER=31 (9.42%)
NEXT_STEP_RECOMMENDATION=Do not run the 5-query pilot yet. Reduce fallback volume offline and treat the arXiv HTML endpoint as having a small cumulative request budget plus a long cooldown; then validate a quota-aware policy separately before model inference.
```

The evidence does not support applying a 1-, 2-, or 3-second global interval as a sufficient fix. A pure RPS limiter would still cause sustained 429 once the apparent cumulative allowance is exhausted.

## Artifacts

- Tier script: `/mnt/nvme3/chenyi/tmp/pasa-rate-ladder/run_tier.py`
- 1-second tier: `tier-1s.jsonl`, `tier-1s-summary.json`, `tier-1s.log`
- 2-second tier: `tier-2s.jsonl`, `tier-2s-summary.json`, `tier-2s.log`
- 3-second tier: `tier-3s.jsonl`, `tier-3s-summary.json`, `tier-3s.log`
- Recovery probes: `preflight-1s.json`, `preflight-2s.json`, `preflight-3s.json`, `preflight-3s-retry.json`
- Artifact directory: `/mnt/nvme3/chenyi/tmp/pasa-rate-ladder`
