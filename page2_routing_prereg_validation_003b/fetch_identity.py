"""Fetch only the two official arXiv identity records; never paper Search."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / 'page2_routing_prereg_validation_003' / 'identity_evidence'

def main():
    OUT.mkdir(exist_ok=True)
    for aid in ('2305.17359', '2303.02909'):
        target = OUT / f'{aid}.html'
        if target.exists():
            assert (OUT / f'{aid}.json').exists()
            continue
        url = f'https://arxiv.org/abs/{aid}'
        started = datetime.now(timezone.utc).isoformat()
        request = urllib.request.Request(url, headers={'User-Agent': 'PaSa static identity audit'})
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
            metadata = {'arxiv_id': aid, 'source_url': url, 'final_url': response.url,
                        'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
                        'http_status': response.status, 'headers': dict(response.headers),
                        'raw_bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        assert metadata['http_status'] == 200
        with target.open('xb') as f:
            f.write(raw)
        with (OUT / f'{aid}.json').open('x') as f:
            json.dump(metadata, f, indent=2)
            f.write('\n')
        print(aid, metadata['sha256'], flush=True)

if __name__ == '__main__':
    main()
