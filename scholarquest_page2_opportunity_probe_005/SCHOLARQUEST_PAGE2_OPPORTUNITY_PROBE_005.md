# SCHOLARQUEST_PAGE2_OPPORTUNITY_PROBE_005

## 数据与冻结

- 官方数据：[ScholarQuest](https://github.com/pty12345/ScholarQuest/tree/a0c6a6a14e70cb776598f878cc28237d81add278)，`datasets/ScholarQuest.jsonl`。
- 数据 commit：`a0c6a6a14e70cb776598f878cc28237d81add278`；原始文件 SHA-256：`9c6420260117d46538f26a6006c2133701ebe0b69a06ff8973817087294475e7`。
- 全部 1111 条均有明确 answer_arxiv_ids；从 1111 条按原文件顺序构成的候选池，以 seed=20260919 均匀无放回抽取 50 题。
- 抽样列表 SHA-256：`0aa40e55bbc32d107b116c41857d8efcf455de971a30e78dfaa24a68af245196`；dataset_manifest SHA-256：`e53230e1a207323c98678459e17a4e3c875f4d064f83aed7c35f9bb8b2bc6ba3`。
- GT 总数：2740（同题去重，不跨题去重），只使用冻结 answer_arxiv_ids，不经过本地论文库、标题匹配或其他 GT 补充。
- 数据、样本、协议和采集代码在首次生成与 Search 前冻结；没有换 seed、重抽样、筛除难题或改写 query。

## 采集配置

- 使用当前 PaSa 原始 Agent.infer、Crawler checkpoint、generate_query prompt、原 parser 与最多前 5 条限制。每题 seed=42；checkpoint sampling 配置不变；max_new_tokens=512。
- Serper 每条 native query 连续请求 Page1 Top10、Page2 Top10；固定 before:2026-09-19 与 site:arxiv.org。全部 raw bytes（Base64）、parsed response、payload、UTC 时间、重试和 SHA-256 均保存。
- Top10 指请求 num=10；搜索源实际返回少于 10 条或空 organic 时原样保留，不补请求、不剔除该题。
- 未运行 Selector、Citation Expand 或 Router；未修改正式 paper_agent.py。
- 完成 50/50 题；native queries=250；成功 Page1/Page2=250/250；实际 HTTP attempts=500。
- Page1 完成到对应 Page2 开始的间隔：均值 0.002s，最大 0.003s。

## 唯一策略比较

| 策略 | GT found | Macro Search Recall | Micro Search Recall | 额外 Page2 logical calls |
|---|---:|---:|---:|---:|
| Native Page1 | 125/2740 | 7.9879% | 4.5620% | 0 |
| Always Page2 | 126/2740 | 8.1417% | 4.5985% | 250 |

- ΔGT：**1**。
- Macro / Micro Recall 增量：0.1538 / 0.0365 个百分点。
- 至少新增 1 个 GT 的问题：**1/50**。
- 有 Page2 isolated gain 的 query：**1/250**。
- ΔGT / extra Page2 call：**0.0040**。

Isolated gain 定义为某条 query 的 Page2 相对同题全部 Native Page1 union 的新增 GT。不同 query 的 isolated gain 可能重复，不能直接相加得到问题 gain。另存 pair-local gain（仅相对该 query Page1）；该次级定义下正 gain queries 为 2，不混用为主指标。

## 搜索源遵循与解释边界

- Page1：organic=2497，原 parser 可识别 arXiv URL=2483（99.44%）；存在非匹配 URL 的 queries=5。
- Page2：organic=2332，原 parser 可识别 arXiv URL=394（16.90%）；存在非匹配 URL 的 queries=206。

这是特定样本、时间和 Google/Serper 搜索源下的 ID Search coverage，不是最终 PaSa Recall。返回结果中的非匹配 URL 不补抓取、不扩展 parser。固定日期过滤不冻结搜索索引。GT 未穷尽所有相关论文的可能性不改变冻结评分口径。
Always Page2 的收益只说明可用机会，不证明任何 Router 可以选择到这些 query。是否继续的探索性门槛在 Search 前固定：ΔGT≥10、至少 5 题有 gain、ΔGT/call≥0.05，同时必须 50/50 完成；它不是显著性检验。

## 逐题 Page2 gain

| QID | 官方 query ID | native queries | GT | Page1 found | Page1+Page2 found | ΔGT |
|---|---|---:|---:|---:|---:|---:|
| Q00 | BQ_000390 | 5 | 27 | 2 | 2 | 0 |
| Q01 | BQ_001798 | 5 | 187 | 7 | 7 | 0 |
| Q02 | BQ_000548 | 5 | 194 | 3 | 3 | 0 |
| Q03 | BQ_001733 | 5 | 49 | 4 | 4 | 0 |
| Q04 | BQ_002117 | 5 | 190 | 6 | 6 | 0 |
| Q05 | BQ_001420 | 5 | 59 | 1 | 1 | 0 |
| Q06 | BQ_000229 | 5 | 7 | 3 | 3 | 0 |
| Q07 | BQ_000253 | 5 | 37 | 1 | 1 | 0 |
| Q08 | BQ_002254 | 5 | 75 | 8 | 8 | 0 |
| Q09 | BQ_000373 | 5 | 44 | 4 | 4 | 0 |
| Q10 | BQ_002973 | 5 | 81 | 5 | 5 | 0 |
| Q11 | BQ_000088 | 5 | 80 | 0 | 0 | 0 |
| Q12 | BQ_001610 | 5 | 14 | 2 | 2 | 0 |
| Q13 | BQ_000097 | 5 | 23 | 2 | 2 | 0 |
| Q14 | BQ_001997 | 5 | 42 | 5 | 5 | 0 |
| Q15 | BQ_000012 | 5 | 25 | 0 | 0 | 0 |
| Q16 | BQ_000165 | 5 | 26 | 7 | 7 | 0 |
| Q17 | BQ_002729 | 5 | 5 | 1 | 1 | 0 |
| Q18 | BQ_001142 | 5 | 31 | 4 | 4 | 0 |
| Q19 | BQ_002958 | 5 | 16 | 1 | 1 | 0 |
| Q20 | BQ_001353 | 5 | 176 | 1 | 1 | 0 |
| Q21 | BQ_002970 | 5 | 83 | 4 | 4 | 0 |
| Q22 | BQ_000841 | 5 | 75 | 7 | 7 | 0 |
| Q23 | BQ_000492 | 5 | 67 | 1 | 1 | 0 |
| Q24 | BQ_001649 | 5 | 6 | 1 | 1 | 0 |
| Q25 | BQ_002543 | 5 | 50 | 0 | 0 | 0 |
| Q26 | BQ_000396 | 5 | 44 | 0 | 0 | 0 |
| Q27 | BQ_000402 | 5 | 6 | 0 | 0 | 0 |
| Q28 | BQ_000329 | 5 | 17 | 1 | 1 | 0 |
| Q29 | BQ_000014 | 5 | 8 | 2 | 2 | 0 |
| Q30 | BQ_000049 | 5 | 27 | 4 | 4 | 0 |
| Q31 | BQ_001019 | 5 | 36 | 0 | 0 | 0 |
| Q32 | BQ_001300 | 5 | 13 | 1 | 2 | 1 |
| Q33 | BQ_000609 | 5 | 14 | 3 | 3 | 0 |
| Q34 | BQ_000322 | 5 | 38 | 2 | 2 | 0 |
| Q35 | BQ_002670 | 5 | 21 | 4 | 4 | 0 |
| Q36 | BQ_001893 | 5 | 93 | 8 | 8 | 0 |
| Q37 | BQ_001281 | 5 | 15 | 3 | 3 | 0 |
| Q38 | BQ_000041 | 5 | 55 | 1 | 1 | 0 |
| Q39 | BQ_002230 | 5 | 14 | 0 | 0 | 0 |
| Q40 | BQ_002238 | 5 | 30 | 0 | 0 | 0 |
| Q41 | BQ_002817 | 5 | 66 | 1 | 1 | 0 |
| Q42 | BQ_001106 | 5 | 12 | 2 | 2 | 0 |
| Q43 | BQ_000412 | 5 | 69 | 0 | 0 | 0 |
| Q44 | BQ_000272 | 5 | 11 | 0 | 0 | 0 |
| Q45 | BQ_000326 | 5 | 147 | 5 | 5 | 0 |
| Q46 | BQ_001084 | 5 | 75 | 0 | 0 | 0 |
| Q47 | BQ_000917 | 5 | 37 | 6 | 6 | 0 |
| Q48 | BQ_000196 | 5 | 23 | 0 | 0 | 0 |
| Q49 | BQ_002354 | 5 | 200 | 2 | 2 | 0 |

## 产物与核验

- `dataset_manifest.json`：官方来源、版本、seed、50 题样本和冻结 GT。
- `snapshot_manifest.json`：全部 generation、response、attempt 和运行记录的 hash；`responses/` 与 `attempts/` 保留原始字节。
- `query_outcomes.json`：每条 query 的两页 ID 集、GT 命中、isolated/pair-local gain 和 response 索引。
- `question_outcomes.json`：同题跨 query/page 去重后的结果。
- `results.json`：仅 Native Page1 与 Always Page2 的聚合结果、机会门槛和源遵循统计。
- `validation.json`：独立重算样本、原始响应、集合运算、指标、冻结文件及正式源码 hash 的结果。
- snapshot ID：`7afa3caf0806ce26c5ba8c304dd79fccca4c53130ee7581604f450eb7add1bb6`。

## ScholarQuest-50 上是否存在足够明显的 Page2 opportunity，值得继续做固定 `max_jaccard top1` 的独立 routing 验证？

**否，按搜索前冻结的门槛，本次证据不足。** 新增 1 个 GT、1 题获得增益、0.0040 GT/额外调用，未同时达到三项门槛；不支持据此推进固定 `max_jaccard top1` 的独立 routing 验证。这不等于 Page2 在其他样本或搜索源上没有机会。
