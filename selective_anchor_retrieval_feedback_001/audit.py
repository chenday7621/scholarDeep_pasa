"""Native cached responses only; descriptive audit, no trigger or evaluator."""
import argparse
import ast
import base64
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

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent
SOURCE = ROOT / 'QUERY_PLANNER_V1_2_SEARCH_AB_001.json'
TEXT = ROOT / 'selective_anchor_audit_001/text_only_features.json'
FEATURES = WORK / 'native_feedback_features.json'
OUT = ROOT / 'SELECTIVE_ANCHOR_RETRIEVAL_FEEDBACK_001.json'
REPORT = ROOT / 'SELECTIVE_ANCHOR_RETRIEVAL_FEEDBACK_001.md'
DETAIL = ROOT / 'SELECTIVE_ANCHOR_RETRIEVAL_FEEDBACK_001_DETAILS.md'
BLOCKED = []
STOP = set('a an the and or of for to in on at by with from as that which who what how why when where is are was were be been being do does did can could would should may might it its their they them these those this there any some all me i you we our please provide give show find search papers paper research researches work works related about use using used have has had such know help list looking arxiv pdf abstract et al'.split())


def guard(event, args):
    net = ((event == 'socket.__new__' and args[1] in (socket.AF_INET, socket.AF_INET6))
           or event in ('socket.getaddrinfo', 'socket.gethostbyname', 'socket.gethostbyaddr')
           or (event in ('socket.connect', 'socket.sendto') and args[0].family in (socket.AF_INET, socket.AF_INET6)))
    forbidden = event == 'import' and args[0].split('.')[0] in ('requests','arxiv','torch','transformers','httpx','aiohttp','models','paper_agent')
    if net or forbidden or event in ('subprocess.Popen','os.system','os.exec','os.posix_spawn','os.fork'):
        BLOCKED.append(event)
        raise RuntimeError('Offline native result audit: prohibited action')


def read(p): return json.loads(Path(p).read_text())
def save(p, x): Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def toks(s): return re.findall('[a-z0-9]+', (s or '').lower())
def jac(a,b): return len(a&b)/len(a|b) if a|b else None
def mean(v): return statistics.mean(x for x in v if x is not None) if any(x is not None for x in v) else None
def literal(span,text): return (' '+' '.join(toks(span))+' ') in (' '+' '.join(toks(text))+' ')


def content(s):
    # Deliberately shallow inflection normalization, NOT synonym/semantic matching.
    def inflect(t):
        if len(t)>4 and t.endswith('ies'): return t[:-3]+'y'
        if len(t)>3 and t.endswith('s') and not t.endswith(('ss','us','is')): return t[:-1]
        return t
    return {inflect(t) for t in toks(s) if t not in STOP}


def feature(q):
    searches=q['searches']; sets=[set(s['candidate_ids']) for s in searches]
    union=set().union(*sets); freq=Counter(i for ids in sets for i in ids)
    seen=set()
    for i,(s,ids) in enumerate(zip(searches,sets)):
        other=set().union(*(x for j,x in enumerate(sets) if i!=j))
        s['exclusive_vs_all_other_ids']=sorted(ids-other)
        s['exclusive_vs_all_other_count']=len(ids-other)
        s['incremental_vs_previous_ids']=sorted(ids-seen)
        s['incremental_vs_previous_count']=len(ids-seen)
        seen|=ids
    pairs=[]
    for i,j in itertools.combinations(range(len(sets)),2):
        a,b=sets[i],sets[j]
        pairs.append({'queries':[i+1,j+1], 'intersection':len(a&b),'union':len(a|b),
                      'jaccard':jac(a,b),'overlap_coefficient':len(a&b)/min(len(a),len(b)) if a and b else None,
                      'both_successful':all(searches[k]['status']=='PASS' for k in (i,j))})
    docs={}
    hits=[]
    for s in searches:
        for h in s['hits']:
            h=dict(h,query_index=s['query_index'],hit_key=f"q{s['query_index']}:r{h['organic_index']+1}")
            hits.append(h)
            docs.setdefault(h['arxiv_id'],{'arxiv_id':h['arxiv_id'],'query_indices':[], 'variants':[]})['variants'].append(h)
    for i,d in docs.items():
        d['query_indices']=sorted({h['query_index'] for h in d['variants']})
        d['query_frequency']=len(d['query_indices'])
    elements=[]
    for e in q.pop('source_elements'):
        needle=content(e['source_span'])
        matched=[]; scores=[]
        for h in hits:
            title,snippet=h['title'] or '',h['snippet'] or ''
            hay=content(title+' '+snippet)
            strict=literal(e['source_span'],title) or literal(e['source_span'],snippet)
            cooccur=bool(needle) and needle<=hay
            score=len(needle&hay)/len(needle) if needle else None
            ev={k:h[k] for k in ('hit_key','query_index','arxiv_id','title','snippet')}
            ev.update(strict_phrase=strict,all_content_tokens_same_hit=cooccur,content_token_fraction=score)
            if strict or cooccur:matched.append(ev)
            scores.append(ev)
        strict_hits=[h for h in matched if h['strict_phrase']]
        token_hits=[h for h in matched if h['all_content_tokens_same_hit']]
        elements.append({k:e[k] for k in ('element_id','source_span','category','high_information')} | {
            'query_text_reviewed_frequency':e['reviewed_native_frequency'],
            'content_tokens':sorted(needle),
            'strict_result_query_indices':sorted({h['query_index'] for h in strict_hits}),
            'strict_result_unique_ids':sorted({h['arxiv_id'] for h in strict_hits}),
            'token_result_query_indices':sorted({h['query_index'] for h in token_hits}),
            'token_result_unique_ids':sorted({h['arxiv_id'] for h in token_hits}),
            'strict_unique_count':len({h['arxiv_id'] for h in strict_hits}),
            'token_unique_count':len({h['arxiv_id'] for h in token_hits}),
            'max_content_token_fraction':max((h['content_token_fraction'] for h in scores if h['content_token_fraction'] is not None),default=None),
            'matching_evidence':matched,
            'best_lexical_evidence':sorted(scores,key=lambda h:-(h['content_token_fraction'] or 0))[:3]})
    # First observation of each unique ID: duplicates cannot inflate text homogeneity.
    docsets=[content(d['variants'][0]['title']+' '+(d['variants'][0]['snippet'] or '')) for d in docs.values()]
    termfreq=Counter(t for d in docsets for t in d)
    total=sum(len(s) for s in sets); high=[e for e in elements if e['high_information']]
    f={'native_query_count':len(sets),'successful_query_count':sum(s['status']=='PASS' for s in searches),
       'organic_count':sum(s['organic_count'] for s in searches),'parsed_candidate_occurrences':len(hits),
       'sum_per_query_unique_ids':total,'unique_arxiv_ids':len(union),
       'duplicate_fraction':1-len(union)/total if total else None,
       'mean_pair_jaccard_successful':mean([p['jaccard'] for p in pairs if p['both_successful']]),
       'mean_pair_jaccard_all_slots':mean([p['jaccard'] for p in pairs]),
       'mean_pair_overlap_successful':mean([p['overlap_coefficient'] for p in pairs if p['both_successful']]),
       'exclusive_unique_fraction':sum(v==1 for v in freq.values())/len(union) if union else None,
       'mean_query_exclusive_count':mean([s['exclusive_vs_all_other_count'] for s in searches if s['status']=='PASS']),
       'zero_exclusive_successful_queries':sum(s['exclusive_vs_all_other_count']==0 and s['status']=='PASS' for s in searches),
       'all_query_shared_ids':len(set.intersection(*sets)),
       'q5_incremental_count':searches[4]['incremental_vs_previous_count'] if len(sets)==5 else None,
       'unique_document_text_jaccard':mean([jac(a,b) for a,b in itertools.combinations(docsets,2)]),
       'element_count':len(elements),'high_element_count':len(high),
       'strict_element_union_coverage':sum(bool(e['strict_unique_count']) for e in elements)/len(elements),
       'token_element_union_coverage':sum(bool(e['token_unique_count']) for e in elements)/len(elements),
       'strict_high_missing':sum(not e['strict_unique_count'] for e in high),
       'token_high_missing':sum(not e['token_unique_count'] for e in high)}
    return dict(q,features=f,elements=elements,query_pairs=pairs,documents=list(docs.values()),
                candidate_query_frequency_histogram=dict(sorted(Counter(freq.values()).items())),
                top_document_terms=termfreq.most_common(15))


def prepare():
    assert not FEATURES.exists(), 'Do not overwrite frozen features'
    text=read(TEXT)
    src=read(SOURCE)
    # Project only native fields; never access GT, metadata, group metrics or anchor.
    helper=ROOT/'query_planner_v1_2_search_ab_001/common.py'
    tree=ast.parse(helper.read_text())
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='parse_hits']
    assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ID_PATTERN' for t in n.targets))
    env={'re':re,'ID_PATTERN':ast.literal_eval(assignment.value)}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),env)
    hashes={str(p):sha(p) for p in (SOURCE,TEXT,helper,ROOT/'utils.py',ROOT/'metrics.py',ROOT/'models.py',ROOT/'paper_agent.py',ROOT/'agent_prompt.json')}
    qs=[]
    for prior,old in zip(text,src['per_query']):
        assert prior['query_id']==old['query_id'] and prior['native_queries']==old['native_queries']
        q={'query_id':prior['query_id'],'original_question':prior['original_question'],
           'native_queries':prior['native_queries'],'source_elements':prior['elements'],'searches':[]}
        for i,native in enumerate(q['native_queries'],1):
            s=old['searches'][f'q{i}']; accepted=[]; artifacts=[]
            for a in s['attempts']:
                path=Path(a['artifact_path']); assert f'_q{i}_attempt' in path.name and '_anchor_' not in path.name
                raw=read(path);hashes[str(path)]=sha(path);artifacts.append(str(path))
                assert raw['query_text']==native and raw['query_key']==f'q{i}'
                if raw.get('response_bytes_base64') is not None:
                    bs=base64.b64decode(raw['response_bytes_base64'])
                    assert hashlib.sha256(bs).hexdigest()==raw['response_sha256']
                if raw['status']=='PASS':
                    assert json.loads(raw['response_text'])==raw['structured_response']
                    accepted.append(raw)
            assert len(accepted)==(1 if s['status']=='PASS' else 0)
            hits=env['parse_hits'](accepted[0]['structured_response']) if accepted else []
            assert hits==s['organic_hits'] and sorted({h['arxiv_id'] for h in hits})==s['returned_arxiv_ids']
            q['searches'].append({'query_index':i,'query_text':native,'status':s['status'],
                'organic_count':len(accepted[0]['structured_response']['organic']) if accepted else 0,
                'parsed_candidate_count':len(hits),'unique_arxiv_count':len(s['returned_arxiv_ids']),
                'candidate_ids':s['returned_arxiv_ids'],'hits':hits,'raw_artifacts':artifacts})
        qs.append(feature(q))
    policy={
        'scope':'Native raw title/snippet only; no GT content, anchor result, metadata title, fulltext, network, model or evaluator calls.',
        'label_awareness':'User disclosed five positives; not a blinded audit. Features and original-element definitions do not use GT contents. Group labels join only after freezing features and qualitative review.',
        'candidate':'Organic hit count is distinct from parsed occurrences and per-query unique IDs. Original parser is extracted unchanged and compared to stored results. Failed Q40 q3 is missing evidence, not an empty successful search.',
        'novelty':'Exclusive=Si minus union of ALL other Sj; sequential increment=Si minus preceding Sj in native order. Both counts and IDs saved.',
        'overlap':'Primary Jaccard averages successful query pairs. All-slot version also saved; empty/empty undefined. Duplicate fraction=1-U/sum(|Si|). Frequency hist counts query membership, not organic positions.',
        'elements':'Reuse all 177 prior source-grounded elements and H flags. Strict=contiguous lowercased alphanumeric phrase in title OR snippet. Token proxy=all content tokens cooccur within one title+snippet, with fixed plural rules and stoplist, not semantic entailment. Explicit paraphrase/relation review is separate; lack of visible evidence is not absence from full paper.',
        'topic':'Unique-document first native occurrence title+snippet pair Jaccard and common document terms are lexical concentration proxies, not semantic clusters. Duplicate IDs counted once. Manual per-question topic review supplements these.',
        'stopwords':sorted(STOP),'no_fitting':'No fitted classifier, threshold selection, trigger implementation or outcome-derived feature definitions.'}
    save(FEATURES,{'policy':policy,'per_query':qs})
    save(WORK/'manifest.json',{'source_sha256':hashes,'features_sha256':sha(FEATURES),
        'script_sha256_at_prepare':sha(__file__),'created_utc':datetime.now(timezone.utc).isoformat(),
        'execution':{'new_network_requests':0,'new_serper_requests':0,'new_anchor_searches':0,'new_crawler_generations':0,'new_selector_calls':0,'new_citation_expand_calls':0,'blocked_events':BLOCKED}})
    lines=[]
    for q in qs:
        lines += [f"## {q['query_id']} {q['original_question']}",json.dumps(q['features']),
                  'recurring: '+str([(d['arxiv_id'],d['query_frequency'],d['variants'][0]['title']) for d in sorted(q['documents'],key=lambda d:-d['query_frequency'])[:5]])]
        for e in q['elements']:
            lines += [f"{e['element_id']} {e['source_span']} | strict/token IDs={e['strict_unique_count']}/{e['token_unique_count']}"]
            seen=set()
            for h in e['matching_evidence']+e['best_lexical_evidence']:
                if h['arxiv_id'] in seen: continue
                seen.add(h['arxiv_id'])
                lines += [f"  {h['hit_key']} {h['arxiv_id']} | {h['title']} | {h['snippet']}"]
                if len(seen)==2:break
        lines += ['']
    (WORK/'review_packet.txt').write_text('\n'.join(lines))
    print(f'Frozen {len(qs)} questions, {sum(len(q["searches"]) for q in qs)} native queries, {len(hashes)-8} raw attempt artifacts. No outcome labels in features.')


def analyze():
    manifest=read(WORK/'manifest.json'); assert sha(FEATURES)==manifest['features_sha256']
    review=read(WORK/'review.json'); assert len(review)==50
    # User supplied binary retrospective labels only; NO GT titles or matching used.
    positive={'Q13','Q19','Q44','Q45','Q48'}
    x=read(FEATURES);rows=x['per_query']
    for q in rows:
        q['qualitative_review']=review[q['query_id']]
        q['positive_label']=q['query_id'] in positive
    stats={}
    for label in (True,False):
        group=[q for q in rows if q['positive_label']==label]
        fkeys=list(group[0]['features'])
        summary={}
        for k in fkeys:
            vals=[q['features'][k] for q in group if q['features'][k] is not None]
            summary[k]={'mean':statistics.mean(vals),'median':statistics.median(vals),'min':min(vals),'max':max(vals),'n':len(vals)}
        summary['core_review_states']=dict(Counter(q['qualitative_review']['core_evidence'] for q in group))
        stats['positive' if label else 'no_gain']={'n':len(group),'features':summary}
    x.update(experiment='SELECTIVE_ANCHOR_RETRIEVAL_FEEDBACK_001',status='analyzed',summary=stats,
             provenance=manifest|{'review_sha256':sha(WORK/'review.json')},execution=manifest['execution'])
    save(OUT,x)
    print(json.dumps(stats,ensure_ascii=False,indent=2))


def esc(s): return str(s).replace('|','\\|').replace('\n',' ')
def render():
    x=read(OUT);rows=x['per_query'];notes=(WORK/'findings.md').read_text()
    lines=['# SELECTIVE_ANCHOR_RETRIEVAL_FEEDBACK_001','',notes,'','## 50题汇总','',
      'N=原生 query 数；C=解析成功的 candidate 出现次数（跨 query 可重复）；U=unique arXiv；D=1−U/每 query unique 数之和；J=成功 query 对的结果 ID Jaccard；E=各 query 相对其余全部 query 的独有 ID 数；Δ=按原生顺序累计新增 ID 数；H0=原文高信息元素在所有 title/snippet 中无严格短语 / 无同条 token 共现证据的数量（不是语义缺失结论）；T=去重论文文本平均 Jaccard。', '',
      '| Q | 正例标签 | N | C/U | D | J | E (q1→) | Δ (q1→) | H0 严格/token | T | 核心结果证据及主题观察 |',
      '|---|---:|---:|---:|---:|---:|---|---|---:|---:|---|']
    details=['# Native retrieval-feedback 逐题证据','', '仅来自已保存 native title/snippet，不用 metadata、全文或 Anchor response。元素表的词面缺失不能直接解释为语义缺失。','']
    for q in rows:
        f=q['features'];r=q['qualitative_review']
        lines += [f"| {q['query_id']} | {int(q['positive_label'])} | {f['native_query_count']} | {f['parsed_candidate_occurrences']}/{f['unique_arxiv_ids']} | {f['duplicate_fraction']:.1%} | {f['mean_pair_jaccard_successful']:.4f} | {','.join(str(s['exclusive_vs_all_other_count']) for s in q['searches'])} | {','.join(str(s['incremental_vs_previous_count']) for s in q['searches'])} | {f['strict_high_missing']}/{f['token_high_missing']} | {f['unique_document_text_jaccard']:.4f} | {esc(r['summary'])} |"]
        details += [f"## {q['query_id']}",'',q['original_question'],'',r['summary'],'',r['detail'],'',
                    '| Native | 状态 | organic / parsed / unique | 独有 / 顺序新增 | query |','|---|---|---|---|---|']
        for s in q['searches']:
            details += [f"| q{s['query_index']} | {s['status']} | {s['organic_count']}/{s['parsed_candidate_count']}/{s['unique_arxiv_count']} | {s['exclusive_vs_all_other_count']}/{s['incremental_vs_previous_count']} | {esc(s['query_text'])} |"]
        details += ['', '| 原文元素 | H | 严格 unique ID 数 / query 位置 | token 共现 ID 数 / query 位置 | 最佳词面证据（只作定位） |','|---|---:|---|---|---|']
        for e in q['elements']:
            ev=(e['matching_evidence'] or e['best_lexical_evidence'])[:1]
            best='; '.join(f"{h['hit_key']} {h['arxiv_id']}: {h['title']} — {h['snippet']}" for h in ev)
            details += [f"| {esc(e['source_span'])} | {int(e['high_information'])} | {e['strict_unique_count']} / {e['strict_result_query_indices']} | {e['token_unique_count']} / {e['token_result_query_indices']} | {esc(best)} |"]
        details += ['', '结果 ID pair Jaccard：'+ '; '.join(f"q{p['queries'][0]}/q{p['queries'][1]}={p['jaccard']:.4f}" if p['jaccard'] is not None else str(p['queries'])+'=NA' for p in q['query_pairs']), '', '按 native 首次出现顺序列出 unique candidates（同 ID 不同 query 的 snippet 全部版本在 JSON 保存）：','']
        for d in q['documents']:
            h=d['variants'][0]
            details += [f"- `{d['arxiv_id']}`，q{d['query_indices']}：{h['title']} — {h['snippet']}"]
        details += ['']
    REPORT.write_text('\n'.join(lines)+'\n');DETAIL.write_text('\n'.join(details)+'\n')
    x['status']='complete';x['provenance']['findings_sha256']=sha(WORK/'findings.md');save(OUT,x)
    print('Rendered 50-row report and full native evidence details.')


def validate():
    x=read(OUT);m=x['provenance'];assert x['status']=='complete'
    assert sha(FEATURES)==m['features_sha256'] and sha(WORK/'review.json')==m['review_sha256']
    assert sha(WORK/'findings.md')==m['findings_sha256']
    assert all(sha(p)==h for p,h in m['source_sha256'].items())
    base=read(FEATURES)['per_query'];assert len(base)==50
    for q,b in zip(x['per_query'],base):
        assert {k:v for k,v in q.items() if k not in ('positive_label','qualitative_review')}==b
        sets=[set(s['candidate_ids']) for s in q['searches']];seen=set()
        assert q['features']['unique_arxiv_ids']==len(set.union(*sets))
        for i,(s,ids) in enumerate(zip(q['searches'],sets)):
            rest=set().union(*(v for j,v in enumerate(sets) if j!=i))
            assert s['exclusive_vs_all_other_ids']==sorted(ids-rest)
            assert s['incremental_vs_previous_ids']==sorted(ids-seen);seen|=ids
        assert sum(s['incremental_vs_previous_count'] for s in q['searches'])==len(seen)
        ps=[len(a&b)/len(a|b) for (i,a),(j,b) in itertools.combinations(enumerate(sets),2) if q['searches'][i]['status']==q['searches'][j]['status']=='PASS' and a|b]
        assert q['features']['mean_pair_jaccard_successful']==statistics.mean(ps)
        for e in q['elements']:
            hs=[h for s in q['searches'] for h in s['hits']]
            exact={h['arxiv_id'] for h in hs if literal(e['source_span'],h['title']) or literal(e['source_span'],h['snippet'])}
            assert exact==set(e['strict_result_unique_ids'])
    assert len(re.findall(r'^\| Q\d+ \|',REPORT.read_text(),re.M))==50
    assert len(re.findall(r'^## Q\d+$',DETAIL.read_text(),re.M))==50
    assert not BLOCKED
    paths=[OUT,REPORT,DETAIL,FEATURES,WORK/'review.json',WORK/'findings.md',Path(__file__)]
    save(WORK/'validation.json',{'status':'PASS','source_artifacts_unchanged':True,
        'checks':'50 Q; 248 native query slots; same original candidate parser; raw response SHA verified; overlap and leave-one-out/sequential novelty independently recounted; strict element matches recounted; frozen label-free features; 50 report rows; no anchor response opened; no evaluator or model calls',
        'execution':x['execution'],'artifact_sha256':{str(p):sha(p) for p in paths},
        'limitation':'Mechanical checks do not certify semantic review judgments or guarantee that truncated snippets represent full papers.'})
    print('Validation PASS')


if __name__=='__main__':
    sys.addaudithook(guard)
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['prepare','analyze','render','validate'])
    globals()[p.parse_args().phase]()
