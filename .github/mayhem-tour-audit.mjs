import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const base=(process.env.BREAK_CARS_AUDIT_URL||'http://127.0.0.1:4173/').replace(/\/?$/,'/');
const out=path.resolve('artifacts/mayhem-tour-audit');
const courses=[
  'classic','crater-crown','maelstrom-pit',
  'hunt-classic','cross-fire','tidal-foundry',
  'rampage-3d','sky-forge','double-orbit'
];
const upgrades=['power','armor','handling','repair','power','armor','handling','repair'];
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
const text=async sel=>{try{return (await page.locator(sel).innerText({timeout:2500})).trim();}catch{return'';}};
const snap=async name=>page.screenshot({path:path.join(out,name),fullPage:false});
const tour=async()=>page.evaluate(()=>window.__breakCarsMayhemTour?.()??null);
const director=async()=>page.evaluate(()=>window.__breakCarsMayhemDirector??null);
const replay=async()=>page.evaluate(()=>window.__breakCarsHighlightReplay??null);
const renderer=async()=>page.evaluate(()=>{const c=document.querySelector('canvas');if(!c)return'none';try{return c.getContext('webgl2')?'webgl2':c.getContext('webgl')?'webgl':'canvas';}catch{return'canvas';}});
const assert=(ok,msg)=>{if(!ok)throw new Error(msg);};
const firstUrl=`${base}?course=${courses[0]}&tour=1&event=0&tourAudit=1`;
const waitTourReady=async i=>{
  await page.waitForFunction(index=>{
    const state=window.__breakCarsMayhemTour?.();
    return state?.event===index&&state?.tourLength===9&&document.querySelector('#mode-tag')?.textContent?.includes('MAYHEM TOUR');
  },i,{timeout:10000});
  await page.waitForTimeout(180);
};
const beginDriving=async()=>{
  await page.click('#start');
  await page.waitForTimeout(650);
  await page.waitForFunction(()=>typeof window.__breakCarsMayhemAuditStart==='function',{timeout:5000});
  await page.evaluate(()=>window.__breakCarsMayhemAuditStart());
  await page.waitForTimeout(450);
};
const finishEvent=async()=>{
  await page.evaluate(()=>window.__breakCarsMayhemAuditFinish());
  await page.waitForTimeout(420);
};
const assertCleanResult=async label=>{
  assert(await page.locator('#tour-run-badge').count()===0,`${label}: Tour badge overlaps result`);
  assert(!(await page.locator('#driving').isVisible()),`${label}: driving HUD visible behind result`);
  assert(!(await page.locator('#hunt-nav').isVisible()),`${label}: target nav visible behind result`);
};

const report={menu:null,events:[],errors};
try{
  await page.goto(`${base}?course=classic`,{waitUntil:'networkidle',timeout:30000});
  await page.waitForTimeout(500);
  report.menu={tourVisible:await page.locator('#mayhem-tour-entry').isVisible(),label:await text('#mayhem-tour-entry'),modes:await page.locator('[data-mode]').count()};
  assert(report.menu.tourVisible,'MAYHEM TOUR entry missing');
  assert(/9 COURSE RUN/.test(report.menu.label),'9-course menu label missing');
  assert(report.menu.modes===3,`expected 3 ordinary modes, got ${report.menu.modes}`);
  await snap('00-normal-menu.png');

  await page.goto(firstUrl,{waitUntil:'networkidle',timeout:30000});
  await page.evaluate(()=>{
    const k='break-cars-mayhem-tour-v2';
    const s=JSON.parse(sessionStorage.getItem(k));
    s.car=1;s.hull=.71;s.rivalHull=.82;
    sessionStorage.setItem(k,JSON.stringify(s));
  });
  await page.reload({waitUntil:'networkidle'});

  let persistentRival=null;
  for(let i=0;i<courses.length;i++){
    await waitTourReady(i);
    const before=await tour();
    assert(before?.eventDef?.course===courses[i],`event ${i+1}: course mismatch ${before?.eventDef?.course}`);
    assert(before?.tourLength===9,`event ${i+1}: tour length is not 9`);
    if(i===0){
      assert(Math.abs(before.hp/before.maxHP-.71)<.04,`event 1: player HULL seed mismatch`);
      assert(Math.abs((before.rival?.hp||0)/(before.rival?.maxHP||1)-.82)<.05,`event 1: RIVAL HULL seed mismatch`);
      persistentRival=before.rival?.id;
    }else{
      assert(before.rival?.id===persistentRival,`event ${i+1}: persistent RIVAL changed`);
    }
    assert(await renderer()!=='none',`event ${i+1}: renderer missing`);
    await snap(`${String(i+1).padStart(2,'0')}-menu-${courses[i]}.png`);

    await beginDriving();
    await page.keyboard.down('ArrowUp');
    await page.waitForTimeout(i===0?1600:520);
    await page.keyboard.up('ArrowUp');
    const liveDirector=await director();
    assert(liveDirector&&['BUILD','PRESSURE','RIVAL RUSH','RELIEF','FINALE'].includes(liveDirector.state),`event ${i+1}: Director telemetry missing`);
    assert(liveDirector.rivalId===persistentRival,`event ${i+1}: Director RIVAL mismatch`);
    if(i===0)await snap('01-live-director.png');

    await finishEvent();
    await assertCleanResult(`event ${i+1}`);
    const after=await tour();
    assert(after?.results?.[i]?.course===courses[i],`event ${i+1}: result not recorded`);
    assert(after?.results?.[i]?.director,`event ${i+1}: Director result not recorded`);

    if(i===0){
      const replayButton=page.locator('[data-tour-replay]');
      assert(await replayButton.isVisible(),'event 1: HIGHLIGHT REPLAY button missing');
      const replayState=await replay();
      assert((replayState?.frames||0)>=2,'event 1: highlight frames were not captured');
      await replayButton.click();
      await page.waitForFunction(()=>window.__breakCarsHighlightReplay?.playing===true,{timeout:3000});
      await snap('02-highlight-replay.png');
      await page.waitForFunction(()=>window.__breakCarsHighlightReplay?.playing===false,{timeout:12000});
      assert(await page.locator('#modal').isVisible(),'event 1: result modal did not return after replay');
    }

    report.events.push({index:i,course:courses[i],before,after,director:liveDirector});
    if(i===courses.length-1){
      assert(await page.locator('.tour-final').isVisible(),'final Tour panel missing');
      assert(/MAYHEM TOUR COMPLETE/.test(await text('.tour-final')),'completion copy missing');
      await snap('99-tour-complete.png');
      break;
    }

    const up=upgrades[i];
    const button=page.locator(`[data-tour-up="${up}"]`);
    assert(await button.isVisible(),`event ${i+1}: PIT ${up} missing`);
    assert(!(await button.isDisabled()),`event ${i+1}: PIT ${up} unexpectedly disabled`);
    await button.click();
    await page.waitForURL(new RegExp(`event=${i+1}`),{timeout:10000});
  }

  const finalState=await tour();
  assert(finalState?.results?.length>=9,'nine Tour results were not recorded');
  assert(finalState?.rival?.id===persistentRival,'RIVAL changed before Tour completion');
  report.final={state:finalState,replay:await replay(),renderer:await renderer()};
  assert(errors.length===0,`browser errors: ${errors.join(' | ')}`);
  await fs.writeFile(path.join(out,'diagnostics.json'),JSON.stringify(report,null,2));
  console.log(`MAYHEM TOUR 9-course audit PASS: results=${finalState.results.length} rival=${persistentRival} hull=${Math.round(finalState.hull*100)}% total=${finalState.total} errors=${errors.length}`);
}catch(err){
  report.failure=String(err?.stack||err);
  try{await snap('98-failure.png');}catch{}
  await fs.writeFile(path.join(out,'diagnostics.json'),JSON.stringify(report,null,2));
  console.error(report.failure);
  process.exitCode=1;
}finally{
  await context.close();await browser.close();
}
