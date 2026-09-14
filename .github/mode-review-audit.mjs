import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const base=process.env.BREAK_CARS_AUDIT_URL||'http://127.0.0.1:4173/';
const out=path.resolve('artifacts/mode-review-audit');
await fs.rm(out,{recursive:true,force:true});
await fs.mkdir(out,{recursive:true});

const cases=[
  {mode:'colosseum',course:'classic',name:'THE COLOSSEUM'},
  {mode:'colosseum',course:'crater-crown',name:'CRATER CROWN'},
  {mode:'colosseum',course:'maelstrom-pit',name:'MAELSTROM PIT'},
  {mode:'wreck-hunt',course:'hunt-classic',name:'WRECK HUNT'},
  {mode:'wreck-hunt',course:'tidal-foundry',name:'TIDAL FOUNDRY'},
  {mode:'wreck-hunt',course:'cross-fire',name:'CROSS FIRE'},
  {mode:'racing',course:'rampage-3d',name:'RAMPAGE 3D'},
  {mode:'racing',course:'sky-forge',name:'SKY FORGE'},
  {mode:'racing',course:'double-orbit',name:'DOUBLE ORBIT'},
];

const browser=await chromium.launch({headless:true,args:[
  '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist',
  '--enable-unsafe-swiftshader','--use-angle=swiftshader-webgl',
  '--disable-background-timer-throttling','--disable-renderer-backgrounding',
  '--disable-backgrounding-occluded-windows'
]});

const report=[];
const text=async(page,sel)=>{try{return (await page.locator(sel).innerText({timeout:800})).trim();}catch{return '';}};
const c2=async page=>await page.evaluate(()=>window.__breakCarsCamera2?{...window.__breakCarsCamera2}:null);

for(const item of cases){
  const dir=path.join(out,item.course);await fs.mkdir(dir,{recursive:true});
  const context=await browser.newContext({
    viewport:{width:852,height:393},deviceScaleFactor:2,isMobile:true,hasTouch:true,
    userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 26_6 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1'
  });
  const page=await context.newPage();
  const errors=[];
  page.on('console',m=>{if(m.type()==='error')errors.push(`console: ${m.text()}`);});
  page.on('pageerror',e=>errors.push(`page: ${String(e)}`));
  const visual=item.mode==='racing'?'&visualAudit=1':'';
  const url=`${base}?course=${encodeURIComponent(item.course)}&modeReview=${Date.now()}${visual}`;
  await page.goto(url,{waitUntil:'networkidle',timeout:30000});
  await page.waitForTimeout(900);
  await page.screenshot({path:path.join(dir,'00-menu.png')});
  const menu={tag:await text(page,'#mode-tag'),subtitle:await text(page,'#mode-subtitle'),lead:await text(page,'#mode-lead'),course:await page.locator('#course-picker').inputValue()};
  await page.click('#start');
  await page.waitForTimeout(4300);
  await page.keyboard.down('ArrowUp');
  await page.waitForTimeout(1100);
  await page.screenshot({path:path.join(dir,'10-follow-early.png')});
  const camera2Early=await c2(page),cameraTrace=[];
  if(camera2Early)cameraTrace.push(camera2Early);

  if(item.mode==='racing'){
    // visualAudit starts 30 m before the first loop. Sample Camera 2.0 through
    // the entire approach/arc so the audit catches a second escape transform
    // stacked on top of the authored loop-stage camera, not merely JS crashes.
    for(let i=0;i<24;i++){await page.waitForTimeout(150);const snap=await c2(page);if(snap)cameraTrace.push(snap);}
  }else{
    // Actual input pass: sweep left/right and drift once so each arena review
    // includes live collisions, terrain loading and camera follow under motion.
    for(let i=0;i<5;i++){
      const key=i%2===0?'ArrowLeft':'ArrowRight';
      await page.keyboard.down(key);await page.waitForTimeout(620);await page.keyboard.up(key);
      if(i===2){await page.keyboard.down('Space');await page.waitForTimeout(330);await page.keyboard.up('Space');}
    }
  }
  await page.screenshot({path:path.join(dir,'20-follow-action.png')});
  const camera2Action=await c2(page);if(camera2Action)cameraTrace.push(camera2Action);

  await page.keyboard.press('KeyC');await page.waitForTimeout(1500);
  await page.screenshot({path:path.join(dir,'30-wide.png')});
  await page.keyboard.press('KeyC');await page.waitForTimeout(1500);
  await page.screenshot({path:path.join(dir,'40-overhead.png')});
  await page.keyboard.press('KeyC');
  if(item.mode!=='racing'){
    await page.keyboard.down('ArrowRight');await page.waitForTimeout(950);await page.keyboard.up('ArrowRight');
  }else await page.waitForTimeout(950);
  await page.screenshot({path:path.join(dir,'50-follow-late.png')});
  const camera2Late=await c2(page);if(camera2Late)cameraTrace.push(camera2Late);
  await page.keyboard.up('ArrowUp');

  const hud={
    positionLabel:await text(page,'#position-label'),alive:await text(page,'#alive'),
    scoreLabel:await text(page,'#score-label'),score:await text(page,'#score'),time:await text(page,'#time'),
    hp:await text(page,'#hp'),speed:await text(page,'#speed'),raceLap:await text(page,'#race-lap'),
    raceTotal:await text(page,'#race-total'),raceState:await text(page,'#race-state'),
    huntCombo:await text(page,'#hunt-combo'),huntState:await text(page,'#hunt-state'),toast:await text(page,'#toast')
  };
  let audit=null;
  if(item.mode==='racing')audit=await page.evaluate(()=>window.__breakCarsAuditState?.()??null);
  const renderer=await page.evaluate(()=>{
    const c=document.querySelector('canvas');if(!c)return 'none';
    try{return c.getContext('webgl2')?'webgl2':c.getContext('webgl')?'webgl':'canvas';}catch{return 'canvas';}
  });
  const camera2={early:camera2Early,action:camera2Action,late:camera2Late};
  const loopTrace=cameraTrace.filter(v=>v?.loopProtected||v?.poseKind==='loop'),loopDistances=loopTrace.map(v=>Number(v?.compositionDistance)||0).filter(v=>v>0);
  const cameraReview={
    loopSamples:loopTrace.length,
    maxLoopEscape:Math.max(0,...loopTrace.map(v=>Math.abs(Number(v?.escape)||0))),
    avgLoopDistance:loopDistances.length?loopDistances.reduce((a,b)=>a+b,0)/loopDistances.length:0,
    maxLoopDistance:Math.max(0,...loopDistances),
  };
  const row={...item,url,menu,hud,audit,camera2,cameraReview,renderer,errors};report.push(row);
  await fs.writeFile(path.join(dir,'diagnostics.json'),JSON.stringify(row,null,2));
  await context.close();
}
await browser.close();
await fs.writeFile(path.join(out,'summary.json'),JSON.stringify(report,null,2));
const bad=report.filter(x=>x.errors.length||x.renderer==='none'||(x.mode==='racing'&&x.cameraReview.loopSamples>0&&x.cameraReview.maxLoopEscape>1.35));
console.log(`MODE REVIEW audit: ${report.length} course/mode variants, errors=${bad.length}`);
for(const x of report){const esc=Math.max(0,...Object.values(x.camera2).map(v=>v?.escape||0));const cam=x.mode==='racing'?` loop=${x.cameraReview.loopSamples} avg=${x.cameraReview.avgLoopDistance.toFixed(1)}m max=${x.cameraReview.maxLoopDistance.toFixed(1)}m`:'';console.log(`${x.mode.padEnd(10)} ${x.course.padEnd(15)} renderer=${x.renderer} hp=${x.hud.hp||'-'} speed=${x.hud.speed.replace(/\s+/g,' ')||'-'} c2=${esc.toFixed(2)}m${cam} errors=${x.errors.length}`);}
if(bad.length){for(const x of bad)console.error(`REVIEW FAIL ${x.mode}/${x.course}: ${x.errors.join('; ')||`loop camera escape=${x.cameraReview.maxLoopEscape.toFixed(2)} avg=${x.cameraReview.avgLoopDistance.toFixed(1)} max=${x.cameraReview.maxLoopDistance.toFixed(1)}`}`);process.exitCode=1;}
