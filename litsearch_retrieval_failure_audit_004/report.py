"""Render the audit report from the frozen machine-readable results."""
from collections import defaultdict
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004.md"

CATEGORY_LABELS = {
    "QUERY_DIRECTION_MISS": "QUERY_DIRECTION_MISS",
    "RANKING_DEPTH_MISS": "RANKING_DEPTH_MISS",
    "SOURCE_INDEX_MISS": "SOURCE_INDEX_MISS",
    "UNCERTAIN": "UNCERTAIN",
}

MODE_LABELS = {
    "OVERGENERALIZATION": "过度泛化",
    "KEY_METHOD_ENTITY_OMISSION": "关键方法/实体遗漏",
    "TASK_FRAMING_DRIFT": "任务框架漂移",
    "RELATION_CONDITION_LOSS": "关系/限定条件丢失",
    "CONSTRAINT_FRAGMENTATION": "约束被拆散",
}


def read(name):
    return json.loads((ROOT / name).read_text())


def pct(value):
    return f"{100 * value:.2f}%"


def ids(cases, category):
    return "、".join(case["question_id"] for case in cases if case["final_category"] == category) or "无"


def category_row(label, record):
    return f"| `{label}` | {record['count']} | {pct(record['fraction'])} |"


def group_category_counts(group):
    return " / ".join(
        str(group["categories"][category]["count"])
        for category in (
            "QUERY_DIRECTION_MISS",
            "RANKING_DEPTH_MISS",
            "SOURCE_INDEX_MISS",
            "UNCERTAIN",
        )
    )


def main():
    summary = read("failure_summary.json")
    case_file = read("failure_cases.json")
    probes = read("diagnostic_probe_results.json")
    cases = case_file["cases"]
    assert summary["status"] == case_file["status"] == probes["status"] == "COMPLETE"
    assert len(cases) == summary["miss_questions"] == 38

    categories = summary["categories"]
    groups = summary["groups"]
    source = summary["frozen_source_adherence"]
    panel = summary["diagnostic_probes"]
    modes = summary["query_direction_failure_modes"]
    by_category = defaultdict(list)
    for case in cases:
        by_category[case["final_category"]].append(case)

    case_rows = []
    for case in cases:
        evidence = case["diagnostic_evidence"]
        probe_signal = (
            f"exact={evidence['exact_title_gold_ranks'] or '-'}; "
            f"core={evidence['core_phrase_gold_ranks'] or '-'}; "
            f"question={evidence['original_question_gold_ranks'] or '-'}; "
            f"depth={evidence['depth_gold_nominal_ranks'] or '-'}"
        )
        modes_text = ", ".join(case["failure_modes"])
        rationale = case["expert_rationale"].replace("|", "\\|").replace("\n", " ")
        case_rows.append(
            f"| {case['question_id']} | {case['group']} | `{case['final_category']}` | "
            f"{case['confidence']} | {modes_text} | {probe_signal} | {rationale} |"
        )

    priority_rows = []
    priority_names = {
        "FEEDBACK_REQUERY": "`FEEDBACK_REQUERY`",
        "CITATION_EXPANSION": "Citation Expansion",
        "ALTERNATIVE_RETRIEVAL_SOURCE": "替换/增加 retrieval source",
        "DEEPER_PAGEN": "更深 PageN",
    }
    for item in summary["next_experiment_priority"]:
        priority_rows.append(
            f"| {item['rank']} | {priority_names[item['experiment']]} | {item['scope']} |"
        )

    report = f"""# LITSEARCH_RETRIEVAL_FAILURE_AUDIT_004

## 审计结论

本审计对 `PAGE2_ROUTING_PREREG_VALIDATION_003B` 中 **Page1 与所有 native-query Page2 均未命中 GT 的 38 题**进行归因。保守分类结果为：

| 类别 | 题数 | 占 38 题 |
|---|---:|---:|
{category_row("QUERY_DIRECTION_MISS", categories["QUERY_DIRECTION_MISS"])}
{category_row("RANKING_DEPTH_MISS", categories["RANKING_DEPTH_MISS"])}
{category_row("SOURCE_INDEX_MISS", categories["SOURCE_INDEX_MISS"])}
{category_row("UNCERTAIN", categories["UNCERTAIN"])}

逐类题号：

- `QUERY_DIRECTION_MISS`（11）：{ids(cases, "QUERY_DIRECTION_MISS")}
- `RANKING_DEPTH_MISS`（0）：{ids(cases, "RANKING_DEPTH_MISS")}
- `SOURCE_INDEX_MISS`（7）：{ids(cases, "SOURCE_INDEX_MISS")}
- `UNCERTAIN`（20）：{ids(cases, "UNCERTAIN")}

核心判断是：**当前证据不支持“主要瓶颈就是 native query quality / query direction，而不是 Page2 本身没有价值”作为 38 题的主解释。** 在能够较明确归因的 18 题中，query-direction miss 的确多于 source-index miss（11 对 7）；但 20/38（52.63%）仍然不确定，不能把它们强行计入 query failure。此外，15 个方向较合理问题的真实 Page3–Page5 probe 没有一次命中 GT，冻结 Page2 的 arXiv source adherence 又从 Page1 的 100% 降到 17.54%，说明 provider pagination/source behavior 是实质性混杂因素。

这也不等于“Page2 没有价值”的一般性结论。本审计只分析 003B 的 38 个双页 miss，且 003B 本身的 Always-Page2 没有为这些题增加 GT；它能支持的是：**对当前 native queries 和当前 Serper/arXiv 请求行为，机械地继续翻页不是优先级最高的修复方向。**

## 数据边界与可审计性

- 输入完全来自冻结的 003B：原始 question、native queries、Page1/Page2 raw response、GT title/metadata，以及本地 GT abstract。
- 未修改 `paper_agent.py`，未修改 003B 的 snapshot、response 或 hash。
- 离线自动证据包括 token coverage、Question→GT 与 Query→GT 的 token/字符/TF-IDF 相似度，以及冻结结果 title+snippet→GT metadata 的主题相似度。
- 每题保留自动规则建议、结构化人工/规则判断、是否覆盖自动建议、置信度、failure modes、probe ranks 和证据路径，详见 `failure_cases.json`。
- `RANKING_DEPTH_MISS` 只在固定 native query 的真实 Page3–Page5 结果直接出现 GT 时成立；不能仅凭“语义方向合理”推测为深度问题。
- `UNCERTAIN` 是有意保留的审计结果，不是待补齐的标签。

## 诊断性 probes

共冻结并执行 {panel['total_requests']} 个 probe，{panel['http_attempts']} 次 HTTP attempt，均保存原始 response bytes、结构化响应、payload 与 SHA-256：

| Probe | 问题数/请求数 | GT 命中题数 |
|---|---:|---:|
| Exact GT title，Page1 Top10 | 38 | {panel['exact_title_hit_questions']} |
| GT deterministic core phrase，Page1 Top10 | 38 | {panel['core_phrase_hit_questions']} |
| Original question，Page1 Top10 | 38 | {panel['original_question_hit_questions']} |
| 方向较合理 native query，Page3–Page5 | {panel['depth_eligible_questions']} 题 / {panel['depth_requests']} 请求 | {panel['depth_hit_questions']} |

**这 {panel['total_requests']} 个请求全部是读取 GT 的 failure-attribution diagnostics。它们不是可部署策略，不是 Controller 候选，不是新的模型性能估计，也没有回写或替换 003B 的结果。** Page3–Page5 子集的 case 选择与 native-query 选择也读取了 GT metadata，因此只能用于诊断“是否观察到更深命中”，不能报告为策略 recall。

Exact title 和 core phrase 都能命中的 31 题，说明至少在诊断时点搜索源能够识别多数 GT；两者都不命中的 7 题支持 `SOURCE_INDEX_MISS`。Original question 只命中 2/38，说明直接照抄问题也不是充分修复。15 个方向较合理 case 的 Page3–Page5 为 0/15，只能说明本次有限深度 panel 没找到正面的 ranking-depth 证据，不能证明 GT 永远不在更深位置。

## Query-direction failure 的常见形式

以下计数只在 11 个 `QUERY_DIRECTION_MISS` 中统计；同一题可有多个 failure mode：

| Query failure mode | 题数 |
|---|---:|
| 过度泛化 | {modes.get("OVERGENERALIZATION", 0)} |
| 关键方法/实体遗漏 | {modes.get("KEY_METHOD_ENTITY_OMISSION", 0)} |
| 任务框架漂移 | {modes.get("TASK_FRAMING_DRIFT", 0)} |
| 关系/限定条件丢失 | {modes.get("RELATION_CONDITION_LOSS", 0)} |
| 约束被拆散 | {modes.get("CONSTRAINT_FRAGMENTATION", 0)} |

最常见的是**过度泛化**和**关键方法/实体遗漏**。典型模式是把一个可识别的方法、工具、数据集或机制改写成宽泛 survey/主题检索；其次是把“方法用于什么任务”“在什么限制下成立”等关系丢掉，或把一个多条件问题拆进不同 query，导致没有任何一条 query 保留完整合取条件。

表面模式也与此一致：38 题共有 {summary['native_query_surface_patterns']['native_queries']} 条 native query，其中 {summary['native_query_surface_patterns']['survey_queries']} 条包含 `survey`，覆盖 {summary['native_query_surface_patterns']['questions_with_survey_query']}/38 题。这个数字只说明生成配置存在明显的泛化倾向，**不能单独作为因果分类规则**。

## Author-written 与 inline-citation

分类顺序为 Query / Depth / Source / Uncertain：

| 分组 | 题数 | Query / Depth / Source / Uncertain |
|---|---:|---:|
| author-written | {groups['author-written']['questions']} | {group_category_counts(groups['author-written'])} |
| inline-citation | {groups['inline-citation']['questions']} | {group_category_counts(groups['inline-citation'])} |

- Author-written：query miss 3/16（18.75%），source miss 1/16（6.25%），uncertain 12/16（75.00%）。主要表现为方向语义合理，但 GT 使用问题中未显式出现的标题术语，因此难以区分 query wording、排序波动和 source behavior。
- Inline-citation：query miss 8/22（36.36%），source miss 6/22（27.27%），uncertain 8/22（36.36%）。它比 author-written 更容易得到明确的方向遗漏或 source-index 归因。

两组 pattern 有描述性差异，但样本只有 16/22，且这是 003B miss 条件下的选择后子集；这里不做显著性推断，也不把差异外推到完整 LitSearch。

## Page2 source-adherence 限制

在这 38 题的冻结响应中：

| 冻结页 | Organic results | 可解析 arXiv URL | 比例 |
|---|---:|---:|---:|
| Page1 | {source['page1']['organic']} | {source['page1']['arxiv_parseable']} | {pct(source['page1']['arxiv_ratio'])} |
| Page2 | {source['page2']['organic']} | {source['page2']['arxiv_parseable']} | {pct(source['page2']['arxiv_ratio'])} |

请求 payload 虽包含 `site:arxiv.org`，但 Page2 大量返回非 arXiv 结果。这使“Page2 没找到 GT”同时混合了 query direction、Google/Serper pagination、site restriction adherence 与索引/排序因素。因而不能把 Page2 miss 全部解释为 native query 错误，也不能用这些诊断 probes 声称某个 Controller 会提升性能。

## 下一步实验优先级

| 优先级 | 实验 | 原因与建议范围 |
|---:|---|---|
{chr(10).join(priority_rows)}

具体建议：

1. **优先 `FEEDBACK_REQUERY`**：只在预注册的新评测上，用原 question 加冻结 Page1 证据生成一次不读取 GT 的 requery；重点测试是否能保留完整限定条件并补回桥接术语。11 个明确 query miss 提供了直接动机。
2. **其次 Citation Expansion**：20 个 uncertain 中大量 case 的检索结果仍在正确主题附近，而 GT 名称包含 hidden terminology；从高相关邻居的引用网络扩展，比盲目继续翻页更有针对性。
3. **并行小规模比较 retrieval source**：7 个 exact/core identity search 都失败的 case 应用于检验 arXiv-native API、Semantic Scholar 或其他学术索引是否解决 source-index miss；同时可隔离当前 Page2 source-adherence 问题。
4. **更深 PageN 暂列低优先级**：本次固定的 Page3–Page5 panel 为 0/15，且越深页 source adherence 恶化。若再测，必须先冻结稳定的学术源和深度预算，不能挑最好看的 PageN。

## 逐题审计索引

| QID | Group | Final category | Confidence | Failure modes | Probe GT ranks | 审计理由 |
|---|---|---|---|---|---|---|
{chr(10).join(case_rows)}

## 产物

- `failure_cases.json`：38 题逐题证据、特征、分类、置信度和判断理由。
- `failure_summary.json`：总体/分组自动统计、probe panel、source adherence 与下一步优先级。
- `diagnostic_probe_results.json`：159 个诊断结果索引、命中位置和 response hashes。
- `validation.json`：独立重算与 hash/原始字节验证结果。

报告由 `report.py` 直接从机器可读结果生成；独立一致性检查由 `validate.py` 执行。
"""
    REPORT.write_text(report)
    print(f"Wrote {REPORT.name} ({len(cases)} case rows).")


if __name__ == "__main__":
    main()
