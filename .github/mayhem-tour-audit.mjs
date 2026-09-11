import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const base=(process.env.BREAK_CARS_AUDIT_URL||'http://127.0.0.1:4173/').replace(/\/?$/,'/');
const out=path.resolve('artifacts/mayhem-tour-audit');
await fs.rm(out,{recursive:true,force:true});
await fs.mkdir(out,{recursive:true});

const browser=await chromium.launch({headless:true,args:[
  '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist',
  '--enable-unsafe-swiftshader','--use-angle=swiftshader-webgl',
  '--disable-background-timer-throttling','--disable-renderer-backgrounding',
  '--disable-backgrounding-occluded-windows'
]});
const context=await browser.newContext({
  viewport:{width:852,height:393},deviceScaleFactor:2,isMobile:true,hasTouch:true,
  userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 26_6 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1'
});
const page=await context.newPage();
const errors=[];
page.on('console',m=>{if(m.type()==='error')errors.push(`console: ${m.text()}`);});
page.on('pageerror',e=>errors.push(`page: ${String(e)}`));
const text=async sel=>{
  for(let i=0;i<5;i++){
    try{const value=(await page.locator(sel).innerText({timeout:1200})).trim();if(value)return value;}catch{}
    await page.waitForTimeout(180);
  }
  return '';
};
const snap=async name=>page.screenshot({path:path.join(out,name),fullPage:false});
const tour=async()=>page.evaluate(()=>window.__breakCarsMayhemTour?.()??null);
const renderer=async()=>page.evaluate(()=>{const c=document.querySelector('canvas');if(!c)return'none';try{return c.getContext('webgl2')?'webgl2':c.getContext('webgl')?'webgl':'canvas';}catch{return'canvas';}});
const assert=(ok,msg)=>{if(!ok)throw new Error(msg);};
const eventUrl=i=>`${base}?course=${['crater-crown','hunt-classic','double-orbit'][i]}&tour=1&event=${i}&tourAudit=1`;
const waitTourReady=async i=>{
  await page.waitForFunction(index=>{
    const state=window.__breakCarsMayhemTour?.();
    return state?.event===index&&document.querySelector('#mode-tag')?.textContent?.includes('MAYHEM TOUR');
  },i,{timeout:8000});
  await page.waitForTimeout(180);
};
const beginDriving=async()=>{
  await page.waitForFunction(()=>typeof window.__breakCarsMayhemAuditStart==='function',{timeout:5000});
  await page.evaluate(()=>window.__breakCarsMayhemAuditStart());
  await page.waitForTimeout(900);
};
const assertResultBadgeClear=async label=>assert(await page.locator('#tour-run-badge').count()===0,`${label}: Tour run badge overlaps result/PIT screen`);

const report={menu:null,events:[],errors};
try{
  // Ordinary menu must expose Tour without removing the existing single-event modes.
  await page.goto(`${base}?course=classic`,{waitUntil:'networkidle',timeout:30000});
  await page.waitForTimeout(700);
  report.menu={
    tourVisible:await page.locator('#mayhem-tour-entry').isVisible(),
    modes:await page.locator('[data-mode]').count(),
    label:await text('#mayhem-tour-entry')
  };
  assert(report.menu.tourVisible,'MAYHEM TOUR entry is not visible on the normal menu');
  assert(report.menu.modes===3,`expected 3 ordinary modes, got ${report.menu.modes}`);
  await snap('00-normal-menu-tour-entry.png');

  // Enter event 1 directly, then seed a deterministic persisted car/HULL state.
  await page.goto(eventUrl(0),{waitUntil:'networkidle',timeout:30000});
  await page.evaluate(()=>{const k='break-cars-mayhem-tour-v1',s=JSON.parse(sessionStorage.getItem(k));s.car=1;s.hull=.63;sessionStorage.setItem(k,JSON.stringify(s));});
  await page.reload({waitUntil:'networkidle'});
  await waitTourReady(0);
  let state=await tour();
  assert(state?.event===0,'event 1 state missing');
  assert(state?.eventDef?.course==='crater-crown','event 1 course mismatch');
  assert(state?.worldMode==='colosseum','event 1 mode mismatch');
  const e1Start={state,tag:await text('#mode-tag'),lead:await text('#mode-lead'),renderer:await renderer()};
  assert(/MAYHEM TOUR/.test(e1Start.tag),'event 1 Tour heading missing');
  assert(e1Start.renderer!=='none','event 1 renderer missing');
  assert(Math.abs(state.hp/state.maxHP-.63)<.035,`event 1 seeded hull mismatch: ${state.hp}/${state.maxHP}`);
  await snap('10-event1-crater-menu.png');
  await page.click('#start');await page.waitForTimeout(700);await beginDriving();
  await page.keyboard.down('ArrowUp');await page.waitForTimeout(1000);await snap('11-event1-crater-play.png');await page.keyboard.up('ArrowUp');
  await page.evaluate(()=>window.__breakCarsMayhemAuditFinish());await page.waitForTimeout(450);
  assert(await page.locator('[data-tour-up="power"]').isVisible(),'event 1 pit POWER choice missing');
  await assertResultBadgeClear('event 1');
  await snap('12-event1-pit.png');
  const beforePower=await tour();
  await page.click('[data-tour-up="power"]');
  await page.waitForURL(/event=1/,{timeout:10000});
  await page.goto(eventUrl(1),{waitUntil:'networkidle',timeout:30000});
  await waitTourReady(1);
  state=await tour();
  const e2Start={state,tag:await text('#mode-tag'),lead:await text('#mode-lead'),renderer:await renderer()};
  assert(state?.event===1&&state?.eventDef?.course==='hunt-classic','event 2 route/state mismatch');
  assert(state?.worldMode==='wreck-hunt','event 2 mode mismatch');
  assert(state?.car===1,'selected car did not persist into event 2');
  assert(state?.power===1,'POWER upgrade did not persist into event 2');
  assert(Math.abs(state.hp/state.maxHP-beforePower.hull)<.04,'HULL did not carry into event 2');
  assert(e2Start.renderer!=='none','event 2 renderer missing');
  await snap('20-event2-hunt-menu.png');
  await page.click('#start');await page.waitForTimeout(700);await beginDriving();
  await page.keyboard.down('ArrowUp');await page.waitForTimeout(1000);await snap('21-event2-hunt-play.png');await page.keyboard.up('ArrowUp');
  await page.evaluate(()=>window.__breakCarsMayhemAuditFinish());await page.waitForTimeout(450);
  assert(await page.locator('[data-tour-up="armor"]').isVisible(),'event 2 pit ARMOR choice missing');
  await assertResultBadgeClear('event 2');
  await snap('22-event2-pit.png');
  const beforeArmor=await tour();
  await page.click('[data-tour-up="armor"]');
  await page.waitForURL(/event=2/,{timeout:10000});
  await page.goto(eventUrl(2),{waitUntil:'networkidle',timeout:30000});
  await waitTourReady(2);
  state=await tour();
  const e3Start={state,tag:await text('#mode-tag'),lead:await text('#mode-lead'),renderer:await renderer()};
  assert(state?.event===2&&state?.eventDef?.course==='double-orbit','event 3 route/state mismatch');
  assert(state?.worldMode==='racing','event 3 mode mismatch');
  assert(state?.car===1&&state?.power===1&&state?.armor===1,'car/upgrades did not persist into event 3');
  assert(Math.abs(state.hp/state.maxHP-beforeArmor.hull)<.04,'HULL did not carry into event 3');
  assert(e3Start.renderer!=='none','event 3 renderer missing');
  await snap('30-event3-double-orbit-menu.png');
  await page.click('#start');await page.waitForTimeout(700);await beginDriving();
  await page.keyboard.down('ArrowUp');await page.waitForTimeout(3000);await snap('31-event3-double-orbit-play.png');await page.keyboard.up('ArrowUp');
  await page.evaluate(()=>window.__breakCarsMayhemAuditFinish());await page.waitForTimeout(500);
  const finalVisible=await page.locator('.tour-final').isVisible();
  const finalText=await text('.tour-final');
  assert(finalVisible,'Tour final panel missing');
  assert(/MAYHEM TOUR COMPLETE/.test(finalText),'Tour completion copy missing');
  await assertResultBadgeClear('final');
  await snap('32-tour-complete.png');
  const finalState=await tour();
  assert(finalState?.results?.length>=3,'three Tour results were not recorded');

  report.events=[e1Start,e2Start,e3Start];
  report.final={state:finalState,text:finalText,visible:finalVisible,badgeClear:true};
  report.renderer=await renderer();
  assert(errors.length===0,`browser errors: ${errors.join(' | ')}`);
  await fs.writeFile(path.join(out,'diagnostics.json'),JSON.stringify(report,null,2));
  console.log(`MAYHEM TOUR audit PASS: car=${finalState.car} hull=${Math.round(finalState.hull*100)}% power=${finalState.power} armor=${finalState.armor} handling=${finalState.handling} total=${finalState.total} errors=${errors.length}`);
}catch(err){
  report.failure=String(err?.stack||err);
  try{await snap('99-failure.png');}catch{}
  await fs.writeFile(path.join(out,'diagnostics.json'),JSON.stringify(report,null,2));
  console.error(report.failure);
  process.exitCode=1;
}finally{
  await context.close();await browser.close();
}
