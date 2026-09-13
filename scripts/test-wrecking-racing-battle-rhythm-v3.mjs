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

const stage=racingBattleRhythm(.6,'jump-flight',3,0,.5),clash=racingBattleRhythm(.02,'neutral',3,0,1),away=racingBattleRhythm(.3,'neutral',3,0,1),rematch=racingBattleRhythm(1.8,'neutral',3,0,1),chase=racingBattleRhythm(4.0,'neutral',3,0,1);
assert.equal(stage.phase,'STAGE');assert.equal(stage.lane,null);
assert.equal(clash.phase,'CLASH');
assert.equal(away.phase,'BREAKAWAY');assert(Math.abs(away.lane)>4.4&&Math.abs(away.lane)<4.9);
assert.equal(rematch.phase,'REMATCH');assert(Math.abs(rematch.lane)>1.4&&Math.abs(rematch.lane)<1.9);
assert.equal(Math.sign(away.lane),-Math.sign(rematch.lane),'rematch must cross back through the pack');
assert.equal(chase.phase,'CHASE');assert.equal(chase.lane,null);
const featureAway=racingBattleRhythm(9,'loop-merge',3,0,.12),featureRematch=racingBattleRhythm(9,'loop-merge',3,0,.62),landingAway=racingBattleRhythm(9,'landing-merge',4,1,.10);
assert.equal(featureAway.phase,'BREAKAWAY','loop runout must first spread the pack');
assert.equal(featureAway.source,'feature');assert(Math.abs(featureAway.lane)>4.3);
assert.equal(featureRematch.phase,'REMATCH','later loop runout must reconverge');
assert.equal(Math.sign(featureAway.lane),-Math.sign(featureRematch.lane));
assert.equal(landingAway.phase,'BREAKAWAY','landing runout must first spread the pack');
assert.equal(racingBattleRhythm(.2,'jump-split',4,2,.8).phase,'STAGE','jump staging must override recent contact');

const physicsSource=await readFile(new URL('../_site/physics.js',import.meta.url),'utf8');
const racingSource=await readFile(new URL('../_site/racing.js',import.meta.url),'utf8');
assert.match(physicsSource,/raceCarContactAt=w\.time/,'car-to-car impacts are not timestamped separately');
assert.match(racingSource,/tactic\.phase\?\?1/,'feature phase is not wired into battle rhythm');

const {makeWorld,step}=await import(`../_site/physics.js?rhythm=${stamp}`);
const w=makeWorld(0,7331,'racing');w.endAt=999;w.limit=999;w.done=false;
let impacts=0,timestamped=0;
for(let frame=0;frame<720&&!w.done;frame++){
  step(w,{},1/60,true);
  impacts+=w.events.filter(e=>e.type==='impact').length;
  timestamped=Math.max(timestamped,w.cars.filter(c=>Number.isFinite(c.raceCarContactAt)).length);
  for(const c of w.cars)assert(Number.isFinite(c.raceDistance+c.trackS+(c.p3?.px??0)+(c.p3?.py??0)+(c.p3?.pz??0)),`${selected}: non-finite race state`);
}
assert(impacts>=3,`${selected}: battle rhythm removed too much contact (${impacts})`);
assert(timestamped>=2,`${selected}: real racing impacts did not stamp both cars`);
const leader=Math.max(...w.cars.map(c=>c.raceDistance));
assert(leader>55,`${selected}: battle rhythm stalled the race leader at ${leader.toFixed(1)}m`);
console.log(`${selected}: impacts=${impacts} timestamped=${timestamped} leader=${leader.toFixed(1)}m featureBeat=BREAKAWAY>REMATCH`);
