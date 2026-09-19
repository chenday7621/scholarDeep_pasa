# QUERY_PLANNER_V1_2_A5_B6_REPLAY_001

只复用 QUERY_PLANNER_V1_2_SEARCH_AB_001 已保存的 response、candidate、metadata 和 GT matching，离线重算并集。没有任何新检索或生成。

A 保留全部 native queries，B 在全部 native queries 之后追加已有 anchor。48 题 A5→B6；Q18、Q28 为 A4→B5。所有 native 顺序与文本不变。

## Recall 与 GT

| 范围 | 指标 | A | B |
|---|---|---:|---:|
| 48Q A5/B6 | GT found / 781 | 144 | 149 |
| | Macro Search Recall | 22.5070% | 23.1172% |
| | Micro Search Recall | 18.4379% | 19.0781% |
| Full 50Q | GT found / 790 | 145 | 150 |
| | Macro Search Recall | 22.0067% | 22.5926% |
| | Micro Search Recall | 18.3544% | 18.9873% |

48Q：B>A / B=A / B<A = **5 / 43 / 0**。Anchor 相对完整 q1–q5 新增 **5** 个 (QID, normalized GT title) 命中。

## 新增 GT 分布

| Q | GT 标题 | Anchor response |
|---|---|---|
| Q13 | On the Intrinsic Self-Correction Capability of LLMs: Uncertainty and Latent Concept | /home/chenyi/pasa/query_planner_v1_2_search_ab_001/requests/Q13_anchor_attempt1.json |
| Q19 | REMARK-LLM: A Robust and Efficient Watermarking Framework for Generative   Large Language Models | /home/chenyi/pasa/query_planner_v1_2_search_ab_001/requests/Q19_anchor_attempt1.json |
| Q44 | Hawk: Accurate and Fast Privacy-Preserving Machine Learning Using Secure<br>  Lookup Table Computation | /home/chenyi/pasa/query_planner_v1_2_search_ab_001/requests/Q44_anchor_attempt1.json |
| Q45 | Training-free Camera Control for Video Generation | /home/chenyi/pasa/query_planner_v1_2_search_ab_001/requests/Q45_anchor_attempt1.json |
| Q48 | Automate Strategy Finding with LLM in Quant investment | /home/chenyi/pasa/query_planner_v1_2_search_ab_001/requests/Q48_anchor_attempt1.json |

## Query budget 成本

这里计算逻辑 query slots，不是本轮真实网络费用：所有结果都来自既有缓存，本轮网络成本为零。

| 指标 | 48Q | Full 50Q |
|---|---:|---:|
| A 平均 query 数 | 5.0 | 4.96 |
| B 平均 query 数 | 6.0 | 5.96 |
| A 总 query slots | 240 | 248 |
| B 总 query slots | 288 | 298 |
| 新增 slots | 48 | 50 |
| Query budget 增幅 | 20.0000% | 20.1613% |
| GT gain / 新增 query slot | 0.104167 | 0.100000 |
| 每题增加 1 slot 对应 Macro Recall 增益（pp） | 0.610217 | 0.585808 |
| 每题增加 1 slot 对应 Micro Recall 增益（pp） | 0.640205 | 0.632911 |
| Macro Recall 增益 / 总新增 slot（pp/slot） | 0.012713 | 0.011716 |
| Micro Recall 增益 / 总新增 slot（pp/slot） | 0.013338 | 0.012658 |

GT/slot = 新增 GT 总数 / 新增 slots 总数。Recall 的分母有两种明确口径：每题预算从 A 增加一个 slot 时的整体 Recall 增益；以及该整体增益除以所有题新增 slots 的摊销值。后者不是逐题 Recall 平均值的另一种定义，也不表示随预算线性增长。

## Q28、Q48

### Q28

Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.

A 0/4 → B 0/4；新增 0。Query slots：4 → 5。

### Q48

Papers that explore using large language models for mining factors in stock exchange analysis.

A 1/8 → B 2/8；新增 1。Query slots：5 → 6。

## 全部逐题结果

| Q | GT | A found | B found | A Recall | B Recall | 新增 GT | A/B slots |
|---|---:|---:|---:|---:|---:|---:|---|
| Q0 | 9 | 0 | 0 | 0.0000% | 0.0000% | 0 | 5/6 |
| Q1 | 29 | 6 | 6 | 20.6897% | 20.6897% | 0 | 5/6 |
| Q2 | 21 | 4 | 4 | 19.0476% | 19.0476% | 0 | 5/6 |
| Q3 | 42 | 3 | 3 | 7.1429% | 7.1429% | 0 | 5/6 |
| Q4 | 44 | 3 | 3 | 6.8182% | 6.8182% | 0 | 5/6 |
| Q5 | 7 | 1 | 1 | 14.2857% | 14.2857% | 0 | 5/6 |
| Q6 | 24 | 1 | 1 | 4.1667% | 4.1667% | 0 | 5/6 |
| Q7 | 35 | 3 | 3 | 8.5714% | 8.5714% | 0 | 5/6 |
| Q8 | 16 | 5 | 5 | 31.2500% | 31.2500% | 0 | 5/6 |
| Q9 | 39 | 5 | 5 | 12.8205% | 12.8205% | 0 | 5/6 |
| Q10 | 15 | 3 | 3 | 20.0000% | 20.0000% | 0 | 5/6 |
| Q11 | 20 | 4 | 4 | 20.0000% | 20.0000% | 0 | 5/6 |
| Q12 | 17 | 4 | 4 | 23.5294% | 23.5294% | 0 | 5/6 |
| Q13 | 12 | 3 | 4 | 25.0000% | 33.3333% | 1 | 5/6 |
| Q14 | 9 | 5 | 5 | 55.5556% | 55.5556% | 0 | 5/6 |
| Q15 | 5 | 1 | 1 | 20.0000% | 20.0000% | 0 | 5/6 |
| Q16 | 8 | 2 | 2 | 25.0000% | 25.0000% | 0 | 5/6 |
| Q17 | 9 | 2 | 2 | 22.2222% | 22.2222% | 0 | 5/6 |
| Q18 | 5 | 1 | 1 | 20.0000% | 20.0000% | 0 | 4/5 |
| Q19 | 37 | 4 | 5 | 10.8108% | 13.5135% | 1 | 5/6 |
| Q20 | 4 | 1 | 1 | 25.0000% | 25.0000% | 0 | 5/6 |
| Q21 | 2 | 0 | 0 | 0.0000% | 0.0000% | 0 | 5/6 |
| Q22 | 3 | 0 | 0 | 0.0000% | 0.0000% | 0 | 5/6 |
| Q23 | 2 | 0 | 0 | 0.0000% | 0.0000% | 0 | 5/6 |
| Q24 | 11 | 4 | 4 | 36.3636% | 36.3636% | 0 | 5/6 |
| Q25 | 1 | 0 | 0 | 0.0000% | 0.0000% | 0 | 5/6 |
| Q26 | 2 | 2 | 2 | 100.0000% | 100.0000% | 0 | 5/6 |
| Q27 | 9 | 4 | 4 | 44.4444% | 44.4444% | 0 | 5/6 |
| Q28 | 4 | 0 | 0 | 0.0000% | 0.0000% | 0 | 4/5 |
| Q29 | 8 | 3 | 3 | 37.5000% | 37.5000% | 0 | 5/6 |
| Q30 | 6 | 3 | 3 | 50.0000% | 50.0000% | 0 | 5/6 |
| Q31 | 15 | 4 | 4 | 26.6667% | 26.6667% | 0 | 5/6 |
| Q32 | 16 | 0 | 0 | 0.0000% | 0.0000% | 0 | 5/6 |
| Q33 | 13 | 5 | 5 | 38.4615% | 38.4615% | 0 | 5/6 |
| Q34 | 7 | 3 | 3 | 42.8571% | 42.8571% | 0 | 5/6 |
| Q35 | 7 | 2 | 2 | 28.5714% | 28.5714% | 0 | 5/6 |
| Q36 | 33 | 9 | 9 | 27.2727% | 27.2727% | 0 | 5/6 |
| Q37 | 10 | 4 | 4 | 40.0000% | 40.0000% | 0 | 5/6 |
| Q38 | 17 | 0 | 0 | 0.0000% | 0.0000% | 0 | 5/6 |
| Q39 | 2 | 0 | 0 | 0.0000% | 0.0000% | 0 | 5/6 |
| Q40 | 5 | 3 | 3 | 60.0000% | 60.0000% | 0 | 5/6 |
| Q41 | 5 | 2 | 2 | 40.0000% | 40.0000% | 0 | 5/6 |
| Q42 | 10 | 2 | 2 | 20.0000% | 20.0000% | 0 | 5/6 |
| Q43 | 28 | 6 | 6 | 21.4286% | 21.4286% | 0 | 5/6 |
| Q44 | 25 | 6 | 7 | 24.0000% | 28.0000% | 1 | 5/6 |
| Q45 | 57 | 12 | 13 | 21.0526% | 22.8070% | 1 | 5/6 |
| Q46 | 65 | 8 | 8 | 12.3077% | 12.3077% | 0 | 5/6 |
| Q47 | 4 | 1 | 1 | 25.0000% | 25.0000% | 0 | 5/6 |
| Q48 | 8 | 1 | 2 | 12.5000% | 25.0000% | 1 | 5/6 |
| Q49 | 8 | 0 | 0 | 0.0000% | 0.0000% | 0 | 5/6 |

## 验证和限制

```text
new Serper requests = 0
new network requests = 0
new Crawler generations = 0
new Selector calls = 0
new Citation Expand calls = 0
```

- Python audit hook 在 replay 前安装，阻止 Internet socket、DNS、子进程和模型/网络客户端模块导入；未发生阻止事件。仅加载本地文件和原版 evaluator。
- 原始 response 字节、SHA-256、原生候选解析、metadata 文件和逐 query GT matching 均核对一致；无新元数据解析。A 的候选与 GT 集合与上一轮 A 完全一致。
- B candidate = A candidate ∪ cached anchor candidate；B GT = A GT ∪ cached anchor GT。逐题验证 A⊆B，B>A 仅代表缓存并集新增覆盖。
- 原版 keep_letters、cal_micro 与 metrics.py 未改动；48Q/50Q 四组均用原版 metrics.py 复核。select_score=0 仅为 Search-only 输入结构占位，未运行 Selector。
- 保留原实验的 Q40 shared q3 失败与 118 个候选标题未解析状态，不补请求、不从分母剔除。相同缓存下并集不会降低 Recall，不能将这种单调性视为等预算策略优势或 End-to-End 结论。
- 主 JSON 保存逐题所有 native/anchor 查询、缓存引用、候选集合、GT 集合和新增命中证据；validation.json 保存原始输入与最终产物哈希。

离线重算到此结束，未进入 End-to-End。
