# REPRO_ARXIV_API_FALLBACK_001

## 修改

`utils.py` 的 local miss / ambiguous fallback 已从 `arxiv.org/search/` HTML 改为 `https://export.arxiv.org/api/query`，查询为 `search_query=ti:"<title>"`。本地唯一标题命中仍直接读取本地论文库。

API fallback 使用一个全局 `requests.Session`，连接池大小和并发上限均为 1；所有线程共享 3 秒 limiter。429、timeout 和临时连接错误最多额外 retry 2 次，retry 同样经过 limiter；429 遵守 `Retry-After` 并至少触发 6 秒全局 cooldown。候选仍使用当前 `_normalized_title()` 严格匹配；0 个精确候选返回 miss，多个不同 ID 的精确候选返回 ambiguous，不做 fuzzy、alias 或 embedding。

Crawler、Selector、Prompt、checkpoint、search query 数、Expand 深度和 Q0 输入均未修改。修改前后 diff、状态和文件哈希保存在本次结果目录。

## Q0 运行结果

运行使用物理 GPU 1、2，输入仍是 `RealScholarQuery_0` 单行文件。Search 完成，5 次 Serper 均返回 200并生成 24 个 Search 节点。Expand 0 期间，API 前 37 次返回 200；从第 38 次开始至停止时，第 38–51 次连续 14 次均返回 429。HTTP 200 停止增长，符合用户指定的“持续大量 429”停止条件，因此主动终止，未重跑。

```text
LOCAL_TITLE_LOOKUPS=656
LOCAL_TITLE_HITS=490
LOCAL_TITLE_MISSES=164
LOCAL_TITLE_AMBIGUOUS=2
ARXIV_API_FALLBACKS=166
API_REQUESTS=51
HTTP_200=37
HTTP_429=14
TIMEOUTS=0
RETRIES=10
FINAL_LOOKUP_FAILURES=35
SEARCH_NODES=24
EXPAND_NODES=N/A (Expand 0 未完成)
CRAWLER_GT_FOUND=N/A
FINAL_GT_FOUND=N/A
FINAL_PRECISION=N/A
FINAL_RECALL=N/A
FINAL_F1=N/A
LATENCY=262.160s (停止时)
PEAK_GPU_MEMORY=GPU1 16698 MiB; GPU2 20610 MiB
```

补充：51 次请求中，200 占 72.55%，429 占 27.45%；最小启动间隔 3.000078s，任意 1 秒窗口最多 1 次。35 个最终 lookup failure 包括 26 个 `no results`、5 个 `title mismatch` 和 4 个三次尝试后仍为 429。进程内已缓存 41 个 API lookup 结果，其中 6 个解析出严格匹配 ID。

## 与 REPRO_LOCAL_RESOLVER_001 对比

| 指标 | 原 local resolver Q0 | API fallback Q0 |
|---|---:|---:|
| 完成状态 | PASS | ABORTED_SUSTAINED_429 |
| Search 节点 | 27 | 24 |
| Expand 节点 | 470 | N/A |
| Crawler GT | 6/9 | N/A |
| Final GT | 5/9 | N/A |
| Precision / Recall / F1 | 0.3333 / 0.5556 / 0.4167 | N/A |
| HTTP 请求 | 856 | 51（停止时） |
| HTTP 200 | 16 | 37 |
| HTTP 429 | 840 | 14 |
| 延迟 | 132.407s | 262.160s（停止时） |

这两个运行的 Search 节点数不同，说明实时 Serper 返回或候选去重存在变化；API 运行又未完成，所以不能把 GT 差异归因于 fallback。

## 判断

- **API fallback 没有稳定完成完整 Q0。** Expand 0 未完成，Expand 1 和最终 Selector 汇总未执行。
- **429 不是仅偶发。** 一次偶发 429 后曾 retry 成功，但随后出现连续 14 次 429，HTTP 200 固定在 37。
- **已观测到的 4 个 HTTP 429 最终失败标题都不是 Q0 GT 的严格规范化标题，因此没有可明确证明的 GT 网络漏失。** 由于运行提前停止，未处理部分及最终 GT 影响无法判断。
- **当前不具备进入 5-query pilot 的条件。** API 相比 HTML 的有效响应显著增加，但在 Q0 所需请求规模下仍触发持续限流；继续扩大 benchmark 会重复消耗请求并产生不可比较的残缺输出。

## 产物

- 原始运行日志：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001/run.log`
- 原始 smoke 统计：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001/smoke_report.json`
- 结构化结论：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001/evaluation_summary.json`
- 修改前 diff：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001/git-diff-before.patch`
- 修改后 diff：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-arxiv-api-fallback-001/git-diff-after.patch`

未生成 `0.json`：中止发生在 Expand 0，完整结果树尚未形成。未启动第二次 Q0。
