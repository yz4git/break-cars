import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const base=process.env.BREAK_CARS_AUDIT_URL||'http://127.0.0.1:4173/';
const out=path.resolve('artifacts/death-colosseum-audit');
await fs.rm(out,{recursive:true,force:true});
await fs.mkdir(out,{recursive:true});
const cases=[
 {course:'death-wheel',name:'DEATH WHEEL'},
 {course:'razor-cross',name:'RAZOR CROSS'},
 {course:'broken-orbit',name:'BROKEN ORBIT'},
 {course:'sky-tiles',name:'SKY TILES'},
 {course:'hex-drop',name:'HEX DROP'},
];
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist','--enable-unsafe-swiftshader','--use-angle=swiftshader-webgl','--disable-background-timer-throttling','--disable-renderer-backgrounding']});
const report=[];
const text=async(page,sel)=>{try{return (await page.locator(sel).innerText({timeout:800})).trim();}catch{return '';}};
const aliveCount=value=>Number((String(value).match(/\d+/)||['0'])[0]);
const state=async page=>({
 countdown:await text(page,'#countdown'),
 time:await text(page,'#time'),
 alive:await text(page,'#alive'),
 speed:await text(page,'#speed b'),
 score:await text(page,'#score'),
 toast:await text(page,'#toast'),
 modalVisible:await page.locator('#modal').evaluate(el=>!el.classList.contains('hidden')).catch(()=>false),
 result:await text(page,'#result-title'),
});
for(const item of cases){
 const dir=path.join(out,item.course);await fs.mkdir(dir,{recursive:true});
 const context=await browser.newContext({viewport:{width:852,height:393},deviceScaleFactor:1.25,isMobile:true,hasTouch:true,userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 26_6 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1'});
 const page=await context.newPage(),errors=[];
 page.on('console',m=>{if(m.type()==='error')errors.push(`console: ${m.text()}`);});page.on('pageerror',e=>errors.push(`page: ${String(e)}`));
 const url=`${base}?course=${encodeURIComponent(item.course)}&deathAudit=${Date.now()}`;
 await page.goto(url,{waitUntil:'networkidle',timeout:30000});await page.waitForTimeout(900);
 await page.screenshot({path:path.join(dir,'00-menu.png')});
 const menu={tag:await text(page,'#mode-tag'),subtitle:await text(page,'#mode-subtitle'),lead:await text(page,'#mode-lead'),course:await page.locator('#course-picker').inputValue(),modeSelected:await page.locator('[data-mode="death-colosseum"]').getAttribute('aria-pressed')};
 await page.click('#start');
 await page.waitForTimeout(800);await page.screenshot({path:path.join(dir,'05-countdown.png')});
 await page.waitForFunction(()=>!(document.querySelector('#countdown')?.textContent||'').trim(),null,{timeout:12000});
 await page.keyboard.down('ArrowUp');await page.waitForTimeout(1500);
 const liveStart=await state(page);await page.screenshot({path:path.join(dir,'10-follow.png')});
 for(let i=0;i<4;i++){const key=i%2?'ArrowRight':'ArrowLeft';await page.keyboard.down(key);await page.waitForTimeout(420);await page.keyboard.up(key);}
 const liveAction=await state(page);await page.screenshot({path:path.join(dir,'20-action.png')});
 await page.keyboard.up('ArrowUp');
 await page.keyboard.down('ArrowDown');await page.waitForTimeout(450);await page.keyboard.up('ArrowDown');await page.waitForTimeout(250);
 await page.keyboard.press('KeyC');await page.waitForTimeout(800);await page.screenshot({path:path.join(dir,'30-wide.png')});
 await page.keyboard.press('KeyC');await page.waitForTimeout(800);await page.screenshot({path:path.join(dir,'40-overhead.png')});
 const hud={position:await text(page,'#position-label'),alive:await text(page,'#alive'),scoreLabel:await text(page,'#score-label'),hp:await text(page,'#hp'),time:await text(page,'#time'),toast:await text(page,'#toast')};
 const renderer=await page.evaluate(()=>{const c=document.querySelector('canvas');if(!c)return'none';try{return c.getContext('webgl2')?'webgl2':c.getContext('webgl')?'webgl':'canvas';}catch{return'canvas';}});
 const deck=await page.evaluate(()=>({mode:document.body.dataset.gameMode||'',recoverHidden:document.querySelector('#recover')?.classList.contains('hidden')??true,courseHint:document.querySelector('.course-hint')?.textContent||''}));
 const row={...item,url,menu,liveStart,liveAction,hud,renderer,deck,errors};report.push(row);await fs.writeFile(path.join(dir,'diagnostics.json'),JSON.stringify(row,null,2));await context.close();
}
await browser.close();await fs.writeFile(path.join(out,'summary.json'),JSON.stringify(report,null,2));
const bad=report.filter(x=>x.errors.length||x.renderer==='none'||x.menu.modeSelected!=='true'||x.menu.course!==x.course||x.deck.mode!=='death-colosseum'||x.hud.scoreLabel!=='RING OUT SCORE'||x.liveStart.countdown||x.hud.time==='1:00'||Number(x.liveStart.speed)<=0||x.liveStart.modalVisible||x.liveAction.modalVisible||x.hud.hp==='0%'||aliveCount(x.hud.alive)<9);
console.log(`DEATH COLOSSEUM live audit: ${report.length} courses, errors=${bad.length}`);
for(const x of report)console.log(`${x.course.padEnd(14)} renderer=${x.renderer} start=${x.liveStart.time} action=${x.liveAction.time} speed=${x.liveAction.speed} alive=${x.hud.alive.replace(/\s+/g,' ')} result=${x.liveAction.result||'-'} errors=${x.errors.length}`);
if(bad.length){for(const x of bad)console.error(`DEATH LIVE REVIEW FAIL ${x.course}: ${x.errors.join('; ')||JSON.stringify({menu:x.menu,deck:x.deck,liveStart:x.liveStart,liveAction:x.liveAction,hud:x.hud})}`);process.exitCode=1;}
