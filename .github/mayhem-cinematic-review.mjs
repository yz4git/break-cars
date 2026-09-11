import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const base=(process.env.BREAK_CARS_AUDIT_URL||'http://127.0.0.1:4173/').replace(/\/?$/,'/');
const out=path.resolve('artifacts/mayhem-cinematic-review');
await fs.rm(out,{recursive:true,force:true});
await fs.mkdir(out,{recursive:true});

const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist','--enable-unsafe-swiftshader','--use-angle=swiftshader-webgl','--disable-background-timer-throttling','--disable-renderer-backgrounding','--disable-backgrounding-occluded-windows']});
const context=await browser.newContext({viewport:{width:852,height:393},deviceScaleFactor:2,isMobile:true,hasTouch:true,userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 26_6 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1'});
const page=await context.newPage();
const errors=[];
page.on('console',m=>{if(m.type()==='error')errors.push(`console: ${m.text()}`);});
page.on('pageerror',e=>errors.push(`page: ${String(e)}`));
const snap=name=>page.screenshot({path:path.join(out,name),fullPage:false});
const assert=(ok,msg)=>{if(!ok)throw new Error(msg);};
const url=(course,event)=>`${base}?course=${course}&tour=1&event=${event}&tourAudit=1`;
const waitReady=async(event,act)=>{await page.waitForFunction(({event,act})=>{const s=window.__breakCarsMayhemTour?.(),tag=document.querySelector('#mode-tag')?.textContent||'';return s?.event===event&&s?.tourLength===9&&tag.includes(act)&&document.body.classList.contains('mayhem-tour');},{event,act},{timeout:10000});await page.waitForTimeout(220);};
const auditStart=async()=>{await page.waitForFunction(()=>typeof window.__breakCarsMayhemAuditStart==='function',null,{timeout:5000});await page.evaluate(()=>window.__breakCarsMayhemAuditStart());await page.waitForTimeout(350);};
const startDriving=async()=>{await page.click('#start');await page.waitForTimeout(600);await auditStart();};

try{
  await page.goto(url('classic',0),{waitUntil:'networkidle',timeout:30000});
  await waitReady(0,'ACT I');
  await page.evaluate(()=>{const k='break-cars-mayhem-tour-v2',s=JSON.parse(sessionStorage.getItem(k));s.car=1;s.hull=.71;s.rivalHull=.82;s.rivalHeat=2;sessionStorage.setItem(k,JSON.stringify(s));});
  await page.reload({waitUntil:'networkidle'});await waitReady(0,'ACT I');
  await snap('00-act1-menu.png');
  await startDriving();await page.keyboard.down('ArrowUp');
  await page.waitForFunction(()=>{const r=window.__breakCarsHighlightReplay;return (r?.bestFrames||r?.frames||0)>=18;},null,{timeout:30000,polling:250});
  await page.keyboard.up('ArrowUp');
  const d=await page.evaluate(()=>window.__breakCarsMayhemDirector);
  assert(d&&d.act?.includes('ACT I'),'ACT I Director telemetry missing');
  assert(await page.locator('#mayhem-director').count()===1,'Director HUD missing');
  assert(await page.locator('#mayhem-rival-marker').count()===1,'RIVAL marker missing');
  await snap('01-act1-live.png');

  await page.evaluate(()=>window.__breakCarsMayhemAuditFinish());await page.waitForTimeout(400);
  const replayButton=page.locator('[data-tour-replay]');
  assert(await replayButton.isVisible(),'HIGHLIGHT REPLAY button missing');
  await replayButton.click();
  await page.waitForFunction(()=>window.__breakCarsHighlightReplay?.shot==='CHASE'&&document.body.classList.contains('mayhem-replay-active'),null,{timeout:4000});
  assert(!(await page.locator('#hud').isVisible()),'HUD visible in replay');
  assert(!(await page.locator('#driving').isVisible()),'controls visible in replay');
  await snap('02a-replay-chase.png');
  await page.waitForFunction(()=>window.__breakCarsHighlightReplay?.shot==='RIVAL TWO-SHOT',null,{timeout:8000});
  await snap('02b-replay-rival-two-shot.png');
  await page.waitForFunction(()=>window.__breakCarsHighlightReplay?.shot==='IMPACT CLOSE',null,{timeout:8000});
  await snap('02c-replay-impact-close.png');
  await page.waitForFunction(()=>window.__breakCarsHighlightReplay?.playing===false,null,{timeout:12000});

  await page.goto(url('rampage-3d',6),{waitUntil:'networkidle',timeout:30000});await waitReady(6,'ACT III');
  await snap('07-act3-menu.png');await startDriving();await page.waitForTimeout(900);
  const d7=await page.evaluate(()=>window.__breakCarsMayhemDirector);
  assert(d7?.act?.includes('ACT III'),'ACT III Director telemetry missing');
  await snap('08-act3-live.png');

  await page.goto(url('double-orbit',8),{waitUntil:'networkidle',timeout:30000});await waitReady(8,'FINAL ACT');
  await page.evaluate(()=>{
    const k='break-cars-mayhem-tour-v2',s=JSON.parse(sessionStorage.getItem(k));
    const courses=['classic','crater-crown','maelstrom-pit','hunt-classic','cross-fire','tidal-foundry','rampage-3d','sky-forge'];
    const scores=[1680,2140,1920,2860,2330,2510,3180,2940],hulls=[.91,.78,.84,.62,.73,.68,.55,.64],directors=['PRESSURE','RIVAL RUSH','FINALE','PRESSURE','RIVAL RUSH','FINALE','RIVAL RUSH','FINALE'];
    s.results=courses.map((course,i)=>({course,score:scores[i],hull:hulls[i],rivalHull:Math.max(.24,.88-i*.07),director:directors[i],rivalResult:i%2===0?'PLAYER':'RIVAL',series:{player:Math.ceil((i+1)/2),rival:Math.floor((i+1)/2)}}));
    s.rivalryPlayer=4;s.rivalryRival=4;s.total=scores.reduce((a,b)=>a+b,0);s.hull=.64;s.rivalHull=.52;s.rivalHeat=5;s.event=8;
    sessionStorage.setItem(k,JSON.stringify(s));
  });
  await page.reload({waitUntil:'networkidle'});await waitReady(8,'FINAL ACT');
  await snap('09-final-menu.png');
  await page.click('#start');
  await page.waitForFunction(()=>window.__breakCarsMayhemShowdown?.stage==='FACE OFF'&&document.body.classList.contains('mayhem-showdown-intro'),null,{timeout:4000});
  assert(await page.locator('#mayhem-showdown-intro').isVisible(),'FINAL SHOWDOWN face-off overlay missing');
  assert((await page.locator('#mayhem-showdown-intro').innerText()).includes('FINAL SHOWDOWN'),'FINAL SHOWDOWN face-off copy missing');
  assert(!(await page.locator('#driving').isVisible()),'driving HUD visible during FINAL SHOWDOWN face-off');
  await snap('10-final-face-off.png');
  await auditStart();
  await page.waitForTimeout(1900);
  const d9=await page.evaluate(()=>window.__breakCarsMayhemDirector);
  const duel=await page.evaluate(()=>window.__breakCarsMayhemFinalDuel);
  assert(d9?.act?.includes('FINAL'),'FINAL ACT Director telemetry missing');
  assert((d9?.eventPressure||0)>=.85,'FINAL ACT pressure too low');
  assert(duel?.active===true&&duel.phase>=1,'FINAL DUEL telemetry missing');
  await snap('11-final-live.png');

  await page.keyboard.down('ArrowUp');
  await page.waitForFunction(()=>{const r=window.__breakCarsHighlightReplay;return (r?.frames||0)>=18;},null,{timeout:30000,polling:250});
  await page.keyboard.up('ArrowUp');
  await page.evaluate(()=>window.__breakCarsMayhemAuditFinish());
  await page.waitForTimeout(500);
  const finalReplay=page.locator('[data-tour-replay]');
  assert(await finalReplay.isVisible(),'SHOWDOWN replay button missing');
  const finalReplayText=await finalReplay.innerText();
  assert(finalReplayText.includes('SHOWDOWN REPLAY')&&finalReplayText.includes('SLOW MOTION'),'final replay button did not switch to compact v8.10 showdown copy');
  const frozen=await page.evaluate(()=>window.__breakCarsHighlightReplay);
  assert((frozen?.frames||0)>=28&&frozen?.finishCut===true,'finish-focused FINAL SHOWDOWN replay was not frozen');
  const recapPanel=page.locator('.tour-recap-panel');
  assert(await recapPanel.isVisible(),'v8.9 TOUR RECAP result panel missing');
  assert(await page.locator('.tour-recap-timeline i').count()===9,'v8.9 nine-event timeline missing');
  const recapReady=await page.evaluate(()=>window.__breakCarsMayhemRecap);
  assert(recapReady?.stage==='READY'&&recapReady?.stats?.events===9,'v8.9 recap did not collect nine event results');
  await snap('12-final-result.png');

  await finalReplay.click();
  await page.waitForFunction(()=>window.__breakCarsMayhemShowdown?.stage==='FINISH REPLAY'&&window.__breakCarsHighlightReplay?.playing===true,null,{timeout:5000});
  const showdownOverlay=page.locator('#mayhem-replay-overlay[data-showdown="1"]');
  assert(await showdownOverlay.isVisible(),'FINAL SHOWDOWN replay overlay missing');
  const showdownText=await showdownOverlay.innerText();
  assert(showdownText.includes('FINAL SHOWDOWN REPLAY')&&showdownText.includes('SLOW MOTION'),'showdown replay title/slow-motion copy missing');
  assert(!(await page.locator('#hud').isVisible()),'HUD visible in FINAL SHOWDOWN replay');
  assert(!(await page.locator('#driving').isVisible()),'controls visible in FINAL SHOWDOWN replay');
  await snap('13-final-showdown-replay.png');

  const ending=page.locator('#mayhem-showdown-ending');
  await ending.waitFor({state:'visible',timeout:12000});
  await page.waitForFunction(()=>document.querySelector('#mayhem-showdown-ending')?.classList.contains('show'),null,{timeout:12000});
  assert(await ending.count()===1,'FINAL SHOWDOWN ending card missing');
  const endingText=await ending.innerText();
  assert(endingText.includes('MAYHEM TOUR CHAMPION')||endingText.includes('RIVAL OWNS THE NIGHT'),'FINAL SHOWDOWN ending verdict missing');
  assert(await page.locator('body').evaluate(el=>el.classList.contains('mayhem-showdown-ending-active')),'v8.10 isolated ending state missing');
  await snap('14-final-ending.png');
  const showdown=await page.evaluate(()=>window.__breakCarsMayhemShowdown);
  await page.waitForFunction(()=>!document.body.classList.contains('mayhem-showdown-ending-active'),null,{timeout:5000});

  const recapButton=page.locator('[data-tour-recap-film]');
  assert(await recapButton.isVisible(),'PLAY TOUR RECAP button missing');
  assert((await recapButton.innerText()).includes('PLAY TOUR RECAP'),'TOUR RECAP CTA copy missing');
  await recapButton.click();
  await page.waitForFunction(()=>window.__breakCarsMayhemRecap?.stage==='OPENING'&&window.__breakCarsMayhemRecap?.active===true,null,{timeout:4000});
  assert(await page.locator('#mayhem-tour-recap').isVisible(),'TOUR RECAP film overlay missing');
  assert(!(await page.locator('#hud').isVisible()),'HUD visible during TOUR RECAP film');
  assert(!(await page.locator('#driving').isVisible()),'controls visible during TOUR RECAP film');
  await snap('15-tour-recap-opening.png');
  await page.waitForFunction(()=>window.__breakCarsMayhemRecap?.stage==='EVENT'&&window.__breakCarsMayhemRecap?.index>=3,null,{timeout:7000});
  assert(await page.locator('.mayhem-recap-track i').count()===9,'TOUR RECAP film timeline missing');
  await snap('16-tour-recap-event.png');
  await page.waitForFunction(()=>window.__breakCarsMayhemRecap?.stage==='FINAL',null,{timeout:10000});
  const recapFinalText=await page.locator('.mayhem-recap-stage').innerText();
  assert(recapFinalText.includes('MAYHEM TOUR CHAMPION')||recapFinalText.includes('RIVAL WINS THE TOUR'),'TOUR RECAP final verdict missing');
  await snap('17-tour-recap-final.png');
  await page.waitForFunction(()=>window.__breakCarsMayhemRecap?.stage==='COMPLETE'&&window.__breakCarsMayhemRecap?.completed===true&&window.__breakCarsMayhemRecap?.active===false,null,{timeout:5000});
  assert(await page.locator('#mayhem-tour-recap').count()===0,'TOUR RECAP overlay did not close after completion');
  assert(await page.locator('#modal').isVisible(),'result modal did not return after TOUR RECAP');
  const recap=await page.evaluate(()=>window.__breakCarsMayhemRecap);

  assert(errors.length===0,`browser errors: ${errors.join(' | ')}`);
  await fs.writeFile(path.join(out,'diagnostics.json'),JSON.stringify({directorAct1:d,directorAct3:d7,directorFinal:d9,finalDuel:duel,finalReplayFrozen:frozen,showdown,recapReady,recap,errors},null,2));
  console.log(`MAYHEM cinematic review PASS: act1=${d.state} act3=${d7.state} final=${d9.state} showdown=${showdown?.stage} recap=${recap?.stage}`);
}catch(err){
  try{await snap('98-failure.png');}catch{}
  await fs.writeFile(path.join(out,'diagnostics.json'),JSON.stringify({failure:String(err?.stack||err),errors},null,2));
  console.error(err);process.exitCode=1;
}finally{await context.close();await browser.close();}
