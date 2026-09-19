"""Static metadata gate only. No Search, model generation, or outcome inputs."""
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
import sys
import zipfile

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
SEED=20260917

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def now():return datetime.now(timezone.utc).isoformat()

def main():
    assert not (ROOT/'PREREGISTRATION.md').exists(),'Frozen registration exists; do not overwrite its dataset manifest.'
    # Network and execution are rejected even if this script is run outside sandbox.
    def offline(event,args):
        if event.startswith('socket.') or event in ['subprocess.Popen','os.system']:
            raise PermissionError('Static compatibility only')
        if event=='import' and args[0].split('.')[0] in ['torch','transformers','requests','arxiv','openai']:
            raise PermissionError('No model/network imports in compatibility')
    sys.addaudithook(offline)
    protected=[REPO/p for p in ['paper_agent.py','utils.py','models.py','metrics.py','agent_prompt.json','run_paper_agent.py']]
    before={str(p):sha(p) for p in protected}
    qdata=read(ROOT/'query_metadata.json'); gold=read(ROOT/'gold_titles.json')
    assert qdata['revision']==gold['dataset_revision']
    query_responses=sorted((ROOT/'metadata_cache').glob('query_rows_*.json'))
    assert len(query_responses)==6
    assert all(read(p)['revision_header']==qdata['revision'] for p in query_responses)
    assert all(not r['truncated_cells'] for r in qdata['rows'])
    source=(REPO/'utils.py').read_text();tree=ast.parse(source)
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['keep_letters','_build_local_title_index']]
    assert len(functions)==2
    idpath=REPO/'data/paper_database/id2paper.json'
    zpath=REPO/'data/paper_database/cs_paper_2nd.zip'
    ids=read(idpath)
    z=zipfile.ZipFile(zpath)
    names=set(z.namelist())
    scope={'id2paper':ids,'_paper_db_names':names}
    exec(compile(ast.Module(body=functions,type_ignores=[]),'utils pure functions','exec'),scope)
    norm=scope['keep_letters'];index,ambiguous_keys=scope['_build_local_title_index']()
    all_local=defaultdict(list)
    for aid,title in ids.items():all_local[norm(title)].append(aid)
    by_corpus=defaultdict(list)
    for r in gold['rows']:by_corpus[int(r['corpusid'])].append(r)
    mappings=[];ambiguities=[]
    for cid in gold['requested_corpusids']:
        rows=by_corpus[cid]
        m={'corpusid':cid,'corpus_rows':rows,'status':None,'arxiv_id':None}
        if len(rows)!=1:
            m['status']='missing_corpus_metadata' if not rows else 'ambiguous_corpusid_rows'
            ambiguities.append({'type':m['status'],'corpusid':cid,'rows':rows})
        else:
            title=rows[0]['title'];key=norm(title)
            m.update(title=title,normalized_title=key,local_candidate_ids=all_local.get(key,[]))
            if key in ambiguous_keys:
                m['status']='ambiguous_local_title'
                ambiguities.append({'type':m['status'],'corpusid':cid,'title':title,'arxiv_ids':all_local[key]})
            elif not key:
                m['status']='empty_normalized_title'
            elif key not in index:
                m['status']='local_title_miss' if key not in all_local else 'local_zip_record_missing'
            else:
                aid=index[key].split('v')[0]
                m['arxiv_id']=aid
                if not re.fullmatch(r'\d{4}\.\d+',aid):m['status']='arxiv_id_not_supported_by_native_parser'
                else:
                    raw=z.read(key);paper=json.loads(raw)
                    m['local_record_sha256']=hashlib.sha256(raw).hexdigest()
                    m['local_record_title']=paper['title']
                    m['status']='compatible' if norm(paper['title'])==key else 'local_record_title_normalization_mismatch'
        mappings.append(m)
    reverse=defaultdict(list)
    for m in mappings:
        if m['status']=='compatible':reverse[m['arxiv_id']].append(m['corpusid'])
    for aid,cids in reverse.items():
        if len(set(cids))>1:
            ambiguities.append({'type':'multiple_gold_corpusids_to_same_arxiv_id','arxiv_id':aid,'corpusids':cids})
    mapped={m['corpusid']:m for m in mappings}
    detailed=[];pools={'author-written':[],'inline-citation':[]};counts=defaultdict(Counter)
    for r in qdata['rows']:
        row=r['row']
        if row['specificity']!=1:continue
        group='author-written' if row['query_set'] in ['manual_acl','manual_iclr'] else 'inline-citation' if row['query_set'] in ['inline_acl','inline_nonacl'] else None
        assert group
        cids=row['corpusids']
        reasons=sorted({mapped[c]['status'] for c in cids if mapped[c]['status']!='compatible'})
        if not cids:reasons.append('empty_gold')
        eligible=not reasons
        entry={'row_index':r['row_idx'],'group':group,'query_set':row['query_set'],'specificity':row['specificity'],
               'question':row['query'],'gold_corpusids':cids,'eligible_all_gold_compatible':eligible,
               'exclusion_reasons':reasons,'gold_mappings':[mapped[c] for c in cids]}
        detailed.append(entry)
        counts[group]['specific_total']+=1
        counts[group]['eligible' if eligible else 'ineligible']+=1
        for reason in reasons:counts[group][reason]+=1
        if eligible:pools[group].append(entry)
    insufficient={g:len(p) for g,p in pools.items() if len(p)<25}
    stop=bool(ambiguities or insufficient)
    status='STOPPED_MAPPING_AMBIGUITY' if ambiguities else 'STOPPED_INSUFFICIENT_COMPATIBLE_SAMPLE' if insufficient else 'COMPATIBILITY_PASSED'
    selected=[]
    if not stop:
        rng=random.Random(SEED)
        for group in ['author-written','inline-citation']:
            selected.extend(rng.sample(sorted(pools[group],key=lambda r:r['row_index']),25))
    provenance={'query_metadata_sha256':sha(ROOT/'query_metadata.json'),'gold_titles_sha256':sha(ROOT/'gold_titles.json'),
                'id2paper_sha256':sha(idpath),'utils_sha256':sha(REPO/'utils.py'),
                'zip_directory_digest':hashlib.sha256('\n'.join(sorted(names)).encode()).hexdigest(),
                'zip_file_bytes':zpath.stat().st_size,'zip_file_mtime_ns':zpath.stat().st_mtime_ns,
                'compatibility_source_sha256':sha(__file__),'protected_sources':before,
                'query_response_hashes':{str(p):sha(p) for p in query_responses},
                'all_query_response_revision_headers_match':True}
    result={'experiment':'PAGE2_ROUTING_PREREG_VALIDATION_003','status':status,'created_utc':now(),
            'dataset':'princeton-nlp/LitSearch','dataset_revision':qdata['revision'],
            'eligibility_rule':'specificity=1; all annotated gold corpusids must map uniquely by unchanged keep_letters/local index to a native-parser-compatible arXiv ID with matching local ZIP title. No gold dropping, fuzzy matching, alias repair, quality filter or retrieval outcomes.',
            'ambiguity_rule':'Any unresolved corpusid/title/arXiv identity ambiguity in compatibility audit triggers stop before sampling/generation/Search, as user requested.',
            'group_counts':dict(counts),'gold_mapping_counts':dict(Counter(m['status'] for m in mappings)),
            'gold_corpusids':len(mappings),'ambiguous_cases':ambiguities,'insufficient_groups':insufficient,
            'local_index_size':len(index),'local_ambiguous_title_count':len(ambiguous_keys),
            'sample_seed':SEED,'sample_size':len(selected),'sample':selected,
            'queries':detailed,'gold_mappings':mappings,'provenance':provenance,
            'crawler_generations':0,'serper_search_requests':0,'page1_requests':0,'page2_requests':0}
    assert all(sha(p)==h for p,h in before.items())
    save(ROOT/'dataset_manifest.json',result)
    save(ROOT/'compatibility_validation.json',{'status':'PASS','official_source_files_unchanged':True,'static_metadata_only':True,
                                            'question_count':len(detailed),'specificity_counts_match_paper':dict(Counter(r['group'] for r in detailed))=={'author-written':211,'inline-citation':231},
                                            'gate_status':status,'sample_size':len(selected)})
    print(json.dumps({'status':status,'group_counts':dict(counts),'gold_mapping_counts':result['gold_mapping_counts'],
                      'ambiguities':ambiguities,'sample_size':len(selected)},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
