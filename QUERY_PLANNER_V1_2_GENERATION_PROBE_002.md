# QUERY_PLANNER_V1_2_GENERATION_PROBE_002

本次是 V1.2 构造规则补充验证。复用 001 已完成的 50 次原生 Crawler generation，本次新增 generation 为 0；每题 A/B 共享同一原始输出。001 及主流程保持不变。

原始 PaSa checkpoint、generate_query prompt、generation 配置和 seed=42 均已核验；未使用 V1/V1.1 prompt。

## 固定构造规则

按原生正则提取并 strip，最多前 5 条。native/A 始终保留 Crawler 原始输出顺序，不排序或重排。
Anchor 仅 trim 并将连续空白合为单个空格，保留原有大小写。比较键额外使用 lowercase。
A 不做任何去重。B 先删除 native[:5] 中比较键与 anchor 完全相同的条目，再按原顺序取前 4 条，前置 anchor；q5 可补位，数量不足时允许少于 5 条。
不做其他去重、semantic/Jaccard dedup、LLM rewrite、constraint extraction 或 acronym expansion。

## Sanity check

```json
{
  "completed_questions": 50,
  "source_native_generation_calls": 50,
  "new_crawler_generation_calls": 0,
  "search_action_parse_success": 50,
  "native_query_count_distribution": {
    "4": 2,
    "5": 48
  },
  "A_query_count_distribution": {
    "4": 2,
    "5": 48
  },
  "B_query_count_distribution": {
    "5": 50
  },
  "B_starts_with_faithful_anchor": 50,
  "anchor_exact_duplicate_questions": 0,
  "anchor_exact_duplicate_occurrences": 0,
  "A_exact_native_order_preserved": 50,
  "B_relative_native_order_preserved": 50,
  "A_B_share_same_generation": 50,
  "serper_requests": 0,
  "selector_calls": 0,
  "citation_expand_calls": 0,
  "sanity_check": "PASS"
}
```

重复出现次数指 native[:5] 中所有 Anchor exact duplicate 条目数，同时另列涉及题数。删除记录含 1-based native 序号、原 query 和比较键；本批未发生重复。
六个独立合成 sanity 样例验证正常构造、q2 重复后 q5 补位、多次 anchor 重复、保留 native-native 重复、不足数量、零 native 和标点差异；不计入 50 题统计。

## 逐题构造与顺序证据

| Q | Native / A / B 条数 | B 保留的原 native 序号 | 删除的原 native 序号 |
|---|---|---|---|
| Q0 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q1 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q2 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q3 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q4 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q5 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q6 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q7 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q8 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q9 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q10 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q11 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q12 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q13 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q14 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q15 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q16 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q17 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q18 | 4 / 4 / 5 | [1, 2, 3, 4] | [] |
| Q19 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q20 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q21 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q22 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q23 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q24 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q25 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q26 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q27 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q28 | 4 / 4 / 5 | [1, 2, 3, 4] | [] |
| Q29 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q30 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q31 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q32 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q33 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q34 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q35 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q36 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q37 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q38 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q39 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q40 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q41 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q42 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q43 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q44 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q45 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q46 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q47 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q48 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |
| Q49 | 5 / 5 / 5 | [1, 2, 3, 4] | [] |

## 产物与边界

主 JSON 保存全部原始 question、normalized anchor、raw Crawler output、native/A/B queries、重复标记、删除条目及原 native 索引，并保留源 generation ID、prompt、seed、token IDs 和哈希。
本脚本只使用 Python 标准库；网络审计钩子阻止 Internet socket/DNS。本次没有模型加载、Serper、Selector、Citation Expand 或真实 Search。
所有保护输入哈希前后相同，当前 Crawler checkpoint 完整哈希与源生成记录相同。构造规则验证到此结束，未进入下一阶段。
