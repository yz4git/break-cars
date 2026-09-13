import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';

const selected=process.env.WRECK_FEUD_COURSE;
if(!selected){
  for(const id of ['rampage-3d','sky-forge','double-orbit']){
    const r=spawnSync(process.execPath,[import.meta.filename],{env:{...process.env,WRECK_FEUD_COURSE:id},encoding:'utf8'});
    process.stdout.write(r.stdout||'');process.stderr.write(r.stderr||'');assert.equal(r.status,0,`${id}: rival feud regression failed`);
  }
  console.log('WRECKING RACING rival feud v5: all 3 courses passed');
  process.exit(0);
}

globalThis.location={search:`?course=${selected}`};
const stamp=`${selected}-${Date.now()}`;
const racing=await import(`../_site/racing.js?feud=${stamp}`);
const {racingRivalFeudDirector,racingAI,TRACK,LENGTH}=racing;
assert.equal(typeof racingRivalFeudDirector,'function');

const mk=(id,d,x)=>({id,dead:false,finished:false,raceDistance:d,x,z:0,p3:{py:0},battleTarget:-1,raceBattlePhase:'CHASE',lap:0});
const mock={mode:'racing',time:10,events:[],cars:[mk(0,100,0),mk(1,104,2),mk(2,101,3)]};
mock.cars[1].battleTarget=0;
mock.events.push({type:'impact',a:0,b:1,power:18,x:1,z:0});
let r=racingRivalFeudDirector(mock,1/60);
assert.equal(r.id,1,'hard-contact rival should be selected');
assert.equal(r.state,'REVENGE','hard targeted hit should create REVENGE');
assert(r.feudHeat>2,'hard contact did not build feud heat');
assert.equal(mock.raceRivalFeudSnapshot.revengeId,1);
assert(mock.events.some(e=>e.type==='rival-revenge-v5'),'REVENGE presentation event missing');
const scoreBefore=mock.cars.map(c=>c.score||0);

// Build more history with CAR 01, then make CAR 02 momentarily nearer. The hot
// opponent must remain the arch rival rather than flickering to the nearest car.
for(let i=0;i<3;i++){
  mock.time+=.25;mock.events=[{type:'impact',a:0,b:1,power:13+i,x:1,z:0}];racingRivalFeudDirector(mock,1/60);
}
mock.time=12;mock.events=[];mock.cars[2].x=.1;mock.cars[2].raceDistance=100.2;r=racingRivalFeudDirector(mock,1/60);
assert.equal(mock.raceRivalFeudSnapshot.archId,1,'contact history did not produce ARCH RIVAL');
assert.equal(r.id,1,'ARCH RIVAL should resist a cold nearer opponent');

// Final lap locks the hottest surviving feud and emits a single finale beat.
mock.time=20;mock.events=[];mock.cars[0].lap=Math.max(0,(TRACK?.laps??4)-1);mock.cars[0].raceDistance=Math.max(mock.cars[0].raceDistance,(LENGTH||400)*3);mock.cars[1].raceDistance=mock.cars[0].raceDistance+7;mock.cars[2].raceDistance=mock.cars[0].raceDistance+2;
r=racingRivalFeudDirector(mock,1/60);
assert.equal(r.id,1,'FINAL DUEL did not lock arch rival');
assert.equal(r.state,'FINAL DUEL');
assert(mock.events.some(e=>e.type==='rival-final-duel-v5'),'FINAL DUEL presentation event missing');
const finalEvents=mock.events.filter(e=>e.type==='rival-final-duel-v5').length;
mock.time+=.2;mock.events=[];racingRivalFeudDirector(mock,1/60);
assert.equal(mock.events.filter(e=>e.type==='rival-final-duel-v5').length,0,'FINAL DUEL event repeated');
assert.equal(finalEvents,1);

// Wrecking the active final rival resolves the feud visually without bonus score.
mock.time+=.2;mock.cars[1].dead=true;mock.events=[{type:'wreck',car:1,by:0,power:30,x:2,z:0}];racingRivalFeudDirector(mock,1/60);
assert(mock.events.some(e=>e.type==='rival-wrecked-v5'),'RIVAL WRECKED event missing');
assert.equal(mock.raceRivalFeudSnapshot.finalDuelResolved,true,'final duel was not resolved');
assert.deepEqual(mock.cars.map(c=>c.score||0),scoreBefore,'feud director must not change scoring');

const gameSource=await readFile(new URL('../_site/game.js',import.meta.url),'utf8');
const racingCss=await readFile(new URL('../_site/racing.css',import.meta.url),'utf8');
assert.match(gameSource,/__breakCarsRivalFeudV5/,'feud telemetry missing');
assert.match(gameSource,/racingRivalFeudDirector\(world,1\/60\)/,'fixed-step feud director not wired');
assert.match(gameSource,/FINAL LAP - RIVAL DUEL/,'FINAL DUEL presentation missing');
assert.match(gameSource,/REVENGE TARGET/,'REVENGE presentation missing');
assert.match(racingCss,/\.rr-heat-v5/,'feud heat styling missing');
assert.match(racingCss,/final-duel-v5/,'final duel styling missing');

// Actual 6DoF race: the feud layer must preserve a stable, finite Rival Duel and
// never stall the leader. Contact heat is not forced because the player may run
// cleanly in a short deterministic window.
const {makeWorld,step}=await import(`../_site/physics.js?feud=${stamp}`);
const w=makeWorld(0,9417,'racing');w.endAt=999;w.limit=999;w.done=false;
let rivalFrames=0,longest=0,streak=0,last=-1,switches=0,maxHeat=0;
for(let frame=0;frame<720&&!w.done;frame++){
  const u=racingAI(w,w.cars[0],1/60);step(w,u,1/60,true);const live=racingRivalFeudDirector(w,1/60);
  if(live){rivalFrames++;maxHeat=Math.max(maxHeat,Number(live.feudHeat)||0);if(live.id===last)streak++;else{if(last>=0)switches++;last=live.id;streak=1;}longest=Math.max(longest,streak);assert(Number.isFinite(live.gap+live.distance+(live.feudHeat||0)),`${selected}: non-finite feud telemetry`);}
}
assert(rivalFrames>=120,`${selected}: feud RIVAL was not visible long enough (${rivalFrames})`);
assert(longest>=45,`${selected}: feud RIVAL flickered (longest ${longest})`);
assert(switches<18,`${selected}: feud caused excessive switching (${switches})`);
const leader=Math.max(...w.cars.map(c=>c.raceDistance));assert(leader>55,`${selected}: feud layer stalled race leader at ${leader.toFixed(1)}m`);
console.log(`${selected}: rivalFrames=${rivalFrames} longest=${longest} switches=${switches} maxHeat=${maxHeat.toFixed(2)} leader=${leader.toFixed(1)}m`);
