# REPRO_LOCAL_ONLY_001

## 范围与实现

Citation title resolver 现在执行：

```text
citation title
  -> keep_letters() normalized exact lookup
  -> 本地唯一命中：读取本地论文
  -> local miss / ambiguous：unresolved，直接跳过
```

`search_paper_by_title()` 不再从 miss/ambiguous 分支调用 HTML 或 arXiv API title search。原在线 helper 保留在源码中但在本模式下不可达。本次未添加 alias、fuzzy、embedding 或 NON_ARXIV 过滤；Crawler、Selector、Prompt、checkpoint、search query 数、Expand 深度和测试样本均未修改。

## Q0 结果

同一个 `RealScholarQuery_0` 完整运行一次，Search、Expand 0、Expand 1 和最终 Selector 均完成。

```text
STATUS=PASS
LOCAL_TITLE_LOOKUPS=1351
LOCAL_TITLE_HITS=991
LOCAL_TITLE_MISSES=359
LOCAL_TITLE_AMBIGUOUS=1
LOCAL_TITLE_HIT_RATE=73.35%
ONLINE_TITLE_REQUESTS=0
SEARCH_NODES=31
EXPAND_NODES=489
CRAWLER_GT_FOUND=6/9
FINAL_GT_FOUND=5/9
FINAL_PRECISION=0.3125
FINAL_RECALL=0.5556
FINAL_F1=0.4000
SERPER_CALLS=5
LATENCY=109.868s
PEAK_GPU_MEMORY=GPU1 34532 MiB; GPU2 37446 MiB
OUTPUT_PATH=/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-only-001/0.json
```

arXiv title lookup 内部统计全部为 0：total lookups、unique titles、HTTP requests、200、429、timeout、retry 和 final failures 均未发生。离线 mock 测试也确认 local hit、miss、ambiguous 三条路径都不会触发在线 title Session。

## GT 命中

Crawler 命中 6 个 GT，与历史 local resolver 完整 Q0 相同：

1. `When Less is More: Investigating Data Pruning for Pretraining LLMs at Scale`
2. `How to Train Data-Efficient LLMs`
3. `Deduplicating Training Data Makes Language Models Better`
4. `AlpaGasus: Training A Better Alpaca with Fewer Data`
5. `Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes`
6. `LESS: Selecting Influential Data for Targeted Instruction Tuning`

Selector 保留其中 5 个；`Deduplicating Training Data Makes Language Models Better` 的 score 为 0.0617，仍低于 0.5。六个 GT 全部来自本地论文库。

## 与历史 local resolver Q0 对比

| 指标 | 历史 local resolver | REPRO_LOCAL_ONLY_001 | 变化 |
|---|---:|---:|---:|
| Crawler GT | 6/9 | 6/9 | 0 |
| Final GT | 5/9 | 5/9 | 0 |
| Precision | 0.3333 | 0.3125 | -0.0208 |
| Recall | 0.5556 | 0.5556 | 0 |
| F1 | 0.4167 | 0.4000 | -0.0167 |
| Search 节点 | 27 | 31 | +4 |
| Expand 节点 | 470 | 489 | +19 |
| 在线 title 请求 | 856 | 0 | -856 |
| Latency | 132.407s | 109.868s | -22.539s |

GT 和 Recall 没有下降。F1 绝对下降 0.0167（约 4.0%），原因是本次最终唯一预测为 16 篇，而历史结果为 15 篇，增加了 1 个 false positive。实时 Serper 搜索节点从 27 变为 31，也说明两次运行并非完全相同的候选集合，不能把这一个 false positive 归因于关闭在线 title fallback。

## 判断

- **local-exact-only 可以完整跑通 Q0。** 没有出现新的非网络异常；只有既有的文件句柄 `ResourceWarning`。
- **关闭在线 title fallback 后，GT 和 Recall 没有下降，F1 仅小幅下降。** 结果与历史 local resolver 基线接近。
- **local-only 可以作为后续 reproduction baseline 的候选。** 它消除了 arXiv title 接口的 429、长延迟和运行间网络状态差异，同时在 Q0 保留相同 GT/Recall。建议下一阶段先运行 5-query pilot 验证跨样本稳定性，再决定是否扩展到 50 条；Serper 搜索仍然在线并可能造成候选波动。

## 产物

- 输出：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-only-001/0.json`
- 运行统计：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-only-001/smoke_report.json`
- 结构化汇总：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-only-001/evaluation_summary.json`
- 日志：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-only-001/run.log`
- 修改前后 diff：`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-only-001/git-diff-before.patch`、`/mnt/nvme3/chenyi/pasa/results/smoke-real-20260909-local-only-001/git-diff-after.patch`
