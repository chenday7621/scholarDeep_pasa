"""Read only corpusid/title column chunks from pinned public Parquet files."""
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))
import pyarrow.parquet as pq

def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

class RangeFile(io.RawIOBase):
    def __init__(self,url,size,name):
        self.url=url;self.size=size;self.position=0;self.name=name
        self.folder=ROOT/'column_ranges'/name
        self.folder.mkdir(parents=True,exist_ok=True)
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.position
    def seek(self,offset,whence=0):
        self.position=offset if whence==0 else self.position+offset if whence==1 else self.size+offset
        if self.position<0:raise ValueError('negative seek')
        return self.position
    def read(self,n=-1):
        if n<0:n=self.size-self.position
        n=min(n,self.size-self.position)
        if n<=0:return b''
        assert n<=8_000_000, f'Refuse unexpectedly large read: {n}'
        start,end=self.position,self.position+n-1
        path=self.folder/f'{start}-{end}.bin'
        meta=path.with_suffix('.json')
        if path.exists():
            raw=path.read_bytes();m=json.loads(meta.read_text())
            assert len(raw)==n and hashlib.sha256(raw).hexdigest()==m['sha256']
        else:
            request=urllib.request.Request(self.url,headers={'Range':f'bytes={start}-{end}','User-Agent':'PaSa-LitSearch-column-metadata'})
            with urllib.request.urlopen(request,timeout=60) as response:
                assert response.status==206, 'Server ignored range; refusing full corpus download'
                content_range=response.headers.get('Content-Range','')
                assert content_range==f'bytes {start}-{end}/{self.size}',content_range
                raw=response.read(n+1)
                assert len(raw)==n
            path.write_bytes(raw)
            save(meta,{'url':self.url,'start':start,'end':end,'bytes':n,'sha256':hashlib.sha256(raw).hexdigest(),
                       'retrieved_utc':datetime.now(timezone.utc).isoformat(),'http_status':206})
            print(self.name,'range',start,end,'bytes',n,flush=True)
        self.position+=n
        return raw
    def readinto(self,b):
        data=self.read(len(b));b[:len(data)]=data;return len(data)

def main():
    query=json.loads((ROOT/'query_metadata.json').read_text())
    revision=query['revision']
    url=f'https://huggingface.co/api/datasets/princeton-nlp/LitSearch/tree/{revision}/corpus_clean'
    listing_path=ROOT/'metadata_cache/corpus_parquet_listing.json'
    if listing_path.exists():listing=json.loads(listing_path.read_text())['data']
    else:
        with urllib.request.urlopen(url,timeout=60) as response:raw=response.read()
        listing=json.loads(raw)
        save(listing_path,{'url':url,'data':listing,'raw_sha256':hashlib.sha256(raw).hexdigest(),'bytes_received':len(raw)})
    files=sorted([r for r in listing if r['path'].endswith('.parquet')],key=lambda x:x['path'])
    assert len(files)==6
    ids=set(json.loads((ROOT/'gold_metadata_request_plan.json').read_text())['gold_corpusids'])
    collected=[];parts=[]
    for f in files:
        name=Path(f['path']).stem
        output=ROOT/(name+'_gold_columns.json')
        if output.exists():part=json.loads(output.read_text())
        else:
            source=f"https://huggingface.co/datasets/princeton-nlp/LitSearch/resolve/{revision}/{f['path']}"
            reader=RangeFile(source,f['size'],name)
            parquet=pq.ParquetFile(reader,pre_buffer=False)
            assert {'corpusid','title'} <= set(parquet.schema.names),parquet.schema.names
            table=parquet.read(columns=['corpusid','title'],use_threads=False)
            rows=[r for r in table.to_pylist() if r['corpusid'] in ids]
            part={'file':f['path'],'revision':revision,'file_bytes':f['size'],'column_names':table.column_names,
                  'metadata_row_count':table.num_rows,'rows':rows}
            save(output,part)
        assert part['revision']==revision
        collected+=part['rows'];parts.append({k:v for k,v in part.items() if k!='rows'})
        print(name,'gold rows',len(part['rows']),flush=True)
    save(ROOT/'gold_titles.json',{'dataset_revision':revision,'requested_corpusids':sorted(ids),'rows':collected,
                                 'extraction':'HTTP Range parquet footer + corpusid/title columns only','parts':parts,
                                 'column_bytes_downloaded':sum(p.stat().st_size for p in (ROOT/'column_ranges').rglob('*.bin'))})
    print('Gold corpusid/title extraction complete:',len(collected))

if __name__=='__main__':main()
