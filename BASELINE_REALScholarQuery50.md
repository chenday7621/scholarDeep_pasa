# RealScholarQuery-50 reproduction baseline

## Purpose

This document freezes the first complete RealScholarQuery-50 reproduction baseline used in this checkout. It is the reference point for subsequent error analysis and targeted optimization experiments.

This is a **reproduction baseline**, not a completely untouched execution of the upstream PaSa repository. The model behavior and retrieval policy were kept fixed, while narrowly scoped infrastructure patches were applied so the benchmark could complete reliably on the available machine.

## Dataset and evaluation semantics

- Dataset: `data/RealScholarQuery/test.jsonl`, Q0 through Q49.
- Valid queries: 50; failed queries: 0.
- The source file contains 791 answer annotations. Q45 contains two formatting variants that collapse to the same normalized title, so evaluation contains 790 unique GT titles.
- Title comparison follows the repository `metrics.py` semantics through `keep_letters` normalization.
- A paper is in the final result when `select_score > 0.5`.
- Crawler GT includes matching papers found in either Search or Citation Expand nodes, regardless of the final Selector decision.
- Macro metrics average the per-query values and weight each query equally.
- Micro metrics pool TP, FP, and FN over all 50 queries and therefore give queries with more GT papers more weight.
- `CRAWLER_RECALL` is the official macro-average Crawler recall. `MICRO_CRAWLER_RECALL` is `404 / 790`.

## Frozen configuration

```text
DATASET=RealScholarQuery test Q0-Q49
VALID_QUERIES=50
SEED=42
PATCHES=REPRO_LOCAL_ONLY_001,REPRO_SELECTOR_SERIALIZATION_001
ONLINE_TITLE_REQUESTS=0
EXPAND_LAYERS=2
SEARCH_QUERIES=5
SEARCH_PAPERS=10
EXPAND_PAPERS=20
THREADS_NUM=20
QUERY_EXECUTION=one independent Python process per query, Q0 to Q49 serially
SELECTOR_GPU_FORWARD=serialized
SERPER_MODE=live with complete response recording
```

The seed was applied to `PYTHONHASHSEED`, Python `random`, NumPy, `torch`, `torch.cuda.manual_seed`, and `torch.cuda.manual_seed_all`. Official generation settings were not changed: no change was made to `do_sample`, temperature, top-p, top-k, or decoding mode.

Crawler and Selector used the official PaSa checkpoints stored locally at:

- `/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-crawler`
- `/mnt/nvme3/chenyi/pasa/checkpoints/pasa-7b-selector`

The Crawler model, Selector model, `agent_prompt.json`, checkpoints, title-selection threshold, Search strategy, Citation Expand strategy, and expand depth were not modified for effectiveness optimization.

`search_queries=5` is an upper bound in the official parser. Q18 and Q28 produced four parseable search queries, and the reproduction harness did not synthesize an additional query.

## Infrastructure patches relative to upstream PaSa

### Local exact title resolver: `REPRO_LOCAL_ONLY_001`

Citation expansion first normalizes a citation title with the same `keep_letters` rule used by evaluation, then looks it up in an in-process `normalized_title -> arXiv ID` index built from `id2paper.json`. A unique local match uses the existing local paper database. A local miss or ambiguous title is recorded as unresolved and skipped.

No fuzzy matching, alias matching, embedding retrieval, or non-arXiv filtering is enabled. No request is made to the arXiv HTML search or `export.arxiv.org` title API in this baseline.

This mode was introduced after repeated arXiv title-search HTTP 429 and connection failures made online Citation Expand lookup unstable. It changes the infrastructure available to Citation Expand and can reduce recall when a citation title is absent from the local database or differs from the indexed title.

### Selector serialization and worker exception propagation: `REPRO_SELECTOR_SERIALIZATION_001`

Expand workers retain their existing CPU-side concurrency, but all calls to the shared `selector.infer_score()` instance enter a global mutex before the GPU forward. This prevents overlapping Selector forwards from exceeding the memory of one A100 40GB GPU. Inputs, batch construction, scores, threshold, and candidate ordering logic were not intentionally changed.

Exceptions raised by worker threads are collected and re-raised in the main query thread. A CUDA OOM or another worker failure therefore marks the current query as failed and prevents the orchestrator from continuing silently.

### Other minimal correctness and secret-handling changes

- `run_paper_agent.py` passes `args.search_queries` to `PaperAgent` instead of the unrelated `args.expand_papers` value.
- The Serper key is read from `SERPER_API_KEY`; no key is stored in source, reports, replay files, or Git.
- The 50-query runner saved each successful query immediately, never overwrote a PASS result, checked GPU release before starting the next query, and could resume at the first query without a valid PASS record.

## Effectiveness results

```text
TOTAL_GT=790
TOTAL_CRAWLER_GT_FOUND=404
TOTAL_FINAL_GT_FOUND=374

MACRO_PRECISION=0.3609
MACRO_RECALL=0.4535
MACRO_F1=0.3547

MICRO_PRECISION=0.3164
MICRO_RECALL=0.4734
MICRO_F1=0.3793

CRAWLER_RECALL=0.4947
MICRO_CRAWLER_RECALL=0.5114
```

The independent aggregation agrees with the repository `metrics.py` output. Its first three official values are Crawler Recall `0.4947`, Precision `0.3609`, and Recall `0.4535`.

## Execution efficiency

```text
AVG_SEARCH_NODES=28.06
AVG_EXPAND_NODES=428.16
AVG_SELECTOR_PROMPTS=456.22
AVG_LOCAL_TITLE_HIT_RATE=66.01%

TOTAL_SERPER_CALLS=248
MAX_GPU_MEMORY=38642MiB
OOM_QUERIES=0
FAILED_QUERIES=0

AVG_LATENCY=79.947s
P50_LATENCY=78.196s
P95_LATENCY=108.253s
MAX_LATENCY=126.798s
TOTAL_WALL_CLOCK=76.51 minutes
```

Across the benchmark, the resolver processed 64,810 citation-title lookups: 43,837 local hits, 20,786 misses, and 187 ambiguous titles. The weighted local hit rate was 67.64%; the reported 66.01% baseline metric is the mean of the 50 per-query hit rates.

## GPU memory and stability

- Hardware used: physical GPU 1 and GPU 2, both NVIDIA A100-PCIE-40GB.
- Maximum observed process memory: 38,642 MiB on GPU 2 during Q3.
- Selector maximum concurrent forward count: 1 for every query.
- CUDA OOM queries: 0.
- Worker-exception queries: 0.
- Failed queries: 0.
- Both Expand layers completed for all 50 queries.
- GPU 1 and GPU 2 returned to 0 MiB after every query process exited.

Q3 remains close to the 40GB device limit, so later experiments should retain the same failure and GPU-release gates.

## Serper requests and replay

The baseline used live Serper results. It made 248 HTTP requests, all of which returned HTTP 200. Each call has an individual replay record containing:

- RealScholarQuery ID;
- generated Crawler search query and its sequence number;
- request timestamp and latency;
- request payload without authentication headers;
- raw response body and parsed structured response;
- raw-response SHA-256.

The replay audit verified a one-to-one correspondence between all 248 calls and replay files. The API key and `X-API-KEY` header are not present in committed files or replay data.

Replay data is retained on the evaluation server because the full result bundle is an execution artifact rather than source code:

- `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/serper_replay_manifest.json`
- `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00` through `q49`, under each successful attempt's `serper_replay/` directory.

## GT miss stage decomposition

The 416 final GT misses were assigned mutually exclusive evidence-based stages:

| Stage | Count | Share |
|---|---:|---:|
| `CRAWLER_SEARCH_MISS` | 283 | 68.03% |
| `CITATION_EXPAND_MISS` | 68 | 16.35% |
| `LOCAL_RESOLVER_UNRESOLVED` | 35 | 8.41% |
| `SELECTOR_FALSE_NEGATIVE` | 30 | 7.21% |

`CRAWLER_SEARCH_MISS` means the GT title was absent from Search and Expand nodes, local unresolved attempts, and exact citation titles visible in the crawled sections. This establishes where it disappeared from the observed run, while its deeper cause can still be query generation, live search coverage, local ID/paper availability, or a path not reached by expansion.

`CITATION_EXPAND_MISS` means the exact normalized GT title appeared in a crawled paper's citation list but never became a node. `LOCAL_RESOLVER_UNRESOLVED` requires direct evidence that the GT title reached the local resolver and was skipped. `SELECTOR_FALSE_NEGATIVE` means a matching node existed but did not pass `select_score > 0.5`.

```text
MAIN_RECALL_BOTTLENECK=CRAWLER_SEARCH_MISS
```

## Known limitations

- Live Serper responses can change over time. `SEED=42` does not freeze external search results; the saved replay is required for controlled A/B comparison.
- Multithreaded Search and Expand work can still vary in scheduling even though Selector GPU forwards are serialized.
- PyTorch deterministic algorithms were not enabled because doing so was outside the frozen inference configuration.
- Local-only exact resolution intentionally drops citation titles that are absent, ambiguous, or formatted differently in the local index.
- The failure-stage classification is based on artifacts observable in this run. The 283 Crawler Search misses need finer replay-based decomposition before choosing an optimization.
- The uncompressed per-query result trees and replay payloads are stored outside Git. Their server-side paths are recorded below.

## Recommended next work

1. Use the saved Serper responses to separate query-generation misses from search-result, arXiv-ID, and local-paper availability misses without issuing new live searches.
2. Audit the 68 Citation Expand misses by parent paper, selected section, depth, and duplicate-ID suppression.
3. Review the 35 direct local-resolver misses for exact-title database coverage and formatting variants before proposing any resolver change.
4. Inspect the 30 Selector false negatives and their score margins. Keep this separate from retrieval-stage experiments.
5. Compare every future experiment against this commit, the frozen summary JSON, and the saved Serper replay.

## Artifacts

Committed documentation:

- `BASELINE_REALScholarQuery50.md` — frozen baseline definition and headline results.
- `REPRO_LOCAL_ONLY_50Q_BASELINE_REPORT.md` — full per-query metrics and all GT miss classifications.
- `REPRO_LOCAL_ONLY_001_REPORT.md` — local-only resolver validation.
- `REPRO_SELECTOR_SERIALIZATION_001_REPORT.md` — Q3 serialization/OOM validation.

Server-side machine-readable and raw artifacts, intentionally excluded from Git:

- Summary JSON: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/summary.json`
- Completion audit: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/completion_audit.json`
- Orchestrator state: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/orchestrator_state.json`
- Official metrics output: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/official_metrics.txt`
- Serper replay manifest: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/serper_replay_manifest.json`
- Per-query outputs and replay: `/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910/q00` through `q49`
- Pre-run provenance, Git diff, hashes, environment and GPU inventory: `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_LOCAL_ONLY_50Q_BASELINE_SEED_42`

The completion audit passed all checks: exactly Q0-Q49, 50 valid PASS results, source hashes unchanged, tracked diff unchanged throughout execution, 248 complete replay records, zero online title requests, zero OOM, zero worker exceptions, and GPU release after every query.
