import {loadModel,execute} from './engine';import type {Model,RunConfig} from '../types';
let model:Model|undefined;
self.onmessage=async(e:MessageEvent<{id:number;config:RunConfig;base:string}>)=>{const {id,config,base}=e.data;try{if(!model){postMessage({id,stage:'Loading and SHA256-verifying exported model artifacts'});model=await loadModel(base);}const result=execute(model,config,stage=>postMessage({id,stage}));postMessage({id,result});}catch(err){postMessage({id,error:err instanceof Error?err.message:String(err)});}};
