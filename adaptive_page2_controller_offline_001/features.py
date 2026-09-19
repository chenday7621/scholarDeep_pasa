"""Page1-only features. Never opens the dataset, Page2 cache, or evaluation reports."""
from collections import Counter, defaultdict
from statistics import mean
from common import HERE, PLAN, BASE, Guard, read, save, sha, digest, key, hits, check_response


def extract(tasks, records):
    grouped = defaultdict(list)
    for t in tasks:
        grouped[t['query_index']].append(t)
    states = []
    for q, members in sorted(grouped.items()):
        members.sort(key=lambda t: t['query_sequence'])
        sets = {key(t): {h['arxiv_id'] for h in hits(records[key(t)])} for t in members}
        union = set().union(*sets.values())
        memberships = sum(map(len, sets.values()))
        previous = set()
        for t in members:
            k = key(t)
            r, own = records[k], sets[k]
            other_sets = [v for kk, v in sets.items() if kk != k]
            others = set().union(*other_sets)
            parsed = hits(r)
            organic = r['structured_response']['organic']
            jaccards = [len(own & v) / len(own | v) if own | v else 0.0 for v in other_sets]
            exclusive = len(own - others)
            n = len(own)
            states.append({
                'query_key': k, 'query_index': q, 'query_sequence': t['query_sequence'],
                'crawler_query': t['crawler_query'], 'request_payload': t['baseline_payload'],
                'page1_path': t['baseline_replay'], 'page1_file_sha256': sha(t['baseline_replay']),
                'candidate_ids': sorted(own),
                'features': {
                    'organic_count': len(organic),
                    'valid_candidate_count': n,
                    'valid_candidate_occurrence_count': len(parsed),
                    'invalid_url_count': len(organic) - len(parsed),
                    'within_query_duplicate_ratio': 1 - n / len(parsed) if parsed else 0.0,
                    'marginal_unique_candidate_count': exclusive,
                    'sequential_marginal_unique_candidate_count': len(own - previous),
                    'mean_jaccard': mean(jaccards), 'max_jaccard': max(jaccards),
                    'cross_query_duplicate_ratio': len(own & others) / n if n else 0.0,
                    'question_duplicate_ratio': 1 - len(union) / memberships if memberships else 0.0,
                    'question_unique_candidate_count': len(union),
                    'question_native_query_count': len(members),
                    'page_fill_ratio': min(n / t['baseline_payload']['num'], 1.0),
                    'exclusive_candidate_ratio': exclusive / n if n else 0.0,
                    'tail5_valid_candidate_count': sum(h['organic_index'] >= 5 for h in parsed),
                    'tail5_exclusive_candidate_count': len({h['arxiv_id'] for h in parsed if h['organic_index'] >= 5} - others),
                    'snippet_available_ratio': sum(bool(h.get('snippet')) for h in organic) / len(organic) if organic else 0.0,
                    'latency_seconds': r['latency_seconds'],
                },
            })
            previous |= own
    return states


def main():
    guard = Guard([PLAN], [HERE / 'states.json', HERE / 'features_access.json'],
                  [__file__, HERE / 'common.py'])
    plan = read(PLAN)
    tasks = sorted(plan['tasks'], key=lambda t: (t['query_index'], t['query_sequence']))
    assert len(tasks) == plan['task_count'] == 248
    assert len({key(t) for t in tasks}) == 248
    for t in tasks:
        assert str(t['baseline_replay']).startswith(str(BASE) + '/')
        assert t['baseline_payload']['page'] == 1 and t['baseline_payload']['num'] == 10
    guard.allow(t['baseline_replay'] for t in tasks)
    records = {key(t): read(t['baseline_replay']) for t in tasks}
    for t in tasks:
        r = records[key(t)]
        check_response(r)
        assert r['request_payload'] == t['baseline_payload']
        assert r['crawler_search_query'] == t['crawler_query']
        assert r['search_query_sequence'] == t['query_sequence']
        assert r['raw_response_sha256'] == t['baseline_response_sha256']
    states = extract(tasks, records)
    manifest = {s['page1_path']: s['page1_file_sha256'] for s in states}
    save(HERE / 'states.json', {
        'schema': 'page1_only_v1', 'query_count': len(states), 'question_count': 50,
        'plan_sha256': sha(PLAN), 'page1_snapshot_id': digest(manifest),
        'source_hashes': {p.name: sha(p) for p in [HERE / 'common.py', HERE / 'features.py']},
        'definitions': {
            'valid_candidate_count': 'unique IDs parsed from organic URLs by the original PaSa regex',
            'marginal_unique_candidate_count': '|S_i minus union of other native queries for the same question|; order invariant',
            'sequential_marginal_unique_candidate_count': '|S_i minus union of preceding native queries|; original generation order',
            'cross_query_duplicate_ratio': '|S_i intersect union of other queries| / |S_i|; zero for empty S_i',
            'jaccard': 'same-question native Page1 ID sets; empty/empty defined as 0',
            'availability': 'all native Page1 responses must be available before one global allocation',
        },
        'states': states,
    })
    save(HERE / 'features_access.json', guard.evidence())
    print('Page1-only feature extraction: 248 queries, 50 questions')


if __name__ == '__main__':
    main()
