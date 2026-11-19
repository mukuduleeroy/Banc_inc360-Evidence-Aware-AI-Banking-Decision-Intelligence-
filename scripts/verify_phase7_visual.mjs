// Actual viewport/keyboard checks against a local-only server, using existing Chrome/Node.
import fs from 'node:fs';import path from 'node:path';
const out=path.resolve('outputs/phase7/responsive');fs.mkdirSync(out,{recursive:true});
const url=process.env.BANCINC_PREVIEW_URL||'http://127.0.0.1:8507';const port=process.env.BANCINC_CDP_URL||'http://127.0.0.1:9225';
const tabs=await(await fetch(port+'/json/list')).json();const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);let id=0;const waiting=new Map();ws.onmessage=({data})=>{const m=JSON.parse(data);if(m.id){const p=waiting.get(m.id);waiting.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result)}};const call=(method,params={})=>new Promise((resolve,reject)=>{waiting.set(++id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
async function evaluate(expression){const r=await call('Runtime.evaluate',{expression,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value}
const pause=ms=>new Promise(r=>setTimeout(r,ms));async function until(expr){for(let n=0;n<600;n++){if(await evaluate(expr))return;await pause(300)}throw Error('View did not settle: '+expr)}
async function settled(){const expr=`!document.querySelector('[data-testid=stSpinner]') && !document.querySelector('[data-stale=true]') && !Array.from(document.querySelectorAll('button')).some(b=>b.innerText.trim()==='Stop')`;await until(expr);await pause(1200);await until(expr)}
const views=[['executive_overview','Executive Overview'],['customer_360','Customer 360'],['inactivity_intelligence','Inactivity Intelligence'],['relationship_value','Relationship Value Intelligence'],['product_opportunities','Product Opportunity Intelligence'],['decision_passport','Decision Passport'],['evidence_replay','Evidence Replay'],['manager_work_queue','Manager Work Queue'],['audit_validation','Audit & Validation Evidence']];
await call('Page.enable');await call('Runtime.enable');const results=[];
for(const width of (process.env.BANCINC_VIEWPORTS||"1440,1280,768,390").split(",").map(Number)){
 await call('Emulation.setDeviceMetricsOverride',{width,height:1080,deviceScaleFactor:1,mobile:false});await call('Page.navigate',{url});
 await until(`document.querySelector('h1')?.innerText==='Executive Overview' && document.body.innerText.includes('Inspect provenance, policy and validation evidence')`);
 await settled();
 if(width>=768){await evaluate(`Array.from(document.querySelectorAll('button')).find(b=>b.innerText.trim()==='keyboard_double_arrow_right')?.click()`);await pause(400)}
 if(width<768){await evaluate(`document.querySelector('[data-testid="stSidebarCollapseButton"] button')?.click()`);await pause(400)}
 for(const [slug,title] of views){
  if(await evaluate(`document.querySelector('h1')?.innerText!==${JSON.stringify(title)}`))await evaluate(`Array.from(document.querySelectorAll('a')).find(a=>a.innerText.trim()===${JSON.stringify(title)})?.click()`);
  await until(`document.querySelector('h1')?.innerText===${JSON.stringify(title)} && !document.querySelector('[data-testid="stSpinner"]')`);await pause(700);
  if(slug==='decision_passport')await until(`document.querySelectorAll('.banc-gate').length===6 && document.body.innerText.includes('Durable human review')`);
  if(slug==='audit_validation')await until(`document.body.innerText.includes('Legacy session notes')`);
  await settled();
  await evaluate(`document.querySelector('[data-testid="stMain"]')?.scrollTo(0,0)`);await pause(150);
  const info=await evaluate(`({width:${width},view:${JSON.stringify(title)},exceptions:document.querySelectorAll('[data-testid="stException"]').length,horizontalOverflow:document.documentElement.scrollWidth>innerWidth,clippedMetricValues:Array.from(document.querySelectorAll('[data-testid="stMetricValue"]')).filter(e=>e.clientWidth>0 && e.scrollWidth>e.clientWidth+1).map(e=>e.innerText),clippedButtons:Array.from(document.querySelectorAll('button')).filter(e=>e.clientWidth>0 && e.scrollWidth>e.clientWidth+1).map(e=>e.innerText),gateCards:document.querySelectorAll('.banc-gate').length,studentIdentity:document.querySelector('.banc-identity')?.innerText.includes('Independent student hackathon prototype'),identityBelowHeader:document.querySelector('.banc-identity')?.getBoundingClientRect().top>=50,fullySettled:!document.querySelector('[data-stale=true]') && !document.querySelector('[data-testid=stSpinner]'),mainCaptionColor:getComputedStyle(document.querySelector('[data-testid=stMain] [data-testid=stCaptionContainer] p')).color})`);
  results.push(info);const shot=await call('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(out,slug+'_'+width+'.png'),Buffer.from(shot.data,'base64'));console.log(JSON.stringify(info));
 }
}
await call('Page.navigate',{url});await until(`document.querySelector('h1')?.innerText==='Executive Overview' && document.body.innerText.includes('Inspect provenance, policy and validation evidence')`);
const focus=[];for(let i=0;i<8;i++){await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});focus.push(await evaluate(`({tag:document.activeElement?.tagName,label:document.activeElement?.getAttribute('aria-label')||document.activeElement?.innerText?.slice(0,80),outline:getComputedStyle(document.activeElement).outlineStyle})`))}
const report={results,keyboardFocusSequence:focus,scope:'Functional layout/keyboard sampling, not formal accessibility certification',screenshotsAreViewportOnly:true};fs.writeFileSync(path.join(out,'visual_validation.json'),JSON.stringify(report,null,2));ws.close();
if(results.some(r=>r.exceptions||r.horizontalOverflow||r.clippedMetricValues.length||r.clippedButtons.length||!r.studentIdentity||!r.identityBelowHeader||!r.fullySettled))throw Error('Visual acceptance failures recorded in visual_validation.json');
