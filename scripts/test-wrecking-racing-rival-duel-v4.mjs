import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';

const selected=process.env.WRECK_RIVAL_COURSE;
if(!selected){
  for(const id of ['rampage-3d','sky-forge','double-orbit']){
    const r=spawnSync(process.execPath,[import.meta.filename],{env:{...process.env,WRECK_RIVAL_COURSE:id},encoding:'utf8'});
    process.stdout.write(r.stdout||'');process.stderr.write(r.stderr||'');assert.equal(r.status,0,`${id}: rival duel regression failed`);
  }
  console.log('WRECKING RACING rival duel v4: all 3 courses passed');
  process.exit(0);
}

globalThis.location={search:`?course=${selected}`};
const stamp=`${selected}-${Date.now()}`;
const racing=await import(`../_site/racing.js?rival=${stamp}`);
const {racingRivalDirector,racingRivalState,racingAI}=racing;
assert.equal(typeof racingRivalDirector,'function');
assert.equal(racingRivalState(12,14,'CHASE'),'HUNT');
assert.equal(racingRivalState(-12,14,'CHASE'),'DEFEND');
assert.equal(racingRivalState(1,7,'CHASE'),'SIDE BY SIDE');
assert.equal(racingRivalState(20,30,'BREAKAWAY'),'BREAKAWAY');
assert.equal(racingRivalState(-20,30,'REMATCH'),'REMATCH');

// Synthetic duel: recent contact wins selection, lock resists flicker, and crossing
// the progress gap emits one PASS then one COUNTER without touching score/physics.
const mk=(id,d,x)=>({id,dead:false,finished:false,raceDistance:d,x,z:0,p3:{py:0},battleTarget:-1,raceBattlePhase:'CHASE'});
const mock={mode:'racing',time:10,events:[],cars:[mk(0,100,0),mk(1,104,2),mk(2,102,3)]};
mock.cars[0].raceCarContactAt=9.96;mock.cars[1].raceCarContactAt=9.96;mock.cars[1].battleTarget=0;
const first=racingRivalDirector(mock,1/60);
assert.equal(first.id,1,'recent real-contact opponent should become RIVAL');
mock.time=10.2;mock.cars[2].x=.2;mock.cars[2].raceDistance=100.5;
assert.equal(racingRivalDirector(mock,1/60).id,1,'RIVAL lock should prevent HUD flicker');
const scoreBefore=mock.cars.map(c=>c.score||0);
mock.time=10.6;mock.cars[1].raceDistance=97.4;racingRivalDirector(mock,1/60);
assert(mock.events.some(e=>e.type==='rival-pass'),'progress crossover did not emit RIVAL PASS');
mock.events.length=0;mock.time=11.0;mock.cars[1].raceDistance=103.1;racingRivalDirector(mock,1/60);
assert(mock.events.some(e=>e.type==='rival-counter'),'reverse crossover did not emit RIVAL COUNTER');
assert.deepEqual(mock.cars.map(c=>c.score||0),scoreBefore,'rival director must not change scoring');

const gameSource=await readFile(new URL('../_site/game.js',import.meta.url),'utf8');
const racingCss=await readFile(new URL('../_site/racing.css',import.meta.url),'utf8');
assert.match(gameSource,/__breakCarsRivalDuelV4/,'RIVAL HUD telemetry missing');
assert.match(gameSource,/rival-pass/,'RIVAL PASS presentation missing');
assert.match(gameSource,/rival-counter/,'RIVAL COUNTER presentation missing');
// v5 wraps the v4 director at the fixed-step boundary; the v4 director remains
// directly exercised below so this wiring check accepts either valid integration.
assert.match(gameSource,/racingRival(?:Feud)?Director\(world,1\/60\)/,'fixed-step RIVAL director/wrapper not wired');
assert.match(racingCss,/#race-rival-v4/,'RIVAL HUD styling missing');

// Actual 6DoF race: require a persistent live opponent, but do not force an
// overtake to happen inside the short deterministic window.
const {makeWorld,step}=await import(`../_site/physics.js?rival=${stamp}`);
const w=makeWorld(0,8417,'racing');w.endAt=999;w.limit=999;w.done=false;
let rivalFrames=0,longest=0,streak=0,last=-1,switches=0;const states=new Set();
for(let frame=0;frame<720&&!w.done;frame++){
  const u=racingAI(w,w.cars[0],1/60);
  step(w,u,1/60,true);
  const r=racingRivalDirector(w,1/60);
  if(r){
    rivalFrames++;states.add(r.state);
    if(r.id===last)streak++;else{if(last>=0)switches++;last=r.id;streak=1;}
    longest=Math.max(longest,streak);
    assert(r.id>0&&r.id<w.cars.length,`${selected}: invalid RIVAL id`);
    assert(Number.isFinite(r.gap+r.distance),`${selected}: non-finite RIVAL telemetry`);
  }
}
assert(rivalFrames>=120,`${selected}: RIVAL was not visible long enough (${rivalFrames} frames)`);
assert(longest>=45,`${selected}: RIVAL selection flickered (longest lock ${longest} frames)`);
assert(switches<18,`${selected}: excessive RIVAL switching (${switches})`);
console.log(`${selected}: rivalFrames=${rivalFrames} longestLock=${longest} switches=${switches} states=${[...states].join('/')}`);
