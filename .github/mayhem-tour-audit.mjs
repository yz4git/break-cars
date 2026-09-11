import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const base=(process.env.BREAK_CARS_AUDIT_URL||'http://127.0.0.1:4173/').replace(/\/?$/,'/');
const out=path.resolve('artifacts/mayhem-tour-audit');
const courses=['classic','crater-crown','maelstrom-pit','hunt-classic','cross-fire','tidal-foundry','rampage-3d','sky-forge','double-orbit'];
const acts=['ACT I','ACT I','ACT I','ACT II','ACT II','ACT II','ACT III','ACT III','FINAL ACT'];
const upgrades=['power','armor','handling','repair','power','armor','handling','repair'];
await fs.rm(out,{recursive:true,force:true});await fs.mkdir(out,{recursive:true});

const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist','--enable-unsafe-swiftshader','--use-angle=swiftshader-webgl','--disable-background-timer-throttling','--disable-renderer-backgrounding','--disable-backgrounding-occluded-windows']});
const context=await browser.newContext({viewport:{width:852,height:393},deviceScaleFactor:2,isMobile:true,hasTouch:true,userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 26_6 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1'});
const page=await context.newPage(),errors=[];
page.on('console',m=>{if(m.type()==='error')errors.push(`console: ${m.text()}`);});page.on('pageerror',e=>errors.push(`page: ${String(e)}`));
const text=async sel=>{try{return(await page.locator(sel).innerText({timeout:2500})).trim();}catch{return'';}};
const snap=async name=>page.screenshot({path:path.join(out,name),fullPage:false});
const tour=async()=>page.evaluate(()=>window.__breakCarsMayhemTour?.()??null);
const director=async()=>page.evaluate(()=>window.__breakCarsMayhemDirector??null);
const replay=async()=>page.evaluate(()=>window.__breakCarsHighlightReplay??null);
const recap=async()=>page.evaluate(()=>window.__breakCarsMayhemRecap??null);
const renderer=async()=>page.evaluate(()=>{const c=document.querySelector('canvas');if(!c)return'none';try{return c.getContext('webgl2')?'webgl2':c.getContext('webgl')?'webgl':'canvas';}catch{return'canvas';}});
const assert=(ok,msg)=>{if(!ok)throw new Error(msg);};
const eventUrl=i=>`${base}?course=${courses[i]}&tour=1&event=${i}&tourAudit=1`;
const waitTourReady=async i=>{await page.waitForFunction(({index,act})=>{const s=window.__breakCarsMayhemTour?.(),tag=document.querySelector('#mode-tag')?.textContent||'';return s?.event===index&&s?.tourLength===9&&document.body.classList.contains('mayhem-tour')&&tag.includes(act);},{index:i,act:acts[i]},{timeout:10000});await page.waitForTimeout(180);};
const beginDriving=async()=>{await page.click('#start');await page.waitForTimeout(650);await page.waitForFunction(()=>typeof window.__breakCarsMayhemAuditStart==='function',null,{timeout:5000});await page.evaluate(()=>window.__breakCarsMayhemAuditStart());await page.waitForTimeout(450);};
const finishEvent=async()=>{await page.evaluate(()=>window.__breakCarsMayhemAuditFinish());await page.waitForTimeout(420);};
const assertCleanResult=async label=>{assert(await page.locator('#tour-run-badge').count()===0,`${label}: Tour badge overlaps result`);assert(!(await page.locator('#driving').isVisible()),`${label}: driving HUD visible behind result`);assert(!(await page.locator('#hunt-nav').isVisible()),`${label}: target nav visible behind result`);};

const report={menu:null,events:[],errors};
try{
  await page.goto(`${base}?course=classic`,{waitUntil:'networkidle',timeout:30000});await page.waitForTimeout(500);
  report.menu={tourVisible:await page.locator('#mayhem-tour-entry').isVisible(),label:await text('#mayhem-tour-entry'),modes:await page.locator('[data-mode]').count()};
  assert(report.menu.tourVisible,'MAYHEM TOUR entry missing');assert(/9 COURSE RUN/.test(report.menu.label),'9-course menu label missing');assert(report.menu.modes===3,`expected 3 ordinary modes, got ${report.menu.modes}`);await snap('00-normal-menu.png');

  await page.goto(eventUrl(0),{waitUntil:'networkidle',timeout:30000});
  await page.evaluate(()=>{const k='break-cars-mayhem-tour-v2',s=JSON.parse(sessionStorage.getItem(k));s.car=1;s.hull=.71;s.rivalHull=.82;sessionStorage.setItem(k,JSON.stringify(s));});await page.reload({waitUntil:'networkidle'});

  let persistentRival=null;
  for(let i=0;i<courses.length;i++){
    await waitTourReady(i);const before=await tour(),tag=await text('#mode-tag');
    assert(tag.includes(acts[i]),`event ${i+1}: expected ${acts[i]} in mode tag, got ${tag}`);assert(before?.eventDef?.course===courses[i],`event ${i+1}: course mismatch ${before?.eventDef?.course}`);assert(before?.tourLength===9,`event ${i+1}: tour length is not 9`);
    if(i===0){assert(Math.abs(before.hp/before.maxHP-.71)<.04,'event 1: player HULL seed mismatch');assert(Math.abs((before.rival?.hp||0)/(before.rival?.maxHP||1)-.82)<.05,'event 1: RIVAL HULL seed mismatch');persistentRival=before.rival?.id;}else assert(before.rival?.id===persistentRival,`event ${i+1}: persistent RIVAL changed`);
    assert((await renderer())!=='none',`event ${i+1}: renderer missing`);await snap(`${String(i+1).padStart(2,'0')}-menu-${courses[i]}.png`);

    await beginDriving();await page.keyboard.down('ArrowUp');
    if(i===0){
      // SwiftShader can run far below real-time. Eighteen recorded frames are
      // enough for the replay's three editorial thirds while keeping CI robust.
      await page.waitForFunction(()=>{const r=window.__breakCarsHighlightReplay;return (r?.bestFrames||r?.frames||0)>=18;},null,{timeout:30000,polling:250});
    }else await page.waitForTimeout(520);
    await page.keyboard.up('ArrowUp');
    const liveDirector=await director();assert(liveDirector&&['BUILD','PRESSURE','RIVAL RUSH','RELIEF','FINALE'].includes(liveDirector.state),`event ${i+1}: Director telemetry missing`);assert(liveDirector.rivalId===persistentRival,`event ${i+1}: Director RIVAL mismatch`);assert(typeof liveDirector.eventPressure==='number',`event ${i+1}: v8 Director pressure telemetry missing`);assert(String(liveDirector.act||'').includes(acts[i].replace('FINAL ACT','FINAL')),`event ${i+1}: Director act telemetry mismatch ${liveDirector.act}`);assert(await page.locator('#mayhem-director').count()===1,`event ${i+1}: compact Director HUD missing`);assert(await page.locator('#mayhem-rival-marker').count()===1,`event ${i+1}: RIVAL marker was not created`);
    if(i===0)await snap('01-live-director.png');if(i===6)await snap('07-live-redline.png');if(i===8)await snap('09-live-final-act.png');

    await finishEvent();await assertCleanResult(`event ${i+1}`);const after=await tour();assert(after?.results?.[i]?.course===courses[i],`event ${i+1}: result not recorded`);assert(after?.results?.[i]?.director,`event ${i+1}: Director result not recorded`);assert(await page.locator('.tour-rival-status').count()===1,`event ${i+1}: PIT/final RIVAL status missing`);

    if(i===0){
      const replayButton=page.locator('[data-tour-replay]');assert(await replayButton.isVisible(),'event 1: HIGHLIGHT REPLAY button missing');const replayState=await replay();assert((replayState?.frames||0)>=18,`event 1: highlight window too short (${replayState?.frames||0})`);
      await replayButton.click();await page.waitForFunction(()=>window.__breakCarsHighlightReplay?.playing===true,null,{timeout:3000});await page.waitForFunction(()=>document.body.classList.contains('mayhem-replay-active')&&document.querySelector('#mayhem-letterbox')&&window.__breakCarsHighlightReplay?.shot==='CHASE',null,{timeout:3000});
      assert(await page.locator('#mayhem-letterbox').isVisible(),'event 1: cinematic letterbox missing');assert(!(await page.locator('#hud').isVisible()),'event 1: ordinary HUD visible during replay');assert(!(await page.locator('#driving').isVisible()),'event 1: driving controls visible during replay');await snap('02a-highlight-chase.png');
      await page.waitForFunction(()=>window.__breakCarsHighlightReplay?.shot==='RIVAL TWO-SHOT',null,{timeout:8000});await snap('02b-highlight-rival-two-shot.png');await page.waitForFunction(()=>window.__breakCarsHighlightReplay?.shot==='IMPACT CLOSE',null,{timeout:8000});await snap('02c-highlight-impact-close.png');await page.waitForFunction(()=>window.__breakCarsHighlightReplay?.playing===false,null,{timeout:12000});
      assert(await page.locator('#modal').isVisible(),'event 1: result modal did not return after replay');assert(!(await page.locator('body').evaluate(el=>el.classList.contains('mayhem-replay-active'))),'event 1: replay body class leaked after playback');
    }

    report.events.push({index:i,course:courses[i],act:acts[i],before,after,director:liveDirector});
    if(i===courses.length-1){
      assert(await page.locator('.tour-final').isVisible(),'final Tour panel missing');assert(/MAYHEM TOUR COMPLETE/.test(await text('.tour-final')),'completion copy missing');
      assert(await page.locator('.tour-recap-panel').isVisible(),'v8.9 final TOUR RECAP panel missing');assert(await page.locator('.tour-recap-timeline i').count()===9,'v8.9 final timeline does not contain nine events');
      const recapState=await recap();assert(recapState?.stage==='READY',`v8.9 recap not READY (${recapState?.stage})`);assert(recapState?.stats?.events===9,`v8.9 recap expected 9 results, got ${recapState?.stats?.events}`);assert(await page.locator('[data-tour-recap-film]').isVisible(),'v8.9 PLAY TOUR RECAP button missing');
      await snap('99-tour-complete.png');break;
    }
    const up=upgrades[i],button=page.locator(`[data-tour-up="${up}"]`);assert(await button.isVisible(),`event ${i+1}: PIT ${up} missing`);assert(!(await button.isDisabled()),`event ${i+1}: PIT ${up} unexpectedly disabled`);await button.click();await page.waitForURL(new RegExp(`event=${i+1}`),{timeout:10000});await page.goto(eventUrl(i+1),{waitUntil:'networkidle',timeout:30000});
  }

  const finalState=await tour(),finalRecap=await recap();assert(finalState?.results?.length>=9,'nine Tour results were not recorded');assert(finalState?.rival?.id===persistentRival,'RIVAL changed before Tour completion');assert(finalRecap?.stats?.events===9,'recap telemetry lost completed Tour results');report.final={state:finalState,replay:await replay(),recap:finalRecap,renderer:await renderer()};assert(errors.length===0,`browser errors: ${errors.join(' | ')}`);await fs.writeFile(path.join(out,'diagnostics.json'),JSON.stringify(report,null,2));console.log(`MAYHEM TOUR v8.9 visual audit PASS: results=${finalState.results.length} recap=${finalRecap.stats.events} rival=${persistentRival} hull=${Math.round(finalState.hull*100)}% total=${finalState.total} errors=${errors.length}`);
}catch(err){report.failure=String(err?.stack||err);try{await snap('98-failure.png');}catch{}await fs.writeFile(path.join(out,'diagnostics.json'),JSON.stringify(report,null,2));console.error(report.failure);process.exitCode=1;}finally{await context.close();await browser.close();}
