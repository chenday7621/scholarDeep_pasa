"""Render the preregistered 003B report directly from frozen result artifacts."""
from common import ROOT, read, sha


def value(number, digits=4):
    return "NA" if number is None else f"{number:.{digits}f}"


def policy_row(name, metric):
    return (
        f"| {name} | {metric['gt_found']}/{metric['total_gt']} | "
        f"{value(metric['macro_recall'])} | {value(metric['micro_recall'])} | "
        f"{metric['delta_gt']} | {metric['extra_page2_calls']} | "
        f"{value(metric['delta_gt_per_extra_call'])} | "
        f"{value(metric['always_page2_gain_retention'])} |"
    )


def main():
    result = read(ROOT / "results.json")
    assert result["status"] == "EVALUATED"
    policies = result["policies"]
    primary = result["primary_endpoint"]
    random = policies["random_top1_1000_trials"]
    lines = [
        "# PAGE2_ROUTING_PREREG_VALIDATION_003B",
        "",
        "## 结论",
        "",
        (
            f"Jaccard Router 在每题 1 次额外 Page2 logical call 下新增 "
            f"**{primary['one_page2_call_per_question_delta_gt']} 个 normalized GT**；"
            f"incremental micro recall={value(primary['one_page2_call_per_question_incremental_micro_recall'])}，"
            f"incremental macro recall={value(primary['one_page2_call_per_question_incremental_macro_recall'])}。"
        ),
        (
            f"1000 次固定 seed Random 中，Random ΔGT >= Router 的经验概率为 "
            f"**{value(primary['p_random_greater_or_equal_router_empirical'])}**；"
            f"加一 Monte Carlo p={value(primary['p_random_greater_or_equal_router_plus_one'])}。"
        ),
        "",
        "该结果按冻结协议完整报告；未根据这 50 题修改方向、threshold、feature、weight、seed、样本或 budget。",
        "",
        "## 数据与冻结",
        "",
        "- Princeton LitSearch specific questions：25 author-written + 25 inline-citation。",
        "- 抽样 seed：20260917；Crawler 每题 generation seed：42。",
        f"- normalized GT 总数：{result['total_normalized_gt']}。",
        f"- native query 总数：{result['native_query_count']}。",
        f"- 实际冻结 Page1/Page2 response：{result['actual_page1_calls']}/{result['actual_page2_calls']}。",
        f"- snapshot ID：`{result['snapshot_id']}`。",
        "- 实际采集为所有 native queries 的 Page1/Page2；各 policy 均 replay 同一 snapshot。",
        "",
        "## Policy 结果",
        "",
        "| Policy | GT found | Macro recall | Micro recall | ΔGT | Page2 calls | ΔGT/call | Always gain retention |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        policy_row("Native Page1", policies["native_page1"]),
        policy_row("Jaccard Router", policies["jaccard_router"]),
        policy_row("Always Page2", policies["always_page2"]),
        policy_row("Oracle top1", policies["oracle_top1"]),
        "",
        "Random top1（1000 trials）：",
        "",
        f"- ΔGT mean={value(random['delta_gt']['mean'])}，std={value(random['delta_gt']['population_std'])}，range={random['delta_gt']['min']}–{random['delta_gt']['max']}。",
        f"- GT found mean={value(random['gt_found']['mean'])}；macro recall mean={value(random['macro_recall']['mean'])}；micro recall mean={value(random['micro_recall']['mean'])}。",
        f"- Random >= Router：{random['random_greater_or_equal_router_count']}/1000。",
        "",
        "## 判别能力",
        "",
        f"- max_jaccard global ROC-AUC：{value(result['auc']['global_roc_auc'])}。",
        f"- within-question pair-weighted AUC：{value(result['auc']['within_question_pair_weighted_auc'])}。",
        f"- 可比较题数：{result['auc']['within_question_comparable_questions']}；positive-negative pairs：{result['auc']['within_question_positive_negative_pairs']}。",
        f"- query labels：positive={result['auc']['positive_queries']}，negative={result['auc']['negative_queries']}。",
        "",
        "标签固定为：单条 query 的 Page2 相对该题全部 native Page1 union 是否新增至少一个 GT；排序方向固定为 max_jaccard 越高越优。",
        "",
        "## 分组结果",
        "",
    ]
    for group in ("author-written", "inline-citation"):
        data = result["groups"][group]
        lines += [
            f"### {group}",
            "",
            "| Policy | GT found | Macro recall | Micro recall | ΔGT | Calls | ΔGT/call | Retention |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
            policy_row("Native Page1", data["native_page1"]),
            policy_row("Jaccard Router", data["jaccard_router"]),
            policy_row("Always Page2", data["always_page2"]),
            policy_row("Oracle top1", data["oracle_top1"]),
            "",
            f"Random ΔGT mean={value(data['random']['delta_gt']['mean'])}，std={value(data['random']['delta_gt']['population_std'])}；macro recall mean={value(data['random']['macro_recall']['mean'])}。",
            "",
        ]
    lines += [
        "## 身份映射修订",
        "",
        "唯一 exact-normalized-title 一对多冲突依据官方静态 arXiv metadata 解决：corpusid 258960101 保留 `2305.17359`（DNA-GPT），拒绝误关联的 `2303.02909`（Dynamic Prompting）。未使用 Search/Page2 outcome，未扩展 fuzzy matching，未补普通 title miss。",
        "",
        "原 PAGE2_ROUTING_PREREG_VALIDATION_003 的停止记录、0 抽样和 0 Search 结论保持不变；003B 由独立 amendment 激活。",
        "",
        "## 口径与限制",
        "",
        "- GT 按冻结的 normalized title groups 与静态唯一 arXiv ID 映射计数，同题跨 query/page 去重。",
        "- Primary 的 50 次 Page2 是 policy replay logical budget；真实采集成本等于 Always Page2。",
        "- Oracle top1 使用 GT，仅为离线上界，不属于可部署 policy。",
        "- Serper Page1/Page2 是尽量连续获取的同次实验快照，但搜索服务本身不是可重复的静态索引。",
        "- CPU 环境预检在首个 forward、生成任何 token 前失败；未产生 query 或 Search，正式采集使用冻结 CUDA/FlashAttention 路径。",
        "",
        "## 产物完整性",
        "",
        f"- PREREGISTRATION.md：`{sha(ROOT / 'PREREGISTRATION.md')}`",
        f"- MAPPING_AMENDMENT.md：`{sha(ROOT / 'MAPPING_AMENDMENT.md')}`",
        f"- dataset_manifest.json：`{sha(ROOT / 'dataset_manifest.json')}`",
        f"- snapshot_manifest.json：`{sha(ROOT / 'snapshot_manifest.json')}`",
        f"- states.json：`{sha(ROOT / 'states.json')}`",
        f"- decisions.json：`{sha(ROOT / 'decisions.json')}`",
        f"- results.json：`{sha(ROOT / 'results.json')}`",
        "",
        "最终独立验证结论见 `validation.json`。",
    ]
    (ROOT / "PAGE2_ROUTING_PREREG_VALIDATION_003B.md").write_text("\n".join(lines) + "\n")
    print("Rendered PAGE2_ROUTING_PREREG_VALIDATION_003B.md")


if __name__ == "__main__":
    main()
