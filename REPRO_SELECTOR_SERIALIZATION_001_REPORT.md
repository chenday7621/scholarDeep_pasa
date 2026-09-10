# REPRO_SELECTOR_SERIALIZATION_001 — Q3 rerun report

## Result

Q3 completed successfully with the shared Selector GPU forward serialized. Both Expand layers completed, the observed maximum number of concurrent `selector.infer_score()` calls was 1, and no CUDA OOM or worker exception occurred. No batch-size, GPU-count, model, checkpoint, prompt, generation parameter, search-query count, expansion depth, or local-only resolver behavior was changed.

```text
STATUS=PASS
SELECTOR_SERIALIZATION_ACTIVE=YES
WORKER_EXCEPTION_PROPAGATION=PASS
SELECTOR_PROMPTS=907
SEARCH_NODES=34
EXPAND_NODES=873
LOCAL_TITLE_LOOKUPS=2325
LOCAL_TITLE_HIT_RATE=78.7097%
CUDA_OOM_COUNT=0
PEAK_GPU_MEMORY=physical_1:34188MiB,physical_2:37796MiB
LATENCY=122.527s
GT_TOTAL=42
CRAWLER_GT_FOUND=24
FINAL_GT_FOUND=24
FINAL_PRECISION=0.3871
FINAL_RECALL=0.5714
FINAL_F1=0.4615
```

Additional execution checks:

```text
PATCH_ID=REPRO_SELECTOR_SERIALIZATION_001
BASE_RESOLVER=REPRO_LOCAL_ONLY_001
SELECTOR_CALLS=59
SELECTOR_MAX_CONCURRENT=1
SELECTOR_MAX_BATCH_PROMPTS=107
EXPAND_LAYERS_COMPLETED=2
LOCAL_TITLE_HITS=1830
LOCAL_TITLE_MISSES=483
LOCAL_TITLE_AMBIGUOUS=12
ONLINE_TITLE_REQUESTS=0
SERPER_CALLS=5
SERPER_HTTP_200=5
WORKER_EXCEPTIONS=0
GPU_BEFORE=physical_1:0MiB,physical_2:0MiB
GPU_AFTER=physical_1:0MiB,physical_2:0MiB
GPU_RELEASED=YES
```

## Minimal patch

Only `paper_agent.py` was changed for this experiment:

1. A process-wide `SELECTOR_INFERENCE_LOCK` now protects the two existing calls to the shared `selector.infer_score()`, in Search and Expand. Worker preparation and title resolution remain concurrent; the prompt list passed by each call is unchanged.
2. `PaperAgent.do_parallel()` now wraps worker entry points, records worker exceptions, joins all workers, and re-raises the first original exception in the caller. A no-model preflight raised a custom exception in a child thread and verified that the main thread received it.

The patch is marked `REPRO_SELECTOR_SERIALIZATION_001`. `models.py`, model loading, dtype, attention backend, generation arguments, batch formation, score threshold, and candidate list construction were not changed.

## Previous Q3 comparison

The previous Q3 result is partial and invalid because three `do_expand` workers failed. Its retrieval metrics are shown only to describe how much work was missing.

| Metric | Previous Q3, concurrent and partial | Serialized Q3, complete | Change |
|---|---:|---:|---:|
| CUDA OOM | 3 | 0 | eliminated |
| Selector max concurrent | at least 2, maximum possible 20 | 1 | serialized |
| Selector prompts | 937 | 907 | -30 |
| Largest known batch | failed batches totaled 233; individual sizes unavailable | 107 | 107-prompt single batch passed |
| Search nodes | 36 | 34 | -2 |
| Expand nodes | 668, incomplete | 873, complete | +205 |
| Physical GPU 1 peak | 39014 MiB | 34188 MiB | -4826 MiB (-12.37%) |
| Physical GPU 2 peak | 40372 MiB | 37796 MiB | -2576 MiB (-6.38%) |
| Latency | 100.071 s, incomplete | 122.527 s, complete | +22.456 s |
| Crawler GT | 20/42, incomplete | 24/42 | complete result |
| Final GT | 20/42, incomplete | 24/42 | complete result |
| Precision | 0.3846, incomplete | 0.3871 | complete result |
| Recall | 0.4762, incomplete | 0.5714 | complete result |
| F1 | 0.4255, incomplete | 0.4615 | complete result |

The Torch allocator peaks also decreased:

| GPU | Previous allocated / reserved | Serialized allocated / reserved |
|---|---:|---:|
| Physical GPU 1 | 32800.8 / 38342.0 MiB | 26687.9 / 33556.0 MiB |
| Physical GPU 2 | 35284.0 / 39700.0 MiB | 30339.8 / 37164.0 MiB |

The rerun did not reproduce exactly the same retrieval workload: live Serper results and thread scheduling produced 34 Search nodes and 907 Selector prompts, compared with 36 and 937 previously. There is no fixed seed in this path. The controlled property relevant to the hypothesis is nevertheless clear: batch formation was not capped or split, the rerun contained a 107-prompt Selector batch, maximum in-flight Selector calls was measured as 1, both Expand layers completed, and GPU peaks fell by 2.5–4.7 GiB.

## Interpretation

This experiment strongly confirms that overlapping Selector forwards were the main cause of the earlier Q3 OOM. Serialization eliminated all OOMs while allowing a 107-prompt batch to complete, so the rerun provides no evidence that a single Selector batch is intrinsically too large for the two 40 GB cards. Memory fragmentation may still affect the exact peak, but it was not sufficient to cause failure once forward lifetimes stopped overlapping.

The exception-propagation fix also passed its dedicated no-model preflight. If a future worker raises CUDA OOM, `do_parallel()` will now re-raise it into the query's main control path, producing a nonzero runner exit and preventing a subsequent query from starting.

## Artifacts

- Output tree: `/mnt/nvme3/chenyi/pasa/results/selector-serialization-q3-20260910/0.json`
- Instrumentation report: `/mnt/nvme3/chenyi/pasa/results/selector-serialization-q3-20260910/smoke_report.json`
- Metric summary: `/mnt/nvme3/chenyi/pasa/results/selector-serialization-q3-20260910/metric_summary.json`
- Run log: `/mnt/nvme3/chenyi/pasa/results/selector-serialization-q3-20260910/run.log`
- Launcher state: `/mnt/nvme3/chenyi/pasa/results/selector-serialization-q3-20260910/launcher_state.json`
- Patch diff: `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_SELECTOR_SERIALIZATION_001/paper_agent_patch.patch`
