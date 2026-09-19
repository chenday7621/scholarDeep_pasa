# REPRO_RELIABILITY_PATCH_001

## 变更范围

本补丁只修改 `utils.search_arxiv_id_by_title()` 的网络可靠性及进程内统计：

- arXiv 标题请求 timeout：连接 5 秒、读取 30 秒。
- 最多 4 次请求（首次 + 3 次 retry），指数退避从 1 秒开始，并增加 0～0.25 秒 jitter。
- HTTP 429 存在 `Retry-After` 时优先使用该值。
- arXiv 标题请求使用进程级 `BoundedSemaphore(8)`。
- 使用原有标题规范化规则作为 key，增加 single-flight 和 `normalized_title -> arxiv_id / miss` 进程内缓存。
- 增加 lookup、unique、cache、HTTP、异常、retry、最终失败及失败标题统计。

未修改 Crawler/Selector、Prompt、checkpoint、attention backend、搜索词数量、Expand 深度、section 选择逻辑或测试样本。离线模拟验证中，全局活动请求峰值为 8；同一标题 10 个并发调用只有 1 个 owner，其余 9 个由 single-flight/cache 合并。`git diff --check` 通过。

补丁前后 Git 记录：

- `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_RELIABILITY_PATCH_001/before.status`
- `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_RELIABILITY_PATCH_001/before.diff`
- `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_RELIABILITY_PATCH_001/after.status`
- `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_RELIABILITY_PATCH_001/after.diff`

## 单条重跑

Query：

```text
Give me papers which show that using a smaller dataset in large language model pre-training can result in better models than using bigger datasets.
```

输入仍为 `/mnt/nvme3/chenyi/tmp/pasa-smoke/real_single.jsonl`，只有 1 行；原始 50 条数据集哈希校验通过。重跑结果：

- `/mnt/nvme3/chenyi/pasa/results/smoke-real-20260908-reliability-001/0.json`
- `/mnt/nvme3/chenyi/pasa/results/smoke-real-20260908-reliability-001/smoke_report.json`
- `/mnt/nvme3/chenyi/pasa/results/smoke-real-20260908-reliability-001/run.log`

## Before / After

| 指标 | Before | After |
|---|---:|---:|
| GT_TOTAL | 9 | 9 |
| Direct Search GT found | 1 | 1 |
| CRAWLER_GT_FOUND | 3 | 1 |
| FINAL_GT_FOUND | 2 | 1 |
| Final papers | 8 | 4 |
| Precision | 0.2500 | 0.2500 |
| Recall | 0.2222 | 0.1111 |
| F1 | 0.2353 | 0.1538 |
| Search queries / Expand layers | 5 / 2 | 5 / 2 |
| Search nodes / Expand nodes | 31 / 108 | 26 / 9 |
| Serper calls | 5 | 5 |
| Logical title lookup calls | 1379 | 884 |
| Unique normalized titles | 未记录 | 571 |
| Cache hits | 0（无缓存） | 313 |
| Actual arXiv title HTTP requests | 1379 | 2245 |
| HTTP 200 | 未单列 | 13 |
| HTTP 429 | 396 | 2148 |
| Connection reset | 814 | 0 |
| Remote disconnect | 12 | 1 |
| 其他请求错误 | 未单列 | 83（主要为 ReadTimeout） |
| Network failure attempts | 1222 | 2232 |
| Retry | 0 | 1674 |
| Unique final lookup failures | 未记录 | 562 / 571 |
| Latency | 95.547 s | 562.731 s |
| GPU peak（物理 GPU 1 / 2） | 19242 / 23010 MiB | 17924 / 21498 MiB |

After 的 cache hit rate 为 `313 / 884 = 35.41%`。但实际 HTTP 请求中 `2148 / 2245 = 95.68%` 返回 429；加上断连和其他请求错误后，失败尝试为 `2232 / 2245 = 99.42%`。571 个唯一标题只有 9 个最终解析成功，562 个被缓存为 miss。

## GT 与网络的直接影响

After 的 Crawler 只命中并最终保留：

- `How to Train Data-Efficient LLMs`

以下 GT 明确进入了 Citation title lookup，但在有限重试后最终记录为 HTTP 429，并且没有进入 Crawler 候选：

1. `When Less is More: Investigating Data Pruning for Pretraining LLMs at Scale`
2. `Deduplicating Training Data Makes Language Models Better`
3. `Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes`
4. `LESS: Selecting Influential Data for Targeted Instruction Tuning`

`How to Train Data-Efficient LLMs` 的引用标题 lookup 也最终为 429，但它已由直接 Search 找到，因此没有形成 GT miss。由此可确认本次至少 4 个最终 GT miss 直接经过失败的 title lookup 路径。

## 对比限制

两次运行的输入、模型、Prompt 和超参数相同，但 Crawler 生成的 5 条 search query 文本并不完全一致，Serper 返回的 Search 节点也从 31 变为 26。这说明模型执行或外部搜索结果存在运行间波动。因此 Crawler Recall 从 `3/9` 降至 `1/9` 不能全部作为补丁的因果效果；不过 4 个 GT 的最终 HTTP 429 是本次产物中可直接验证的网络漏失。

## 结论

- 网络失败没有基本消除。connection reset 几乎消失，但转化为持续、大量的 HTTP 429 和读取超时。
- Crawler Recall 从 `0.3333` 降至 `0.1111`；Citation Expand 只生成 9 个节点，补丁前为 108 个。
- 仍有至少 4 个 GT 明确经过最终失败的 title lookup，失败原因为 HTTP 429。
- 当前不具备运行 5-query pilot 的条件。继续扩大测试会消耗 Serper 配额、显著增加运行时间，同时得到受 arXiv 限流污染的低召回结果。

```text
PATCH_ID=REPRO_RELIABILITY_PATCH_001
GT_TOTAL=9
CRAWLER_GT_FOUND_BEFORE=3
CRAWLER_GT_FOUND_AFTER=1
FINAL_GT_FOUND_BEFORE=2
FINAL_GT_FOUND_AFTER=1
FINAL_PRECISION_BEFORE=0.2500
FINAL_PRECISION_AFTER=0.2500
FINAL_RECALL_BEFORE=0.2222
FINAL_RECALL_AFTER=0.1111
FINAL_F1_BEFORE=0.2353
FINAL_F1_AFTER=0.1538
ARXIV_TITLE_REQUESTS=2245
UNIQUE_TITLE_REQUESTS=571
CACHE_HITS=313
NETWORK_FAILURES=2232
RETRIES=1674
SEARCH_QUERIES=5
EXPAND_LAYERS=2
SERPER_CALLS=5
LATENCY=562.731s
PEAK_GPU_MEMORY=GPU1 17924 MiB; GPU2 21498 MiB
NETWORK_CAUSED_GT_MISS=4（可确认）
FIVE_QUERY_PILOT_READY=NO
```
