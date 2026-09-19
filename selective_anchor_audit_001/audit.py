"""Offline descriptive audit; annotations are review judgments, no trigger code."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import re
import socket
import statistics
import sys
from annotations import ANNOTATIONS, NAME, LIMIT

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent
SOURCE = ROOT / 'QUERY_PLANNER_V1_2_A5_B6_REPLAY_001.json'
OUT = ROOT / 'SELECTIVE_ANCHOR_AUDIT_001.json'
REPORT = ROOT / 'SELECTIVE_ANCHOR_AUDIT_001.md'
DETAIL = ROOT / 'SELECTIVE_ANCHOR_AUDIT_001_ELEMENT_REVIEW.md'
# Fixed generic English/request words; no task terms, acronym expansion or stemming.
STOPWORDS = set('a an the and or but of for to in on at by with from as that which who what how why when where is are was were be been being do does did can could would should may might it its their they them these those this there any some all me i you we our please provide give show find search papers paper research researches work works related about use using used have has had such know help list looking'.split())
DENIED = []


def guard(event, args):
    network = ((event == 'socket.__new__' and args[1] in (socket.AF_INET, socket.AF_INET6))
               or event in ('socket.getaddrinfo', 'socket.gethostbyname', 'socket.gethostbyaddr')
               or (event in ('socket.connect', 'socket.sendto') and args[0].family in (socket.AF_INET, socket.AF_INET6)))
    forbidden = event == 'import' and args[0].split('.')[0] in ('requests', 'arxiv', 'torch', 'transformers', 'httpx', 'aiohttp', 'models', 'paper_agent')
    if network or forbidden or event in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn', 'os.fork'):
        DENIED.append(event)
        raise RuntimeError('Selective Anchor audit is offline; no network/model/subprocess calls')


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def tokens(text):
    return re.findall(r'[a-z0-9]+', text.lower())


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 0.0


def literal_contains(span, text):
    needle, haystack = tokens(span), tokens(text)
    return any(haystack[i:i+len(needle)] == needle for i in range(len(haystack)-len(needle)+1))


def feature_row(q):
    # This function accepts ONLY original question and native queries, never GT/gain.
    qid, original, native = q['query_id'], q['original_question'], q['native_queries']
    elements = []
    for i, annotation in enumerate(ANNOTATIONS[qid], 1):
        a = dict(annotation)
        span = a['source_span']
        positions = list(re.finditer(re.escape(span), original, flags=re.I))
        assert positions, (qid, span, 'not a verbatim source substring')
        indices = a['reviewed_retained_native_indices']
        assert indices == sorted(set(indices)) and all(1 <= index <= len(native) for index in indices)
        a.update(element_id=f'{qid}_E{i}', source_offsets=[[m.start(), m.end()] for m in positions],
                 strict_lexical_native_indices=[j for j, n in enumerate(native, 1) if literal_contains(span, n)],
                 reviewed_native_frequency=len(indices),
                 reviewed_retention_evidence=[{'native_index': j, 'native_query': native[j-1]} for j in indices])
        elements.append(a)
    sets = [set(tokens(n)) for n in native]
    orig = set(tokens(original))
    pairs = [{'native_indices': [i+1, j+1], 'jaccard_all_tokens': jaccard(sets[i], sets[j]),
              'jaccard_content_tokens': jaccard(sets[i]-STOPWORDS, sets[j]-STOPWORDS)}
             for i, j in itertools.combinations(range(len(native)), 2)]
    similarities = [{'native_index': i+1, 'jaccard_all_tokens': jaccard(orig, ns),
                     'jaccard_content_tokens': jaccard(orig-STOPWORDS, ns-STOPWORDS)} for i, ns in enumerate(sets)]
    missing = [a for a in elements if not a['reviewed_native_frequency']]
    high = [a for a in elements if a['high_information']]
    high_missing = [a for a in high if not a['reviewed_native_frequency']]
    features = {
        'native_count': len(native), 'element_count': len(elements),
        'reviewed_retained_count': len(elements)-len(missing),
        'native_union_coverage': (len(elements)-len(missing))/len(elements),
        'strict_lexical_union_coverage': sum(bool(a['strict_lexical_native_indices']) for a in elements)/len(elements),
        'missing_count': len(missing), 'high_information_count': len(high),
        'high_information_missing_count': len(high_missing),
        'high_information_union_coverage': (len(high)-len(high_missing))/len(high) if high else None,
        'missing_name_acronym_count': sum(a['category'] == NAME for a in missing),
        'missing_comparison_condition_count': sum(a['category'] == LIMIT for a in missing),
        'high_elements_retained_in_exactly_one_query': sum(a['reviewed_native_frequency'] == 1 for a in high),
        'native_queries_retaining_all_high_elements': sum(all(i in a['reviewed_retained_native_indices'] for a in high) for i in range(1, len(native)+1)),
        'mean_native_pair_jaccard': statistics.mean(p['jaccard_all_tokens'] for p in pairs),
        'mean_native_pair_content_jaccard': statistics.mean(p['jaccard_content_tokens'] for p in pairs),
        'mean_original_native_jaccard': statistics.mean(p['jaccard_all_tokens'] for p in similarities),
        'min_original_native_jaccard': min(p['jaccard_all_tokens'] for p in similarities),
        'max_original_native_jaccard': max(p['jaccard_all_tokens'] for p in similarities),
        'mean_original_native_content_jaccard': statistics.mean(p['jaccard_content_tokens'] for p in similarities),
        'original_token_count': len(tokens(original)),
        'mean_native_token_count': statistics.mean(len(tokens(n)) for n in native),
    }
    return dict(q, elements=elements, features=features,
                all_native_omitted_elements=[a['element_id'] for a in missing],
                all_native_omitted_high_information_elements=[a['element_id'] for a in high_missing],
                native_pair_similarities=pairs, original_native_similarities=similarities)


def distribution(values):
    return {'mean': statistics.mean(values), 'median': statistics.median(values), 'min': min(values), 'max': max(values)}


def summarize(rows):
    summary = {}
    for label in ('positive', 'no_added_gain'):
        qs = [q for q in rows if q['outcome']['label'] == label]
        fs = [q['features'] for q in qs]
        summary[label] = {'questions': len(qs), 'qids': [q['query_id'] for q in qs],
                          'element_totals': sum(f['element_count'] for f in fs),
                          'questions_with_any_missing_element': sum(f['missing_count'] > 0 for f in fs),
                          'questions_with_missing_high_information': sum(f['high_information_missing_count'] > 0 for f in fs),
                          'questions_with_missing_name_acronym': sum(f['missing_name_acronym_count'] > 0 for f in fs),
                          'questions_with_missing_comparison_condition': sum(f['missing_comparison_condition_count'] > 0 for f in fs),
                          'questions_with_single_query_only_high_elements': sum(f['high_elements_retained_in_exactly_one_query'] > 0 for f in fs),
                          'questions_without_one_query_covering_all_high_elements': sum(f['native_queries_retaining_all_high_elements'] == 0 for f in fs),
                          'questions_with_full_reviewed_coverage': sum(f['native_union_coverage'] == 1 for f in fs),
                          'continuous': {key: distribution([f[key] for f in fs]) for key in (
                              'element_count', 'high_information_missing_count', 'native_union_coverage', 'strict_lexical_union_coverage',
                              'mean_native_pair_jaccard', 'mean_native_pair_content_jaccard', 'mean_original_native_jaccard',
                              'mean_original_native_content_jaccard', 'original_token_count')}}
    # Outcome-free metrics; references are each positive's observed value, not fitted cutoffs or trigger thresholds.
    negatives = [q for q in rows if q['outcome']['label'] == 'no_added_gain']
    summary['positive_overlap_with_negatives'] = []
    for q in rows:
        if q['outcome']['label'] != 'positive':
            continue
        f = q['features']
        summary['positive_overlap_with_negatives'].append({
            'query_id': q['query_id'],
            'negative_qids_with_native_jaccard_at_least_this_positive': [n['query_id'] for n in negatives if n['features']['mean_native_pair_jaccard'] >= f['mean_native_pair_jaccard']],
            'negative_qids_with_original_native_jaccard_at_most_this_positive': [n['query_id'] for n in negatives if n['features']['mean_original_native_jaccard'] <= f['mean_original_native_jaccard']],
        })
    return summary


def analyze():
    assert not OUT.exists(), 'Do not silently overwrite an audit'
    source = read(SOURCE)
    assert source['status'] == 'complete'
    validation = read(ROOT / 'query_planner_v1_2_a5_b6_replay_001/validation.json')
    frozen = dict(validation['artifact_sha256'])
    frozen.update({str(ROOT / n): sha(ROOT / n) for n in ('agent_prompt.json', 'models.py', 'paper_agent.py', 'utils.py', 'metrics.py')})
    assert all(sha(path) == expected for path, expected in frozen.items())
    projection = [{k: q[k] for k in ('query_id', 'original_question', 'native_queries')} for q in source['per_query']]
    assert set(ANNOTATIONS) == {q['query_id'] for q in projection} and len(projection) == 50
    rows = [feature_row(q) for q in projection]
    # Freeze text-only features before adding existing outcome labels.
    feature_path = WORK / 'text_only_features.json'
    save(feature_path, rows)
    feature_hash = sha(feature_path)
    for q, old in zip(rows, source['per_query']):
        q['outcome'] = {'label': 'positive' if old['added_gt'] else 'no_added_gain',
                        'anchor_new_gt': len(old['added_gt']), 'A_found': old['groups']['A']['gt_found'],
                        'B_found': old['groups']['B']['gt_found'], 'total_gt': old['gt']['total']}
    assert [q['query_id'] for q in rows if q['outcome']['label'] == 'positive'] == ['Q13','Q19','Q44','Q45','Q48']
    policy = {
        'annotation_author': 'Assistant/analyst-authored review judgments; not a human panel, gold annotation or automatic semantic model.',
        'label_awareness': 'Positive QIDs were provided by the user before this audit. This is not blinded annotation. Elements are grounded only in original spans and native query text; no GT titles, retrieved paper content or gain magnitude used to define elements.',
        'categories': ['entity_method_model', 'benchmark_dataset_acronym', 'domain_technical_phrase', 'numeric_comparison_negation_condition'],
        'unit': 'One explicitly annotated research requirement. Long relational spans deliberately coexist with their component entities, so element counts are not independent facts. Source boilerplate such as all papers/provide/find is excluded; soft recency/popularity preferences included as non-high-information conditions.',
        'high_information': 'Narrow task/method/domain phrases, named benchmarks or specialist acronyms, and substantive numeric/comparison/negation/conditional restrictions. Generic LLM/model class alone, generic training, bare modality nouns, generic dataset/benchmark requests and soft popularity/recency are not flagged. This is a disclosed analyst judgment, not an IDF or learned score.',
        'reviewed_retention': 'Count a native query only if it retains the full annotated element, allowing explicitly reviewed morphology/direct task paraphrases. Bare language model is not an explicit LLM; neutral impact/comparison is not directional benefit/negation. Composite relation must be preserved within one query; parts scattered across queries do not count for the composite element. Borderline judgments have per-element notes.',
        'strict_retention': 'Contiguous exact lowercased ASCII alphanumeric token sequence from source span. Hyphens/underscores split; no stemming, acronym expansion, synonym substitution or stopword removal. Strict lexical misses are not automatically semantic misses.',
        'jaccard': 'Primary: set of lowercased ASCII letter/digit tokens, no stemming or stopword removal. Mean over all within-question native pairs; separately report original vs each native (mean/min/max). Secondary sensitivity view removes a single predefined generic English/request stopword list, with negation/comparison/task terms retained.',
        'stopwords': sorted(STOPWORDS),
        'outcome': 'Existing full-native+anchor replay marginal gain (not prior q5 replacement delta). Positive means at least one cached GT title added; no-added-gain is specific to this cached Top10/title-matching run, not inherent no value.',
        'prohibited': 'No new network, Serper, Crawler, Selector, Citation Expand, GT-based threshold tuning, classifier fitting, trigger implementation or Search. Candidate trigger ideas are prose only.'}
    d = {'experiment': 'SELECTIVE_ANCHOR_AUDIT_001', 'status': 'analyzed', 'policy': policy,
         'provenance': {'source': str(SOURCE), 'source_sha256': sha(SOURCE), 'annotations_sha256': sha(WORK / 'annotations.py'),
                        'analysis_script_sha256': sha(__file__), 'text_only_features_sha256': feature_hash,
                        'frozen_inputs': frozen, 'analyzed_utc': datetime.now(timezone.utc).isoformat()},
         'execution': {'new_network_requests': 0, 'new_serper_requests': 0, 'new_crawler_generations': 0,
                       'new_selector_calls': 0, 'new_citation_expand_calls': 0, 'trigger_implemented': False,
                       'thresholds_tuned': False, 'blocked_events': DENIED},
         'summary': summarize(rows), 'per_query': rows}
    assert not DENIED and sha(feature_path) == feature_hash
    assert all(sha(path) == expected for path, expected in frozen.items())
    save(OUT, d)
    print(json.dumps(d['summary'], ensure_ascii=False, indent=2))


def esc(text):
    return str(text).replace('|', '\\|').replace('\n', '<br>')


def render():
    d = read(OUT)
    assert d['status'] in ('analyzed', 'complete')
    details = ['# Selective Anchor 逐元素复核', '',
               '此表为 assistant/analyst 文本复核，不是外部人工标注金标准。列出的元素频次来自 reviewed_retained_native_indices；严格词面频次另列。元素定义、重叠计数及边界说明见主报告。', '']
    for q in d['per_query']:
        details += [f"## {q['query_id']}", '', 'Original question:', '', q['original_question'], '', 'Native queries:', '']
        details += [f'{i}. {n}' for i, n in enumerate(q['native_queries'], 1)]
        details += ['', '| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |', '|---|---|---|---|---|---|']
        for a in q['elements']:
            details.append(f"| {a['element_id']}: {esc(a['source_span'])} | {a['category']} | {'是' if a['high_information'] else '否'} | {a['reviewed_native_frequency']}/{len(q['native_queries'])}; {a['reviewed_retained_native_indices']} | {a['strict_lexical_native_indices']} | {esc(a['review_note']) or '直接词面、词形或任务同义表达；完整 query 证据见 JSON。'} |")
        details += ['', '| Native # | Original-native Jaccard | 去通用词 Jaccard |', '|---|---:|---:|']
        details += [f"| {r['native_index']} | {r['jaccard_all_tokens']:.4f} | {r['jaccard_content_tokens']:.4f} |" for r in q['original_native_similarities']]
        details += ['', f"既有收益标签：{q['outcome']['label']}；anchor 新增 GT={q['outcome']['anchor_new_gt']}。", '']
    DETAIL.write_text('\n'.join(details))
    findings = (WORK / 'findings.md').read_text()
    lines = ['# SELECTIVE_ANCHOR_AUDIT_001', '', findings, '', '## 审计口径与边界', '',
             '- 数据：RealScholarQuery-50，native 保持原始顺序；Q18/Q28 为 4 条，其余为 5 条。正例来自已有 A5/B6 replay，5 题各新增 1 GT；其余 45 题为本次缓存实验无新增收益。',
             '- 每个元素都是 original question 的原文片段。按实体/方法、benchmark/dataset/acronym、领域技术短语、数字比较否定条件四类标注；同一复杂条件可与组成元素重叠，因此元素总数不是独立条件数。',
             '- 主 coverage 使用逐项文本复核：完整元素至少被一条 native 保留。允许明确词形和直接任务同义表达；关系/比较/否定要求完整保留，不能把散落在不同 queries 的实体当成完整关系。原文措辞不自动纠错，不展开未知缩写。',
             '- 高信息 H 是显式人工判断的窄任务、方法、领域短语、专名或实质条件，不是 IDF/模型打分。裸 LLM、通用模型类别、泛化训练/模态及软热度偏好不标 H。H 缺失数是全体 native 都没有保留的 H 元素数。',
             '- 同时报告严格词面 coverage：lowercase ASCII 字母数字 token 连续匹配，不词干化或同义替换。严格词面遗漏不等于语义遗漏；QAT→原文已经给出的完整名称就是反例。',
             '- Jaccard 主指标用小写 ASCII 字母数字 token 集合，不去停用词、不词干化。native-pair 为题内所有 pair 的等权平均，original-native 为该题所有 native 的等权平均。JSON/逐元素表保留每条 original-native 及每个 native pair；固定通用停用词版本仅作敏感性参照。',
             '- 标注由 assistant/analyst 编写并逐题复核，不能称为独立人工金标准。已知正例名单，所以不是盲审；特征计算只接收 original/native，先保存 text_only_features.json，再连接既有增益标签。未使用 GT 标题或检索正文设计元素。',
             '- 不设 Jaccard/覆盖率 trigger 阈值，不拟合分类器，不按 GT 调阈值。下述组间差异是描述性比较；只有 5 个正例，不能给出可泛化的触发准确率。', '',
             '## 50题汇总', '',
             'E=元素总数，R=至少一条 native 保留数；Cov=R/E（语义复核）；LexCov=严格词面 union coverage；Hmiss=高信息全遗漏数；Jnn=native 平均词面 Jaccard；Jon=original-native 平均词面 Jaccard。最后一列列出全部复核遗漏元素，包括非 H。', '',
             '| Q | Anchor新增GT | N | E | R | Cov | LexCov | Hmiss | Jnn | Jon | 全部 native 遗漏元素 |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for q in d['per_query']:
        f = q['features']
        missing = '；'.join(a['source_span'] for a in q['elements'] if not a['reviewed_native_frequency']) or '无'
        lines.append(f"| {q['query_id']} | {q['outcome']['anchor_new_gt']} | {f['native_count']} | {f['element_count']} | {f['reviewed_retained_count']} | {f['native_union_coverage']:.1%} | {f['strict_lexical_union_coverage']:.1%} | {f['high_information_missing_count']} | {f['mean_native_pair_jaccard']:.4f} | {f['mean_original_native_jaccard']:.4f} | {esc(missing)} |")
    lines += ['', '## 正例/无增益题的描述性分布', '', '| 特征 | 正例（5题） | 无增益（45题） |', '|---|---:|---:|']
    for key, label in [
        ('questions_with_any_missing_element','至少一个完整元素全遗漏'),
        ('questions_with_missing_high_information','至少一个高信息元素全遗漏'),
        ('questions_with_missing_name_acronym','专名/数据集/缩写元素全遗漏'),
        ('questions_with_missing_comparison_condition','比较/否定/数字/条件元素全遗漏'),
        ('questions_with_single_query_only_high_elements','至少一个高信息元素仅被1条query保留'),
        ('questions_without_one_query_covering_all_high_elements','无单条query覆盖全部H元素'),
        ('questions_with_full_reviewed_coverage','复核 union coverage=100%'),
    ]:
        a,b=d['summary']['positive'][key],d['summary']['no_added_gain'][key]
        lines.append(f'| {label} | {a}/5 ({a/5:.1%}) | {b}/45 ({b/45:.1%}) |')
    lines += ['', '连续特征显示：平均值 / 中位数 [最小, 最大]。', '', '| 特征 | 正例 | 无增益 |', '|---|---|---|']
    for key in d['summary']['positive']['continuous']:
        values=[]
        for label in ('positive','no_added_gain'):
            x=d['summary'][label]['continuous'][key]
            values.append(f"{x['mean']:.4f} / {x['median']:.4f} [{x['min']:.4f}, {x['max']:.4f}]")
        lines.append(f'| {key} | {values[0]} | {values[1]} |')
    lines += ['', '## 产物与执行边界', '',
              f'- 逐元素表：`{DETAIL.name}`，覆盖全部 50 题，包含每个元素原文、类别、H标记、保留位置/频次、严格词面位置和边界说明。',
              f'- 主 JSON：`{OUT.name}`；另存 annotations.py 与 text_only_features.json，允许独立复核标注和统计。',
              '- new network requests=0；new Serper requests=0；new Crawler generations=0；Selector/Citation Expand=0。网络、DNS、模型客户端及子进程由审计钩子阻止。',
              '- trigger implemented=false；thresholds tuned=false。候选只写在文字讨论中，没有 trigger 函数、打标决策或新 Search。',
              '- 继承原实验标题精确匹配、118 个未解析候选和 Q40 共享 q3 失败；无收益不等于领域中没有相关论文，也不等于 anchor 在未来必然无用。', '',
              '本阶段到离线规律审计为止。', '']
    REPORT.write_text('\n'.join(lines))
    d['status']='complete'
    d['provenance']['findings_sha256']=sha(WORK/'findings.md')
    save(OUT,d)
    print(f'Wrote {REPORT.name} and {DETAIL.name}')


def validate():
    d=read(OUT)
    assert d['status']=='complete'
    p=d['provenance']
    assert p['annotations_sha256']==sha(WORK/'annotations.py')
    assert p['analysis_script_sha256']==sha(__file__)
    assert p['text_only_features_sha256']==sha(WORK/'text_only_features.json')
    assert p['findings_sha256']==sha(WORK/'findings.md')
    assert all(sha(path)==expected for path,expected in p['frozen_inputs'].items())
    saved=read(WORK/'text_only_features.json')
    assert len(saved)==50 and all('outcome' not in q for q in saved)
    for q,text_only in zip(d['per_query'],saved):
        assert {k:v for k,v in q.items() if k!='outcome'}==text_only
        n=len(q['native_queries'])
        elements=q['elements']
        assert q['features']['reviewed_retained_count']==sum(bool(e['reviewed_retained_native_indices']) for e in elements)
        assert q['features']['element_count']==len(elements)
        for e in elements:
            assert e['reviewed_native_frequency']==len(e['reviewed_retained_native_indices'])
            assert all(q['original_question'][a:b].lower()==e['source_span'].lower() for a,b in e['source_offsets'])
        qs=[set(re.findall('[a-z0-9]+',text.lower())) for text in q['native_queries']]
        pairs=[len(a&b)/len(a|b) if a|b else 0 for a,b in itertools.combinations(qs,2)]
        assert q['features']['mean_native_pair_jaccard']==statistics.mean(pairs)
        orig=set(re.findall('[a-z0-9]+',q['original_question'].lower()))
        vals=[len(orig&s)/len(orig|s) for s in qs]
        assert q['features']['mean_original_native_jaccard']==statistics.mean(vals)
        assert len(q['native_pair_similarities'])==n*(n-1)//2
        assert len(q['original_native_similarities'])==n
    assert d['summary']==summarize(d['per_query'])
    table=REPORT.read_text()
    assert len(re.findall(r'^\| Q\d+ \|',table,re.M))==50
    assert re.findall(r'^## (Q\d+)$',DETAIL.read_text(),re.M)==[f'Q{i}' for i in range(50)]
    assert not DENIED
    save(WORK/'validation.json',{'status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),
         'checks':'50 verbatim-grounded annotated questions; exact stored review indices/frequencies; independent lexical Jaccard recount; summary and positive IDs; outcome-free feature artifact; 50 report rows and 50 element tables; unchanged source/model/evaluator files; zero network/model events; no trigger code or thresholds',
         'limitation':'Mechanical validation does not certify semantic annotation correctness; judgments and ambiguous conventions remain reviewable.',
         'execution':d['execution'], 'artifact_sha256':{str(path):sha(path) for path in (OUT,REPORT,DETAIL,WORK/'annotations.py',WORK/'findings.md',WORK/'text_only_features.json',Path(__file__))}})
    print('Validation PASS (mechanical consistency; semantic judgments remain explicit review annotations).')


if __name__=='__main__':
    sys.addaudithook(guard)
    parser=argparse.ArgumentParser()
    parser.add_argument('phase',choices=('analyze','render','validate'))
    {'analyze':analyze,'render':render,'validate':validate}[parser.parse_args().phase]()
