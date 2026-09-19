# PaSa Q0 API fallback rerun

## 结果

同一个 `RealScholarQuery_0` 已完整运行一次，Search、Expand 0、Expand 1 和最终 Selector 均完成，状态为 `PASS`。没有运行其他样本。

本次在 `REPRO_ARXIV_API_FALLBACK_001` 上增加连续 429 阈值 20：达到阈值后，当前标题立即返回 miss，不再消耗该标题剩余 retry；后续标题仍发起一次受全局 limiter 控制的 API 请求。任何非 429 响应都会清零连续计数。模型、Prompt、checkpoint、search query 数、Expand 深度和 Q0 输入未变。

```text
STATUS=PASS
LOCAL_TITLE_LOOKUPS=1166
LOCAL_TITLE_HITS=848
LOCAL_TITLE_MISSES=316
LOCAL_TITLE_AMBIGUOUS=2
ARXIV_API_FALLBACKS=318
API_REQUESTS=259
HTTP_200=94
HTTP_429=165
TIMEOUTS=0
RETRIES=41
MAX_CONSECUTIVE_HTTP_429=57
CONSECUTIVE_429_SKIPS=106
FINAL_LOOKUP_FAILURES=187
SEARCH_NODES=26
EXPAND_NODES=450
CRAWLER_GT_FOUND=4/9
FINAL_GT_FOUND=3/9
FINAL_PRECISION=0.3000
FINAL_RECALL=0.3333
FINAL_F1=0.3158
SERPER_CALLS=5
LATENCY=1464.133s
PEAK_GPU_MEMORY=GPU1 24620 MiB; GPU2 28290 MiB
OUTPUT_PATH=/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001-rerun/0.json
```

API 请求最小启动间隔为 3.000070s，任意 1 秒窗口最多 1 次。259 次请求中 94 次为 200（36.29%），165 次为 429（63.71%），无 timeout/连接异常。最长连续 429 为 57。阈值策略跳过 106 个标题，使两个 Expand 层最终完成；这些跳过结果按现有进程内缓存语义保存为 miss，即使 API 后来恢复也不会重查同一标题。在不同限流窗口之间，API 曾恢复并继续返回 200。

187 个最终 lookup failure 分为：54 个 `no results`、9 个 `title mismatch`、18 个普通三次尝试后 `HTTP 429`、106 个达到连续阈值后的 `HTTP 429`。218 个唯一 fallback 标题均进入缓存，其中 31 个由 API 得到严格匹配 ID。

## GT

Crawler 命中：

- `Deduplicating Training Data Makes Language Models Better`，Selector score 0.0617，未进入最终结果；
- `How to Train Data-Efficient LLMs`；
- `LESS: Selecting Influential Data for Targeted Instruction Tuning`；
- `When Less is More: Investigating Data Pruning for Pretraining LLMs at Scale`。

四个 GT 都通过本地论文库解析。最终 10 篇唯一论文中包含 3 个 GT。最终因 429 失败的 124 个标题与 9 个 GT 均无严格 normalized-title 重合，因此没有可明确确认的直接网络 GT 漏失；429 造成的中间论文丢失仍可能间接改变后续 citation graph。

## 与原 local resolver Q0 对比

| 指标 | 原结果 | 本次 rerun |
|---|---:|---:|
| Crawler GT | 6/9 | 4/9 |
| Final GT | 5/9 | 3/9 |
| Precision | 0.3333 | 0.3000 |
| Recall | 0.5556 | 0.3333 |
| F1 | 0.4167 | 0.3158 |
| Search / Expand 节点 | 27 / 470 | 26 / 450 |
| Latency | 132.407s | 1464.133s |

Crawler 生成的一个查询文本存在单复数差异，实时 Serper 节点也从 27 变为 26；因此本次 GT 下降不能单独归因于 API fallback。原结果额外命中的 `AlpaGasus` 和 `Distilling Step-by-Step!` 当时也来自本地库，本次没有到达相同引用节点。

## 判断

- 连续 429 达到 20 后跳过并继续的机制工作正常，Q0 可以完整结束。
- API 仍严重限流，429 占 63.71%，最长连续 57 次；完整结束不代表 fallback 稳定。
- 本次结果不适合作为高质量 benchmark 基线，当前仍不建议进入 5-query pilot。

## 产物

- 输出：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001-rerun/0.json`
- 运行统计：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001-rerun/smoke_report.json`
- 结构化汇总：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001-rerun/evaluation_summary.json`
- 日志：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001-rerun/run.log`
- 修改前后 diff：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001-rerun/git-diff-before.patch`、`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001-rerun/git-diff-after.patch`
