"""Label-free validation, including deny-before-read checks for protected inputs."""
from collections import Counter
from common import HERE, PLAN, SOURCE, REPO, BUDGETS, Guard, read, save, sha, digest, key, check_response
from features import extract
from controller import rank


def main():
    inputs = [PLAN] + [HERE / p for p in ['states.json', 'decisions.json', 'features_access.json', 'controller_access.json']]
    guard = Guard(inputs, [HERE / 'validation_controller.json'],
                  [HERE / p for p in ['common.py', 'features.py', 'controller.py', 'validate.py']])
    states, decisions = read(HERE / 'states.json'), read(HERE / 'decisions.json')
    tasks = sorted(read(PLAN)['tasks'], key=lambda t: (t['query_index'], t['query_sequence']))
    guard.allow(t['baseline_replay'] for t in tasks)
    records = {key(t): read(t['baseline_replay']) for t in tasks}
    for r in records.values():
        check_response(r)
    assert extract(tasks, records) == states['states']
    counts = Counter(s['query_index'] for s in states['states'])
    assert len(states['states']) == len(tasks) == len(decisions['ranking']) == 248
    assert dict(counts) == {i: 4 if i in (18, 28) else 5 for i in range(50)}
    assert decisions['states_sha256'] == sha(HERE / 'states.json')
    assert decisions['controller_source_sha256'] == sha(HERE / 'controller.py')
    assert all(sha(HERE / p) == h for p, h in states['source_hashes'].items())
    assert decisions['ranking'] == rank(states['states'])
    manifest = {s['page1_path']: s['page1_file_sha256'] for s in states['states']}
    assert states['page1_snapshot_id'] == digest(manifest) == decisions['page1_snapshot_id']
    ordered = [r['query_key'] for r in decisions['ranking']]
    for b in BUDGETS:
        selected = decisions['budgets'][str(b)]
        n = len(ordered) if b == 'all' else b
        assert selected == ordered[:n] and len(set(selected)) == n
    f_access, c_access = read(HERE / 'features_access.json'), read(HERE / 'controller_access.json')
    allowed_f = {str(PLAN.resolve())} | set(manifest) | {str(HERE / p) for p in ['common.py', 'features.py']}
    assert set(f_access['read_paths']) <= allowed_f
    assert set(c_access['read_paths']) <= {str(HERE / p) for p in ['states.json', 'controller.py', 'common.py']}
    assert not f_access['denied_attempts'] and not c_access['denied_attempts']
    denied = []
    for path in [REPO / 'data/RealScholarQuery/test.jsonl', REPO / 'PAGE2_SEARCH_PROBE_001.json',
                 SOURCE / 'q00/s01/attempt_002.json', HERE / 'results.json']:
        try:
            path.read_bytes()
        except PermissionError:
            denied.append(str(path))
        else:
            raise AssertionError('Forbidden input readable: ' + str(path))
    # Synthetic set case checks leave-one-out vs sequential marginal definitions.
    sets = [{'a', 'b'}, {'b', 'c'}, {'b'}]
    assert [len(s - set().union(*(v for j, v in enumerate(sets) if j != i))) for i, s in enumerate(sets)] == [1, 1, 0]
    save(HERE / 'validation_controller.json', {
        'status': 'PASS', 'query_count': 248, 'question_count': 50,
        'query_count_distribution': {'4': 2, '5': 48},
        'all_features_recomputed_identically': True, 'ranking_recomputed_identically': True,
        'budget_prefixes_valid': True, 'source_hashes_match': True,
        'feature_read_allowlist_verified': True, 'controller_reads_states_only': True,
        'protected_read_attempts_denied_before_io': denied, 'access_evidence': guard.evidence(),
    })
    print('Label-free controller validation: PASS (including 4 forbidden-read checks)')


if __name__ == '__main__':
    main()
