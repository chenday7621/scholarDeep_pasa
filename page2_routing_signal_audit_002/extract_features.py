"""Label-free Page1 extraction with exact file allowlists and no model calls."""
from collections import Counter
import math
import re
from statistics import mean

from audit_common import HERE, PREVIOUS, PROMPTS, SHARED_CODE, PLAN, PLAN_SPEC, Guard, read, save, sha, digest, hits, check_response
from features import extract as original_extract

STOP = frozenset('a an the and or of to in on for from with by at as is are was were be been being this that these those it its their we our they you your i me my any some which what how can could would should do does did has have had using use used paper papers study studies research related work works show provide find arxiv http https org com'.split())


def tokens(text):
    return [t for t in re.findall(r'[a-z0-9]+', text.lower()) if len(t) > 1 and t not in STOP]


def aggregate(pairs):
    def avg(values):
        return mean(values) if values else None
    top = [v for r, v in pairs if 1 <= r <= 3]
    tail = [v for r, v in pairs if 8 <= r <= 10]
    top1 = [v for r, v in pairs if r == 1]
    values = [v for _, v in pairs]
    slope = None
    if len(pairs) > 1:
        mx, my = mean(r for r, _ in pairs), mean(values)
        denom = sum((r - mx)**2 for r, _ in pairs)
        slope = sum((r - mx)*(v - my) for r, v in pairs) / denom if denom else None
    return {'mean': avg(values), 'max': max(values) if values else None,
            'top1': avg(top1), 'top3': avg(top), 'tail3': avg(tail),
            'top3_minus_tail3': avg(top)-avg(tail) if top and tail else None,
            'rank_slope': slope}


def main():
    prompts = [PROMPTS / f'{q:02d}_extract.json' for q in range(50)]
    inputs = [PREVIOUS / 'states.json', PLAN, HERE / 'environment_audit.json', *prompts]
    outputs = [HERE / p for p in ['page1_features.json', 'feature_access.json', 'analysis_plan.json', 'feature_definitions.json']]
    guard = Guard(inputs, outputs, [__file__, *SHARED_CODE, PREVIOUS / 'features.py'])
    save(HERE / 'analysis_plan.json', PLAN_SPEC)
    environment = read(HERE / 'environment_audit.json')
    assert environment['semantic_embedding_status'] == 'unavailable_in_checked_project_and_user_caches'
    frozen = read(PREVIOUS / 'states.json')
    tasks = sorted(read(PLAN)['tasks'], key=lambda t: (t['query_index'], t['query_sequence']))
    guard.allow(s['page1_path'] for s in frozen['states'])
    records = {s['query_key']: read(s['page1_path']) for s in frozen['states']}
    for s in frozen['states']:
        check_response(records[s['query_key']])
        assert sha(s['page1_path']) == s['page1_file_sha256']
    assert original_extract(tasks, records) == frozen['states']
    questions, question_provenance = {}, {}
    for q, path in enumerate(prompts):
        cached = read(path)
        assert set(cached) <= {'query_id', 'stage', 'status', 'parsed', 'attempts'}
        prompt = cached['attempts'][0]['prompt']
        assert prompt.count('USER QUESTION:\n') == 1
        questions[q] = prompt.split('USER QUESTION:\n', 1)[1].strip()
        assert cached['query_id'] == f'RealScholarQuery_{q}'
        question_provenance[str(q)] = {'path': str(path), 'sha256': sha(path), 'json_pointer': '/attempts/0/prompt', 'delimiter': 'USER QUESTION:\n'}
    # IDF on deduplicated visible texts only; no question/GT/Page2-derived corpus.
    texts = sorted({(h.get('title', '') + '\n' + h.get('snippet', '')).strip() for r in records.values() for h in hits(r)})
    counts = Counter(t for text in texts for t in set(tokens(text)))
    total = len(texts)
    idf = {t: 1 + math.log((1 + total)/(1 + df)) for t, df in counts.items()}

    def vector(text):
        term_counts = Counter(tokens(text))
        values = {t: (1+math.log(n))*idf[t] for t, n in term_counts.items() if t in idf}
        norm = math.sqrt(sum(v*v for v in values.values()))
        return {t: v/norm for t, v in values.items()} if norm else {}

    vectors = {text: vector(text) for text in texts}
    output = []
    for s in frozen['states']:
        r = records[s['query_key']]
        feats = dict(s['features'])
        feats['original_need_more_search_score'] = feats['page_fill_ratio'] * (0.5*feats['exclusive_candidate_ratio'] + 0.5*(1-feats['mean_jaccard']))
        qs = questions[s['query_index']]
        evidence = []
        for h in hits(r):
            rank = h['organic_index'] + 1  # retain provider order; never re-rank by labels
            text = (h.get('title', '') + '\n' + h.get('snippet', '')).strip()
            evidence.append({'rank': rank, 'arxiv_id': h['arxiv_id'], 'title': h.get('title', ''), 'snippet': h.get('snippet', '')})
        for source, query in [('question', qs), ('query', s['crawler_query'])]:
            query_vector = vector(query)
            pairs = []
            for h in evidence:
                text = (h['title']+'\n'+h['snippet']).strip()
                relevance = sum(v*vectors[text].get(t, 0.0) for t, v in query_vector.items())
                h[source+'_lexical_cosine'] = relevance
                pairs.append((h['rank'], relevance))
            feats.update({source+'_lexical_'+name: value for name, value in aggregate(pairs).items()})
        feats['text_top3_observed_count'] = sum(h['rank'] <= 3 for h in evidence)
        feats['text_tail3_observed_count'] = sum(8 <= h['rank'] <= 10 for h in evidence)
        output.append({'query_key': s['query_key'], 'query_index': s['query_index'], 'query_sequence': s['query_sequence'],
                       'question': qs, 'native_query': s['crawler_query'], 'page1_path': s['page1_path'],
                       'page1_sha256': s['page1_file_sha256'], 'features': feats, 'page1_text_scores': evidence})
    definitions = {}
    for name in output[0]['features']:
        family = 'question_lexical' if name.startswith('question_lexical_') else 'query_lexical' if name.startswith('query_lexical_') else 'original_heuristic_diagnostic' if name == 'original_need_more_search_score' else 'set_statistics'
        definitions[name] = {'family': family, 'semantic_embedding': False}
    result = {
        'status': 'PASS', 'query_count': len(output), 'question_count': len(questions),
        'page1_snapshot_id': frozen['page1_snapshot_id'], 'frozen_states_sha256': sha(PREVIOUS / 'states.json'),
        'analysis_plan_content_digest': digest(PLAN_SPEC),
        'embedding_status': 'NOT_MEASURED_NO_LOCAL_EMBEDDING_MODEL',
        'lexical_definition': {'tokens': '[a-z0-9]+ lowercase; length>1; fixed stop words; no stemming, synonyms or acronym expansion',
                               'stop_words': sorted(STOP), 'tf': '1+ln(count)', 'idf': '1+ln((1+N)/(1+df)); Page1-only distinct title/snippet texts',
                               'corpus_unique_text_count': total, 'vocabulary_size': len(idf),
                               'oov': 'tokens absent from Page1 corpus ignored', 'similarity': 'L2-normalized sparse TF-IDF cosine, lexical proxy only',
                               'windows': 'original organic array ranks 1-3 and 8-10, parsed valid URLs only; missing windows null; partial windows mean observed slots',
                               'duplicates': 'each ranked occurrence contributes, including within-page duplicate IDs; no reranking'},
        'question_provenance': question_provenance, 'feature_definitions': definitions,
        'source_hashes': {str(p): sha(p) for p in [__file__, *SHARED_CODE, PREVIOUS / 'features.py']},
        'rows': output,
    }
    assert len(output) == 248
    save(HERE / 'feature_definitions.json', definitions)
    save(HERE / 'page1_features.json', result)
    save(HERE / 'feature_access.json', guard.evidence())
    print(f'Frozen {len(output)} Page1 rows; {len(definitions)} features; no outcomes/GT read.')


if __name__ == '__main__':
    main()
