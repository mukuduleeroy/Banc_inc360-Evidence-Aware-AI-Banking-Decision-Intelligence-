// Existing Chrome and Node built-ins only. Every persisted approval is a local demo outcome.
import fs from 'node:fs';import path from 'node:path';
const mode=process.argv[2]||'create';if(!['create','reopen'].includes(mode))throw Error('Mode must be create or reopen');
const url=process.env.BANCINC_PREVIEW_URL||'http://127.0.0.1:8503';const out=path.resolve(process.env.BANCINC_BROWSER_OUT||'outputs/phase4');fs.mkdirSync(path.join(out,'screenshots'),{recursive:true});
const targets=await (await fetch((process.env.BANCINC_CDP_URL||'http://127.0.0.1:9222')+'/json/list')).json();const target=targets.find(t=>t.type==='page');const ws=new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});let id=0;const waiting=new Map();
ws.onmessage=({data})=>{const m=JSON.parse(data);if(m.id&&waiting.has(m.id)){const p=waiting.get(m.id);clearTimeout(p.timer);waiting.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}};
const cdp=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;const timer=setTimeout(()=>reject(Error('CDP timeout '+method)),60000);waiting.set(n,{resolve,reject,timer});ws.send(JSON.stringify({id:n,method,params}))});
async function evaluate(expression){const r=await cdp('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(expression,timeout=90000){const start=Date.now();while(Date.now()-start<timeout){if(await evaluate(expression))return;await sleep(400)}throw Error('Browser wait timed out')}
async function click(expr){await evaluate(`(()=>{const e=${expr};if(!e)throw Error('Control not found');e.scrollIntoView({block:'center',behavior:'instant'})})()`);await sleep(250);const p=await evaluate(`(()=>{const r=(${expr}).getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}})()`);await cdp('Input.dispatchMouseEvent',{type:'mouseMoved',...p});await cdp('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...p});await cdp('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,...p})}
async function choose(label,option){await click(`Array.from(document.querySelectorAll('[data-testid="stSelectbox"]')).find(e=>e.innerText.includes(${JSON.stringify(label)})).querySelector('[data-baseweb="select"]')`);await until(`Array.from(document.querySelectorAll('[role="option"]')).some(e=>e.innerText.trim().startsWith(${JSON.stringify(option)}))`);await click(`Array.from(document.querySelectorAll('[role="option"]')).find(e=>e.innerText.trim().startsWith(${JSON.stringify(option)}))`);await until(`Array.from(document.querySelectorAll('[data-testid="stSelectbox"]')).find(e=>e.innerText.includes(${JSON.stringify(label)}))?.innerText.includes(${JSON.stringify(option)})`);await sleep(350)}
async function shot(name,heading){if(heading)await evaluate(`Array.from(document.querySelectorAll('h3')).find(e=>e.innerText.includes(${JSON.stringify(heading)}))?.scrollIntoView({block:'start'})`);await sleep(800);const image=await cdp('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(out,'screenshots',name+'.png'),Buffer.from(image.data,'base64'))}
await cdp('Page.enable');await cdp('Runtime.enable');await cdp('Emulation.setDeviceMetricsOverride',{width:1440,height:1080,deviceScaleFactor:1,mobile:false});await cdp('Page.navigate',{url});
await until(`Array.from(document.querySelectorAll('a')).some(a=>a.innerText.trim()==='Manager Work Queue')`);
await evaluate(`Array.from(document.querySelectorAll('a')).find(a=>a.innerText.trim()==='Manager Work Queue').click()`);
await until(`document.querySelector('h1')?.innerText==='Manager Work Queue' && document.body.innerText.includes('Durable human review — local prototype only') && document.body.innerText.includes('Case status:')`);
if(mode==='create'){
 await until(`Array.from(document.querySelectorAll('button')).some(b=>b.innerText.trim()==='Open case and inspect Passport')`);
 await choose('Demo reviewer — explicit unverified selection','DEMO-RM-01');
 await until(`Array.from(document.querySelectorAll('button')).some(b=>b.innerText.trim()==='Open case and inspect Passport' && !b.disabled)`);
 await click(`Array.from(document.querySelectorAll('button')).find(b=>b.innerText.trim()==='Open case and inspect Passport')`);
 await until(`Array.from(document.querySelectorAll('button')).some(b=>b.innerText.trim()==='Save durable review')`);
 await choose('Local prototype review outcome','Approve');
 await click(`Array.from(document.querySelectorAll('[data-testid="stTextArea"]')).find(e=>e.innerText.includes('Required review reason')).querySelector('textarea')`);
 await cdp('Input.insertText',{text:'Browser presentation rehearsal: supported passport inspected; local prototype review only. No banking action.'});
 await click(`Array.from(document.querySelectorAll('[data-testid="stCheckbox"]')).find(e=>e.innerText.includes('I inspected this current six-gate Passport')).querySelector('label')`);
 await until(`Array.from(document.querySelectorAll('[data-testid="stCheckbox"]')).find(e=>e.innerText.includes('I inspected this current six-gate Passport'))?.querySelector('input')?.checked`);
 await click(`Array.from(document.querySelectorAll('button')).find(b=>b.innerText.trim()==='Save durable review')`);
}
await until(`document.body.innerText.includes('APPROVED_LOCAL')`);await sleep(800);
const page=await evaluate(`({caseId:document.body.innerText.match(/CASE-[a-f0-9]{32}/)?.[0],approvedLocal:document.body.innerText.includes('APPROVED_LOCAL'),bankDisclaimer:document.body.innerText.includes('not login, identity verification or bank authorization'),exceptions:document.querySelectorAll('[data-testid="stException"]').length})`);
if(page.exceptions||!page.approvedLocal||!page.bankDisclaimer)throw Error('Review state/disclaimer verification failed');
await shot(mode==='create'?'review_approved':'review_after_restart','Durable human review');
await evaluate(`Array.from(document.querySelectorAll('a')).find(a=>a.innerText.trim()==='Audit & Validation Evidence').click()`);
await until(`document.querySelector('h1')?.innerText==='Audit & Validation Evidence' && document.body.innerText.includes('Inspect event passport') && document.body.innerText.includes('Legacy session notes')`);
const events=await evaluate(`Array.from(document.querySelectorAll('[data-testid="stMetric"]')).find(e=>e.innerText.includes('Immutable review events'))?.querySelector('[data-testid="stMetricValue"]')?.innerText`);
if(events!=='2')throw Error('Expected actual OPEN and APPROVE events in isolated presentation DB');
await shot(mode==='create'?'audit_timeline':'audit_after_restart','Durable review audit');
const result={mode,url,...page,immutableEvents:Number(events),reviewerAttribution:'DEMO_UNVERIFIED',sourceTraceability:'FEATURE_LEVEL',realBankAuthorization:false};fs.writeFileSync(path.join(out,'browser_'+mode+'.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));ws.close();
