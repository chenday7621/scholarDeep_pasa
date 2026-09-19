"""Fixed, dictionary-free lexical indicators. Never assess expansion correctness."""
import collections
import itertools
import re
import unicodedata

CONNECTORS=frozenset('a an the of for from with without in on at to by and or via using'.split())
WORD=re.compile(r'[A-Za-z]+(?:[’\'][A-Za-z]+)?')

def norm(text):
    return ' '.join(re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKC',text).casefold()))

def acronym_pattern(acronym):
    return re.compile(r'(?<![A-Za-z0-9_])'+re.escape(acronym)+r'(?:s)?(?![A-Za-z0-9_])',re.I)

def candidates(query,acronym,original_question):
    """Contiguous word-span initials, optional connectors, nested caps token support.

    Literal model-produced substrings only. No expansion allowlist or inferred words.
    Prefer minimal nested spans to avoid counting surrounding connector words twice.
    """
    target=acronym.casefold()
    words=list(WORD.finditer(query))
    found=[]
    for start in range(len(words)):
        for end in range(start+2,min(len(words),start+2*len(target)+2)+1):
            chunk=words[start:end]
            if chunk[0].group().casefold() in CONNECTORS or chunk[-1].group().casefold() in CONNECTORS: continue
            # A candidate cannot include the target acronym itself or bridge query clauses.
            if any(acronym_pattern(acronym).fullmatch(w.group()) for w in chunk): continue
            if re.search(r'[,;:.!?()\[\]/]',query[chunk[0].start():chunk[-1].end()]): continue
            if sum(w.group().casefold() not in CONNECTORS for w in chunk)<2: continue
            states={''}
            for word in chunk:
                token=word.group(); choices={token[0].casefold()}
                if token.casefold() in CONNECTORS: choices.add('')
                if token.isupper() and 2<=len(token)<=5: choices.add(token.casefold())
                states={s+c for s in states for c in choices if target.startswith(s+c)}
                if not states: break
            if target not in states: continue
            a,b=chunk[0].start(),chunk[-1].end()
            phrase=query[a:b]
            found.append({'text':phrase,'start':a,'end':b,'rule':'contiguous_initials_with_optional_connectors',
                          'also_in_original_question':(' '+norm(phrase)+' ') in (' '+norm(original_question)+' '),
                          'human_judgment':None})
    return [c for c in found if not any(c['start']<=o['start'] and c['end']>=o['end'] and (c['start'],c['end'])!=(o['start'],o['end']) for o in found)]

def metrics(run,sample):
    queries=run['search_queries']; a=sample['acronym']; pat=acronym_pattern(a)
    per_query=[]
    for i,q in enumerate(queries):
        cs=candidates(q,a,sample['original_question'])
        per_query.append({'query_index':i,'query':q,'acronym_retained':bool(pat.search(q)),
                          'original_surface_retained':any(re.search(r'(?<![A-Za-z0-9_])'+re.escape(m['text'])+r'(?![A-Za-z0-9_])',q) for m in sample['mentions']),
                          'expansion_candidates':cs,'expansion_attempt_proxy':bool(cs),
                          'acronym_expansion_cooccurrence_proxy':bool(cs) and bool(pat.search(q))})
    exact=[];near=[];collapsed=[]
    for i,j in itertools.combinations(range(len(queries)),2):
        left,right=norm(queries[i]),norm(queries[j])
        if left and left==right: exact.append([i,j])
        x,y=set(left.split()),set(right.split())
        score=len(x&y)/len(x|y) if x|y else 0
        if left!=right and score>=.85: near.append({'query_indices':[i,j],'token_set_jaccard':score})
        def collapse(item):
            text=item['query']
            for c in sorted(item['expansion_candidates'],key=lambda c:c['start'],reverse=True): text=text[:c['start']]+a+text[c['end']:]
            text=pat.sub(a,text)
            tokens=norm(text).split(); out=[]
            for t in tokens:
                if not(out and t==a.casefold() and out[-1]==t): out.append(t)
            return ' '.join(out)
        if left!=right and (per_query[i]['expansion_candidates'] or per_query[j]['expansion_candidates']) and collapse(per_query[i])==collapse(per_query[j]): collapsed.append([i,j])
    raw=run['raw_output']
    # Strict format check is supplemental; native parsing remains unchanged.
    strict=bool(re.fullmatch(r'\s*(?:\[Search\][^\[\]]+)+\[StopSearch\]\s*',raw,re.DOTALL))
    return {'query_count':len(queries),'all_generated_query_count':len(run['all_parsed_search_queries']),
            'parse_success':bool(queries) and all(bool(q) for q in queries),'strict_native_envelope':strict,
            'literal_search_marker_count':raw.count('[Search]'),'non_search_action_marker_present':bool(re.search(r'\[(?:Expand|StopExpand|Select)\]',raw)),
            'empty_query_count':sum(not q for q in queries),'query_cap_applied':bool(run['discarded_queries_by_native_cap']),
            'unparsed_literal_search_markers':max(0,raw.count('[Search]')-len(run['all_parsed_search_queries'])),
            'per_query':per_query,'acronym_retained':any(q['acronym_retained'] for q in per_query),
            'original_surface_retained':any(q['original_surface_retained'] for q in per_query),
            'expansion_attempt_proxy':any(q['expansion_attempt_proxy'] for q in per_query),
            'acronym_expansion_cooccurrence_proxy':any(q['acronym_expansion_cooccurrence_proxy'] for q in per_query),
            'has_candidate_not_in_original':any(not c['also_in_original_question'] for q in per_query for c in q['expansion_candidates']),
            'normalized_duplicate_pairs':exact,'near_duplicate_pairs':near,'candidate_collapsed_duplicate_pairs':collapsed,
            'any_normalized_duplicate':bool(exact),'any_near_duplicate':bool(near),'any_candidate_collapsed_duplicate':bool(collapsed)}

def summarize(samples,group):
    runs=[r for s in samples for r in s['groups'][group]['runs']]
    n=len(runs); parsed=sum(r['metrics']['parse_success'] for r in runs)
    result={'sample_count':len(samples),'generation_count':n,'final_query_count':sum(len(r['search_queries']) for r in runs)}
    keys=['parse_success','strict_native_envelope','acronym_retained','original_surface_retained','expansion_attempt_proxy','acronym_expansion_cooccurrence_proxy','has_candidate_not_in_original','any_normalized_duplicate','any_near_duplicate','any_candidate_collapsed_duplicate','non_search_action_marker_present','query_cap_applied']
    for k in keys:
        count=sum(r['metrics'][k] for r in runs)
        result[k]={'run_count':count,'rate':count/n,'denominator':n,
                   'sample_count':sum(any(r['metrics'][k] for r in s['groups'][group]['runs']) for s in samples)}
    result['rates_among_parsed_runs']={k:sum(r['metrics'][k] and r['metrics']['parse_success'] for r in runs)/parsed if parsed else None for k in ('acronym_retained','expansion_attempt_proxy','acronym_expansion_cooccurrence_proxy')}
    result['unparsed_literal_search_markers']=sum(r['metrics']['unparsed_literal_search_markers'] for r in runs)
    result['empty_queries']=sum(r['metrics']['empty_query_count'] for r in runs)
    result['truncated_generations']=sum(not r['ended_with_eos'] for r in runs)
    result['accuracy']=None
    return result
