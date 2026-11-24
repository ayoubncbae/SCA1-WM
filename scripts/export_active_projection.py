"""Shared existing residual PCA projection for the SAME deployed neural ensemble."""
import sys,pickle,json
from pathlib import Path
import numpy as np
import pandas as pd
WEB=Path(__file__).resolve().parents[1];ROOT=WEB.parent;sys.path.insert(0,str(ROOT))
from src.v7.evaluate import sample_counts
def main():
    with (ROOT/'outputs/v7_final/models/grouped_1/preprocessor.pkl').open('rb') as f:d=pickle.load(f)
    obs=pd.read_csv(ROOT/'derived/v4/cells.csv',index_col=0,dtype={'animal_id':str});raw=np.load(ROOT/'derived/v4/counts.npy',mmap_mode='r');lib=np.load(ROOT/'derived/v4/library.npy');rng=np.random.default_rng(709);points=[]
    for i,r in enumerate(d.meta.itertuples()):
        ids=np.flatnonzero((obs.animal_id==r.animal_id)&(obs.ctype==r.ctype));ids=rng.choice(ids,min(8,len(ids)),replace=False);x=np.log1p(np.asarray(raw[ids][:,d.ix])/lib[ids,None]*10000);z=(np.c_[x,x]-d.baseline[i]-d.pca.mean_)@d.pca.components_[:2].T/d.scale[:2]
        for a,b in z:points.append(dict(cell_type=r.ctype,genotype=r.genotype,age=int(r.age),source='observed',role='training_reference' if d.train[i] else 'heldout_reference',x=float(a),y=float(b)))
    index=json.loads((WEB/'tests/fixtures/saved-reference-index.json').read_text());pred=np.fromfile(WEB/'tests/fixtures/saved-primary-simulation.f32',dtype='<f4').reshape(-1,4000)
    for j,r in enumerate(index):
        if r['route']!='direct':continue
        ct=r['type_id'];x,ll=sample_counts(np.expm1(pred[j,2000:]).clip(0,1e6),d,ct,rng,8);log=np.log1p(x/ll[:,None]*10000);target=pd.DataFrame([dict(type_id=ct,genotype=r['genotype'],age=r['age'])]);base=d.base(target)[0][0];z=(np.c_[log,log]-base-d.pca.mean_)@d.pca.components_[:2].T/d.scale[:2]
        for a,b in z:points.append(dict(cell_type=d.meta[d.meta.type_id==ct].ctype.iloc[0],genotype=r['genotype'],age=r['age'],source='neural_generated',role='same_frozen_neural_checkpoint_reference',x=float(a),y=float(b)))
    p=WEB/'public/verified-predictions/shared-atlas.json';p.write_text(json.dumps(dict(modelId='sca1-wm-primary-v7-grouped-1-neural',projection='First two training-fitted residual PCA coordinates; no new UMAP fitting',role='Stored same-checkpoint reference projection, not a new embedding of each live RNA sample',points=points),separators=(',',':')),encoding='utf8');print('Same-checkpoint projection exported',len(points),'points')
if __name__=='__main__':main()
