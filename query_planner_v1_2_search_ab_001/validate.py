"""Independent saved-response replay and paired GT/call accounting checks."""
import base64
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
from urllib.parse import urlparse, parse_qs
from common import ROOT, WORK, SOURCE, OUT, REPORT, now, read, save, sha, protected, project_questions


def main():
    d = read()
    assert d['status'] == 'complete'
    p = d['provenance']
    assert p['protected_before'] == p['protected_after_search'] == p['protected_after_metadata'] == p['protected_after_scoring'] == protected()
    assert p['source_sha256'] == sha(SOURCE)
    source = read(SOURCE)
    seq, recomputed, shared = [], {}, 0
    for q, original, old in zip(d['per_query'], project_questions(), source['per_query']):
        assert all(q[k] == value for k, value in original.items())
        assert q['groups']['A']['queries'] == old['A_queries']
        assert q['groups']['B']['queries'] == old['B_queries']
        assert q['source_generation_id'] == old['generation_id']
        assert q['before_date'] == '2024-09-24'
        groups = {name: g['search_keys'] for name, g in q['groups'].items()}
        assert groups['A'] == [f'q{i+1}' for i in range(len(old['native_queries']))]
        assert groups['B'] == ['anchor', 'q1', 'q2', 'q3', 'q4']
        assert set(groups['A']) & set(groups['B']) == {'q1', 'q2', 'q3', 'q4'}
        assert q['execution_order'][:4] == ['q1', 'q2', 'q3', 'q4']
        assert set(q['execution_order']) == set(q['searches'])
        assert read(WORK / 'completed_queries' / f"{q['query_id']}.json")['searches'] == {
            key: {k: v for k, v in s.items() if k not in ('matched_gt', 'missing_metadata_ids', 'matched_gt_evidence')}
            for key, s in q['searches'].items()}
        labels = {''.join(c for c in title if c.isalpha()).lower() for title in q['gt']['raw_titles']}
        assert len(labels) == q['gt']['total']
        hits, candidate_sets = {}, {}
        for key, s in q['searches'].items():
            expected = {'q': f"{s['query_text']} before:2024-09-24 site:arxiv.org", 'num': 10, 'page': 1}
            assert s['request_payload'] == expected
            assert 1 <= len(s['attempts']) <= 3
            for index, a in enumerate(s['attempts'], 1):
                assert a['attempt'] == index and a['query_id'] == q['query_id'] and a['query_key'] == key
                assert a['request_payload'] == expected and read(a['artifact_path']) == a
                seq.append(a['global_attempt_sequence'])
                assert not {'headers', 'X-API-KEY', 'api_key'} & set(a)
                if a.get('http_status') is not None:
                    raw = base64.b64decode(a['response_bytes_base64'])
                    assert hashlib.sha256(raw).hexdigest() == a['response_sha256']
                    if a['structured_response'] is not None:
                        assert json.loads(raw) == json.loads(a['response_text']) == a['structured_response']
                if index < len(s['attempts']):
                    assert a['status'] != 'PASS'
            ids = set()
            if s['status'] == 'PASS':
                last = s['attempts'][-1]
                assert last['status'] == 'PASS' and last['http_status'] == 200
                for hit in last['structured_response']['organic']:
                    match = re.search(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)', hit.get('link', ''))
                    if match:
                        ids.add(match.group(1))
            assert ids == set(s['returned_arxiv_ids'])
            pred = {''.join(c for c in d['metadata'][aid]['title'] if c.isalpha()).lower()
                    for aid in ids if d['metadata'][aid]['status'] == 'PASS'}
            candidate_sets[key], hits[key] = ids, pred & labels
            assert hits[key] == set(s['matched_gt'])
            assert {e['normalized_gt_title'] for e in s['matched_gt_evidence']} == hits[key]
        for name, g in q['groups'].items():
            assert [q['searches'][key]['query_text'] for key in g['search_keys']] == g['queries']
            found = set().union(*(hits[key] for key in g['search_keys']))
            candidates = set().union(*(candidate_sets[key] for key in g['search_keys']))
            assert found == set(g['matched_gt']) and len(found) == g['gt_found']
            assert candidates == set(g['candidate_ids'])
            assert g['recall'] == len(found) / len(labels)
            assert g['serper_attempts'] == sum(len(q['searches'][key]['attempts']) for key in g['search_keys'])
        shared += len(set(groups['A']) & set(groups['B']))
        c = set().union(*(hits[f'q{i}'] for i in range(1, 5)))
        fifth, anchor = hits.get('q5', set()), hits['anchor']
        a, b = c | fifth, c | anchor
        expected_parts = {'common_gt': c, 'q5_component_gt': fifth, 'anchor_component_gt': anchor,
                          'q5_only_gt': a - b, 'anchor_only_gt': b - a,
                          'q5_marginal_gt': fifth - c, 'anchor_marginal_gt': anchor - c,
                          'shared_exclusive_component_marginal_gt': (fifth & anchor) - c}
        assert all(set(q['comparison'][key]) == value for key, value in expected_parts.items())
        assert q['comparison']['delta_gt'] == len(b) - len(a)
        assert math.isclose(q['comparison']['delta_recall'], (len(b) - len(a)) / len(labels))
        recomputed[q['query_id']] = {'gt': len(labels), 'A': len(a), 'B': len(b), 'parts': expected_parts}
    assert shared == 200
    assert sorted(seq) == list(range(1, len(seq) + 1))
    assert len(list((WORK / 'requests').glob('*.json'))) == len(seq)
    for subset, summary in d['summary'].items():
        qs = d['per_query'] if subset == 'full_50Q' else [q for q in d['per_query'] if q['query_id'] not in ('Q18', 'Q28')]
        assert len(qs) == summary['questions']
        total = sum(recomputed[q['query_id']]['gt'] for q in qs)
        assert total == summary['TOTAL_GT']
        for group in ('A', 'B'):
            found = sum(recomputed[q['query_id']][group] for q in qs)
            macro = statistics.mean(recomputed[q['query_id']][group] / recomputed[q['query_id']]['gt'] for q in qs)
            assert found == summary[group]['GT_FOUND']
            assert math.isclose(macro, summary[group]['MACRO_SEARCH_RECALL'])
            assert math.isclose(found / total, summary[group]['MICRO_SEARCH_RECALL'])
            assert p['official_evaluator_verification'][subset][group]['macro_search_recall'] == round(macro, 4)
        for key in expected_parts:
            assert sum(len(recomputed[q['query_id']]['parts'][key]) for q in qs) == summary[key + '_count']
        counts = Counter('gt' if q['comparison']['delta_gt'] > 0 else 'lt' if q['comparison']['delta_gt'] < 0 else 'eq' for q in qs)
        assert all(summary['comparison'][f'B_{k}_A_questions'] == counts[k] for k in ('gt', 'lt', 'eq'))
        assert summary['actual_unique_serper_attempts'] == sum(len(s['attempts']) for q in qs for s in q['searches'].values())
    assert d['summary']['equal_budget_48Q']['A']['LOGICAL_SERPER_CALLS'] == d['summary']['equal_budget_48Q']['B']['LOGICAL_SERPER_CALLS'] == 240
    network = read(WORK / 'metadata_network.json')
    network_indices = []
    for aid, record in d['metadata'].items():
        assert record == read(WORK / 'metadata' / f'{aid}.json')
        indices = record['network_record_indices']
        network_indices.extend(indices)
        assert len(indices) <= 4
        for i in indices:
            request = network[i]
            assert request['arxiv_id'] == aid and request['method'].upper() == 'GET'
            parsed = urlparse(request['url'])
            assert parsed.hostname in ('export.arxiv.org', 'arxiv.org')
            params = request['params'] or parse_qs(parsed.query, keep_blank_values=True)
            assert params['id_list'] == [aid] and params.get('search_query') in (None, '', [''])
    assert sorted(network_indices) == list(range(len(network)))
    assert len(network) == p['metadata_summary']['http_attempts']
    assert p['new_crawler_generations'] == 0
    save(WORK / 'validation.json', {'validated_utc': now(), 'status': 'PASS',
         'checks': '50 source query arrays; exact shared-response binding; 298 logical requests and every attempt/raw bytes/hash/parser; independent GT/title sets, component exclusives/marginals, cohort separation, attributed/actual calls, 4 unchanged official evaluator matches, frozen sources',
         'source_sha256': sha(SOURCE), 'shared_logical_queries': shared, 'actual_serper_attempts': len(seq),
         'artifact_sha256': {str(path): sha(path) for path in (OUT, REPORT, Path(__file__))}})
    print('Independent validation PASS: all queries, raw responses, pairing, GT sets, cohorts and frozen evaluator.', flush=True)


if __name__ == '__main__':
    main()
