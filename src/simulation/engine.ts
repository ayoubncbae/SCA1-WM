import type {Model,Manifest,Schema,RunConfig,RunResult,State,Genotype,NeuralModel} from '../types';
export const asset=(p:string)=>`${import.meta.env.BASE_URL}${p}`;
export async function loadModel(base=import.meta.env.BASE_URL):Promise<Model>{
 const [manifest,schemaBytes]=await Promise.all([fetch(base+'model-manifest.json').then(check).then(r=>r.json()),fetch(base+'assets/model-data.json').then(check).then(r=>r.arrayBuffer())]) as [Manifest,ArrayBuffer];
 const schemaHash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',schemaBytes))).map(x=>x.toString(16).padStart(2,'0')).join('');
 if(schemaHash!==manifest.schemaSha256)throw Error('Neural artifact integrity mismatch');
 const schema=JSON.parse(new TextDecoder().decode(schemaBytes)) as Schema;
 if(schema.modelId!==manifest.id||schema.genePanelSha256!==manifest.genePanelSha256||JSON.stringify(schema.checkpointHashes)!==JSON.stringify(manifest.checkpointFiles.map(c=>c.sha256)))throw Error('Checkpoint or evaluation protocol mismatch');
 const panelHash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(manifest.genes.join('\n'))))).map(x=>x.toString(16).padStart(2,'0')).join('');if(panelHash!==manifest.genePanelSha256)throw Error('Gene order mismatch');
 const buffers=await Promise.all(['backbone.f32','encoder.f32'].map(n=>fetch(base+'assets/'+n).then(check).then(r=>r.arrayBuffer())));
 for(let i=0;i<buffers.length;i++){const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',buffers[i]))).map(x=>x.toString(16).padStart(2,'0')).join('');if(hash!==schema.files[i?'encoder.f32':'backbone.f32'])throw Error('Model integrity check failed');}
 if(manifest.neuralWeight!==.5||schema.neural.length!==3||schema.channels!==4000||manifest.genes.length!==2000)throw Error('Unsupported neural model export');
 return {manifest,schema,training:new Float32Array(buffers[0]),encoder:new Float32Array(buffers[1])};
}
function check(r:Response){if(!r.ok)throw Error(`Asset unavailable (${r.status})`);return r;}
export function validate(c:RunConfig,m:Manifest){
 if(!Number.isInteger(c.type)||c.type<0||c.type>=14)throw Error('Choose one of the14 supported cell types');
 if(!['WT','SCA1'].includes(c.genotype))throw Error('Unsupported genotype');
 if(c.sourceAge!==5)throw Error('Only the verified week5 source anchor is supported');
 if(!m.queriedAges.includes(c.targetAge)||c.targetAge<c.sourceAge)throw Error('Unsupported target age');
 if(!['direct','recursive'].includes(c.route))throw Error('Unsupported route: RNA re-entry and backward cycles are not implemented');
 if(!Number.isInteger(c.nuclei)||c.nuclei<8||c.nuclei>64)throw Error('Generate8–64 nuclei');
 if(!Number.isInteger(c.seed)||c.seed<0||c.seed>2147483647)throw Error('Seed must be an integer between0 and2147483647');
 if(c.steps.some((a,i)=>!m.queriedAges.includes(a)||a<=5||a>=c.targetAge||(i>0&&a<=c.steps[i-1])))throw Error('Intermediate ages must be supported, strictly increasing and inside the interval');
}
export function backbone(m:Model,type:number,g:Genotype,age:number):number[]{
 const {schema:s,training:y}=m;const ids=s.rows.map((r,i)=>({r,i})).filter(x=>x.r.type===type);
 const w=ids.map(x=>Math.exp(-.5*((x.r.age-age)/s.kernel.width)**2));const total=w.reduce((a,b)=>a+b,0);const same=w.reduce((a,b,i)=>a+(ids[i].r.genotype===g?b:0),0);const p=new Float64Array(s.channels);
 ids.forEach((x,i)=>{const weight=(1-s.kernel.shrink)*w[i]/total+(x.r.genotype===g?s.kernel.shrink*w[i]/same:0);const offset=x.i*s.channels;for(let j=0;j<s.channels;j++)p[j]+=weight*y[offset+j];});
 return Array.from(p,x=>Math.max(x,0));
}
export function encodeSource(m:Model,type:number,g:Genotype):number[]{
 const s=m.schema;const ids=s.rows.map((r,i)=>({r,i})).filter(x=>x.r.type===type&&x.r.genotype===g&&x.r.age===5);const base=backbone(m,type,g,5);const a=new Float64Array(s.channels);
 ids.forEach(x=>{for(let j=0;j<s.channels;j++)a[j]+=m.training[x.i*s.channels+j]/ids.length;});
 const result=[];for(let k=0;k<s.latent;k++){let z=0;for(let j=0;j<s.channels;j++)z+=(a[j]-base[j]-m.encoder[j])*m.encoder[s.encoder.basisOffset+k*s.channels+j];result.push(z/m.encoder[s.encoder.scaleOffset+k]);}return result;
}
function linear(x:number[],w:number[][],b:number[]){return w.map((row,j)=>{let v=b[j];for(let i=0;i<x.length;i++)v+=row[i]*x[i];return v;});}
const silu=(v:number)=>v/(1+Math.exp(-v));
export function transition(nn:NeuralModel,state:number[],tokens:number[][],type:number,g:Genotype,from:number,to:number,steps=1):number[]{
 const w=nn.weights,d=state.length;const ctx=new Array(d).fill(0);
 for(const token of tokens){const h=linear(token,w['token_encoder.0.weight'] as number[][],w['token_encoder.0.bias'] as number[]).map(silu);const out=linear(h,w['token_encoder.2.weight'] as number[][],w['token_encoder.2.bias'] as number[]);for(let j=0;j<d;j++)ctx[j]+=out[j]/tokens.length;}
 const h=(to-from)/25/steps,delta=(to-from)/25,t0=(from-5)/25,embed=(w['type_embed.weight'] as number[][])[type],decay=w.decay as number[];let s=[...state];
 for(let k=0;k<steps;k++){let hidden=[...s,...ctx,...embed,g==='SCA1'?1:0,t0+(k+.5)*h,h,delta];for(let l=0;l<=nn.config.depth;l++){hidden=linear(hidden,w[`velocity.${l*2}.weight`] as number[][],w[`velocity.${l*2}.bias`] as number[]);if(l<nn.config.depth)hidden=hidden.map(silu);}s=s.map((z,j)=>Math.exp(-Math.log1p(Math.exp(decay[j]))*Math.abs(h))*z+h*2*Math.tanh(hidden[j]/2));}return s;
}
function decode(m:Model,z:number[]){const {schema:s,encoder:e}=m;const out=Array.from(e.slice(0,s.channels));for(let j=0;j<s.channels;j++){let x=out[j];for(let k=0;k<s.latent;k++)x+=z[k]*e[s.encoder.scaleOffset+k]*e[s.encoder.basisOffset+k*s.channels+j];out[j]=x;}return out;}
export function predict(m:Model,type:number,g:Genotype,age:number,route:'direct'|'recursive'='direct'):number[]{
 const base=backbone(m,type,g,age),src=m.schema.sources[`${type}:${g}`],encoded=encodeSource(m,type,g),states=m.schema.neural.map(nn=>transition(nn,encoded,src.tokens,type,g,5,age,route==='direct'?1:4));const out=new Array(4000).fill(0);
 for(const state of states){const delta=decode(m,state);for(let j=0;j<4000;j++)out[j]+=Math.max(0,base[j]+m.manifest.neuralWeight*delta[j])/states.length;}return out;
}
export function rng(seed:number){let a=seed>>>0;return()=>{a+=0x6D2B79F5;let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};}
function normal(r:()=>number){return Math.sqrt(-2*Math.log(Math.max(r(),1e-15)))*Math.cos(2*Math.PI*r());}
function gamma(shape:number,r:()=>number):number{if(shape<1)return gamma(shape+1,r)*Math.pow(Math.max(r(),1e-15),1/shape);const d=shape-1/3,c=1/Math.sqrt(9*d);for(;;){const x=normal(r);let v=1+c*x;if(v<=0)continue;v=v*v*v;const u=r();if(u<1-.0331*x**4||Math.log(u)<.5*x*x+d*(1-v+Math.log(v)))return d*v;}}
function logGamma(z:number):number{const coef=[676.5203681218851,-1259.1392167224028,771.32342877765313,-176.61502916214059,12.507343278686905,-.13857109526572012,9.9843695780195716e-6,1.5056327351493116e-7];if(z<.5)return Math.log(Math.PI)-Math.log(Math.sin(Math.PI*z))-logGamma(1-z);z--;let x=.99999999999980993;coef.forEach((c,i)=>x+=c/(z+i+1));const t=z+7.5;return .5*Math.log(2*Math.PI)+(z+.5)*Math.log(t)-t+Math.log(x);}
function poisson(mu:number,r:()=>number):number{
 if(mu<=0)return 0;if(mu<30){const limit=Math.exp(-mu);let k=0,p=1;do{k++;p*=r();}while(p>limit);return k-1;}
 const b=.931+2.53*Math.sqrt(mu),a=-.059+.02483*b,inv=1.1239+1.1328/(b-3.4),vr=.9277-3.6224/(b-2);
 for(;;){const u=r()-.5,v=r(),us=.5-Math.abs(u),k=Math.floor((2*a/us+b)*u+mu+.43);if(us>=.07&&v<=vr&&k>=0)return k;if(k<0||(us<.013&&v>us))continue;if(Math.log(v*inv/(a/(us*us)+b))<=-mu+k*Math.log(mu)-logGamma(k+1))return k;}
}
export function sample(m:Model,type:number,cp:number[],n:number,seed:number){const r=rng(seed),libs=m.schema.libraries[type];const libraries=Array.from({length:n},()=>libs[Math.floor(r()*libs.length)]);const counts=libraries.map(l=>cp.map((p,j)=>{const theta=m.schema.theta[type][j],mu=Math.max(p,0)*l/10000;const lambda=gamma(theta,r)*mu/theta;return poisson(Math.min(lambda,1e7),r);}));return {counts,libraries};}
export function execute(m:Model,c:RunConfig,onStage?:(s:string)=>void):RunResult{
 validate(c,m.manifest);const started=performance.now(),stages:string[]=[];const stage=(s:string)=>{stages.push(s);onStage?.(s);};stage('Configuration and artifact integrity verified');const sourceLatent=encodeSource(m,c.type,c.genotype);stage('Training-source residual PCA state encoded');
 const ages=[5,...c.steps,...(c.targetAge===5?[]:[c.targetAge])];const states:State[]=[];const latent:Record<string,number[][]>={};for(const g of ['WT','SCA1'] as Genotype[]){const encoded=encodeSource(m,c.type,g);latent[g]=m.schema.neural.map(()=>[...encoded]);}let previous=5;
 for(const age of ages){for(const genotype of ['WT','SCA1'] as Genotype[]){let y:number[];
  if(c.route==='direct')y=predict(m,c.type,genotype,age,'direct');else{const src=m.schema.sources[`${c.type}:${genotype}`],base=backbone(m,c.type,genotype,age);const values=m.schema.neural.map((nn,k)=>{latent[genotype][k]=transition(nn,latent[genotype][k],src.tokens,c.type,genotype,previous,age,4);const delta=decode(m,latent[genotype][k]);return base.map((v,j)=>Math.max(0,v+m.manifest.neuralWeight*delta[j]));});y=values[0].map((_,j)=>values.reduce((v,row)=>v+row[j]/values.length,0));}
  states.push({age,genotype,meanLog:y.slice(0,2000),cp10k:y.slice(2000).map(Math.expm1),role:m.manifest.measuredAges.includes(age)?'animal_disjoint_prediction':'unmeasured_prediction'});}previous=age;}
 stage('Three frozen neural transitions executed; inverse PCA decoded with active weight0.5');const end=states.find(s=>s.age===c.targetAge&&s.genotype===c.genotype)!;const sampled=sample(m,c.type,end.cp10k.map(x=>Math.min(x,1e6)),c.nuclei,c.seed);stage('Conditional negative-binomial RNA counts sampled');
 return {config:c,states,sourceLatent,sample:sampled,metadata:{modelId:m.manifest.id,genePanel:m.manifest.genePanelSha256,mode:'live_browser_neural_inference',neuralWeight:.5,routeEffect:'Active shared neural state transition. Recursive schedules reuse previous latent states with four substeps per segment; direct queries evolve the original week5 anchor in one step. No RNA re-entry or reverse cycle.',checkpointIds:m.manifest.checkpointFiles.map(c=>c.id),elapsedMs:performance.now()-started},stages};
}
export function metrics(a:number[],b:number[]){if(a.length!==b.length||!a.length)return null;const n=a.length,ma=a.reduce((x,y)=>x+y,0)/n,mb=b.reduce((x,y)=>x+y,0)/n;let se=0,ae=0,cov=0,va=0,vb=0,sign=0;for(let i=0;i<n;i++){se+=(a[i]-b[i])**2;ae+=Math.abs(a[i]-b[i]);cov+=(a[i]-ma)*(b[i]-mb);va+=(a[i]-ma)**2;vb+=(b[i]-mb)**2;sign+=Math.sign(a[i])===Math.sign(b[i])?1:0;}return {RMSE:Math.sqrt(se/n),MAE:ae/n,Pearson:va>1e-20&&vb>1e-20?cov/Math.sqrt(va*vb):null,R2:va>1e-20?1-se/va:null,direction:sign/n};}
export const effect=(wt:number[],sca:number[])=>wt.map((v,i)=>Math.log2((sca[i]+.1)/(v+.1)));
