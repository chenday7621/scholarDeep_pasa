"""The only stage permitted to read GT, Page2 outcomes, and evaluation references."""
from collections import defaultdict
from itertools import combinations
from math import comb
import random
import sys
from statistics import mean, pstdev
import ast
import base64
import hashlib

from common import HERE, REPO, SOURCE, PLAN, BUDGETS, Guard, read, save, sha, digest, key, hits, check_response

SEED = 20260916
TRIALS = 1000
REPORT = HERE / 'ADAPTIVE_PAGE2_CONTROLLER_OFFLINE_001.md'


def bit_union(values):
    result = 0
    for v in values:
        result |= v
    return result


def oracle_exact(keys_by_question, masks, denominators):
    """Exact multiple-choice knapsack: enumerate <=32 subsets/question, then DP.

    Outcomes never overlap across questions. At each exact cost, keep the local
    best GT coverage; maximizing the sum is therefore globally exact. Macro is
    only a secondary tiebreak, not a separate macro-recall upper bound.
    """
    local = []
    for q, keys in sorted(keys_by_question.items()):
        choices = []
        for cost in range(len(keys) + 1):
            best = None
            for selected in combinations(keys, cost):
                gain = bit_union(masks[k] for k in selected).bit_count()
                candidate = (gain, selected)
                if best is None or gain > best[0] or (gain == best[0] and selected < best[1]):
                    best = candidate
            choices.append((cost, best[0], best[0] / denominators[q] / 50, best[1]))
        local.append(choices)
    dp = {0: (0, 0.0, ())}
    for choices in local:
        nxt = {}
        for spent, (gain, macro, selected) in dp.items():
            for cost, extra, macro_extra, subset in choices:
                budget = spent + cost
                candidate = (gain + extra, macro + macro_extra, selected + subset)
                if budget not in nxt or candidate[:2] > nxt[budget][:2] or (candidate[:2] == nxt[budget][:2] and candidate[2] < nxt[budget][2]):
                    nxt[budget] = candidate
        dp = nxt
    return dp


def permutations(keys):
    rng = random.Random(SEED)
    output = []
    for _ in range(TRIALS):
        row = list(keys)
        rng.shuffle(row)
        output.append(row)
    return output


def main():
    source_paths = [HERE / p for p in ['common.py', 'features.py', 'controller.py', 'validate.py', 'evaluate.py']]
    local_inputs = [HERE / p for p in ['states.json', 'decisions.json', 'features_access.json', 'controller_access.json', 'validation_controller.json']]
    reference = REPO / 'PAGE2_SEARCH_PROBE_001.json'
    dataset = REPO / 'data/RealScholarQuery/test.jsonl'
    protected = [REPO / p for p in ['paper_agent.py', 'models.py', 'utils.py', 'metrics.py', 'paper_node.py', 'run_paper_agent.py', 'agent_prompt.json']]
    outputs = [HERE / p for p in ['results.json', 'random_trials.json', 'evaluation_query_outcomes.json', 'validation_evaluation.json', 'evaluation_access.json', 'snapshot_manifest.json']]
    guard = Guard([PLAN, reference, dataset, *local_inputs, *protected], [*outputs, REPORT], source_paths)
    pre_hashes = {str(p): sha(p) for p in [*source_paths, *local_inputs, *protected, PLAN, reference, dataset]}
    assert read(HERE / 'validation_controller.json')['status'] == 'PASS'
    states, decisions = read(HERE / 'states.json'), read(HERE / 'decisions.json')
    assert decisions['states_sha256'] == sha(HERE / 'states.json')
    assert decisions['controller_source_sha256'] == sha(HERE / 'controller.py')
    tasks = sorted(read(PLAN)['tasks'], key=lambda t: (t['query_index'], t['query_sequence']))
    ref = read(reference)
    ref_requests = {(r['query_index'], r['query_sequence']): r for r in ref['requests']}
    assert len(tasks) == len(ref_requests) == len(states['states']) == 248
    states_by_key = {s['query_key']: s for s in states['states']}
    snapshot, p1sets, p2sets, by_question = {}, {}, {}, defaultdict(list)
    # Exactly one immutable response pair/query, shared by every replay policy.
    for t in tasks:
        k = key(t)
        rr = ref_requests[(t['query_index'], t['query_sequence'])]
        assert rr['page1_replay'] == t['baseline_replay']
        paths = [t['baseline_replay'], rr['page2_replay']]
        guard.allow(paths)
        p1, p2 = map(read, paths)
        for r in [p1, p2]:
            check_response(r)
        assert p1['request_payload'] == t['baseline_payload']
        assert p2['request_payload'] == dict(t['baseline_payload'], page=2)
        assert p2['structured_response']['searchParameters']['page'] == 2
        assert p2['structured_response']['searchParameters']['q'] == p2['request_payload']['q']
        raw_bytes = base64.b64decode(p2['raw_response_base64'])
        assert hashlib.sha256(raw_bytes).hexdigest() == p2['response_bytes_sha256']
        assert json_loads(raw_bytes) == p2['structured_response']
        assert sha(paths[0]) == states_by_key[k]['page1_file_sha256']
        assert sha(paths[1]) == rr['page2_file_sha256']
        assert p1['raw_response_sha256'] == rr['page1_raw_response_sha256'] == t['baseline_response_sha256']
        assert p2['raw_response_sha256'] == rr['page2_raw_response_sha256']
        p1sets[k], p2sets[k] = ({h['arxiv_id'] for h in hits(r)} for r in [p1, p2])
        assert sorted(p1sets[k]) == states_by_key[k]['candidate_ids'] == rr['page1_ids']
        assert sorted(p2sets[k]) == rr['page2_ids']
        snapshot[k] = {'page1_path': str(paths[0]), 'page1_sha256': sha(paths[0]),
                       'page2_path': str(paths[1]), 'page2_sha256': sha(paths[1])}
        by_question[t['query_index']].append(k)
    snapshot_id = digest(snapshot)
    # Extract the actual pure keep_letters function without importing utils and its I/O.
    tree = ast.parse((REPO / 'utils.py').read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'keep_letters')
    namespace = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'utils.keep_letters (AST isolated)', 'exec'), namespace)
    normalize = namespace['keep_letters']
    gt_rows = [json_loads(line) for line in dataset.read_text().splitlines()]
    groups, denominators, question_masks, id_to_bits, gt_info = [], {}, {}, {}, []
    for q, row in enumerate(gt_rows):
        assert len(row['answer']) == len(row['answer_arxiv_id'])
        local = defaultdict(set)
        for title, aid in zip(row['answer'], row['answer_arxiv_id']):
            local[normalize(title)].add(aid)
        denominators[q] = len(local)
        question_masks[q] = 0
        id_to_bits[q] = defaultdict(int)
        for title_key, aids in sorted(local.items()):
            bit = 1 << len(groups)
            groups.append((q, title_key))
            question_masks[q] |= bit
            gt_info.append({'query_index': q, 'normalized_gt_title': title_key, 'arxiv_ids': sorted(aids)})
            for aid in aids:
                id_to_bits[q][aid] |= bit
    assert len(groups) == 790 and len(gt_rows) == 50
    p1_by_q = {q: set().union(*(p1sets[k] for k in keys)) for q, keys in by_question.items()}
    base_mask = bit_union(id_to_bits[q].get(aid, 0) for q, ids in p1_by_q.items() for aid in ids)
    masks = {key(t): bit_union(id_to_bits[t['query_index']].get(aid, 0) for aid in p2sets[key(t)]) & ~base_mask for t in tasks}
    all_gain_mask = bit_union(masks.values())
    base_count, all_gain = base_mask.bit_count(), all_gain_mask.bit_count()
    assert (base_count, all_gain) == (157, 63)
    assert ref['metrics']['all_normalized_GT_790']['PAGE1_GT_FOUND'] == base_count
    assert ref['metrics']['all_normalized_GT_790']['NEW_GT_FROM_PAGE2'] == all_gain
    original_cases = {(c['query_index'], c['normalized_gt_title']): c for c in ref['all_gt_cases']}
    for i, g in enumerate(groups):
        c = original_cases[g]
        assert bool(base_mask & (1 << i)) == c['page1_found']
        assert bool(all_gain_mask & (1 << i)) == c['new_from_page2']

    def measure(selected):
        gained = bit_union(masks[k] for k in selected)
        total, calls = base_mask | gained, len(selected)
        delta = gained.bit_count()
        return {'gt_found': total.bit_count(), 'delta_gt': delta,
                'macro_search_recall': mean((total & question_masks[q]).bit_count() / denominators[q] for q in range(50)),
                'micro_search_recall': total.bit_count() / 790,
                'extra_page2_calls': calls, 'delta_gt_per_extra_call': delta / calls if calls else None,
                'always_page2_gain_retention': delta / all_gain,
                'snapshot_id': snapshot_id}

    keys = [key(t) for t in tasks]
    native, always = measure([]), measure(keys)
    for q, row in enumerate(ref['per_query']):
        assert (base_mask & question_masks[q]).bit_count() == row['page1_gt_found']
        assert ((base_mask | all_gain_mask) & question_masks[q]).bit_count() == row['page1_plus_page2_gt_found']
    oracle = oracle_exact(by_question, masks, denominators)
    # Verify exact solver against full enumeration on an overlapping synthetic case.
    synthetic = {'a': 0b0011, 'b': 0b0110, 'c': 0b1000, 'd': 0b1000}
    synthetic_dp = oracle_exact({0: ['a', 'b'], 1: ['c', 'd']}, synthetic, {0: 3, 1: 1})
    for b in range(5):
        assert synthetic_dp[b][0] == max(bit_union(synthetic[k] for k in ss).bit_count() for ss in combinations(synthetic, b))
    draws = permutations(keys)
    assert draws == permutations(keys)
    draw_hash = digest(draws)
    trials_by_budget, results, p_values = {}, {}, []
    metric_names = ['gt_found', 'delta_gt', 'macro_search_recall', 'micro_search_recall', 'extra_page2_calls', 'delta_gt_per_extra_call', 'always_page2_gain_retention']
    for budget in BUDGETS:
        b = len(keys) if budget == 'all' else budget
        adaptive_keys = decisions['budgets'][str(budget)]
        assert len(adaptive_keys) == len(set(adaptive_keys)) == b
        adaptive = measure(adaptive_keys)
        oracle_keys = list(oracle[b][2])
        exact = measure(oracle_keys)
        assert exact['delta_gt'] == oracle[b][0]
        trials = [measure(draw[:b]) for draw in draws]
        assert all(t['extra_page2_calls'] == b for t in trials)
        assert exact['delta_gt'] >= max(adaptive['delta_gt'], max(t['delta_gt'] for t in trials))
        stat = {m: {'mean': mean(t[m] for t in trials), 'std': pstdev(t[m] for t in trials)} for m in metric_names}
        deltas = sorted(t['delta_gt'] for t in trials)
        # Exact expectation under uniform sampling without replacement.
        expected_gain = sum(1 - (comb(len(keys) - sum(bool(mask & (1 << i)) for mask in masks.values()), b) / comb(len(keys), b)) for i in range(len(groups)) if all_gain_mask & (1 << i))
        expected_macro_gain = sum((1 - comb(len(keys) - sum(bool(mask & (1 << i)) for mask in masks.values()), b) / comb(len(keys), b)) / denominators[groups[i][0]] / 50 for i in range(len(groups)) if all_gain_mask & (1 << i))
        p = (1 + sum(t['delta_gt'] >= adaptive['delta_gt'] for t in trials)) / (TRIALS + 1)
        comparison = {'adaptive_minus_random_mean_delta_gt': adaptive['delta_gt'] - stat['delta_gt']['mean'],
                      'adaptive_strict_win_fraction': mean(adaptive['delta_gt'] > t['delta_gt'] for t in trials),
                      'adaptive_tie_fraction': mean(adaptive['delta_gt'] == t['delta_gt'] for t in trials),
                      'random_ge_adaptive_one_sided_p': p,
                      'random_delta_gt_central95_interval': [deltas[24], deltas[974]],
                      'random_exact_expected_delta_gt': expected_gain,
                      'random_exact_expected_macro_recall': native['macro_search_recall'] + expected_macro_gain}
        if budget != 'all':
            p_values.append((str(budget), p))
        results[str(budget)] = {'budget': b, 'snapshot_id': snapshot_id, 'native_page1': native,
                               'random_page2': {'trials': TRIALS, 'seed': SEED, 'snapshot_id': snapshot_id, 'metrics': stat},
                               'adaptive': adaptive, 'oracle': dict(exact, selected_query_keys=oracle_keys),
                               'always_page2': dict(always, within_budget=(b == len(keys))), 'comparison': comparison}
        trials_by_budget[str(budget)] = [{m: t[m] for m in metric_names} for t in trials]
        if budget == 'all':
            assert all(t == always for t in trials) and adaptive == always and exact == always
    running_p = 0
    for i, (budget, p) in enumerate(sorted(p_values, key=lambda x: x[1])):
        running_p = max(running_p, min(1.0, (len(p_values) - i) * p))
        results[budget]['comparison']['holm_adjusted_p_six_budgets'] = running_p
    # Recompute full random metrics independently from the same seed, not only selections.
    for budget in BUDGETS:
        b = len(keys) if budget == 'all' else budget
        second = [{m: t[m] for m in metric_names} for draw in permutations(keys) for t in [measure(draw[:b])]]
        assert second == trials_by_budget[str(budget)]
    outcomes = []
    running_mask = 0
    for ranked in decisions['ranking']:
        k = ranked['query_key']
        new = masks[k] & ~running_mask
        outcomes.append(dict(ranked, isolated_new_gt_vs_all_page1=masks[k].bit_count(),
                             incremental_new_gt_in_controller_order=new.bit_count(),
                             new_gt=[gt_info[i] for i in range(len(groups)) if masks[k] & (1 << i)]))
        running_mask |= masks[k]
    score_bins = []
    for start in range(0, len(keys), 25):
        subset = [r['query_key'] for r in decisions['ranking'][start:start + 25]]
        score_bins.append({'ranks': [start + 1, start + len(subset)], 'query_count': len(subset),
                           'unique_gain_within_bin': bit_union(masks[k] for k in subset).bit_count(),
                           'positive_query_count': sum(bool(masks[k]) for k in subset)})
    result = {'experiment': HERE.name, 'status': 'PASS', 'snapshot_id': snapshot_id,
              'query_count': 248, 'question_count': 50, 'gt_denominator': 790,
              'python_version': sys.version,
              'matching': 'Original keep_letters GT-title grouping; group covered if any annotated ID appears in parsed organic URL. ID-assisted coverage, not official metadata-title matching.',
              'policy': decisions['policy'], 'random_seed': SEED, 'random_trials': TRIALS,
              'random_permutation_sha256': draw_hash,
              'oracle_method': 'Exact local subset enumeration and cross-question dynamic programming; maximize GT found, macro recall secondary tiebreak.',
              'budgets': results, 'posthoc_score_bins': score_bins,
              'controller_artifact_hashes_before_evaluation': {str(p): pre_hashes[str(p)] for p in local_inputs},
              'network_requests': 0, 'crawler_generations': 0, 'model_calls': 0,
              'notes': ['Always Page2 uses 248 extra logical calls at every budget; not budget-feasible except all.',
                        '1000 uniform random permutations; nested prefixes give uniform subsets at each budget; population std (ddof=0).',
                        'Calls mean successful cached logical Page2 slots, excluding original transport retries; new real calls are zero.',
                        'Random p values quantify allocation variation on this snapshot, not generalization to new questions or time.',
                        'This known benchmark has prior public outcome reports; code-level outcome isolation is not prospective blind validation.']}
    unchanged = {p: sha(p) == h for p, h in pre_hashes.items()}
    assert all(unchanged.values())
    for pair in snapshot.values():
        assert sha(pair['page1_path']) == pair['page1_sha256']
        assert sha(pair['page2_path']) == pair['page2_sha256']
    validation = {'status': 'PASS', 'queries_match_original_248': True,
                  'all_790_original_gt_group_outcomes_reproduced': True,
                  'page1_gt_found': base_count, 'always_page2_delta_gt': all_gain,
                  'identical_snapshot_for_all_policies': True, 'snapshot_id': snapshot_id,
                  'random_selections_and_all_trial_metrics_reproduced': True,
                  'random_seed': SEED, 'random_trials': TRIALS,
                  'oracle_synthetic_exhaustive_check': True, 'all_budget_policies_converge_at_all': True,
                  'all_inputs_and_controller_artifacts_unchanged': unchanged,
                  'all_496_response_files_unchanged': True}
    save(HERE / 'snapshot_manifest.json', {'snapshot_id': snapshot_id, 'responses': snapshot, 'input_hashes': pre_hashes})
    save(HERE / 'random_trials.json', {'seed': SEED, 'permutation_sha256': draw_hash, 'ordered_query_universe': keys,
                                     'sampling': 'random.Random(seed); shuffle canonical list once per trial; nested budget prefixes',
                                     'trials_by_budget': trials_by_budget})
    save(HERE / 'evaluation_query_outcomes.json', {'queries': outcomes})
    save(HERE / 'validation_evaluation.json', validation)
    save(HERE / 'results.json', result)
    write_report(result, score_bins)
    save(HERE / 'evaluation_access.json', guard.evidence())
    print('Offline evaluation and all validations: PASS')
    for b, r in results.items():
        print(f"budget={b}: Adaptive +{r['adaptive']['delta_gt']}, Random +{r['random_page2']['metrics']['delta_gt']['mean']:.3f} ± {r['random_page2']['metrics']['delta_gt']['std']:.3f}, Oracle +{r['oracle']['delta_gt']}")


def json_loads(value):
    import json
    return json.loads(value)


def write_report(result, score_bins):
    # Report is produced only after evaluation; it is never a controller input.
    data = result['budgets']
    b50 = data['50']
    a50 = b50['adaptive']['delta_gt']
    r50 = b50['random_page2']['metrics']['delta_gt']
    above = [b for b in data if b != 'all' and data[b]['comparison']['adaptive_minus_random_mean_delta_gt'] > 0]
    significant = [b for b in data if b != 'all' and data[b]['comparison']['holm_adjusted_p_six_budgets'] < .05]
    p = lambda v: f'{100*v:.4f}%'
    lines = ['# ADAPTIVE_PAGE2_CONTROLLER_OFFLINE_001', '',
             f"在固定历史 snapshot 上，budget=50 时 Adaptive 新增 **{a50} GT**，Random 为 **{r50['mean']:.3f} ± {r50['std']:.3f}**，Oracle 为 **{b50['oracle']['delta_gt']}**。Always Page2 全部 248 次新增 63 GT；Adaptive 保留 **{p(a50/63)}**。", '',
             '## 结论', '',
             f"- **是否稳定优于 Random：**6 个非全量预算中，{len(above)} 个高于 Random 均值（{', '.join(above) or '无'}）；Holm 校正后的单侧 p<0.05 有 {len(significant)} 个（{', '.join(significant) or '无'}）。" + ('本次显示跨预算的明显分配信号，但仍需独立题集/时间快照验证。' if len(significant) >= 4 and len(above) == 6 else '当前规则在全部非全量预算均低于 Random 均值，未获得预期优势。' if not above else '本次不足以声称稳定优于随机分配。'),
             f"- **budget=50：**248 次原始 Page1 基础上增加 50 个逻辑槽位，即 +20.16%；新增 {a50} GT，效率 {a50/50:.4f} GT/call。随机分配同预算已新增 {r50['mean']:.3f}，因此路由本身的贡献应看与随机的差值 {a50-r50['mean']:+.3f}，不能用全部新增量代表 Controller 效果。",
             f"- **与 unconditional Anchor +50→+5：**数值上{'高于' if a50>5 else '等于' if a50==5 else '低于'} +5（{a50} vs 5；{a50/50:.3f} vs 0.100 GT/call）。本次仅多 1 GT，不能称为明显改善。但 Page2 是旧 baseline 的 ID 辅助覆盖，Anchor 是另一次快照上的原生 metadata 标题匹配，不能宣称同口径显著优于 Anchor，也不能把 Page2 自身的收益归功于路由。",
             '- **是否值得进入下一阶段：**' + ('可进入独立数据上的 Controller 验证，保持公式冻结；尚不能直接接入正式流程。' if len(significant) >= 4 and len(above) == 6 else '当前启发式的排序方向失败，不支持按现规则推进集成；但不能推出 retrieval feedback 完全无信号。分层呈现反向趋势，足以提出一个后续离线假设；若研究“高重叠/检索饱和更需要 Page2”，应事先固定规则并在独立数据上验证。本轮不反转排序、不调权重、不报告事后改良 policy。'), '',
             '## 数据与评测口径', '',
             '- 50 个用户问题、248 条 native query：Q18/Q28 各 4 条，其余各 5 条。一个 query 的 Page2 占一个全局预算槽位；不是每题相同配额。',
             '- 仅使用 PAGE2_SEARCH_PROBE_001 的配对响应。Page1 为 2026-09-10、Page2 为 2026-09-11；不是同时获取，before 日期不能冻结索引/排名。所有 policy 共享同一历史配对快照。',
             '- 复用 utils.py 的 keep_letters 函数，通过 AST 仅加载该纯函数，避免导入 utils 触发数据加载或网络 SDK。GT 按归一化标题分成 790 组；组内任一标注 arXiv ID 出现在原 URL parser 的 organic 链接中即算命中。每题内跨 query、跨 page 去重，不跨用户问题合并。',
             '- Q45 Panacea/Panacea+ 两个 ID 归到同一标题组，沿用原实验；不使用 snippet 提及、fuzzy matching、站外链接补充。该口径是 ID-assisted Search coverage，不能混同官方 metadata-title Recall。',
             '- 复现原实验 Page1=157、Page1+全部 Page2=220、新增=63；逐个核验全部 790 组的原始命中状态。Macro Search Recall 对 50 个用户问题等权，Micro 分母为 790。',
             '- 预算单位为逻辑 Page2 calls。原缓存含失败重试，本实验不把重试算作预算，也未实际请求任何网络；不评测 Selector/Expand 或最终端到端效果。', '',
             '## 冻结 heuristic 与特征', '',
             '```text', result['policy']['formula'], '```', '',
             '- fill = min(Page1 unique valid IDs / requested num=10, 1)。exclusive ratio = 该 query 相对同题其他全部 native queries 的独有 ID 数 / 该 query unique ID 数。mean Jaccard 为与同题其他 query 的结果 ID 集合 Jaccard 均值。',
             '- 直觉：完整的一页提示可能还有后续候选，独有候选与较低重叠提示独立的检索方向。它不判断论文相关性，属于未经收益调参的假设。',
             '- 同时输出：valid occurrences、invalid URL 数、页内重复率、leave-one-out marginal unique、原序 marginal unique、mean/max Jaccard、跨 query 重复率、整题重复率与 union 大小、末 5 个位置的有效/独有候选数、snippet 可用率、延迟。仅公式中的 3 个特征参与打分，其余用于可审计状态。',
             '- marginal_unique_candidate_count 定义为 leave-one-out 独有数，避免原生顺序优势；sequential_marginal_unique_candidate_count 单独保留。cross_query_duplicate_ratio = 与其他 query 并集重合比例。空集合比率按 0 处理。',
             '- score 降序，全局排序；并列使用 query key 与原生 query 文本的 SHA256 排序。权重固定 0.5/0.5，先生成 states/decisions 再实现和运行评测，未训练、未尝试收益驱动的替代公式。',
             '- 所有 Page1 返回后做一次预算分配；不读取已执行 Page2 的反馈。这个批量全局控制器不等同于单用户在线调度器。', '',
             '## 全策略结果', '',
             'Random 为 1000 次均值 ± 总体标准差（ddof=0）。Native 和 Always 在每个预算下作为固定参照；Always 仅在 all 满足预算。保留率分母为 Always 新增的 63 GT。', '',
             '| Budget | Policy | GT found | ΔGT | Macro Search Recall | Extra calls | ΔGT/call | 保留 Always 新增GT |',
             '|---|---|---:|---:|---:|---:|---:|---:|']
    for b, row in data.items():
        for policy in ['native_page1', 'random_page2', 'adaptive', 'oracle', 'always_page2']:
            if policy == 'random_page2':
                m = row[policy]['metrics']
                val = lambda name, digits=3, scale=1: f"{m[name]['mean']*scale:.{digits}f} ± {m[name]['std']*scale:.{digits}f}"
                fields = [val('gt_found'), val('delta_gt'), val('macro_search_recall', 4, 100)+'%', str(row['budget']), val('delta_gt_per_extra_call',4), val('always_page2_gain_retention',2,100)+'%']
            else:
                m = row[policy]
                fields = [str(m['gt_found']), str(m['delta_gt']), p(m['macro_search_recall']), str(m['extra_page2_calls']), f"{m['delta_gt_per_extra_call']:.4f}" if m['extra_page2_calls'] else '—', p(m['always_page2_gain_retention'])]
            label = policy + ('（超预算参照）' if policy == 'always_page2' and b != 'all' else '')
            lines.append('| ' + ' | '.join([b, label, *fields]) + ' |')
    lines += ['', '## 随机比较与稳定性', '',
              f'固定 seed={SEED}。每次均匀打乱全部 248 个 query，取预算长度前缀；1000 次 trial，每个预算都是无放回均匀采样。各预算共享随机排列的嵌套前缀。重新从 seed 生成选择并重算全部指标，逐项完全相同。随机均值另用超几何覆盖概率计算精确期望作为核查。', '',
              '| Budget | Adaptive ΔGT | Random ΔGT mean ± std | Random ΔGT 95%区间 | Adaptive−Random mean | 严格胜率 | P(Random≥Adaptive) | Holm校正p | 精确随机期望ΔGT |',
              '|---|---:|---:|---|---:|---:|---:|---:|---:|']
    for b, row in data.items():
        c, r = row['comparison'], row['random_page2']['metrics']['delta_gt']
        adjusted = f"{c['holm_adjusted_p_six_budgets']:.4f}" if b != 'all' else '—'
        lines.append(f"| {b} | {row['adaptive']['delta_gt']} | {r['mean']:.3f} ± {r['std']:.3f} | {c['random_delta_gt_central95_interval']} | {c['adaptive_minus_random_mean_delta_gt']:+.3f} | {p(c['adaptive_strict_win_fraction'])} | {c['random_ge_adaptive_one_sided_p']:.4f} | {adjusted} | {c['random_exact_expected_delta_gt']:.3f} |")
    lines += ['', '单侧 Monte Carlo p=(1+随机ΔGT≥Adaptive的次数)/1001；六个非全量预算做 Holm 校正。95%区间是随机分配结果的经验区间，不是均值置信区间。胜率/显著性仅描述此 snapshot 的预算随机性，不代表跨题集、跨随机生成种子或跨时间稳定性。已知历史基准存在结果报告，代码阶段隔离不能替代前瞻盲测。', '',
              '## Oracle 上界', '',
              '对每个用户问题枚举至多 2^5=32 个 native query 子集，计算其 Page2 相对整题全部 Page1 的去重 GT 增量；每个精确成本保留最优局部子集，再用跨 50 题动态规划求每个总预算的精确最优。因 GT 按用户问题区分，各题收益可相加。这避免将每条 query 的独立收益排序误称全局 Oracle。Oracle 在同 GT 数时以 Macro Recall 作第二目标，其 Macro 值不是独立最大化 Macro 的理论上界。Oracle 读取 GT 仅位于 evaluate.py，不能部署。', '',
              '## 事后分数分层诊断', '',
              '下面仅用于评测解释，没有反馈给 Controller。每层 unique gain 在层内去重，但不同层可重复，不能求和。', '',
              '| 排名区间 | query数 | Page2有新增GT的query数 | 层内去重新增GT |', '|---|---:|---:|---:|']
    for row in score_bins:
        lines.append(f"| {row['ranks']} | {row['query_count']} | {row['positive_query_count']} | {row['unique_gain_within_bin']} |")
    lines += ['',
              '最高分 25 条没有新增 GT，最低分 23 条中 15 条有新增 GT，呈现与原假设相反的方向。低重叠和高 novelty 只能说明候选集合不同，也可能来自主题扩散；它们并不自动意味着深一页更容易命中目标。这一机制解释是事后推测，未做内容相关性验证。相反方向是否能泛化，需要新验证；不能仅据本批把负相关翻转成已证实的可部署 signal。Oracle 在预算 50 下可覆盖全部 63 个新增 GT，说明收益有集中空间，但不证明 Page1 可观测特征足以识别那些 query。', '',
              '## 数据隔离与离线验证', '',
              '- features.py：只允许原请求计划、Page1 原始响应和自身源码。请求计划是执行前创建，不含 GT/Page2 outcomes；不读取混合了评测信息的 PAGE2_SEARCH_PROBE_001.json。',
              '- controller.py：数据输入只有 states.json；SHA256 绑定特征和源码，排序/预算选择保存在 decisions.json。',
              '- validate.py：无标签重算全部特征和排序，检查访问记录。主动读取 GT、Page2 响应、原结果报告、本实验 results.json 均在 I/O 前被拒绝。',
              '- evaluate.py：唯一允许读取 GT/标签的阶段；读取冻结 decisions，不更改权重或排序。全部 policy 使用同一内存中的配对 ID 集，结果记录相同 snapshot ID。',
              '- 所有脚本启用审计钩子，拒绝 socket/DNS、子进程、模型和网络库导入；只允许指定输出文件写入。实际网络请求、Crawler generation、模型调用均为 0。',
              '- query 数量与原实验一致；496 份响应原始文本/字节及文件哈希核验；原始 790 组结果逐组复现；随机排列与全部 trial metrics 重算一致；Oracle 通过带重复覆盖的合成穷举核验；all 时所有策略收敛到同一结果。',
              '- 主流程和全部输入文件哈希前后一致；Controller 的源码和产物在评测前后不变。没有修改 paper_agent.py 或其他正式代码。', '',
              '## 产物与复现', '',
              '- states.json：248 个 Page1 状态及特征；decisions.json：冻结分数、排序和预算选择；results.json：全部策略指标与随机比较。',
              '- random_trials.json：7000 组 trial 指标、固定种子、采样顺序及排列哈希；evaluation_query_outcomes.json：仅评测阶段生成的逐 query GT 证据。',
              '- snapshot_manifest.json：配对快照及输入哈希；features_access.json/controller_access.json/evaluation_access.json：读文件审计；validation_controller.json/validation_evaluation.json：验证结果。', '',
              '在项目根目录执行（只读取已有本地缓存，不需要 GPU、网络或额外依赖）：', '',
              '```bash', 'python3 -B adaptive_page2_controller_offline_001/features.py',
              'python3 -B adaptive_page2_controller_offline_001/controller.py',
              'python3 -B adaptive_page2_controller_offline_001/validate.py',
              'python3 -B adaptive_page2_controller_offline_001/evaluate.py', '```', '',
              f"Snapshot ID: `{result['snapshot_id']}`", '']
    REPORT.write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
