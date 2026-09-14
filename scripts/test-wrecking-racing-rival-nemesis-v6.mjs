import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';

const selected=process.env.WRECK_NEMESIS_COURSE;
if(!selected){
  for(const id of ['rampage-3d','sky-forge','double-orbit']){
    const r=spawnSync(process.execPath,[import.meta.filename],{env:{...process.env,WRECK_NEMESIS_COURSE:id},encoding:'utf8'});
    process.stdout.write(r.stdout||'');process.stderr.write(r.stderr||'');assert.equal(r.status,0,`${id}: rival nemesis v6 regression failed`);
  }
  console.log('WRECKING RACING rival nemesis v6: all 3 courses passed');
  process.exit(0);
}

globalThis.location={search:`?course=${selected}`};
const stamp=`${selected}-${Date.now()}`;
const racing=await import(`../_site/racing.js?nemesis=${stamp}`);
const {LENGTH,trackPoint,racingTacticalZone,racingRivalPersonality,racingNemesisShouldPursue,racingNemesisLaneIntent,racingRivalNemesisResult,racingAI}=racing;
for(const fn of [trackPoint,racingTacticalZone,racingRivalPersonality,racingNemesisShouldPursue,racingNemesisLaneIntent,racingRivalNemesisResult,racingAI])assert.equal(typeof fn,'function');

const roles=new Set(Array.from({length:8},(_,i)=>racingRivalPersonality(i+1,selected).key));
assert.deepEqual([...roles].sort(),['BLOCKER','BRAWLER','DAREDEVIL','HUNTER'],`${selected}: deterministic personality coverage incomplete`);
const persona=racingRivalPersonality(1,selected);
assert.equal(racingNemesisShouldPursue(persona,90,'neutral',true),true,'FINAL DUEL must force pursuit intent');
assert.equal(racingNemesisShouldPursue(persona,0,'jump-flight',false),false,'jump flight must suppress pursuit');
const jump=racingNemesisLaneIntent(persona,3,1.5,-1,'jump-flight',true,true);
assert.equal(jump.active,false,'jump flight must disable nemesis lane pressure');
assert.equal(jump.strength,0,'jump flight must have zero personality pressure');
const normal=racingNemesisLaneIntent(persona,3,1.5,-1,'neutral',false,true);
const finale=racingNemesisLaneIntent(persona,3,1.5,-1,'neutral',true,true);
assert(normal.active&&finale.active,'safe-road personality pressure should be active');
assert(finale.strength>normal.strength,`${selected}: FINAL DUEL should strengthen safe-road pressure`);
assert(Math.abs(finale.laneGoal)<=5.05,`${selected}: final lane goal escaped safety envelope`);

const mk=(id,extra={})=>({id,dead:false,finished:false,finishOrder:0,score:100+id,hp:80+id,maxHP:100,...extra});
const mock={mode:'racing',time:88,events:[],cars:[mk(0,{finished:true,finishOrder:1}),mk(1,{finished:true,finishOrder:2})],raceRivalId:1,raceRivalFeud:{history:{},archId:1,finalDuelId:1,finalDuelResolved:false}};
const before=mock.cars.map(c=>({score:c.score,hp:c.hp}));
const won=racingRivalNemesisResult(mock);
assert.equal(won.result,'WON','finish-order feud win did not resolve');
assert.equal(won.rivalId,1);
assert(mock.events.some(e=>e.type==='rival-feud-result-v6'&&e.result==='WON'),'feud verdict event missing');
assert.deepEqual(mock.cars.map(c=>({score:c.score,hp:c.hp})),before,'nemesis resolver must not change score or damage');
const eventCount=mock.events.length;racingRivalNemesisResult(mock);assert.equal(mock.events.length,eventCount,'resolved feud emitted duplicate verdict');

const crushed={mode:'racing',time:42,events:[],cars:[mk(0),mk(1,{dead:true})],raceRivalId:1,raceRivalFeud:{history:{},archId:1,finalDuelId:1,finalDuelResolved:true}};
assert.equal(racingRivalNemesisResult(crushed).result,'CRUSHED','wrecked nemesis should resolve as CRUSHED');

const gameSource=await readFile(new URL('../_site/game.js',import.meta.url),'utf8');
const racingSource=await readFile(new URL('../_site/racing.js',import.meta.url),'utf8');
const racingCss=await readFile(new URL('../_site/racing.css',import.meta.url),'utf8');
assert.match(racingSource,/WRECKING_RACING_RIVAL_NEMESIS_V6/,'v6 runtime marker missing');
assert.match(racingSource,/p\.kind!==['"]loop['"]/,'loop safety gate missing');
assert.match(racingSource,/tactic\.type!==['"]jump-split['"]&&tactic\.type!==['"]jump-flight['"]/,'jump tactical safety gate missing');
assert.match(racingSource,/c\.raceRivalPersonality=personaV6\.key;c\.raceNemesisIntent=/,'AI personality telemetry not wired');
assert.match(gameSource,/__breakCarsRivalNemesisV6/,'nemesis telemetry missing');
assert.match(gameSource,/rival-feud-result-v6/,'feud verdict presentation missing');
assert.match(racingCss,/#race-feud-result-v6/,'feud verdict styling missing');

// Exercise the actual AI at a deliberately safe road sample. The previous test
// counted telemetry on every fixed-step frame, but the production AI intentionally
// returns early during loop approaches and stunts. Search for a road sample where
// the normal AI body runs, then verify the active ARCH RIVAL receives personality
// pressure without touching score/HP.
const {makeWorld}=await import(`../_site/physics.js?nemesis=${stamp}`);
const w=makeWorld(0,9261,'racing');w.endAt=999;w.limit=999;w.done=false;
w.raceRivalId=1;w.raceRivalFeud={version:'5.0',history:{},archId:1,revengeId:-1,revengeUntil:-1,finalDuelId:-1,finalDuelAnnounced:false,finalDuelResolved:false,lastDefeatedId:-1,lastEvent:'',lastEventAt:-99};
const player=w.cars[0],rival=w.cars[1];
const wrap=s=>(s%LENGTH+LENGTH)%LENGTH;
const place=(car,s,lane,raceDistance=s)=>{
  const p=trackPoint(s,lane);
  Object.assign(car,{x:p.x,z:p.z,heading:p.heading,trackS:wrap(s),raceDistance,lane,dead:false,finished:false,aiReverse:0,stallTime:0,battleTimer:1});
  if(car.p3){Object.assign(car.p3,{px:p.x,py:p.y??0,pz:p.z,vx:0,vy:0,vz:0});}
};
let safeSample=null;
for(let s=0;s<LENGTH;s+=6){
  const p=trackPoint(s,0),zone=racingTacticalZone(s),kind=String(p.kind||'');
  if(kind==='loop'||kind.startsWith('jump')||zone.type==='jump-split'||zone.type==='jump-flight')continue;
  place(player,s+3,.45,s+3);place(rival,s,-.45,s);
  rival.battleTarget=0;delete rival.raceRivalPersonality;delete rival.raceNemesisIntent;
  const score=rival.score,hp=rival.hp;racingAI(w,rival,1/60);
  if(rival.raceNemesisIntent?.active){safeSample={s,zone:zone.type,intent:{...rival.raceNemesisIntent}};assert.equal(rival.score,score,'nemesis AI must not change score');assert.equal(rival.hp,hp,'nemesis AI must not change HP');break;}
}
assert(safeSample,`${selected}: no safe-road ARCH RIVAL personality sample executed`);
assert.equal(safeSample.intent.safe,true,`${selected}: active personality intent was not safety-gated`);
assert(safeSample.intent.strength>0&&safeSample.intent.strength<=.92+1e-9,`${selected}: personality pressure escaped strength cap`);
assert(Math.abs(safeSample.intent.laneGoal)<=5.05+1e-9,`${selected}: personality lane goal escaped safety envelope`);

// The same real AI integration must upgrade to FINAL DUEL on safe road.
Object.assign(w.raceRivalFeud,{archId:1,finalDuelId:1,finalDuelAnnounced:true,finalDuelResolved:false});
place(player,safeSample.s+3,.45,safeSample.s+3);place(rival,safeSample.s,-.45,safeSample.s);rival.battleTarget=0;delete rival.raceNemesisIntent;
racingAI(w,rival,1/60);
assert.equal(rival.raceNemesisIntent?.finalDuel,true,`${selected}: FINAL DUEL personality behavior never activated`);
assert(rival.raceNemesisIntent.strength>=safeSample.intent.strength,`${selected}: FINAL DUEL weakened personality pressure`);

// And an actual loop/jump sample must never gain active lane pressure. Clearing
// the telemetry first ensures an early return cannot accidentally reuse a stale
// safe-road intent from the preceding call.
let unsafeChecked=false;
for(let s=0;s<LENGTH;s+=3){
  const p=trackPoint(s,0),kind=String(p.kind||''),zone=racingTacticalZone(s);
  if(!(kind==='loop'||kind.startsWith('jump')||zone.type==='jump-flight'||zone.type==='jump-split'))continue;
  place(player,s+2,0,s+2);place(rival,s,0,s);rival.battleTarget=0;delete rival.raceNemesisIntent;
  racingAI(w,rival,1/60);
  assert(!rival.raceNemesisIntent?.active,`${selected}: nemesis lane pressure activated inside protected stunt/loop region`);
  unsafeChecked=true;break;
}
assert(unsafeChecked,`${selected}: no protected loop/jump sample found`);
console.log(`${selected}: roles=${[...roles].join('/')} safeZone=${safeSample.zone} strength=${safeSample.intent.strength.toFixed(2)} final=${rival.raceRivalPersonality||persona.key}`);
