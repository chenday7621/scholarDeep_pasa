"""Render only the completed Search-only paired results."""
import json
from datetime import datetime
import statistics
from common import WORK, OUT, REPORT, now, read, save


def pct(value):
    return f'{value:.4%}'


def esc(value):
    return str(value).replace('|', '\\|').replace('\n', '<br>')


def titles(q, keys):
    return [' / '.join(a['title'] for a in q['gt']['normalized_groups'][key]) for key in keys]


def title_list(q, keys):
    values = titles(q, keys)
    return '\n'.join(f'- {value}' for value in values) if values else '无。'


def table(qs):
    lines = ['| Q | GT | A found / Recall | B found / Recall | Δ Recall | q5 marginal / anchor marginal |',
             '|---|---:|---|---|---|---|']
    for q in qs:
        a, b, c = q['groups']['A'], q['groups']['B'], q['comparison']
        lines.append(f"| {q['query_id']} | {q['gt']['total']} | {a['gt_found']} / {pct(a['recall'])} | {b['gt_found']} / {pct(b['recall'])} | {100*c['delta_recall']:+.4f} pp | {len(c['q5_marginal_gt'])} / {len(c['anchor_marginal_gt'])} |")
    return lines


def main():
    d = read()
    assert d['status'] in ('evaluated', 'complete')
    eq, full = d['summary']['equal_budget_48Q'], d['summary']['full_50Q']
    lines = ['# QUERY_PLANNER_V1_2_SEARCH_AB_001', '',
             f"48Q equal-budget：A/B GT found **{eq['A']['GT_FOUND']} / {eq['B']['GT_FOUND']}**，Macro Search Recall **{pct(eq['A']['MACRO_SEARCH_RECALL'])} → {pct(eq['B']['MACRO_SEARCH_RECALL'])}**（{100*eq['comparison']['macro_recall_delta']:+.4f} pp）。", '',
             '本次只测 Search-only paired A/B。复用已验证的 V1.2 002 queries，未重新调用 Crawler，未执行 Selector、Citation Expand 或完整 PaSa。', '',
             '## 48Q equal-budget replacement', '',
             '仅含 native=5 的 48 题；每组每题 5 个逻辑查询槽位。共同 q1–q4 只请求一次；比较 q5 与 anchor。Q18、Q28 不在此汇总中。', '',
             '| 指标 | A：native | B：anchor + 前4 native |', '|---|---:|---:|',
             f"| GT denominator | {eq['TOTAL_GT']} | {eq['TOTAL_GT']} |",
             f"| GT found | {eq['A']['GT_FOUND']} | {eq['B']['GT_FOUND']} |",
             f"| Macro Search Recall | {pct(eq['A']['MACRO_SEARCH_RECALL'])} | {pct(eq['B']['MACRO_SEARCH_RECALL'])} |",
             f"| Micro Search Recall | {pct(eq['A']['MICRO_SEARCH_RECALL'])} | {pct(eq['B']['MICRO_SEARCH_RECALL'])} |",
             f"| Logical Serper calls | {eq['A']['LOGICAL_SERPER_CALLS']} | {eq['B']['LOGICAL_SERPER_CALLS']} |",
             f"| Attributed Serper attempts（含失败） | {eq['A']['ATTRIBUTED_SERPER_ATTEMPTS']} | {eq['B']['ATTRIBUTED_SERPER_ATTEMPTS']} |", '',
             f"B>A / B=A / B<A：**{eq['comparison']['B_gt_A_questions']} / {eq['comparison']['B_eq_A_questions']} / {eq['comparison']['B_lt_A_questions']} 题**。", '',
             '| Component / marginal 指标 | GT 数量 |', '|---|---:|']
    labels = {'common_gt_count': 'Common GT：q1–q4 合并命中', 'q5_component_gt_count': 'q5 单条 query 命中（含与 common/anchor 重叠）',
              'anchor_component_gt_count': 'anchor 单条 query 命中（含与 common/q5 重叠）',
              'q5_only_gt_count': 'q5-only GT：仅 A 命中，Q − (C ∪ H)',
              'anchor_only_gt_count': 'anchor-only GT：仅 B 命中，H − (C ∪ Q)',
              'q5_marginal_gt_count': 'q5 marginal GT gain：Q − C',
              'anchor_marginal_gt_count': 'anchor marginal GT gain：H − C',
              'shared_exclusive_component_marginal_gt_count': 'q5/anchor 共同新增：(Q ∩ H) − C'}
    lines += [f'| {label} | {eq[key]} |' for key, label in labels.items()]
    lines += ['', 'C、Q、H 分别表示同题 common、q5、anchor 找到的归一化 GT 标题集合。所有总数按 (QID, normalized GT title) 累加，不跨问题合并。Macro 对问题等权，Micro 为 pooled found / pooled GT。', '',
              '## Full 50Q（包含两题追加 anchor）', '',
              '| 指标 | A | B |', '|---|---:|---:|',
              f"| GT denominator | {full['TOTAL_GT']} | {full['TOTAL_GT']} |",
              f"| GT found | {full['A']['GT_FOUND']} | {full['B']['GT_FOUND']} |",
              f"| Macro Search Recall | {pct(full['A']['MACRO_SEARCH_RECALL'])} | {pct(full['B']['MACRO_SEARCH_RECALL'])} |",
              f"| Micro Search Recall | {pct(full['A']['MICRO_SEARCH_RECALL'])} | {pct(full['B']['MICRO_SEARCH_RECALL'])} |",
              f"| Logical Serper calls（组归属） | {full['A']['LOGICAL_SERPER_CALLS']} | {full['B']['LOGICAL_SERPER_CALLS']} |",
              f"| Attributed Serper attempts（含失败） | {full['A']['ATTRIBUTED_SERPER_ATTEMPTS']} | {full['B']['ATTRIBUTED_SERPER_ATTEMPTS']} |",
              f"| Successful query responses（组归属） | {full['A']['SUCCESSFUL_QUERY_RESPONSES']} | {full['B']['SUCCESSFUL_QUERY_RESPONSES']} |", '',
              f"实际唯一 logical query **{full['actual_unique_logical_queries']}**，实际请求尝试 **{full['actual_unique_serper_attempts']}**，成功响应 **{full['actual_successful_responses']}**；HTTP 状态 `{json.dumps(full['http_statuses'])}`。共享请求在 A/B 各自归属计数中各计一次，但真实网络只执行一次，不能相加当作实际费用。", '',
              '## Q18、Q28：追加 anchor 的补充实验', '']
    for q in d['per_query']:
        if q['query_id'] not in ('Q18', 'Q28'):
            continue
        a, b = q['groups']['A'], q['groups']['B']
        lines += [f"### {q['query_id']}", '', q['original_question'], '',
                  f"A：{a['gt_found']}/{q['gt']['total']}，B：{b['gt_found']}/{q['gt']['total']}；新增 {len(q['comparison']['anchor_only_gt'])}，丢失 {len(q['comparison']['q5_only_gt'])}。A 为 4 条，B 为 5 条，属于增加一次 anchor 搜索。", '',
                  '新增 GT：', '', title_list(q, q['comparison']['anchor_only_gt']), '']
    eq_qs = [q for q in d['per_query'] if q['cohort'] == 'equal_budget_48Q']
    lines += ['## 48Q Recall 变化最大的题', '', '### 提升最大', '']
    lines += table(sorted([q for q in eq_qs if q['comparison']['delta_recall'] > 0], key=lambda q: -q['comparison']['delta_recall'])[:5])
    lines += ['', '### 下降最大', '']
    lines += table(sorted([q for q in eq_qs if q['comparison']['delta_recall'] < 0], key=lambda q: q['comparison']['delta_recall'])[:5])
    lines += ['', '## Q28、Q48 的 constraint loss 重点核查', '']
    for q in d['per_query']:
        if q['query_id'] not in ('Q28', 'Q48'):
            continue
        lines += [f"### {q['query_id']}", '', 'Original question：', '', q['original_question'], '',
                  '| Component | 固定 query | 命中 GT | 无标题候选数 |', '|---|---|---:|---:|']
        for key, s in q['searches'].items():
            lines.append(f"| {key} | {esc(s['query_text'])} | {len(s['matched_gt'])} | {len(s['missing_metadata_ids'])} |")
        lines += ['', 'Anchor 原样保留问题中的实体和约束；本次只依据实际搜索命中报告效果，不将约束保留与特定 GT 的找回直接等同为因果证明。', '',
                  'Anchor marginal GT（相对 common）：', '', title_list(q, q['comparison']['anchor_marginal_gt']), '',
                  'q5-only GT（替换后丢失）：', '', title_list(q, q['comparison']['q5_only_gt']), '',
                  'anchor-only GT（替换或追加后新增）：', '', title_list(q, q['comparison']['anchor_only_gt']), '']
    lines += ['## 全部逐题结果', ''] + table(d['per_query'])
    missing = [aid for aid, m in d['metadata'].items() if m['status'] != 'PASS']
    failed = [{'query_id': q['query_id'], 'query_key': k, 'attempts': len(s['attempts'])}
              for q in d['per_query'] for k, s in q['searches'].items() if s['status'] != 'PASS']
    gaps = []
    for q in eq_qs:
        times = [datetime.fromisoformat(q['searches'][k]['attempts'][0]['started_utc']) for k in ('q5', 'anchor')]
        gaps.append(abs((times[1] - times[0]).total_seconds()))
    lines += ['', '## 冻结规则、配对与基础设施', '',
              '- Serper endpoint、Top-K=10、page=1、before:2024-09-24 site:arxiv.org 与先前 Search-only 实验一致；URL 仅按原生现代 arXiv ID 正则解析。before 是搜索操作符，不新增本地日期过滤。',
              '- 原生标题 resolver：local ZIP 优先，仅对直接返回 ID 作 arXiv 元数据 fallback。所有组件共享同一 ID→title 快照，不使用 GT/Serper 标题补全，不使用 fuzzy/alias/embedding 匹配。',
              '- 正式评测沿用 keep_letters（Unicode 字母、小写、删除非字母）完全匹配。791 个原始标注归一化为 790 个标题组；已知标题碰撞不在本实验修改。48Q/50Q A/B 四组都用未改动 metrics.py 复算。',
              f"- 元数据候选 {len(d['metadata'])} 个，未解析标题 {len(missing)} 个。未解析候选不进入正式标题命中，指标包含此基础设施限制。元数据 HTTP：`{json.dumps(d['provenance']['metadata_summary']['http_statuses'])}`。",
              '- 元数据进程在已保存 935 个 ID 后停止；确认旧进程已结束后恢复，跳过全部已完成 ID。网络日志与逐 ID 索引完整保留，恢复前没有已发送但缺少终态记录的 ID；没有重跑 Serper。',
              '- A/B query 顺序与上一阶段完全相同；HTTP 调度先 common，再交错 q5/anchor 的先后。共同 query 使用同一请求记录和原始响应，无 A/B 间重复请求。',
              f"- q5/anchor 首次请求起始间隔中位数 {statistics.median(gaps):.3f}s，最大 {max(gaps):.3f}s。紧邻调度降低时间差，不能固定搜索索引。",
              '- 所有尝试保留 raw response text、原始响应 bytes base64、SHA-256、structured response、payload、query ID、component key、时间与状态；不保存认证头或 API key。',
              '- 首次本地沙箱网络失败保留在请求尝试数中；已成功请求不会补跑。网络失败不等于已成功到达 Serper。',
              f"- 达原定重试上限仍失败的 query：`{json.dumps(failed)}`。失败响应作为空候选保留，不从问题分母剔除；共享 query 失败对 A/B 使用同一记录。本轮 Q40 的 common q3 失败，因此该题结果包含共同检索不完整的影响。",
              '- 无 Crawler、Selector、Citation Expand 或完整 PaSa 调用，无主流程或 evaluator 修改。', '',
              '## 产物', '',
              '- 主 JSON：查询、共同响应引用、GT 集合分解、元数据、逐题命中证据和全部汇总。',
              '- requests/：每条 query 每次尝试的完整原始响应；completed_queries/：搜索完成时的快照。',
              '- metadata/ 与 metadata_network.json：直接返回 ID 的标题解析结果和网络日志。',
              '- official_metric_inputs/：四组 Search-only 树；select_score=0 仅为原版 evaluator 的结构占位，没有运行 Selector。',
              '- validation.json：独立 replay/集合/调用次数复核。', '',
              '本阶段在 Search-only paired A/B 完成后停止，未运行下一阶段。', '']
    REPORT.write_text('\n'.join(lines))
    d['status'] = 'complete'
    d['provenance']['report_written_utc'] = now()
    save(OUT, d)
    print(f'Report written: {REPORT}', flush=True)


if __name__ == '__main__':
    main()
