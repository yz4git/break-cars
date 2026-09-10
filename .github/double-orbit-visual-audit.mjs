import { mkdir, writeFile } from 'node:fs/promises';
import { chromium } from 'playwright';

const baseUrl=process.env.BREAK_CARS_AUDIT_URL||'http://127.0.0.1:4173/';
const outputDir=process.env.BREAK_CARS_AUDIT_DIR||'artifacts/double-orbit-visual-audit';
await mkdir(outputDir,{recursive:true});

const browser=await chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--disable-dev-shm-usage']});
const context=await browser.newContext({viewport:{width:852,height:393},deviceScaleFactor:2,isMobile:true,hasTouch:true});
const page=await context.newPage();
const consoleErrors=[],pageErrors=[];
page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});
page.on('pageerror',e=>pageErrors.push(String(e)));

const url=`${baseUrl}${baseUrl.includes('?')?'&':'?'}course=double-orbit&visualAudit=${Date.now()}`;
await page.goto(url,{waitUntil:'networkidle',timeout:60000});
const spec=await page.evaluate(async()=>{const m=await import('./racing3d.js');return m.race3DFeatureSpec();});
if(!spec?.loops||spec.loops.length!==2)throw new Error(`DOUBLE ORBIT expected 2 loops, got ${spec?.loops?.length??0}`);
await page.screenshot({path:`${outputDir}/00-menu.png`,fullPage:true});

const racing=page.locator('[data-mode="racing"]');
await racing.waitFor({state:'visible',timeout:15000});
if(!(await racing.getAttribute('aria-pressed')==='true'))await racing.click({force:true});
await page.locator('#start').click({force:true});
await page.screenshot({path:`${outputDir}/00b-countdown.png`,fullPage:true});
// Software WebGL can make a nominal 3-second countdown take much longer in
// wall-clock time. Wait for the game state rather than weakening traversal.
await page.waitForFunction(()=>window.__breakCarsAuditState?.()?.mode==='race',undefined,{timeout:60000});

const renderer=await page.evaluate(()=>{const c=document.querySelector('#scene');return c?.getContext('webgl2')||c?.getContext('webgl')?'webgl':'none';});
if(renderer!=='webgl')throw new Error(`WebGL renderer unavailable: ${renderer}`);
const canvas=page.locator('#scene');

async function freezeRaf(){await page.evaluate(()=>{if(window.__doAuditFrozen)return;window.__doAuditOriginalRaf=window.requestAnimationFrame;window.__doAuditQueue=[];let n=1;window.requestAnimationFrame=cb=>{window.__doAuditQueue.push(cb);return -n++;};window.__doAuditFrozen=true;});await page.waitForTimeout(90);}
async function resumeRaf(){await page.evaluate(()=>{if(!window.__doAuditFrozen)return;const r=window.__doAuditOriginalRaf,q=window.__doAuditQueue||[];window.requestAnimationFrame=r;window.__doAuditFrozen=false;window.__doAuditQueue=[];for(const cb of q)r.call(window,cb);});}
async function snap(name){await freezeRaf();await canvas.screenshot({path:`${outputDir}/${name}.png`});await resumeRaf();}

// Capture two alternate camera views before driving, then return to the chase camera.
await freezeRaf();
await page.keyboard.press('KeyC');await page.waitForTimeout(60);await canvas.screenshot({path:`${outputDir}/01-wide.png`});
await page.keyboard.press('KeyC');await page.waitForTimeout(60);await canvas.screenshot({path:`${outputDir}/02-overhead.png`});
await page.keyboard.press('KeyC');await page.waitForTimeout(60);await resumeRaf();

const samples=[];const loopShots=[false,false],topShots=[false,false],exitShots=[false,false];
await page.keyboard.down('ArrowUp');
for(let frame=1;frame<=110;frame++){
  await page.waitForTimeout(300);
  const state=await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>resolve(window.__breakCarsAuditState?.()??null))));
  if(!state)continue;
  let loopIndex=-1;
  for(let i=0;i<spec.loops.length;i++)if(state.trackS>=spec.loops[i].startS&&state.trackS<=spec.loops[i].endS)loopIndex=i;
  samples.push({frame,...state,loopIndex});
  if(loopIndex>=0){
    const loop=spec.loops[loopIndex],u=(state.trackS-loop.startS)/(loop.endS-loop.startS);
    if(!loopShots[loopIndex]&&u>.08){loopShots[loopIndex]=true;await snap(`${10+loopIndex*3}-loop${loopIndex+1}-entry`);}
    if(!topShots[loopIndex]&&u>.42){topShots[loopIndex]=true;await snap(`${11+loopIndex*3}-loop${loopIndex+1}-crown`);}
    if(!exitShots[loopIndex]&&u>.82){exitShots[loopIndex]=true;await snap(`${12+loopIndex*3}-loop${loopIndex+1}-exit`);}
  }
  if(exitShots[1]&&frame>55)break;
}
await page.keyboard.up('ArrowUp').catch(()=>{});

const loopSamples=[0,1].map(i=>samples.filter(s=>s.loopIndex===i));
const traversal=loopSamples.map((arr,i)=>({
  loop:i+1,
  samples:arr.length,
  entered:loopShots[i],crown:topShots[i],exited:exitShots[i],
  inverted:arr.some(s=>s.upY<-.55),
  minSpeedMps:arr.length?Number(Math.min(...arr.map(s=>s.speedMps)).toFixed(2)):null,
  maxSpeedMps:arr.length?Number(Math.max(...arr.map(s=>s.speedMps)).toFixed(2)):null,
  maxLoopT:arr.length?Number(Math.max(...arr.map(s=>s.loopT??0)).toFixed(3)):null,
}));
const layout=await page.evaluate(async spec=>{const m=await import('./racing3d.js');return spec.loops.map((l,i)=>{const mid=(l.startS+l.endS)/2,p=m.racePointAt(mid,0);return{loop:i+1,radius:l.radius,startS:l.startS,endS:l.endS,maxY:l.maxY,mid:{x:p.x,y:p.y,z:p.z}};});},spec);
const diagnostics={url,renderer,viewport:await page.evaluate(()=>({width:innerWidth,height:innerHeight,dpr:devicePixelRatio})),spec,layout,traversal,samples,consoleErrors,pageErrors};
await writeFile(`${outputDir}/diagnostics.json`,JSON.stringify(diagnostics,null,2));
await browser.close();

const failures=[];
for(const t of traversal){if(!t.entered||!t.crown||!t.exited)failures.push(`loop ${t.loop} was not fully traversed`);if(!t.inverted)failures.push(`loop ${t.loop} never reached inverted attitude`);if(t.minSpeedMps!==null&&t.minSpeedMps<2.5)failures.push(`loop ${t.loop} nearly stalled at ${t.minSpeedMps} m/s`);}
if(consoleErrors.length)failures.push(`console errors: ${consoleErrors.join(' | ')}`);
if(pageErrors.length)failures.push(`page errors: ${pageErrors.join(' | ')}`);
if(failures.length)throw new Error(failures.join(' ; '));
console.log(`DOUBLE ORBIT live WebGL audit OK: loops=${traversal.map(t=>`${t.loop}:${t.samples} samples min ${t.minSpeedMps}m/s`).join(', ')}`);
