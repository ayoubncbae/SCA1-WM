"""Lightweight exported artifact checks; no original model/data processing."""
from pathlib import Path
import hashlib,json,numpy as np
WEB=Path(__file__).resolve().parents[1]
def main():
    p=WEB/'public';m=json.loads((p/'model-manifest.json').read_text());b=(p/'assets/model-data.json').read_bytes();assert hashlib.sha256(b).hexdigest()==m['schemaSha256'];s=json.loads(b);assert s['modelId']==m['id'];assert m['neuralWeight']==s['neuralWeight']==.5;assert len(s['neural'])==3
    for name,digest in s['files'].items():assert hashlib.sha256((p/'assets'/name).read_bytes()).hexdigest()==digest
    assert len(m['genes'])==len(set(m['genes']))==2000;assert hashlib.sha256('\n'.join(m['genes']).encode()).hexdigest()==m['genePanelSha256']
    for i in range(14):
        r=json.loads((p/f'verified-predictions/observed-{i:02d}.json').read_text());assert all(e['age'] in m['measuredAges'] and e['nMice']==1 and len(e['meanLog'])==2000 for e in r['entries'])
    fixture=np.fromfile(WEB/'tests/fixtures/saved-primary-simulation.f32',dtype='<f4');assert fixture.size==504*4000 and np.isfinite(fixture).all()
    print('PASS: neural model identities, hashes, gene order,14 measured-only GT references,504 Python cases')
if __name__=='__main__':main()
