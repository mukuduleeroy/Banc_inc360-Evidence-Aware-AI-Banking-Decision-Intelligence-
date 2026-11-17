// Existing Chrome + Node's built-in CDP/WebSocket client; no new browser dependencies.
import fs from 'node:fs';
import path from 'node:path';
const out=path.resolve(process.env.BANCINC_BROWSER_OUT||'outputs/phase3');
const previewUrl=process.env.BANCINC_PREVIEW_URL||'http://127.0.0.1:8502';fs.mkdirSync(path.join(out,'screenshots'),{recursive:true});
const targets=await (await fetch((process.env.BANCINC_CDP_URL||'http://127.0.0.1:9222')+'/json/list')).json();
const target=targets.find(x=>x.type==='page');if(!target)throw Error('No local Chrome page target');
const ws=new WebSocket(target.webSocketDebuggerUrl);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
let id=0;const pending=new Map();
ws.onmessage=({data})=>{const msg=JSON.parse(data);if(msg.id&&pending.has(msg.id)){const {resolve,reject,timer}=pending.get(msg.id);clearTimeout(timer);pending.delete(msg.id);msg.error?reject(Error(JSON.stringify(msg.error))):resolve(msg.result)}};
function cdp(method,params={}){return new Promise((resolve,reject)=>{const n=++id;const timer=setTimeout(()=>{pending.delete(n);reject(Error('CDP timeout: '+method))},60000);pending.set(n,{resolve,reject,timer});ws.send(JSON.stringify({id:n,method,params}))})}
async function evaluate(expression){const r=await cdp('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error('Browser script failed: '+r.exceptionDetails.text);return r.result.value}
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function until(expression,timeout=90000){const start=Date.now();while(Date.now()-start<timeout){if(await evaluate(expression))return;await pause(400)}throw Error('Timed out waiting for rendered page')}
await cdp('Page.enable');await cdp('Runtime.enable');await cdp('Emulation.setDeviceMetricsOverride',{width:1440,height:1080,deviceScaleFactor:1,mobile:false});
await cdp('Page.navigate',{url:previewUrl});
const views=[['executive_overview','Executive Overview'],['customer_360','Customer 360'],['inactivity_intelligence','Inactivity Intelligence'],['relationship_value','Relationship Value Intelligence'],['product_opportunities','Product Opportunity Intelligence'],['decision_passport','Decision Passport'],['evidence_replay','Evidence Replay'],['manager_work_queue','Manager Work Queue'],['audit_validation','Audit & Validation Evidence']];
const markers={executive_overview:'Inspect provenance, policy and validation evidence',customer_360:'Try a labeled evidence simulation',inactivity_intelligence:'Open Decision Passport',relationship_value:'Open Decision Passport',product_opportunities:'Open Decision Passport',decision_passport:'Session review notes',evidence_replay:'Return to the real-data Decision Passport',manager_work_queue:'Selected case evidence',audit_validation:'Legacy session notes — not bank approvals'};
const minTables={executive_overview:5,customer_360:2,inactivity_intelligence:3,relationship_value:3,product_opportunities:2,decision_passport:2,evidence_replay:2,manager_work_queue:3,audit_validation:3};
const results=[];
for(const [slug,title] of views){
 await until(`document.querySelector('h1') && Array.from(document.querySelectorAll('a')).some(a=>a.innerText.trim()===${JSON.stringify(title)})`);
 await evaluate(`Array.from(document.querySelectorAll('a')).find(a=>a.innerText.trim()===${JSON.stringify(title)}).click()`);
 await until(`document.querySelector('h1')?.innerText===${JSON.stringify(title)} && !document.querySelector('[data-testid="stSpinner"]')`);
 await until(`document.body.innerText.includes(${JSON.stringify(markers[slug])}) && document.querySelectorAll('[data-testid="stDataFrame"]').length>=${minTables[slug]}`);
 await pause(1000);
 const info=await evaluate(`({title:document.querySelector('h1')?.innerText,exceptions:Array.from(document.querySelectorAll('[data-testid="stException"]')).map(e=>e.innerText.slice(0,100)),tableCount:document.querySelectorAll('[data-testid="stDataFrame"]').length,horizontalOverflow:document.documentElement.scrollWidth>innerWidth,buttons:Array.from(document.querySelectorAll('button')).map(b=>b.innerText.trim()).filter(Boolean)})`);
 if(info.exceptions.length)throw Error(title+': '+JSON.stringify(info.exceptions));
 const image=await cdp('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(out,'screenshots',slug+'.png'),Buffer.from(image.data,'base64'));
 results.push({view:title,exceptions:info.exceptions.length,tables:info.tableCount,horizontalOverflow:info.horizontalOverflow,screenshot:'screenshots/'+slug+'.png'});
 console.log(title+': rendered, '+info.tableCount+' tables, screenshot saved');
}
// Exercise a real baseline only as a labeled, non-actionable browser simulation.
await evaluate(`Array.from(document.querySelectorAll('a')).find(a=>a.innerText.trim()==='Evidence Replay').click()`);
await until(`document.querySelector('h1')?.innerText==='Evidence Replay' && document.body.innerText.includes('Return to the real-data Decision Passport')`);
const metricExpr=label=>`Array.from(document.querySelectorAll('[data-testid="stMetric"]')).find(e=>e.innerText.includes(${JSON.stringify(label)}))?.innerText`;
const baseline=await evaluate(metricExpr('Baseline decision'));
if(!baseline?.includes('SUPPORTED'))throw Error('Expected an actually supported starting customer');
async function click(expression){const p=await evaluate(`(()=>{const e=${expression};if(!e)throw Error('Control not found');e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}})()`);await cdp('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...p});await cdp('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,...p});}
await click(`Array.from(document.querySelectorAll('[data-testid="stSelectbox"]')).find(e=>e.innerText.includes('SIMULATED KYC status')).querySelector('[data-baseweb="select"]')`);
await until(`Array.from(document.querySelectorAll('[role="option"]')).some(e=>e.innerText.trim()==='Pending')`);
await click(`Array.from(document.querySelectorAll('[role="option"]')).find(e=>e.innerText.trim()==='Pending')`);
await until(`${metricExpr('SIMULATED decision')}?.includes('ABSTAIN')`);
await evaluate(`document.querySelector('[data-testid="stMain"]')?.scrollTo(0,0)`);await pause(700);
let replayShot=await cdp('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(out,'screenshots','evidence_replay_pending.png'),Buffer.from(replayShot.data,'base64'));
await click(`Array.from(document.querySelectorAll('button')).find(e=>e.innerText.trim()==='Reset simulation')`);
await until(`${metricExpr('SIMULATED decision')}?.includes('SUPPORTED') && document.body.innerText.includes('None — simulation matches baseline')`);
await evaluate(`document.querySelector('[data-testid="stMain"]')?.scrollTo(0,0)`);await pause(700);
replayShot=await cdp('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(out,'screenshots','evidence_replay_reset.png'),Buffer.from(replayShot.data,'base64'));
const replay={baseline:'SUPPORTED',simulatedPendingKYC:'ABSTAIN',afterReset:'SUPPORTED',noActionControls:!(await evaluate(`Array.from(document.querySelectorAll('button')).some(e=>e.innerText.trim()==='Record decision')`))};
console.log('Browser replay: actual baseline SUPPORTED → simulated Pending KYC ABSTAIN → reset SUPPORTED');
// Verify a practical narrow viewport without pretending this is an accessibility certification.
await cdp('Emulation.setDeviceMetricsOverride',{width:768,height:1024,deviceScaleFactor:1,mobile:false});await cdp('Page.navigate',{url:previewUrl});
await until(`document.querySelector('h1')?.innerText==='Executive Overview' && !document.querySelector('[data-testid="stSpinner"]')`);await until(`document.body.innerText.includes('Inspect provenance, policy and validation evidence')`);await pause(1000);
const narrow=await evaluate(`({width:innerWidth,horizontalOverflow:document.documentElement.scrollWidth>innerWidth,exceptions:document.querySelectorAll('[data-testid="stException"]').length,clippedMetricValues:Array.from(document.querySelectorAll('[data-testid="stMetricValue"]')).filter(e=>e.scrollWidth>e.clientWidth+1).length})`);
const shot=await cdp('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(out,'screenshots','overview_narrow.png'),Buffer.from(shot.data,'base64'));
fs.writeFileSync(path.join(out,'browser_verification.json'),JSON.stringify({browser:'Local headless Chrome via CDP',views:results,replay,narrowViewport:narrow,screenshotsAreViewportOnly:true},null,2));ws.close();
