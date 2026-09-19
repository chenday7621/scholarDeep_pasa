# REPRO_LOCAL_RESOLVER_001

## 修改范围

Citation Expand 的标题解析现在按以下顺序执行：

```text
引用标题
  -> keep_letters() 精确规范化
  -> 进程内 normalized_title -> arxiv_id 索引
  -> 唯一本地命中：直接读取本地 ZIP 论文
  -> miss / ambiguous：进入原有 arXiv title search fallback
```

未修改 Crawler、Selector、Prompt、checkpoint、attention backend、search query 数量、Expand 深度、section 选择或测试样本。原 `REPRO_RELIABILITY_PATCH_001` 的并发上限 8、timeout、有限 retry、指数退避、jitter 和 fallback cache 均保留。

## 本地索引检查

| 项目 | 数值 |
|---|---:|
| `id2paper.json` 记录 | 569,432 |
| 非空 normalized title key | 556,050 |
| 唯一 key | 555,260 |
| 可直接读取本地 ZIP 的索引项 | 554,478 |
| Ambiguous key | 790 |
| Ambiguous key 比例 | 0.142% |
| 空 normalized title | 62 |

冲突比例不高。冲突 key 不保存任意 ID，运行时统一进入 fallback。9 个当前 GT 均为唯一且可直接读取的本地命中。

离线验证结果：

- 9/9 GT 标题都解析到预期 arXiv ID。
- 在禁止 `requests.get` 的情况下，9/9 GT 仍能读取本地论文，证明本地 hit 不访问 arXiv。
- Ambiguous 和 miss 分别正确进入 fallback。
- 全局 fallback 网络并发上限仍为 8。
- `git diff --check` 通过。

## 单条重跑

Query：

```text
Give me papers which show that using a smaller dataset in large language model pre-training can result in better models than using bigger datasets.
```

只运行 `/mnt/nvme3/chenyi/tmp/pasa-smoke/real_single.jsonl` 的这一行。原始 50 条测试集哈希保持不变。

结果文件：

- `/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-resolver-001/0.json`
- `/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-resolver-001/smoke_report.json`
- `/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-resolver-001/run.log`

## Before / After

Before 使用紧邻本补丁之前的 `REPRO_RELIABILITY_PATCH_001` 单条结果。

| 指标 | Before | After |
|---|---:|---:|
| GT_TOTAL | 9 | 9 |
| Crawler GT | 1 | 6 |
| Final GT | 1 | 5 |
| Final papers | 4 | 15 |
| Precision | 0.2500 | 0.3333 |
| Recall | 0.1111 | 0.5556 |
| F1 | 0.1538 | 0.4167 |
| Search nodes | 26 | 27 |
| Expand nodes | 9 | 470 |
| Logical arXiv fallback calls | 884 | 331 |
| Actual arXiv title HTTP requests | 2,245 | 856 |
| HTTP 429 | 2,148 | 840 |
| Final fallback lookup failures | 562 | 220 |
| Retry | 1,674 | 630 |
| Serper calls | 5 | 5 |
| Latency | 562.731 s | 132.407 s |
| GPU peak（物理 GPU 1 / 2） | 17,924 / 21,498 MiB | 23,448 / 29,292 MiB |

本地解析统计：

```text
LOCAL_TITLE_LOOKUPS=1236
LOCAL_TITLE_HITS=905
LOCAL_TITLE_MISSES=329
LOCAL_TITLE_AMBIGUOUS=2
ARXIV_FALLBACKS=331
LOCAL_TITLE_HIT_RATE=73.22%
```

本地索引把实际 arXiv HTTP 请求减少 61.87%，把 429 次数减少 60.89%，总延迟减少 76.47%（约快 4.25 倍）。由于更多引用被成功解析，Expand 节点从 9 增加到 470，GPU 峰值相应提高，但仍未 OOM。

## GT 结果

Crawler 找到 6 个 GT：

1. `When Less is More: Investigating Data Pruning for Pretraining LLMs at Scale`
2. `How to Train Data-Efficient LLMs`
3. `Deduplicating Training Data Makes Language Models Better`
4. `AlpaGasus: Training A Better Alpaca with Fewer Data`
5. `Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes`
6. `LESS: Selecting Influential Data for Targeted Instruction Tuning`

Selector 最终保留其中 5 个。`Deduplicating Training Data Makes Language Models Better` 已由本地 resolver 找到，但 Selector 分数为 `0.0617`，低于 `0.5` 阈值。

剩余 3 个未进入 Crawler 候选：

- `Automatic Document Selection for Efficient Encoder Pretraining`
- `Farewell to aimless large-scale pretraining: Influential subset selection for language model`
- `Babyllama-2: Ensemble-distilled models consistently outperform teachers with limited data.`

这些标题没有出现在本次 resolver 的失败标题中，说明它们没有到达 title lookup，而不是本地 title 解析失败。After 没有 GT 因 arXiv fallback 失败而丢失。

## 限制

fallback 服务仍不健康：856 次实际 HTTP 请求中有 840 次返回 429。现在本地索引保护了 73.22% 的引用解析，并避免了本条 query 的 GT title lookup 漏失，但本地 miss/ambiguous 论文仍几乎无法从 arXiv 搜索页补全。

两次运行的 Crawler search query 文本和 Serper 返回节点略有变化，因此 Before/After 并非严格逐候选的确定性对照。不过新增的 5 个 Crawler GT 均可在 After 输出中确认来自 `SearchFrom:local_paper_db`，本地 resolver 的绕网行为也已通过离线禁止网络测试验证。

## 补丁记录

- `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_LOCAL_RESOLVER_001/before.status`
- `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_LOCAL_RESOLVER_001/before.diff`
- `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_LOCAL_RESOLVER_001/after.status`
- `/mnt/nvme3/chenyi/pasa/repro-records/REPRO_LOCAL_RESOLVER_001/after.diff`

```text
PATCH_ID=REPRO_LOCAL_RESOLVER_001
GT_TOTAL=9
CRAWLER_GT_FOUND=6
FINAL_GT_FOUND=5
FINAL_PRECISION=0.3333
FINAL_RECALL=0.5556
FINAL_F1=0.4167
EXPAND_NODES=470
ARXIV_TITLE_REQUESTS=856
HTTP_429=840
FINAL_LOOKUP_FAILURES=220
LATENCY=132.407s
LOCAL_TITLE_LOOKUPS=1236
LOCAL_TITLE_HITS=905
LOCAL_TITLE_MISSES=329
LOCAL_TITLE_AMBIGUOUS=2
ARXIV_FALLBACKS=331
LOCAL_TITLE_HIT_RATE=73.22%
```
