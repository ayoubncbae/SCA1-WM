"""Read-only export of selected primaryV7; all writes remain in web01."""
import argparse,sys,json,hashlib,pickle,copy
from pathlib import Path
import numpy as np
import pandas as pd

WEB=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,separators=(',',':'),allow_nan=False),encoding='utf8')
def safe_records(t):return json.loads(t.to_json(orient='records'))
def main():
    a=argparse.ArgumentParser();a.add_argument('--project-root',type=Path,default=WEB.parent);args=a.parse_args();root=args.project_root.resolve();sys.path.insert(0,str(root))
    source=root/'outputs/v7_final';raw=source/'final_raw_data';public=WEB/'public';assets=public/'assets';ref=public/'verified-predictions';fixtures=WEB/'tests/fixtures'
    for p in [assets,ref,fixtures]:p.mkdir(parents=True,exist_ok=True)
    # User-requested active proposed neural model: frozen primary grouped_1,
    # selected internally with weight0.5; never force on the all-animal model.
    import torch
    from src.v7.core import Transition,prediction
    torch.set_num_threads(2)
    fold='grouped_1';selection=json.loads((source/'models'/fold/'SELECTION_LOCK.json').read_text());weight=selection['selected']['calibration']['shrink'];assert weight==.5
    pp=source/'models'/fold/'preprocessor.pkl'
    with pp.open('rb') as f:d=pickle.load(f)
    assert d.panel==2000 and d.config=={'kind':'kernel','width':3,'shrink':.25}
    meta=d.meta.iloc[d.ids].reset_index(drop=True);y=d.y[d.ids].astype('<f4');y.tofile(assets/'backbone.f32');enc=np.r_[d.pca.mean_,d.scale,d.pca.components_.ravel()].astype('<f4');enc.tofile(assets/'encoder.f32')
    types=meta.groupby('type_id').ctype.first().sort_index().tolist();genes=d.genes.tolist();programs=json.loads((raw/'PROGRAM_DEFINITIONS.json').read_text());allages=[5,9,12,15,18,21,24,27,30];measured=[5,12,18,24,30]
    checkpoints=[];models=[];neural=[]
    for s in [7,17,27]:
        p=source/f'models/{fold}/outer_s{s}/best.pt';checkpoints.append(dict(id=f'primary-v7-{fold}-seed-{s}',sha256=sha(p)));ck=torch.load(p,map_location='cpu',weights_only=False);model=Transition(**ck['config']);model.load_state_dict(ck['model']);model.eval();models.append(model);neural.append(dict(config=ck['config'],weights={k:v.cpu().numpy().tolist() for k,v in ck['model'].items()}))
    schema=dict(rowCount=len(meta),channels=4000,genes=2000,latent=d.dim,rows=[dict(type=int(r.type_id),genotype=r.genotype,age=int(r.age)) for r in meta.itertuples()],kernel=d.config,theta=[d.theta[i].tolist() for i in range(14)],libraries=[d.libraries[i].tolist() for i in range(14)],encoder=dict(meanOffset=0,scaleOffset=4000,basisOffset=4000+d.dim),files={'backbone.f32':sha(assets/'backbone.f32'),'encoder.f32':sha(assets/'encoder.f32')})
    schema['neural']=neural;schema['neuralWeight']=weight
    schema['sources']={}
    for ct in range(14):
        for geno in ['WT','SCA1']:
            j=d.meta.index[(d.meta.type_id==ct)&(d.meta.genotype==geno)][0];schema['sources'][f'{ct}:{geno}']=dict(latent=d.source_z[j].tolist(),tokens=d.source_tokens[j].tolist(),age=float(d.source_age[j]))
    js(assets/'model-data.json',schema)
    stats=np.load(root/'derived/v4/population_stats.npz');ix=pd.Index(stats['genes']).get_indexer(genes);assert np.all(ix>=0)
    for ct in range(14):
        entries=[]
        for geno in ['WT','SCA1']:
            for age in measured:
                ids=np.flatnonzero((d.meta.type_id==ct)&(d.meta.genotype==geno)&(d.meta.age==age)&d.meta.animal_id.isin(selection['fold']['test']));entries.append(dict(genotype=geno,age=age,nMice=len(ids),nNuclei=int(d.meta.iloc[ids].n_cells.sum()),meanLog=d.mean[ids].mean(0).tolist(),cp10k=d.cp[ids].mean(0).tolist()))
        js(ref/f'observed-{ct:02d}.json',dict(type=ct,entries=entries,role='observed_bounded_population_reference',scale='Equal mouse mean of bounded population statistics; not raw UMI sums'))
    # CPU references for the exported active ensemble, covering all nine ages.
    query=[]
    for ct in range(14):
        for geno in ['WT','SCA1']:
            for age in allages:query.append(dict(type_id=ct,ctype=types[ct],genotype=geno,age=age,animal_id='query'))
    qmeta=pd.DataFrame(query);qd=copy.copy(d);qd.meta=qmeta;qd.baseline=d.base(qmeta)[0];qd.source_z=np.stack([schema['sources'][f'{r.type_id}:{r.genotype}']['latent'] for r in qmeta.itertuples()]).astype('float32');qd.source_tokens=np.stack([schema['sources'][f'{r.type_id}:{r.genotype}']['tokens'] for r in qmeta.itertuples()]).astype('float32');qd.source_age=np.full(len(qmeta),5,dtype='float32');rows=[];pred=[]
    for route,steps in [('direct',1),('recursive',4)]:
        p=np.mean([prediction(m,qd,np.arange(len(qmeta)),weight,steps) for m in models],axis=0);pred.append(p)
        for r in qmeta.itertuples():rows.append(dict(type_id=int(r.type_id),genotype=r.genotype,age=int(r.age),route=route))
    np.concatenate(pred).astype('<f4').tofile(fixtures/'saved-primary-simulation.f32');js(fixtures/'saved-reference-index.json',rows)
    # Saved reference fixture is not an inference substitute. Every504 condition
    # is compared to actual live-browser numerical output in the test suite.
    js(public/'model-manifest.json',dict(id='sca1-wm-primary-v7-grouped-1-neural',title='SCA1-WM | Interactive Transcriptomic World Model',mode='live_browser_neural_inference',modelVersion='primary V7 · frozen grouped_1 neural ensemble',cellTypes=types,genes=genes,programs={k:dict(requested=v,present=[g for g in v if g in genes],missing=[g for g in v if g not in genes]) for k,v in programs.items()},measuredAges=measured,queriedAges=allages,sourceAges=[5],genotypes=['WT','SCA1'],neuralWeight=weight,checkpointFiles=checkpoints,preprocessorSha256=sha(pp),genePanelSha256=hashlib.sha256('\n'.join(genes).encode()).hexdigest(),biologicalUnits=dict(mice=30,trainingAndValidationMice=20,heldoutReferenceMice=10,cellTypes=14,genes=2000,measuredAges=5,genotypes=2),supportedRoutes=['direct','recursive'],unsupportedRoutes=['RNA re-entry','backward cycle','arbitrary source RNA','backward prediction'],sampling=dict(minNuclei=8,maxNuclei=64,defaultNuclei=32,distribution='conditional marginal negative binomial',depth='empirical training technical library distribution'),scope='Frozen grouped_1 animal-disjoint primary neural ensemble. Measured-age GT is held-out mice at ages seen during training, not future-age extrapolation. Intermediate ages lack GT. One held-out mouse/genotype/age limits biological inference.',sourceEncoding='Training-fitted residual PCA and earliest training population anchor; learned token encoder and neural state transition active, selected weight0.5',referenceTolerance=dict(maxAbsoluteMeanLog=0.0001,maxAbsoluteCP10K=0.05),redistribution='Derived mouse population model and author-provided results; owner-private demo. Data rights are not granted by the code license. Confirm data permission before public redistribution.'))
    metrics=pd.read_parquet(raw/'ALL_DISTRIBUTIONS.parquet');metrics=metrics[metrics.model=='v7_selected'];group=metrics.groupby(['cell_type','fold']).agg(NB_NLL=('count_NB_NLL','mean'),W1=('marginal_w1','mean'),MMD=('mmd2','mean'),zeroError=('zero_fraction_mae','mean'),varianceError=('variance_rmse','mean'),covarianceError=('full_covariance_rmse','mean')).reset_index();js(ref/'heldout-evaluation.json',dict(role='Separate adaptive internal held-out fold ensembles; NOT metrics for current all-animal simulation',records=safe_records(group)))
    selections=pd.read_parquet(raw/'MODEL_SELECTIONS.parquet');primary=pd.read_parquet(raw/'ANIMAL_PRIMARY_STATISTICS.parquet');js(ref/'model-evidence.json',dict(selections=safe_records(selections),statistics=safe_records(primary[primary.model=='v7_selected']),scope='Existing frozen adaptive internal evaluation; fold-specific models/panels distinct from deployed all-animal checkpoint'))
    atlas=pd.read_parquet(root/'SCA1_WM_ALL_RESULTS/01_NEW_AZ_ANALYSES/TRAIN_ONLY_UMAP_COORDINATES.parquet');rng=np.random.default_rng(97);keep=[]
    for _,ii in atlas.groupby(['source','cell_type'],observed=True).indices.items():keep.extend(rng.choice(ii,min(len(ii),160),replace=False))
    atlas=atlas.iloc[keep];cols=[c for c in ['cell_type','genotype','age','route','role','x','y','source'] if c in atlas];js(ref/'shared-atlas.json',dict(role='Stored shared training-observation PCA/UMAP projection; all-animal generated RNA is retrospective, not a new projection or held-out simulation',points=safe_records(atlas[cols])))
    reference={}
    for ct in range(14):
        for geno in ['WT','SCA1']:
            ids=d.sources[(ct,geno)];reference[f'{ct}:{geno}']=dict(age=float(d.meta.iloc[ids].age.min()),latent=d.source_z[ids[0]].tolist())
    js(fixtures/'source-latents.json',reference)
    # Original held-out predictions provide an independent export reproduction
    # check, in addition to the nine-age CPU fixture.
    saved=np.load(raw/fold/'predictions.npz');saved_meta=pd.read_csv(raw/fold/'population_manifest.csv',dtype={'animal_id':str});ids=np.flatnonzero(d.meta.animal_id.isin(selection['fold']['test']));cpu=np.mean([prediction(m,d,ids,weight) for m in models],axis=0);assert np.allclose(cpu,saved['v7_selected'],atol=2e-5);assert np.array_equal(saved['genes'],d.genes)
    saved['v7_selected'].astype('<f4').tofile(fixtures/'original-heldout.f32');js(fixtures/'original-heldout-index.json',safe_records(saved_meta[['type_id','genotype','age']]))
    (WEB/'docs').mkdir(exist_ok=True)
    js(WEB/'docs/EXPORT_AUDIT.json',dict(status='PASS',cellsTypes=14,genes=2000,referencePopulations=len(rows),checkpointLoaded=True,neuralWeight=weight,sourceGeneOrderVerified=True,noOriginalFilesWritten=True,originalHeldoutCPUMaxError=float(abs(cpu-saved['v7_selected']).max()),artifactHashes=schema['files']))
    import subprocess
    subprocess.run([sys.executable,str(WEB/'scripts/export_active_projection.py')],check=True)
    from create_model_manifest import bind
    bind()
    print('Exported exact proposed neural ensemble, encoder, transitions, decoder and504 CPU references')
if __name__=='__main__':main()
