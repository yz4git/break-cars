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
const startDriving=async()=>{await page.click('#start');await page.waitForTimeout(600);await page.waitForFunction(()=>typeof window.__breakCarsMayhemAuditStart==='function',null,{timeout:5000});await page.evaluate(()=>window.__breakCarsMayhemAuditStart());await page.waitForTimeout(350);};

try{
  // ACT I + live Director/RIVAL composition.
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

  // Finish event and review all editorial replay cameras.
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

  // ACT III REDLINE composition.
  await page.goto(url('rampage-3d',6),{waitUntil:'networkidle',timeout:30000});await waitReady(6,'ACT III');
  await snap('07-act3-menu.png');await startDriving();await page.waitForTimeout(900);
  const d7=await page.evaluate(()=>window.__breakCarsMayhemDirector);
  assert(d7?.act?.includes('ACT III'),'ACT III Director telemetry missing');
  await snap('08-act3-live.png');

  // FINAL ACT composition and final pressure read.
  await page.goto(url('double-orbit',8),{waitUntil:'networkidle',timeout:30000});await waitReady(8,'FINAL ACT');
  await snap('09-final-menu.png');await startDriving();await page.waitForTimeout(900);
  const d9=await page.evaluate(()=>window.__breakCarsMayhemDirector);
  assert(d9?.act?.includes('FINAL'),'FINAL ACT Director telemetry missing');
  assert((d9?.eventPressure||0)>=.85,'FINAL ACT pressure too low');
  await snap('10-final-live.png');

  assert(errors.length===0,`browser errors: ${errors.join(' | ')}`);
  await fs.writeFile(path.join(out,'diagnostics.json'),JSON.stringify({directorAct1:d,directorAct3:d7,directorFinal:d9,errors},null,2));
  console.log(`MAYHEM cinematic review PASS: act1=${d.state} act3=${d7.state} final=${d9.state}`);
}catch(err){
  try{await snap('98-failure.png');}catch{}
  await fs.writeFile(path.join(out,'diagnostics.json'),JSON.stringify({failure:String(err?.stack||err),errors},null,2));
  console.error(err);process.exitCode=1;
}finally{await context.close();await browser.close();}
