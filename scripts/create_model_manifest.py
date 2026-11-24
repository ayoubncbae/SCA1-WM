"""Bind browser artifacts to the exported neural checkpoint and panel."""
import json,hashlib
from pathlib import Path
WEB=Path(__file__).resolve().parents[1]
def bind():
    p=WEB/'public';m=json.loads((p/'model-manifest.json').read_text());s=json.loads((p/'assets/model-data.json').read_text());s['modelId']=m['id'];s['genePanelSha256']=m['genePanelSha256'];s['checkpointHashes']=[c['sha256'] for c in m['checkpointFiles']]
    b=json.dumps(s,separators=(',',':')).encode();(p/'assets/model-data.json').write_bytes(b);m['schemaSha256']=hashlib.sha256(b).hexdigest();(p/'model-manifest.json').write_text(json.dumps(m,separators=(',',':')),encoding='utf8');(p/'health.json').write_text(json.dumps(dict(status='ok',mode='static_browser_neural_inference',modelId=m['id'],neuralWeight=m['neuralWeight'])),encoding='utf8')
if __name__=='__main__':bind()
