# QUERY_PLANNER_V1_2_SEARCH_AB_001

48Q equal-budget：A/B GT found **144 / 138**，Macro Search Recall **22.5070% → 21.6167%**（-0.8903 pp）。

本次只测 Search-only paired A/B。复用已验证的 V1.2 002 queries，未重新调用 Crawler，未执行 Selector、Citation Expand 或完整 PaSa。

## 48Q equal-budget replacement

仅含 native=5 的 48 题；每组每题 5 个逻辑查询槽位。共同 q1–q4 只请求一次；比较 q5 与 anchor。Q18、Q28 不在此汇总中。

| 指标 | A：native | B：anchor + 前4 native |
|---|---:|---:|
| GT denominator | 781 | 781 |
| GT found | 144 | 138 |
| Macro Search Recall | 22.5070% | 21.6167% |
| Micro Search Recall | 18.4379% | 17.6697% |
| Logical Serper calls | 240 | 240 |
| Attributed Serper attempts（含失败） | 243 | 245 |

B>A / B=A / B<A：**4 / 36 / 8 题**。

| Component / marginal 指标 | GT 数量 |
|---|---:|
| Common GT：q1–q4 合并命中 | 131 |
| q5 单条 query 命中（含与 common/anchor 重叠） | 62 |
| anchor 单条 query 命中（含与 common/q5 重叠） | 62 |
| q5-only GT：仅 A 命中，Q − (C ∪ H) | 11 |
| anchor-only GT：仅 B 命中，H − (C ∪ Q) | 5 |
| q5 marginal GT gain：Q − C | 13 |
| anchor marginal GT gain：H − C | 7 |
| q5/anchor 共同新增：(Q ∩ H) − C | 2 |

C、Q、H 分别表示同题 common、q5、anchor 找到的归一化 GT 标题集合。所有总数按 (QID, normalized GT title) 累加，不跨问题合并。Macro 对问题等权，Micro 为 pooled found / pooled GT。

## Full 50Q（包含两题追加 anchor）

| 指标 | A | B |
|---|---:|---:|
| GT denominator | 790 | 790 |
| GT found | 145 | 139 |
| Macro Search Recall | 22.0067% | 21.1521% |
| Micro Search Recall | 18.3544% | 17.5949% |
| Logical Serper calls（组归属） | 248 | 250 |
| Attributed Serper attempts（含失败） | 251 | 255 |
| Successful query responses（组归属） | 247 | 249 |

实际唯一 logical query **298**，实际请求尝试 **303**，成功响应 **297**；HTTP 状态 `{"None": 6, "200": 297}`。共享请求在 A/B 各自归属计数中各计一次，但真实网络只执行一次，不能相加当作实际费用。

## Q18、Q28：追加 anchor 的补充实验

### Q18

Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? Provide related papers.

A：1/5，B：1/5；新增 0，丢失 0。A 为 4 条，B 为 5 条，属于增加一次 anchor 搜索。

新增 GT：

无。

### Q28

Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.

A：0/4，B：0/4；新增 0，丢失 0。A 为 4 条，B 为 5 条，属于增加一次 anchor 搜索。

新增 GT：

无。

## 48Q Recall 变化最大的题

### 提升最大

| Q | GT | A found / Recall | B found / Recall | Δ Recall | q5 marginal / anchor marginal |
|---|---:|---|---|---|---|
| Q48 | 8 | 1 / 12.5000% | 2 / 25.0000% | +12.5000 pp | 0 / 1 |
| Q13 | 12 | 3 / 25.0000% | 4 / 33.3333% | +8.3333 pp | 0 / 1 |
| Q44 | 25 | 6 / 24.0000% | 7 / 28.0000% | +4.0000 pp | 0 / 1 |
| Q19 | 37 | 4 / 10.8108% | 5 / 13.5135% | +2.7027 pp | 0 / 1 |

### 下降最大

| Q | GT | A found / Recall | B found / Recall | Δ Recall | q5 marginal / anchor marginal |
|---|---:|---|---|---|---|
| Q40 | 5 | 3 / 60.0000% | 2 / 40.0000% | -20.0000 pp | 1 / 0 |
| Q35 | 7 | 2 / 28.5714% | 1 / 14.2857% | -14.2857 pp | 1 / 0 |
| Q24 | 11 | 4 / 36.3636% | 3 / 27.2727% | -9.0909 pp | 1 / 0 |
| Q8 | 16 | 5 / 31.2500% | 4 / 25.0000% | -6.2500 pp | 1 / 0 |
| Q36 | 33 | 9 / 27.2727% | 7 / 21.2121% | -6.0606 pp | 2 / 0 |

## Q28、Q48 的 constraint loss 重点核查

### Q28

Original question：

Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.

| Component | 固定 query | 命中 GT | 无标题候选数 |
|---|---|---:|---:|
| q1 | Survey papers on code evaluation datasets | 0 | 2 |
| q2 | Middle difficulty level code evaluation datasets | 0 | 0 |
| q3 | Code evaluation datasets with mid-level hardness | 0 | 1 |
| q4 | Comparison studies on difficulty levels of different code evaluation datasets | 0 | 1 |
| anchor | Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests. | 0 | 0 |

Anchor 原样保留问题中的实体和约束；本次只依据实际搜索命中报告效果，不将约束保留与特定 GT 的找回直接等同为因果证明。

Anchor marginal GT（相对 common）：

无。

q5-only GT（替换后丢失）：

无。

anchor-only GT（替换或追加后新增）：

无。

### Q48

Original question：

Papers that explore using large language models for mining factors in stock exchange analysis.

| Component | 固定 query | 命中 GT | 无标题候选数 |
|---|---|---:|---:|
| q1 | Application of large language models in stock market analysis | 1 | 0 |
| q2 | Role of AI and language models in stock prediction | 0 | 0 |
| q3 | Impact of large language models on stock exchange analysis | 1 | 0 |
| q4 | Use of GPT-3 in stock market trend analysis | 0 | 4 |
| q5 | Survey papers on large language models in stock exchange analysis | 1 | 0 |
| anchor | Papers that explore using large language models for mining factors in stock exchange analysis. | 2 | 0 |

Anchor 原样保留问题中的实体和约束；本次只依据实际搜索命中报告效果，不将约束保留与特定 GT 的找回直接等同为因果证明。

Anchor marginal GT（相对 common）：

- Automate Strategy Finding with LLM in Quant investment

q5-only GT（替换后丢失）：

无。

anchor-only GT（替换或追加后新增）：

- Automate Strategy Finding with LLM in Quant investment

## 全部逐题结果

| Q | GT | A found / Recall | B found / Recall | Δ Recall | q5 marginal / anchor marginal |
|---|---:|---|---|---|---|
| Q0 | 9 | 0 / 0.0000% | 0 / 0.0000% | +0.0000 pp | 0 / 0 |
| Q1 | 29 | 6 / 20.6897% | 6 / 20.6897% | +0.0000 pp | 0 / 0 |
| Q2 | 21 | 4 / 19.0476% | 4 / 19.0476% | +0.0000 pp | 0 / 0 |
| Q3 | 42 | 3 / 7.1429% | 3 / 7.1429% | +0.0000 pp | 0 / 0 |
| Q4 | 44 | 3 / 6.8182% | 3 / 6.8182% | +0.0000 pp | 0 / 0 |
| Q5 | 7 | 1 / 14.2857% | 1 / 14.2857% | +0.0000 pp | 0 / 0 |
| Q6 | 24 | 1 / 4.1667% | 1 / 4.1667% | +0.0000 pp | 0 / 0 |
| Q7 | 35 | 3 / 8.5714% | 3 / 8.5714% | +0.0000 pp | 0 / 0 |
| Q8 | 16 | 5 / 31.2500% | 4 / 25.0000% | -6.2500 pp | 1 / 0 |
| Q9 | 39 | 5 / 12.8205% | 3 / 7.6923% | -5.1282 pp | 2 / 0 |
| Q10 | 15 | 3 / 20.0000% | 3 / 20.0000% | +0.0000 pp | 0 / 0 |
| Q11 | 20 | 4 / 20.0000% | 4 / 20.0000% | +0.0000 pp | 0 / 0 |
| Q12 | 17 | 4 / 23.5294% | 3 / 17.6471% | -5.8824 pp | 1 / 0 |
| Q13 | 12 | 3 / 25.0000% | 4 / 33.3333% | +8.3333 pp | 0 / 1 |
| Q14 | 9 | 5 / 55.5556% | 5 / 55.5556% | +0.0000 pp | 0 / 0 |
| Q15 | 5 | 1 / 20.0000% | 1 / 20.0000% | +0.0000 pp | 0 / 0 |
| Q16 | 8 | 2 / 25.0000% | 2 / 25.0000% | +0.0000 pp | 0 / 0 |
| Q17 | 9 | 2 / 22.2222% | 2 / 22.2222% | +0.0000 pp | 0 / 0 |
| Q18 | 5 | 1 / 20.0000% | 1 / 20.0000% | +0.0000 pp | 0 / 0 |
| Q19 | 37 | 4 / 10.8108% | 5 / 13.5135% | +2.7027 pp | 0 / 1 |
| Q20 | 4 | 1 / 25.0000% | 1 / 25.0000% | +0.0000 pp | 0 / 0 |
| Q21 | 2 | 0 / 0.0000% | 0 / 0.0000% | +0.0000 pp | 0 / 0 |
| Q22 | 3 | 0 / 0.0000% | 0 / 0.0000% | +0.0000 pp | 0 / 0 |
| Q23 | 2 | 0 / 0.0000% | 0 / 0.0000% | +0.0000 pp | 0 / 0 |
| Q24 | 11 | 4 / 36.3636% | 3 / 27.2727% | -9.0909 pp | 1 / 0 |
| Q25 | 1 | 0 / 0.0000% | 0 / 0.0000% | +0.0000 pp | 0 / 0 |
| Q26 | 2 | 2 / 100.0000% | 2 / 100.0000% | +0.0000 pp | 0 / 0 |
| Q27 | 9 | 4 / 44.4444% | 4 / 44.4444% | +0.0000 pp | 0 / 0 |
| Q28 | 4 | 0 / 0.0000% | 0 / 0.0000% | +0.0000 pp | 0 / 0 |
| Q29 | 8 | 3 / 37.5000% | 3 / 37.5000% | +0.0000 pp | 0 / 0 |
| Q30 | 6 | 3 / 50.0000% | 3 / 50.0000% | +0.0000 pp | 0 / 0 |
| Q31 | 15 | 4 / 26.6667% | 4 / 26.6667% | +0.0000 pp | 0 / 0 |
| Q32 | 16 | 0 / 0.0000% | 0 / 0.0000% | +0.0000 pp | 0 / 0 |
| Q33 | 13 | 5 / 38.4615% | 5 / 38.4615% | +0.0000 pp | 0 / 0 |
| Q34 | 7 | 3 / 42.8571% | 3 / 42.8571% | +0.0000 pp | 0 / 0 |
| Q35 | 7 | 2 / 28.5714% | 1 / 14.2857% | -14.2857 pp | 1 / 0 |
| Q36 | 33 | 9 / 27.2727% | 7 / 21.2121% | -6.0606 pp | 2 / 0 |
| Q37 | 10 | 4 / 40.0000% | 4 / 40.0000% | +0.0000 pp | 0 / 0 |
| Q38 | 17 | 0 / 0.0000% | 0 / 0.0000% | +0.0000 pp | 0 / 0 |
| Q39 | 2 | 0 / 0.0000% | 0 / 0.0000% | +0.0000 pp | 0 / 0 |
| Q40 | 5 | 3 / 60.0000% | 2 / 40.0000% | -20.0000 pp | 1 / 0 |
| Q41 | 5 | 2 / 40.0000% | 2 / 40.0000% | +0.0000 pp | 0 / 0 |
| Q42 | 10 | 2 / 20.0000% | 2 / 20.0000% | +0.0000 pp | 0 / 0 |
| Q43 | 28 | 6 / 21.4286% | 5 / 17.8571% | -3.5714 pp | 1 / 0 |
| Q44 | 25 | 6 / 24.0000% | 7 / 28.0000% | +4.0000 pp | 0 / 1 |
| Q45 | 57 | 12 / 21.0526% | 12 / 21.0526% | +0.0000 pp | 2 / 2 |
| Q46 | 65 | 8 / 12.3077% | 8 / 12.3077% | +0.0000 pp | 1 / 1 |
| Q47 | 4 | 1 / 25.0000% | 1 / 25.0000% | +0.0000 pp | 0 / 0 |
| Q48 | 8 | 1 / 12.5000% | 2 / 25.0000% | +12.5000 pp | 0 / 1 |
| Q49 | 8 | 0 / 0.0000% | 0 / 0.0000% | +0.0000 pp | 0 / 0 |

## 冻结规则、配对与基础设施

- Serper endpoint、Top-K=10、page=1、before:2024-09-24 site:arxiv.org 与先前 Search-only 实验一致；URL 仅按原生现代 arXiv ID 正则解析。before 是搜索操作符，不新增本地日期过滤。
- 原生标题 resolver：local ZIP 优先，仅对直接返回 ID 作 arXiv 元数据 fallback。所有组件共享同一 ID→title 快照，不使用 GT/Serper 标题补全，不使用 fuzzy/alias/embedding 匹配。
- 正式评测沿用 keep_letters（Unicode 字母、小写、删除非字母）完全匹配。791 个原始标注归一化为 790 个标题组；已知标题碰撞不在本实验修改。48Q/50Q A/B 四组都用未改动 metrics.py 复算。
- 元数据候选 1268 个，未解析标题 118 个。未解析候选不进入正式标题命中，指标包含此基础设施限制。元数据 HTTP：`{"429": 300, "200": 12, "503": 15, "None": 167}`。
- 元数据进程在已保存 935 个 ID 后停止；确认旧进程已结束后恢复，跳过全部已完成 ID。网络日志与逐 ID 索引完整保留，恢复前没有已发送但缺少终态记录的 ID；没有重跑 Serper。
- A/B query 顺序与上一阶段完全相同；HTTP 调度先 common，再交错 q5/anchor 的先后。共同 query 使用同一请求记录和原始响应，无 A/B 间重复请求。
- q5/anchor 首次请求起始间隔中位数 1.412s，最大 6.018s。紧邻调度降低时间差，不能固定搜索索引。
- 所有尝试保留 raw response text、原始响应 bytes base64、SHA-256、structured response、payload、query ID、component key、时间与状态；不保存认证头或 API key。
- 首次本地沙箱网络失败保留在请求尝试数中；已成功请求不会补跑。网络失败不等于已成功到达 Serper。
- 达原定重试上限仍失败的 query：`[{"query_id": "Q40", "query_key": "q3", "attempts": 3}]`。失败响应作为空候选保留，不从问题分母剔除；共享 query 失败对 A/B 使用同一记录。本轮 Q40 的 common q3 失败，因此该题结果包含共同检索不完整的影响。
- 无 Crawler、Selector、Citation Expand 或完整 PaSa 调用，无主流程或 evaluator 修改。

## 产物

- 主 JSON：查询、共同响应引用、GT 集合分解、元数据、逐题命中证据和全部汇总。
- requests/：每条 query 每次尝试的完整原始响应；completed_queries/：搜索完成时的快照。
- metadata/ 与 metadata_network.json：直接返回 ID 的标题解析结果和网络日志。
- official_metric_inputs/：四组 Search-only 树；select_score=0 仅为原版 evaluator 的结构占位，没有运行 Selector。
- validation.json：独立 replay/集合/调用次数复核。

本阶段在 Search-only paired A/B 完成后停止，未运行下一阶段。
