"""Validate isolation with deliberate forbidden reads, denied before filesystem I/O."""
from audit_common import HERE, REPO, PREVIOUS, SOURCE, SHARED_CODE, Guard, read, save, sha


def main():
    paths=[HERE/'page1_features.json',HERE/'feature_access.json']
    guard=Guard(paths,[HERE/'validation_feature_isolation.json'],[__file__,*SHARED_CODE])
    data=read(paths[0]);access=read(paths[1])
    allowed={str(p.resolve()) for p in [HERE/'environment_audit.json',PREVIOUS/'states.json',SOURCE/'request_plan.json',
                                      HERE/'extract_features.py',PREVIOUS/'features.py',*SHARED_CODE]}
    allowed.update(r['page1_path'] for r in data['rows'])
    allowed.update(p['path'] for p in data['question_provenance'].values())
    assert set(access['read_paths'])<=allowed and access['denied_attempts']==[]
    assert len(data['rows'])==248
    assert all('positive' not in r and 'page2_gain' not in r and 'label' not in r for r in data['rows'])
    forbidden=[REPO/'data/RealScholarQuery/test.jsonl', REPO/'PAGE2_SEARCH_PROBE_001.json',
               PREVIOUS/'evaluation_query_outcomes.json',SOURCE/'q00/s01/attempt_002.json',
               HERE/'query_signal_table.json',HERE/'feature_stats.json']
    denied=[]
    for path in forbidden:
        try:path.read_bytes()
        except PermissionError:denied.append(str(path))
        else:raise AssertionError('Leakage guard failed: '+str(path))
    save(HERE/'validation_feature_isolation.json',{'status':'PASS','feature_rows':248,
         'actual_feature_access_allowlist_verified':True,'feature_payload_has_no_outcome_fields':True,
         'forbidden_reads_denied_before_io':denied,'feature_sha256':sha(HERE/'page1_features.json'),
         'access':guard.evidence()})
    print('Feature isolation PASS: six protected inputs denied before I/O.')


if __name__=='__main__':main()
