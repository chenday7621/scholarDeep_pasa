"""Public dataset metadata only. No Crawler, Serper, or experiment Search code."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parent
CACHE=ROOT/'metadata_cache'
DATASET='princeton-nlp/LitSearch'

def save(p,d):
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def fetch(name,url):
    assert urllib.parse.urlsplit(url).hostname in {'huggingface.co','datasets-server.huggingface.co','raw.githubusercontent.com','api.github.com'}
    CACHE.mkdir(parents=True,exist_ok=True)
    p=CACHE/(name+'.json')
    if p.exists():
        r=json.loads(p.read_text())
        assert r['url']==url
        return r['data']
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PaSa-LitSearch-metadata-compatibility'}),timeout=60) as response:
        raw=response.read(30_000_001)
        assert len(raw)<=30_000_000,'Unexpectedly large response; do not fetch full corpus'
        status=response.status
        content_type=response.headers.get('Content-Type')
        revision=response.headers.get('X-Revision') or response.headers.get('X-Repo-Commit')
    try:data=json.loads(raw)
    except json.JSONDecodeError:data=raw.decode()
    save(p,{'url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'http_status':status,
            'bytes_received':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'content_type':content_type,
            'revision_header':revision,'data':data})
    print(name,status,len(raw),flush=True)
    return data

def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['queries','gold','sources','gold_probe']);args=parser.parse_args()
    repo=fetch('hf_dataset_info','https://huggingface.co/api/datasets/'+DATASET)
    if args.stage=='queries':
        rows=[]
        for offset in range(0,597,100):
            url='https://datasets-server.huggingface.co/rows?'+urllib.parse.urlencode({'dataset':DATASET,'config':'query','split':'full','offset':offset,'length':100})
            response=fetch(f'query_rows_{offset:03d}',url)
            assert response['num_rows_total']==597
            rows+=response['rows']
        assert len(rows)==597 and len({r['row_idx'] for r in rows})==597
        save(ROOT/'query_metadata.json',{'dataset':DATASET,'revision':repo['sha'],'rows':rows})
        from collections import Counter
        print('query_set/specificity',Counter((r['row']['query_set'],r['row']['specificity']) for r in rows))
    elif args.stage=='sources':
        tree=fetch('github_tree','https://api.github.com/repos/princeton-nlp/LitSearch/git/trees/main?recursive=1')
        print([r['path'] for r in tree['tree'] if r['path'].endswith('.py')])
    elif args.stage=='gold_probe':
        plan=json.loads((ROOT/'gold_metadata_request_plan.json').read_text())
        cid=plan['gold_corpusids'][0]
        url='https://datasets-server.huggingface.co/filter?'+urllib.parse.urlencode({'dataset':DATASET,'config':'corpus_clean','split':'full','where':f'"corpusid"={cid}','offset':0,'length':1})
        data=fetch('gold_single_probe',url)
        print('Matching rows:',data.get('num_rows_total'))
    else:
        # Definition of specific must be confirmed from upstream code before creating this plan.
        plan=json.loads((ROOT/'gold_metadata_request_plan.json').read_text())
        assert plan['static_metadata_only'] and plan['specificity_value_verified']
        ids=plan['gold_corpusids']
        collected=[]
        for offset in range(0,len(ids),25):
            batch=ids[offset:offset+25]
            where=' OR '.join(f'"corpusid"={int(cid)}' for cid in batch)
            url='https://datasets-server.huggingface.co/filter?'+urllib.parse.urlencode({'dataset':DATASET,'config':'corpus_clean','split':'full','where':where,'offset':0,'length':100})
            data=fetch(f'gold_batch_{offset:04d}',url)
            assert data.get('partial') is False
            assert data['num_rows_total']==len(data['rows'])
            for r in data['rows']:
                assert r['row']['corpusid'] in batch
                assert 'title' not in r.get('truncated_cells',[])
                collected.append({'corpusid':r['row']['corpusid'],'title':r['row']['title'],'source_row_index':r['row_idx'],'cache':f'metadata_cache/gold_batch_{offset:04d}.json'})
        save(ROOT/'gold_titles.json',{'dataset_revision':repo['sha'],'requested_corpusids':ids,'rows':collected,
                                     'note':'Server filter returns complete matching rows; downstream projection uses only corpusid/title. No full corpus download.'})

if __name__=='__main__':main()
