"""Frozen, interpretable heuristic; only states.json is a data input."""
from common import HERE, BUDGETS, Guard, read, save, sha

POLICY = {
    'name': 'full_page_independent_frontier_v1',
    'formula': 'page_fill_ratio * (0.5 * exclusive_candidate_ratio + 0.5 * (1 - mean_jaccard))',
    'hypothesis': 'Full pages with independent, less redundant candidate frontiers may yield more new papers when deepened.',
    'weights': [0.5, 0.5],
    'tie_break': 'SHA256(query_key + newline + crawler_query), ascending; no GT or outcome-based ordering',
    'tuning': 'One heuristic fixed before evaluation; no outcome-based variants or parameter tuning.',
    'scope': 'global batch budget across 248 native queries; all Page1 responses observed',
}


def rank(states):
    import hashlib
    ranked = []
    for s in states:
        f = s['features']
        score = f['page_fill_ratio'] * (0.5 * f['exclusive_candidate_ratio'] + 0.5 * (1 - f['mean_jaccard']))
        ranked.append({'query_key': s['query_key'], 'need_more_search_score': score,
                       'fill': f['page_fill_ratio'], 'exclusive_ratio': f['exclusive_candidate_ratio'],
                       'mean_jaccard': f['mean_jaccard'],
                       'tie_key': hashlib.sha256((s['query_key'] + '\n' + s['crawler_query']).encode()).hexdigest()})
    ranked.sort(key=lambda s: (-s['need_more_search_score'], s['tie_key']))
    return [dict(s, rank=i + 1) for i, s in enumerate(ranked)]


def main():
    guard = Guard([HERE / 'states.json'], [HERE / 'decisions.json', HERE / 'controller_access.json'],
                  [__file__, HERE / 'common.py'])
    data = read(HERE / 'states.json')
    ranked = rank(data['states'])
    decisions = {
        'policy': POLICY, 'states_sha256': sha(HERE / 'states.json'),
        'page1_snapshot_id': data['page1_snapshot_id'],
        'controller_source_sha256': sha(__file__), 'ranking': ranked,
        'budgets': {str(b): [r['query_key'] for r in ranked[:len(ranked) if b == 'all' else b]] for b in BUDGETS},
    }
    save(HERE / 'decisions.json', decisions)
    save(HERE / 'controller_access.json', guard.evidence())
    print('Controller decisions frozen for budgets: ' + ', '.join(map(str, BUDGETS)))


if __name__ == '__main__':
    main()
