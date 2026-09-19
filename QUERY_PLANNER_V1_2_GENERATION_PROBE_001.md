# QUERY_PLANNER_V1_2_GENERATION_PROBE_001

Generation-only + A/B query 构造验证；不评估语义质量或检索 Recall。

每题仅一次原始 PaSa Crawler generation，A/B 共享同一输出。原 prompt 从 agent_prompt.json 读取；未使用 V1/V1.1 prompt。
A = native[:5]；B = [original_question.strip()] + native[:4]。native 少于 5 条仍使用同一公式；不补齐、不去重、不修复或重采样。

seed=42，每次生成前重置；GPU 1，batch_size=1，max_new_tokens=512，其余 generation 配置全部沿用 checkpoint。

## Sanity check

```json
{
  "completed_questions": 50,
  "crawler_generation_calls": 50,
  "search_action_parse_success": 50,
  "strict_search_format_questions": 50,
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
  "native_total": 248,
  "A_total": 248,
  "B_total": 250,
  "faithful_anchor_present_first": 50,
  "shared_native_prefix_exact": 50,
  "same_generation_for_A_B": 50,
  "empty_native_queries": 0,
  "non_eos_generations": 0,
  "serper_requests": 0,
  "sanity_check": "PASS"
}
```

共享位置严格检查 B[1:] == A[:4]。native 为 5 条时 B 移除 q5 并前置 anchor；native 为 4 条或更少时保留全部 native 并前置 anchor，因此两组数量可以不同。

## 执行边界

只加载本地 Crawler。HF 离线模式、local_files_only 和 Python 网络审计钩子阻止 Internet socket/DNS；没有 Search、Serper、Selector、Citation Expand 或外部 LLM 调用。
网络钩子阻止事件：[{"event": "socket.__new__", "utc": "2026-09-14T14:45:52.974613+00:00"}]。被阻止的 socket 创建或 DNS 事件不是成功网络请求。
主流程、原 prompt、既有报告/实验 JSON 与 checkpoint 前后 SHA-256 一致。没有修改 generation config、models.py、Selector 或 Expand。

## 原始生成 Prompt

```text
Please generate some mutually exclusive queries in a list to search the relevant papers according to the User Query. Searching for survey papers would be better.
User Query: {user_query}
```

## 产物

- 主 JSON 保存每题原始 question、native queries、A queries、B queries，以及 prompt、seed、原始输出、token IDs 和 generation ID。
- raw_generations/Q0.json 至 Q49.json：每题唯一 generation 与 A/B 构造的完整记录。
- validation.json：sanity check 与产物哈希。

实验到此结束，未进入真实 Search 或下一阶段。
