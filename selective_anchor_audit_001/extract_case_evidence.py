"""Copy existing retrieval evidence for interpretation AFTER text features freeze."""
import sys
from pathlib import Path
from audit import ROOT, WORK, DENIED, guard, read, save, sha

sys.addaudithook(guard)
source_path = ROOT / 'QUERY_PLANNER_V1_2_A5_B6_REPLAY_001.json'
replay = read(source_path)
search_path = Path(replay['provenance']['source'])
assert sha(search_path) == replay['provenance']['source_sha256']
search = read(search_path)
audit = read(ROOT / 'SELECTIVE_ANCHOR_AUDIT_001.json')
assert sha(WORK / 'text_only_features.json') == audit['provenance']['text_only_features_sha256']
assert sha(source_path) == audit['provenance']['source_sha256']
sources = {str(p): sha(p) for p in (source_path, search_path)}
cases = []
for q in replay['per_query']:
    if q['query_id'] not in ('Q13', 'Q19', 'Q28', 'Q44', 'Q45', 'Q48'):
        continue
    old = next(x for x in search['per_query'] if x['query_id'] == q['query_id'])
    anchor = old['searches']['anchor']
    assert q['cached_queries']['anchor']['matched_gt'] == anchor['matched_gt']
    hits = []
    for hit in anchor['organic_hits']:
        metadata = search['metadata'][hit['arxiv_id']]
        hits.append(dict(hit, metadata_status=metadata['status'],
                         metadata_title=metadata['title']))
    for path in q['cached_queries']['anchor']['response_artifacts']:
        sources[path] = sha(path)
    cases.append({
        'query_id': q['query_id'], 'original_question': q['original_question'],
        'native_queries': q['native_queries'], 'gt': q['gt'],
        'full_native_gt_found': q['groups']['A']['gt_found'],
        'full_native_plus_anchor_gt_found': q['groups']['B']['gt_found'],
        'added_gt_evidence': q['added_gt_evidence'],
        'anchor': {'status': anchor['status'], 'request_payload': anchor['request_payload'],
                   'http_statuses': [a['http_status'] for a in anchor['attempts']],
                   'matched_gt': anchor['matched_gt'],
                   'missing_metadata_ids': anchor['missing_metadata_ids'],
                   'returned_arxiv_ids': anchor['returned_arxiv_ids'],
                   'hits_with_existing_metadata': hits,
                   'response_artifacts': q['cached_queries']['anchor']['response_artifacts']}})
q28 = next(q for q in cases if q['query_id'] == 'Q28')
assert len(q28['anchor']['hits_with_existing_metadata']) == 8
assert not q28['anchor']['missing_metadata_ids'] and not q28['anchor']['matched_gt']
assert all(h['metadata_status'] == 'PASS' for h in q28['anchor']['hits_with_existing_metadata'])
assert not DENIED and all(sha(p) == h for p, h in sources.items())
save(WORK / 'case_evidence.json', {
    'purpose': 'Existing outcome/rank evidence for retrospective interpretation only; NEVER input-only features or trigger inputs. No evaluator, title normalization or matching was rerun or modified.',
    'source_sha256': sources,
    'script_sha256': sha(__file__),
    'text_only_features_sha256': sha(WORK / 'text_only_features.json'),
    'execution': {'new_network_requests': 0, 'new_serper_requests': 0,
                  'new_crawler_generations': 0, 'blocked_events': DENIED},
    'cases': cases})
print('Copied 6 cached cases; Q28 has 8 parsed, metadata-complete, non-GT anchor hits.')
