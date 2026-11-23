// Synthetic-only actual upload/activation/rollback, using existing Chrome/Node CDP.
import fs from 'node:fs';import path from 'node:path';
const out=path.resolve(process.env.BANCINC_BROWSER_OUT);fs.mkdirSync(out,{recursive:true});
const targets=await(await fetch(process.env.BANCINC_CDP_URL+'/json/list')).json();
const ws=new WebSocket(targets.find(x=>x.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);let id=0;const pending=new Map();
ws.onmessage=({data})=>{const m=JSON.parse(data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}};
const call=(method,params={})=>new Promise((resolve,reject)=>{pending.set(++id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
async function evaluate(expression){const r=await call('Runtime.evaluate',{expression,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value}
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function until(expression){for(let n=0;n<300;n++){if(await evaluate(expression))return;await pause(300)}throw Error('Browser state did not settle: '+expression)}
async function settled(){await until(`!document.querySelector('[data-testid=stSpinner]') && !document.querySelector('[data-stale=true]') && !Array.from(document.querySelectorAll('button')).some(b=>b.innerText.trim()==='Stop')`);await pause(400)}
async function click(text){await evaluate(`Array.from(document.querySelectorAll('button')).find(b=>b.innerText.trim()===${JSON.stringify(text)})?.click()`);await pause(400);await settled()}
async function upload(name){const doc=await call('DOM.getDocument');const node=await call('DOM.querySelector',{nodeId:doc.root.nodeId,selector:'input[type=file]'});await call('DOM.setFileInputFiles',{nodeId:node.nodeId,files:[path.resolve('outputs/phase9/examples/'+name)]});await until(`document.body.innerText.includes(${JSON.stringify(name)})`);await settled()}
async function shot(name){const s=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(s.data,'base64'))}
await call('Page.enable');await call('Runtime.enable');await call('DOM.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1080,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:process.env.BANCINC_PREVIEW_URL});await until(`document.querySelector('h1')?.innerText==='Dataset Ingestion & Refresh' && document.body.innerText.includes('F · Audit and Provenance')`);await settled();
const result={syntheticOnly:true};
await upload('synthetic-valid.csv');await click('Validate upload');await until(`document.body.innerText.includes('Validation PASSED')`);await shot('validation_pass');result.validated=true;
await click('Process validated dataset');await until(`document.body.innerText.includes('Candidate snapshot:')`);await click('Preview candidate snapshot');
await until(`Array.from(document.querySelectorAll('[data-testid=stMetricValue]')).map(e=>e.innerText.trim()).join(',')==='4,1,1,2'`);
result.reconciledCounts=[4,1,1,2];result.sixGates=await evaluate(`document.querySelectorAll('.banc-gate').length===6`);await shot('candidate_preview');
await click('Activate validated preview snapshot');await until(`!document.body.innerText.includes('Active companion selection: baseline')`);result.activated=true;await shot('active_snapshot');
await click('Return to accepted baseline');await until(`Array.from(document.querySelectorAll('[data-testid=stMetricValue]')).map(e=>e.innerText.trim()).join(',')==='50000,2052,20,47928'`);result.returnedToBaseline=true;await shot('baseline_restored');
await upload('synthetic-invalid-date.csv');await click('Validate upload');await until(`document.body.innerText.includes('Validation FAILED')`);
result.invalidProcessingBlocked=await evaluate(`Array.from(document.querySelectorAll('button')).find(b=>b.innerText.trim()==='Process validated dataset')?.disabled===true`);result.invalidActivationBlocked=await evaluate(`Array.from(document.querySelectorAll('button')).find(b=>b.innerText.trim()==='Activate validated preview snapshot')?.disabled===true`);await shot('invalid_rejected');
result.exceptions=await evaluate(`document.querySelectorAll('[data-testid=stException]').length`);result.noOutreachControls=await evaluate(`!Array.from(document.querySelectorAll('button')).some(b=>/send|approve|outreach|record decision/i.test(b.innerText))`);
result.responsive=[];
for(const width of [1440,768,390]){await call('Emulation.setDeviceMetricsOverride',{width,height:1080,deviceScaleFactor:1,mobile:false});await pause(600);await settled();result.responsive.push(await evaluate(`({width:${width},overflow:document.documentElement.scrollWidth>innerWidth,exceptions:document.querySelectorAll('[data-testid=stException]').length})`));await shot('companion_'+width)}
fs.writeFileSync(path.join(out,'browser_result.json'),JSON.stringify(result,null,2));ws.close();
if(!result.sixGates||!result.invalidProcessingBlocked||!result.invalidActivationBlocked||result.exceptions||!result.noOutreachControls||result.responsive.some(r=>r.overflow||r.exceptions))throw Error('Phase 9 browser acceptance failed');
console.log(JSON.stringify(result,null,2));
