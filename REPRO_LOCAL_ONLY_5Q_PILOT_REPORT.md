# REPRO_LOCAL_ONLY_001 — RealScholarQuery 5-query pilot

## Outcome

The pilot did not complete all five queries. Q0–Q2 completed successfully. Q3 raised three CUDA out-of-memory exceptions inside `PaperAgent.do_expand` worker threads. PaSa's thread runner did not propagate those exceptions to the main thread, so the temporary runner initially wrote `PASS` and the orchestrator began loading Q4. Q4 was interrupted as soon as the hidden Q3 failures were detected; it did not enter Search and made no Serper call.

`FIVE_QUERY_PILOT=FAIL`

`READY_FOR_REALScholarQuery_50=NO`

`REMAINING_ISSUES=Q3 worker-thread CUDA OOM; worker exceptions do not propagate to the main thread; Q1 and Q3 approach the 40 GB GPU limit; local-only resolution directly skipped at least two Q1 GT citation titles; no fixed random seed is configured.`

No arXiv HTML or API title-search request was made. The source patch remained `REPRO_LOCAL_ONLY_001`; Crawler, Selector, prompts, checkpoints, generation parameters, search query count, expansion depth, and resolver semantics were unchanged.

## Per-query results

Metrics use the repository's evaluation semantics: titles are normalized with `keep_letters`, all unique paper nodes form the Crawler set, and nodes with `select_score > 0.5` form the final set.

| Query | GT | Crawler GT | Final GT | Precision | Recall | F1 | Search nodes | Expand nodes | Local lookups | Hits | Misses | Ambiguous | Hit rate | Online title requests | Serper | Latency | Peak GPU MiB (physical 1 / 2) | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| RealScholarQuery_0 | 9 | 7 | 6 | 0.3529 | 0.6667 | 0.4615 | 29 | 511 | 1452 | 1008 | 440 | 4 | 69.42% | 0 | 5 | 90.970 s | 31582 / 36322 | PASS |
| RealScholarQuery_1 | 29 | 17 | 16 | 0.5714 | 0.5517 | 0.5614 | 27 | 566 | 1721 | 1282 | 435 | 4 | 74.49% | 0 | 5 | 88.673 s | 39650 / 40268 | PASS |
| RealScholarQuery_2 | 21 | 14 | 14 | 0.7000 | 0.6667 | 0.6829 | 26 | 415 | 1432 | 1221 | 204 | 7 | 85.27% | 0 | 5 | 60.793 s | 25698 / 29146 | PASS |
| RealScholarQuery_3 | 42 | 20* | 20* | 0.3846* | 0.4762* | 0.4255* | 36* | 668* | 2448* | 1914* | 517* | 17* | 78.19%* | 0 | 5 | 100.071 s | 39014 / 40372 | FAIL — 3 worker-thread OOMs |
| RealScholarQuery_4 | 44 | N/A | N/A | N/A | N/A | N/A | 0 | 0 | 0 | 0 | 0 | 0 | N/A | 0 | 0 | 10.991 s† | 10100 / 13306 | FAIL — aborted before Search |

`*` Q3 values describe the partial tree written after three expansion workers failed. They are invalid as evaluation results and are excluded from aggregates.

`†` Q4 time covers partial model loading only. No Q4 inference was run and no output tree was produced.

Requested key-value records:

```text
QUERY_ID=RealScholarQuery_0
GT_TOTAL=9
CRAWLER_GT_FOUND=7
FINAL_GT_FOUND=6
FINAL_PRECISION=0.3529
FINAL_RECALL=0.6667
FINAL_F1=0.4615
SEARCH_NODES=29
EXPAND_NODES=511
LOCAL_TITLE_LOOKUPS=1452
LOCAL_TITLE_HITS=1008
LOCAL_TITLE_MISSES=440
LOCAL_TITLE_AMBIGUOUS=4
LOCAL_TITLE_HIT_RATE=69.42%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=90.970s
PEAK_GPU_MEMORY=physical_1:31582MiB,physical_2:36322MiB
STATUS=PASS

QUERY_ID=RealScholarQuery_1
GT_TOTAL=29
CRAWLER_GT_FOUND=17
FINAL_GT_FOUND=16
FINAL_PRECISION=0.5714
FINAL_RECALL=0.5517
FINAL_F1=0.5614
SEARCH_NODES=27
EXPAND_NODES=566
LOCAL_TITLE_LOOKUPS=1721
LOCAL_TITLE_HITS=1282
LOCAL_TITLE_MISSES=435
LOCAL_TITLE_AMBIGUOUS=4
LOCAL_TITLE_HIT_RATE=74.49%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=88.673s
PEAK_GPU_MEMORY=physical_1:39650MiB,physical_2:40268MiB
STATUS=PASS

QUERY_ID=RealScholarQuery_2
GT_TOTAL=21
CRAWLER_GT_FOUND=14
FINAL_GT_FOUND=14
FINAL_PRECISION=0.7000
FINAL_RECALL=0.6667
FINAL_F1=0.6829
SEARCH_NODES=26
EXPAND_NODES=415
LOCAL_TITLE_LOOKUPS=1432
LOCAL_TITLE_HITS=1221
LOCAL_TITLE_MISSES=204
LOCAL_TITLE_AMBIGUOUS=7
LOCAL_TITLE_HIT_RATE=85.27%
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=60.793s
PEAK_GPU_MEMORY=physical_1:25698MiB,physical_2:29146MiB
STATUS=PASS

QUERY_ID=RealScholarQuery_3
GT_TOTAL=42
CRAWLER_GT_FOUND=20 (partial/invalid)
FINAL_GT_FOUND=20 (partial/invalid)
FINAL_PRECISION=0.3846 (partial/invalid)
FINAL_RECALL=0.4762 (partial/invalid)
FINAL_F1=0.4255 (partial/invalid)
SEARCH_NODES=36 (partial)
EXPAND_NODES=668 (partial)
LOCAL_TITLE_LOOKUPS=2448 (partial)
LOCAL_TITLE_HITS=1914 (partial)
LOCAL_TITLE_MISSES=517 (partial)
LOCAL_TITLE_AMBIGUOUS=17 (partial)
LOCAL_TITLE_HIT_RATE=78.19% (partial)
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
LATENCY=100.071s
PEAK_GPU_MEMORY=physical_1:39014MiB,physical_2:40372MiB
STATUS=FAIL

QUERY_ID=RealScholarQuery_4
GT_TOTAL=44
CRAWLER_GT_FOUND=N/A
FINAL_GT_FOUND=N/A
FINAL_PRECISION=N/A
FINAL_RECALL=N/A
FINAL_F1=N/A
SEARCH_NODES=0
EXPAND_NODES=0
LOCAL_TITLE_LOOKUPS=0
LOCAL_TITLE_HITS=0
LOCAL_TITLE_MISSES=0
LOCAL_TITLE_AMBIGUOUS=0
LOCAL_TITLE_HIT_RATE=N/A
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=0
LATENCY=N/A (10.991s partial model-loading process)
PEAK_GPU_MEMORY=physical_1:10100MiB,physical_2:13306MiB
STATUS=FAIL
```

## Valid partial aggregate (Q0–Q2 only)

There is no valid five-query aggregate because Q3 failed and Q4 was stopped. The following numbers cover only the three completed queries:

```text
VALID_QUERIES=3/5
TOTAL_GT=59
CRAWLER_GT_FOUND=38
FINAL_GT_FOUND=36
MACRO_PRECISION=0.5415
MACRO_RECALL=0.6284
MACRO_F1=0.5686
MICRO_PRECISION=0.5538
MICRO_RECALL=0.6102
MICRO_F1=0.5806
AVG_LATENCY=80.145s
P50_LATENCY=88.673s
MAX_LATENCY=90.970s
AVG_LOCAL_TITLE_HIT_RATE=76.39%
TOTAL_SERPER_CALLS=15
TOTAL_ONLINE_TITLE_REQUESTS=0
```

The repository's `metrics.py` independently reproduced the completed-query macro Crawler Recall/Precision/Recall as `0.6769 / 0.5415 / 0.6284`. Micro scores were calculated by summing TP/FP/FN over Q0–Q2.

## GPU lifecycle and failure

Each query used an independent Python process with `CUDA_VISIBLE_DEVICES=1,2`. Physical GPUs 1 and 2 were at 0 MiB before every query and returned to 0 MiB after Q0, Q1, Q2, and Q3. They also returned to 0 MiB after Q4 was interrupted, so there was no cross-query memory accumulation.

Q3 recorded three `torch.OutOfMemoryError` exceptions in `do_expand` workers. Requested allocations were 1.35 GiB, 1.01 GiB, and 3.38 GiB. The observed peak on physical GPU 2 was 40372 MiB. Q1 had already peaked at 40268 MiB, showing that this workload has very little headroom on 40 GB cards.

`PaperAgent.do_parallel` joins worker threads but does not inspect or re-raise their exceptions. This allowed Q3's main thread to finish and incorrectly mark the run as successful. The raw Q3 output must therefore not be used as a complete result.

## Local-only GT misses

There is direct evidence that local-only resolution caused at least two GT misses in the completed queries. During Q1, both titles below appeared in citation lookups, normalized exactly to missing GT titles, returned unresolved, and were skipped:

- `In-context Learning and Induction Heads` (12 lookup occurrences)
- `Transformers generalize differently from information stored in context vs in weights` (1 lookup occurrence)

Q0 and Q2 had no missing GT whose normalized title appeared directly in their unresolved citation-title logs. This does not rule out indirect losses caused by skipped intermediate citations.

The failed Q3 partial run contained three more direct unresolved GT titles (`Gemini: A Family of Highly Capable Multimodal Models`, `ImageBind: One Embedding Space to Bind Them All`, and `AudioCLIP: Extending CLIP to Image, Text and Audio`), but Q3 is excluded from valid metrics.

## Reproducibility and artifacts

No fixed seed mechanism exists in the current PaSa execution path, so `SEED=NOT_SET`. No seed or generation behavior was added for this pilot. All 20 Serper calls made by Q0–Q3 returned HTTP 200; Q4 made none.

- Raw result root: `/mnt/nvme3/chenyi/pasa/results/local-only-5q-pilot-20260910`
- Independent metric analysis: `/mnt/nvme3/chenyi/pasa/results/local-only-5q-pilot-20260910/analysis.json`
- Orchestrator log: `/mnt/nvme3/chenyi/tmp/pasa-local-only-5q/orchestrator.log`
- Q3 OOM log: `/mnt/nvme3/chenyi/pasa/results/local-only-5q-pilot-20260910/q3/run.log`
- Pre-run source diff: `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_LOCAL_ONLY_5Q_PILOT/source_diff_before.patch`

The 50-query run is not ready. A later, separately authorized diagnostic should first make worker failures visible to the controller and establish enough GPU-memory headroom without changing the requested model behavior.
