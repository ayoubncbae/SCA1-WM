import {test,expect} from '@playwright/test';
test('static integration endpoints preserve exact model and observed-reference contracts',async({request})=>{
 const r=await request.get('/model-manifest.json');expect(r.status()).toBe(200);const m=await r.json();expect(m.neuralWeight).toBe(.5);expect(m.cellTypes).toHaveLength(14);const s=await (await request.get('/assets/model-data.json')).json();expect(s.modelId).toBe(m.id);expect(s.checkpointHashes).toEqual(m.checkpointFiles.map((c:any)=>c.sha256));
 for(let i=0;i<14;i++){const response=await request.get(`/verified-predictions/observed-${String(i).padStart(2,'0')}.json`);expect(response.status()).toBe(200);const o=await response.json();for(const e of o.entries){expect([5,12,18,24,30]).toContain(e.age);expect(e.nMice).toBe(1);expect(e.meanLog).toHaveLength(2000);}}
 const health=await (await request.get('/health.json')).json();expect(health.modelId).toBe(m.id);expect(health.neuralWeight).toBe(.5);
});
