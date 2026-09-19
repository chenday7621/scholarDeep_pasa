"""Offline A5/B6 union replay. No network, model, or metadata resolution calls."""
import ast
import base64
from collections import Counter
import contextlib
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import runpy
import socket
import statistics
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent
SOURCE = ROOT / 'QUERY_PLANNER_V1_2_SEARCH_AB_001.json'
SOURCE_WORK = ROOT / 'query_planner_v1_2_search_ab_001'
OUT = ROOT / 'QUERY_PLANNER_V1_2_A5_B6_REPLAY_001.json'
REPORT = ROOT / 'QUERY_PLANNER_V1_2_A5_B6_REPLAY_001.md'


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def frozen_function(name, expected):
    source = (ROOT / 'utils.py').read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    assert ast.get_source_segment(source, node) == expected
    env = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(ROOT / 'utils.py'), 'exec'), env)
    return env[name]


def aggregate(qs):
    n = len(qs)
    total = sum(q['gt']['total'] for q in qs)
    result = {'questions': n, 'TOTAL_GT': total}
    for group in ('A', 'B'):
        gs = [q['groups'][group] for q in qs]
        found = sum(g['gt_found'] for g in gs)
        slots = sum(len(g['queries']) for g in gs)
        result[group] = {'GT_FOUND': found, 'MACRO_SEARCH_RECALL': statistics.mean(g['recall'] for g in gs),
                         'MICRO_SEARCH_RECALL': found / total, 'QUERY_SLOTS': slots,
                         'AVG_QUERY_COUNT': slots / n,
                         'QUERY_COUNT_DISTRIBUTION': dict(sorted(Counter(str(len(g['queries'])) for g in gs).items()))}
    gained = sum(len(q['added_gt']) for q in qs)
    delta_macro = result['B']['MACRO_SEARCH_RECALL'] - result['A']['MACRO_SEARCH_RECALL']
    delta_micro = result['B']['MICRO_SEARCH_RECALL'] - result['A']['MICRO_SEARCH_RECALL']
    slots_added = result['B']['QUERY_SLOTS'] - result['A']['QUERY_SLOTS']
    avg_added = slots_added / n
    result['comparison'] = {'B_gt_A': sum(bool(q['added_gt']) for q in qs),
                            'B_eq_A': sum(not q['added_gt'] for q in qs), 'B_lt_A': 0,
                            'ANCHOR_NEW_GT': gained, 'MACRO_RECALL_DELTA': delta_macro,
                            'MICRO_RECALL_DELTA': delta_micro,
                            'ADDED_GT_DISTRIBUTION': {q['query_id']: len(q['added_gt']) for q in qs if q['added_gt']}}
    result['cost'] = {'ADDITIONAL_QUERY_SLOTS': slots_added, 'AVG_ADDITIONAL_QUERY_SLOTS': avg_added,
                      'QUERY_BUDGET_RELATIVE_INCREASE': slots_added / result['A']['QUERY_SLOTS'],
                      'GT_GAIN_PER_ADDITIONAL_QUERY_SLOT': gained / slots_added,
                      'MACRO_RECALL_PP_PER_ADDITIONAL_TOTAL_QUERY_SLOT': 100 * delta_macro / slots_added,
                      'MICRO_RECALL_PP_PER_ADDITIONAL_TOTAL_QUERY_SLOT': 100 * delta_micro / slots_added,
                      'MACRO_RECALL_PP_PER_ONE_EXTRA_SLOT_PER_QUESTION': 100 * delta_macro / avg_added,
                      'MICRO_RECALL_PP_PER_ONE_EXTRA_SLOT_PER_QUESTION': 100 * delta_micro / avg_added,
                      'new_actual_requests': 0}
    assert result['B']['GT_FOUND'] - result['A']['GT_FOUND'] == gained
    return result


def official(qs, subset, metadata, keep, cal, expected):
    checks = {}
    for group in ('A', 'B'):
        folder = WORK / 'official_metric_inputs' / subset / group
        for q in qs:
            nodes = [{'title': metadata[aid]['title'], 'child': {}, 'select_score': 0}
                     for aid in q['groups'][group]['candidate_ids'] if metadata[aid]['status'] == 'PASS']
            save(folder / f"{q['query_id']}.json", {'title': q['original_question'], 'extra': {'answer': q['gt']['raw_titles']},
                 'child': {'Search-only replay candidates': nodes}})
        shim = types.ModuleType('utils')
        shim.keep_letters, shim.cal_micro = keep, cal
        old_utils, old_argv = sys.modules.get('utils'), sys.argv[:]
        sys.modules['utils'] = shim
        sys.argv = [str(ROOT / 'metrics.py'), '--output_folder', str(folder)]
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                runpy.run_path(str(ROOT / 'metrics.py'), run_name='__main__')
        finally:
            sys.argv = old_argv
            if old_utils is None:
                sys.modules.pop('utils', None)
            else:
                sys.modules['utils'] = old_utils
        value = float(output.getvalue().strip().splitlines()[0].split('&')[0])
        assert value == round(expected[group]['MACRO_SEARCH_RECALL'], 4)
        checks[group] = {'stdout': output.getvalue(), 'matches_macro_recall': True, 'value': value}
    return checks


def render(d):
    lines = ['# QUERY_PLANNER_V1_2_A5_B6_REPLAY_001', '',
             '只复用 QUERY_PLANNER_V1_2_SEARCH_AB_001 已保存的 response、candidate、metadata 和 GT matching，离线重算并集。没有任何新检索或生成。', '',
             'A 保留全部 native queries，B 在全部 native queries 之后追加已有 anchor。48 题 A5→B6；Q18、Q28 为 A4→B5。所有 native 顺序与文本不变。', '',
             '## Recall 与 GT', '', '| 范围 | 指标 | A | B |', '|---|---|---:|---:|']
    for subset, title in [('native5_48Q', '48Q A5/B6'), ('full_50Q', 'Full 50Q')]:
        s = d['summary'][subset]
        lines += [f"| {title} | GT found / {s['TOTAL_GT']} | {s['A']['GT_FOUND']} | {s['B']['GT_FOUND']} |",
                  f"| | Macro Search Recall | {s['A']['MACRO_SEARCH_RECALL']:.4%} | {s['B']['MACRO_SEARCH_RECALL']:.4%} |",
                  f"| | Micro Search Recall | {s['A']['MICRO_SEARCH_RECALL']:.4%} | {s['B']['MICRO_SEARCH_RECALL']:.4%} |"]
    eq = d['summary']['native5_48Q']
    lines += ['', f"48Q：B>A / B=A / B<A = **{eq['comparison']['B_gt_A']} / {eq['comparison']['B_eq_A']} / 0**。Anchor 相对完整 q1–q5 新增 **{eq['comparison']['ANCHOR_NEW_GT']}** 个 (QID, normalized GT title) 命中。", '',
              '## 新增 GT 分布', '', '| Q | GT 标题 | Anchor response |', '|---|---|---|']
    for q in d['per_query']:
        for key in q['added_gt']:
            titles = ' / '.join(x['title'] for x in q['gt']['normalized_groups'][key]).replace('|', '\\|').replace('\n', '<br>')
            lines.append(f"| {q['query_id']} | {titles} | {q['added_gt_evidence'][key][0]['response_artifact']} |")
    lines += ['', '## Query budget 成本', '',
              '这里计算逻辑 query slots，不是本轮真实网络费用：所有结果都来自既有缓存，本轮网络成本为零。', '',
              '| 指标 | 48Q | Full 50Q |', '|---|---:|---:|']
    full = d['summary']['full_50Q']
    for label, a, b in [
        ('A 平均 query 数', eq['A']['AVG_QUERY_COUNT'], full['A']['AVG_QUERY_COUNT']),
        ('B 平均 query 数', eq['B']['AVG_QUERY_COUNT'], full['B']['AVG_QUERY_COUNT']),
        ('A 总 query slots', eq['A']['QUERY_SLOTS'], full['A']['QUERY_SLOTS']),
        ('B 总 query slots', eq['B']['QUERY_SLOTS'], full['B']['QUERY_SLOTS']),
        ('新增 slots', eq['cost']['ADDITIONAL_QUERY_SLOTS'], full['cost']['ADDITIONAL_QUERY_SLOTS']),
    ]:
        lines.append(f'| {label} | {a} | {b} |')
    lines += [f"| Query budget 增幅 | {eq['cost']['QUERY_BUDGET_RELATIVE_INCREASE']:.4%} | {full['cost']['QUERY_BUDGET_RELATIVE_INCREASE']:.4%} |",
              f"| GT gain / 新增 query slot | {eq['cost']['GT_GAIN_PER_ADDITIONAL_QUERY_SLOT']:.6f} | {full['cost']['GT_GAIN_PER_ADDITIONAL_QUERY_SLOT']:.6f} |"]
    for key, label in [
        ('MACRO_RECALL_PP_PER_ONE_EXTRA_SLOT_PER_QUESTION', '每题增加 1 slot 对应 Macro Recall 增益（pp）'),
        ('MICRO_RECALL_PP_PER_ONE_EXTRA_SLOT_PER_QUESTION', '每题增加 1 slot 对应 Micro Recall 增益（pp）'),
        ('MACRO_RECALL_PP_PER_ADDITIONAL_TOTAL_QUERY_SLOT', 'Macro Recall 增益 / 总新增 slot（pp/slot）'),
        ('MICRO_RECALL_PP_PER_ADDITIONAL_TOTAL_QUERY_SLOT', 'Micro Recall 增益 / 总新增 slot（pp/slot）'),
    ]:
        lines.append(f"| {label} | {eq['cost'][key]:.6f} | {full['cost'][key]:.6f} |")
    lines += ['', 'GT/slot = 新增 GT 总数 / 新增 slots 总数。Recall 的分母有两种明确口径：每题预算从 A 增加一个 slot 时的整体 Recall 增益；以及该整体增益除以所有题新增 slots 的摊销值。后者不是逐题 Recall 平均值的另一种定义，也不表示随预算线性增长。', '',
              '## Q28、Q48', '']
    for q in d['per_query']:
        if q['query_id'] in ('Q28', 'Q48'):
            lines += [f"### {q['query_id']}", '', q['original_question'], '',
                      f"A {q['groups']['A']['gt_found']}/{q['gt']['total']} → B {q['groups']['B']['gt_found']}/{q['gt']['total']}；新增 {len(q['added_gt'])}。Query slots：{len(q['groups']['A']['queries'])} → {len(q['groups']['B']['queries'])}。", '']
    lines += ['## 全部逐题结果', '', '| Q | GT | A found | B found | A Recall | B Recall | 新增 GT | A/B slots |', '|---|---:|---:|---:|---:|---:|---:|---|']
    for q in d['per_query']:
        a, b = q['groups']['A'], q['groups']['B']
        lines.append(f"| {q['query_id']} | {q['gt']['total']} | {a['gt_found']} | {b['gt_found']} | {a['recall']:.4%} | {b['recall']:.4%} | {len(q['added_gt'])} | {len(a['queries'])}/{len(b['queries'])} |")
    lines += ['', '## 验证和限制', '', '```text', 'new Serper requests = 0', 'new network requests = 0', 'new Crawler generations = 0',
              'new Selector calls = 0', 'new Citation Expand calls = 0', '```', '',
              '- Python audit hook 在 replay 前安装，阻止 Internet socket、DNS、子进程和模型/网络客户端模块导入；未发生阻止事件。仅加载本地文件和原版 evaluator。',
              '- 原始 response 字节、SHA-256、原生候选解析、metadata 文件和逐 query GT matching 均核对一致；无新元数据解析。A 的候选与 GT 集合与上一轮 A 完全一致。',
              '- B candidate = A candidate ∪ cached anchor candidate；B GT = A GT ∪ cached anchor GT。逐题验证 A⊆B，B>A 仅代表缓存并集新增覆盖。',
              '- 原版 keep_letters、cal_micro 与 metrics.py 未改动；48Q/50Q 四组均用原版 metrics.py 复核。select_score=0 仅为 Search-only 输入结构占位，未运行 Selector。',
              '- 保留原实验的 Q40 shared q3 失败与 118 个候选标题未解析状态，不补请求、不从分母剔除。相同缓存下并集不会降低 Recall，不能将这种单调性视为等预算策略优势或 End-to-End 结论。',
              '- 主 JSON 保存逐题所有 native/anchor 查询、缓存引用、候选集合、GT 集合和新增命中证据；validation.json 保存原始输入与最终产物哈希。', '',
              '离线重算到此结束，未进入 End-to-End。', '']
    REPORT.write_text('\n'.join(lines))


def main():
    assert not OUT.exists() and not REPORT.exists(), 'Refuse to overwrite a replay'
    denied = []
    forbidden_modules = {'requests', 'arxiv', 'torch', 'transformers', 'httpx', 'aiohttp', 'models', 'paper_agent'}

    def guard(event, args):
        network = ((event == 'socket.__new__' and args[1] in (socket.AF_INET, socket.AF_INET6))
                   or event in ('socket.getaddrinfo', 'socket.gethostbyname', 'socket.gethostbyaddr')
                   or (event in ('socket.connect', 'socket.sendto') and args[0].family in (socket.AF_INET, socket.AF_INET6)))
        external = event in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn', 'os.fork')
        forbidden_import = event == 'import' and args[0].split('.')[0] in forbidden_modules
        if network or external or forbidden_import:
            denied.append({'event': event})
            raise RuntimeError('Offline replay forbids networks, subprocesses, models and retrieval clients')

    sys.addaudithook(guard)
    started = datetime.now(timezone.utc).isoformat()
    src = read(SOURCE)
    validation = read(SOURCE_WORK / 'validation.json')
    assert src['status'] == 'complete' and validation['status'] == 'PASS'
    frozen = dict(validation['artifact_sha256'])
    frozen.update(src['provenance']['protected_after_scoring'])
    frozen[str(SOURCE_WORK / 'validation.json')] = sha(SOURCE_WORK / 'validation.json')
    assert all(sha(path) == expected for path, expected in frozen.items())
    keep = frozen_function('keep_letters', src['provenance']['frozen_evaluator_functions']['keep_letters'])
    cal = frozen_function('cal_micro', src['provenance']['frozen_evaluator_functions']['cal_micro'])
    metadata = src['metadata']
    for aid, record in metadata.items():
        path = SOURCE_WORK / 'metadata' / f'{aid}.json'
        assert record == read(path)
        frozen[str(path)] = sha(path)
        if record['status'] == 'PASS':
            assert record['normalized_title'] == keep(record['title'])
    records, raw_count = [], 0
    assert len(src['per_query']) == 50
    for q in src['per_query']:
        labels = {keep(title) for title in q['gt']['raw_titles']}
        assert labels == set(q['gt']['normalized_groups']) and len(labels) == q['gt']['total']
        for key, s in q['searches'].items():
            for attempt in s['attempts']:
                path = Path(attempt['artifact_path'])
                assert read(path) == attempt
                frozen[str(path)] = sha(path)
                raw_count += 1
                if attempt.get('http_status') is not None:
                    body = base64.b64decode(attempt['response_bytes_base64'])
                    assert hashlib.sha256(body).hexdigest() == attempt['response_sha256']
                    if attempt['structured_response'] is not None:
                        assert json.loads(body) == json.loads(attempt['response_text']) == attempt['structured_response']
            ids = set()
            if s['status'] == 'PASS':
                for hit in s['attempts'][-1]['structured_response']['organic']:
                    match = re.search(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)', hit.get('link', ''))
                    if match:
                        ids.add(match.group(1))
            assert ids == set(s['returned_arxiv_ids'])
            found = {metadata[aid]['normalized_title'] for aid in ids if metadata[aid]['status'] == 'PASS'} & labels
            assert found == set(s['matched_gt'])
        a_keys = list(q['groups']['A']['search_keys'])
        b_keys = a_keys + ['anchor']
        assert a_keys == [f'q{i+1}' for i in range(len(q['native_queries']))]
        result = {'query_id': q['query_id'], 'original_question': q['original_question'], 'gt': q['gt'],
                  'native_queries': q['native_queries'], 'anchor': q['anchor'], 'groups': {},
                  'cached_queries': {k: {'query_text': s['query_text'], 'status': s['status'],
                                        'candidate_ids': s['returned_arxiv_ids'], 'matched_gt': s['matched_gt'],
                                        'response_artifacts': [a['artifact_path'] for a in s['attempts']]}
                                     for k, s in q['searches'].items()}}
        for group, keys in [('A', a_keys), ('B', b_keys)]:
            ids = set().union(*(set(q['searches'][k]['returned_arxiv_ids']) for k in keys))
            cached_gt = set().union(*(set(q['searches'][k]['matched_gt']) for k in keys))
            pred = {metadata[aid]['normalized_title'] for aid in ids if metadata[aid]['status'] == 'PASS'}
            tp, fp, fn = cal(pred, labels)
            assert pred & labels == cached_gt and tp == len(cached_gt)
            result['groups'][group] = {'search_keys': keys, 'queries': [q['searches'][k]['query_text'] for k in keys],
                                       'candidate_ids': sorted(ids), 'matched_gt': sorted(cached_gt),
                                       'gt_found': tp, 'recall': tp / len(labels),
                                       'missing_metadata_ids': sorted(aid for aid in ids if metadata[aid]['status'] != 'PASS')}
        a, b = result['groups']['A'], result['groups']['B']
        assert a['queries'] == q['native_queries'] == q['groups']['A']['queries']
        assert a['candidate_ids'] == q['groups']['A']['candidate_ids'] and a['matched_gt'] == q['groups']['A']['matched_gt']
        assert b['queries'] == a['queries'] + [q['anchor']]
        assert set(a['candidate_ids']) <= set(b['candidate_ids']) and set(a['matched_gt']) <= set(b['matched_gt'])
        added = set(b['matched_gt']) - set(a['matched_gt'])
        assert added == set(q['searches']['anchor']['matched_gt']) - set(a['matched_gt'])
        result['added_gt'] = sorted(added)
        result['added_gt_evidence'] = {key: [e for e in q['searches']['anchor']['matched_gt_evidence'] if e['normalized_gt_title'] == key] for key in added}
        assert all(result['added_gt_evidence'].values())
        records.append(result)
    assert raw_count == 303
    subsets = {'native5_48Q': [q for q in records if len(q['native_queries']) == 5], 'full_50Q': records}
    assert len(subsets['native5_48Q']) == 48
    assert [q['query_id'] for q in records if len(q['native_queries']) == 4] == ['Q18', 'Q28']
    summaries = {name: aggregate(qs) for name, qs in subsets.items()}
    checks = {name: official(qs, name, metadata, keep, cal, summaries[name]) for name, qs in subsets.items()}
    assert all(sha(path) == expected for path, expected in frozen.items())
    assert not denied
    assert not forbidden_modules & set(sys.modules)
    execution = {'new_serper_requests': 0, 'new_network_requests': 0, 'new_crawler_generations': 0,
                 'new_selector_calls': 0, 'new_citation_expand_calls': 0, 'blocked_events': denied}
    output = {'experiment': 'QUERY_PLANNER_V1_2_A5_B6_REPLAY_001', 'status': 'complete', 'execution': execution,
              'provenance': {'source': str(SOURCE), 'source_sha256': sha(SOURCE), 'script_sha256': sha(__file__),
                             'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
                             'mode': 'Offline cached union only; A=all native, B=all native then anchor',
                             'raw_attempts_verified': raw_count, 'metadata_records_verified': len(metadata),
                             'official_evaluator_checks': checks, 'metrics_py_sha256': sha(ROOT / 'metrics.py'),
                             'frozen_functions': src['provenance']['frozen_evaluator_functions'],
                             'network_policy': 'Audit hook blocks Internet/DNS, process launch and model/network-client imports; no model/pipeline imports; run entirely in network-restricted sandbox'},
              'summary': summaries, 'per_query': records}
    render(output)
    save(OUT, output)
    save(WORK / 'validation.json', {'status': 'PASS', 'execution': execution,
         'checks': '303 raw response replays; 1268 cached metadata; identical per-query GT matching; 50 A matches; B exact union and monotonicity; cached new-GT evidence; 48/50 cohort accounting; 4 unchanged metrics.py checks; preserved inputs',
         'frozen_input_sha256': frozen, 'artifact_sha256': {str(path): sha(path) for path in (OUT, REPORT, Path(__file__))}})
    print(json.dumps({'summary': summaries, 'execution': execution}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
