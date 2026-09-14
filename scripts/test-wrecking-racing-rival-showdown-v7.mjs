import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';

const selected=process.env.WRECK_SHOWDOWN_COURSE;
if(!selected){
  for(const id of ['rampage-3d','sky-forge','double-orbit']){
    const r=spawnSync(process.execPath,[import.meta.filename],{env:{...process.env,WRECK_SHOWDOWN_COURSE:id},encoding:'utf8'});
    process.stdout.write(r.stdout||'');process.stderr.write(r.stderr||'');assert.equal(r.status,0,`${id}: rival showdown v7 regression failed`);
  }
  console.log('WRECKING RACING rival showdown v7: all 3 courses passed');
  process.exit(0);
}

globalThis.location={search:`?course=${selected}`};
const stamp=`${selected}-${Date.now()}`;
const racing=await import(`../_site/racing.js?showdown=${stamp}`);
const {LENGTH,trackPoint,racingTacticalZone,racingRivalPersonality,racingRivalSignature,racingAI}=racing;
for(const fn of [trackPoint,racingTacticalZone,racingRivalPersonality,racingRivalSignature,racingAI])assert.equal(typeof fn,'function');

const cases={
  BRAWLER:{gap:6,tactic:'neutral'},
  HUNTER:{gap:8,tactic:'neutral'},
  BLOCKER:{gap:-6,tactic:'neutral'},
  DAREDEVIL:{gap:8,tactic:'overtake'},
};
const expected=new Map([['BRAWLER','BODY CHECK'],['HUNTER','LOCK ON'],['BLOCKER','SHUT DOOR'],['DAREDEVIL','CROSS CUT']]);
for(const key of expected.keys()){
  const persona={key,side:1};const cfg=cases[key];
  let normal=null;
  for(let t=0;t<4;t+=.1){const q=racingRivalSignature(persona,cfg.gap,1.2,-.8,cfg.tactic,false,true,t,3);if(q.active){normal=q;break;}}
  assert(normal,`${selected}: ${key} signature never entered its safe-road cadence`);
  assert.equal(normal.label,expected.get(key));
  assert.equal(normal.safe,true);
  assert(normal.strength>0&&normal.strength<=.36+1e-9,`${key}: signature strength escaped cap`);
  assert(Math.abs(normal.laneGoal)<=5.05+1e-9,`${key}: signature lane goal escaped safety envelope`);
  const finale=racingRivalSignature(persona,cfg.gap,1.2,-.8,cfg.tactic,true,true,.25,3);
  assert.equal(finale.active,true,`${key}: FINAL DUEL must activate signature cadence on safe road`);
  assert(finale.strength>=normal.strength,`${key}: FINAL DUEL weakened signature pressure`);
  assert(finale.strength<=.36+1e-9,`${key}: FINAL DUEL signature escaped strength cap`);
  const jump=racingRivalSignature(persona,cfg.gap,1.2,-.8,'jump-flight',true,true,.25,3);
  assert.equal(jump.active,false,`${key}: signature activated in jump flight`);assert.equal(jump.strength,0);
}
assert.equal(new Set([...expected.values()]).size,4,'signature labels must remain distinct');

const gameSource=await readFile(new URL('../_site/game.js',import.meta.url),'utf8');
const racingSource=await readFile(new URL('../_site/racing.js',import.meta.url),'utf8');
const racingCss=await readFile(new URL('../_site/racing.css',import.meta.url),'utf8');
assert.match(racingSource,/WRECKING_RACING_RIVAL_SHOWDOWN_V7/,'v7 runtime marker missing');
assert.match(racingSource,/c\.raceRivalSignature=\{version:'7\.0'/,'AI signature telemetry not wired');
assert.match(gameSource,/__breakCarsRivalShowdownV7/,'showdown telemetry missing');
assert.match(gameSource,/ARCH RIVAL #/,'arch-rival arrival presentation missing');
assert.match(gameSource,/FINAL DUEL ·/,'final-duel presentation missing');
assert.match(gameSource,/RIVAL DEFEATED/,'result presentation missing');
assert.match(racingCss,/#race-showdown-v7/,'showdown styling missing');

const {makeWorld}=await import(`../_site/physics.js?showdown=${stamp}`);
const w=makeWorld(0,9261,'racing');w.endAt=999;w.limit=999;w.done=false;
w.raceRivalId=1;w.raceRivalFeud={version:'5.0',history:{},archId:1,revengeId:-1,revengeUntil:-1,finalDuelId:-1,finalDuelAnnounced:false,finalDuelResolved:false,lastDefeatedId:-1,lastEvent:'',lastEventAt:-99};
const player=w.cars[0],rival=w.cars[1],persona=racingRivalPersonality(1,selected);
const wrap=s=>(s%LENGTH+LENGTH)%LENGTH;
const place=(car,s,lane,raceDistance=s)=>{const p=trackPoint(s,lane);Object.assign(car,{x:p.x,z:p.z,heading:p.heading,trackS:wrap(s),raceDistance,lane,dead:false,finished:false,aiReverse:0,stallTime:0,battleTimer:1});if(car.p3)Object.assign(car.p3,{px:p.x,py:p.y??0,pz:p.z,vx:0,vy:0,vz:0});};
const desiredGap=persona.key==='BLOCKER'?-3:3;
let safeSample=null;
for(let s=0;s<LENGTH&&!safeSample;s+=6){
  const p=trackPoint(s,0),zone=racingTacticalZone(s),kind=String(p.kind||'');
  if(kind==='loop'||kind.startsWith('jump')||zone.type==='jump-split'||zone.type==='jump-flight')continue;
  for(let t=0;t<4;t+=.1){
    w.time=t;const pd=s+desiredGap;place(player,pd,.45,pd);place(rival,s,-.45,s);rival.battleTarget=0;delete rival.raceRivalSignature;
    const score=rival.score,hp=rival.hp;racingAI(w,rival,1/60);const sig=rival.raceRivalSignature;
    if(sig?.active){safeSample={s,zone:zone.type,sig:{...sig}};assert.equal(rival.score,score,'signature AI must not change score');assert.equal(rival.hp,hp,'signature AI must not change HP');break;}
  }
}
assert(safeSample,`${selected}: no safe-road signature integration sample executed for ${persona.key}`);
assert.equal(safeSample.sig.safe,true);assert(safeSample.sig.strength<=.36+1e-9);assert(Math.abs(safeSample.sig.laneGoal)<=5.05+1e-9);

Object.assign(w.raceRivalFeud,{archId:1,finalDuelId:1,finalDuelAnnounced:true,finalDuelResolved:false});
w.time=.25;const finalPd=safeSample.s+desiredGap;place(player,finalPd,.45,finalPd);place(rival,safeSample.s,-.45,safeSample.s);rival.battleTarget=0;delete rival.raceRivalSignature;racingAI(w,rival,1/60);
assert.equal(rival.raceRivalSignature?.finalDuel,true,`${selected}: FINAL DUEL signature never activated`);
assert.equal(rival.raceRivalSignature?.active,true,`${selected}: FINAL DUEL signature inactive on safe road`);
const finalStrength=rival.raceRivalSignature.strength;

let protectedChecked=false;
for(let s=0;s<LENGTH;s+=3){const p=trackPoint(s,0),kind=String(p.kind||''),zone=racingTacticalZone(s);if(!(kind==='loop'||kind.startsWith('jump')||zone.type==='jump-flight'||zone.type==='jump-split'))continue;w.time=.25;place(player,s+2,0,s+2);place(rival,s,0,s);rival.battleTarget=0;delete rival.raceRivalSignature;racingAI(w,rival,1/60);assert(!rival.raceRivalSignature?.active,`${selected}: signature pressure activated inside protected stunt/loop region`);protectedChecked=true;break;}
assert(protectedChecked,`${selected}: no protected loop/jump sample found`);
console.log(`${selected}: persona=${persona.key} signature=${safeSample.sig.label} safeZone=${safeSample.zone} strength=${safeSample.sig.strength.toFixed(2)} finalStrength=${finalStrength.toFixed(2)}`);
