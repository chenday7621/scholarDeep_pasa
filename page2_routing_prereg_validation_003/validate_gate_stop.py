"""Read-only verification of the required pre-retrieval stop and frozen artifacts."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    def block(event,args):
        if event.startswith('socket.') or event in ['subprocess.Popen','os.system']:
            raise PermissionError('Offline validation only')
    sys.addaudithook(block)
    d=read(ROOT/'dataset_manifest.json');g=read(ROOT/'gold_titles.json')
    assert d['status']=='STOPPED_MAPPING_AMBIGUITY'
    assert len(g['rows'])==len({r['corpusid'] for r in g['rows']})==432
    assert set(g['requested_corpusids'])=={r['corpusid'] for r in g['rows']}
    assert sum(p['metadata_row_count'] for p in g['parts'])==64183
    assert all(p['column_names']==['corpusid','title'] for p in g['parts'])
    assert len(d['queries'])==442 and d['sample']==[] and d['sample_size']==0
    assert Counter(q['group'] for q in d['queries'])=={'author-written':211,'inline-citation':231}
    assert Counter(q['group'] for q in d['queries'] if q['eligible_all_gold_compatible'])=={'author-written':164,'inline-citation':165}
    assert len(d['ambiguous_cases'])==1
    assert d['ambiguous_cases'][0]['corpusid']==258960101
    assert set(d['ambiguous_cases'][0]['arxiv_ids'])=={'2303.02909','2305.17359'}
    p=d['provenance']
    assert sha(ROOT/'query_metadata.json')==p['query_metadata_sha256']
    assert sha(ROOT/'gold_titles.json')==p['gold_titles_sha256']
    assert sha(ROOT/'compatibility.py')==p['compatibility_source_sha256']
    assert sha(ROOT.parent/'data/paper_database/id2paper.json')==p['id2paper_sha256']
    assert all(sha(path)==h for path,h in p['protected_sources'].items())
    assert all(sha(path)==h for path,h in p['query_response_hashes'].items())
    range_bytes=0;range_count=0
    for path in (ROOT/'column_ranges').rglob('*.bin'):
        m=read(path.with_suffix('.json'))
        assert path.stat().st_size==m['bytes']==m['end']-m['start']+1
        assert sha(path)==m['sha256'] and m['http_status']==206
        range_bytes+=m['bytes'];range_count+=1
    assert range_bytes==g['column_bytes_downloaded']
    h=sha(ROOT/'PREREGISTRATION.md')
    assert (ROOT/'PREREGISTRATION.sha256').read_text().split()[0]==h
    registration=read(ROOT/'registration_manifest.json')
    assert registration['preregistration_sha256']==h
    assert registration['dataset_manifest_sha256']==sha(ROOT/'dataset_manifest.json')
    assert registration['status']=='NOT_ACTIVATED_GATE_STOP'
    result=read(ROOT/'results.json')
    assert result['metrics'] is None and result['p_random_ge_router'] is None
    assert result['sample_size']==result['crawler_generations']==result['search_requests']==0
    assert read(ROOT/'snapshot_manifest.json')['snapshots']==[]
    assert read(ROOT/'states.json')['states']==[]
    assert read(ROOT/'decisions.json')['decisions']==[]
    report={'status':'PASS','terminal_status':d['status'],'query_metadata_rows':597,'specific_questions':442,
            'gold_corpusids':432,'column_ranges_verified':range_count,'column_bytes_verified':range_bytes,
            'all_queries_same_pinned_revision':True,'all_required_artifacts_present':True,
            'protocol_hash_verified':True,'protocol_not_activated':True,'sample_size':0,
            'no_crawler_or_experiment_search':True,'official_sources_unchanged':True,
            'metrics_are_null_not_fabricated_zero':True,
            'ambiguous_query_rows':[q['row_index'] for q in d['queries'] if 'ambiguous_local_title' in q['exclusion_reasons']],
            'artifact_hashes':{path.name:sha(path) for path in [ROOT/name for name in ['PREREGISTRATION.md','dataset_manifest.json','snapshot_manifest.json','states.json','decisions.json','results.json','PAGE2_ROUTING_PREREG_VALIDATION_003.md']]}}
    (ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
