import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';

const selected=process.env.WRECK_RHYTHM_COURSE;
if(!selected){
  for(const id of ['rampage-3d','sky-forge','double-orbit']){
    const r=spawnSync(process.execPath,[import.meta.filename],{env:{...process.env,WRECK_RHYTHM_COURSE:id},encoding:'utf8'});
    process.stdout.write(r.stdout||'');process.stderr.write(r.stderr||'');assert.equal(r.status,0,`${id}: battle rhythm regression failed`);
  }
  console.log('WRECKING RACING battle rhythm v3: all 3 courses passed');
  process.exit(0);
}

globalThis.location={search:`?course=${selected}`};
const stamp=`${selected}-${Date.now()}`;
const racing=await import(`../_site/racing.js?rhythm=${stamp}`);
const {racingBattleRhythm}=racing;
assert.equal(typeof racingBattleRhythm,'function');

const stage=racingBattleRhythm(.6,'jump-flight',3,0),clash=racingBattleRhythm(.1,'neutral',3,0),away=racingBattleRhythm(.7,'neutral',3,0),rematch=racingBattleRhythm(2.0,'neutral',3,0),chase=racingBattleRhythm(4.0,'neutral',3,0),landing=racingBattleRhythm(9,'landing-merge',3,0);
assert.equal(stage.phase,'STAGE');assert.equal(stage.lane,null);
assert.equal(clash.phase,'CLASH');
assert.equal(away.phase,'BREAKAWAY');assert(Math.abs(away.lane)>4.4&&Math.abs(away.lane)<4.9);
assert.equal(rematch.phase,'REMATCH');assert(Math.abs(rematch.lane)>1.4&&Math.abs(rematch.lane)<1.9);
assert.equal(Math.sign(away.lane),-Math.sign(rematch.lane),'rematch must cross back through the pack');
assert.equal(chase.phase,'CHASE');assert.equal(chase.lane,null);
assert.equal(landing.phase,'REMATCH','landing merge should reopen the fight');
assert.equal(racingBattleRhythm(.7,'jump-split',4,2).phase,'STAGE','jump staging must override recent contact');

const physicsSource=await readFile(new URL('../_site/physics.js',import.meta.url),'utf8');
assert.match(physicsSource,/raceCarContactAt=w\.time/,'car-to-car impacts are not timestamped separately');

const {makeWorld,step}=await import(`../_site/physics.js?rhythm=${stamp}`);
const w=makeWorld(0,7331,'racing');w.endAt=999;w.limit=999;w.done=false;
let impacts=0;const phases=new Set();
for(let frame=0;frame<900&&!w.done;frame++){
  step(w,{},1/60,true);
  impacts+=w.events.filter(e=>e.type==='impact').length;
  for(const c of w.cars){
    if(c.raceBattlePhase)phases.add(c.raceBattlePhase);
    assert(Number.isFinite(c.raceDistance+c.trackS+(c.p3?.px??0)+(c.p3?.py??0)+(c.p3?.pz??0)),`${selected}: non-finite race state`);
  }
}
assert(impacts>=3,`${selected}: battle rhythm removed too much contact (${impacts})`);
assert(phases.has('BREAKAWAY'),`${selected}: no natural BREAKAWAY observed after impacts`);
const leader=Math.max(...w.cars.map(c=>c.raceDistance));
assert(leader>55,`${selected}: battle rhythm stalled the race leader at ${leader.toFixed(1)}m`);
console.log(`${selected}: impacts=${impacts} phases=${[...phases].sort().join('/')} leader=${leader.toFixed(1)}m`);
