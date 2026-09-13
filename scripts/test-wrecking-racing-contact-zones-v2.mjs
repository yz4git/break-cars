import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';

const selected=process.env.WRECK_CONTACT_COURSE;
if(!selected){
  for(const id of ['rampage-3d','sky-forge','double-orbit']){
    const r=spawnSync(process.execPath,[import.meta.filename],{env:{...process.env,WRECK_CONTACT_COURSE:id},encoding:'utf8'});
    process.stdout.write(r.stdout||'');process.stderr.write(r.stderr||'');assert.equal(r.status,0,`${id}: tactical contact regression failed`);
  }
  console.log('WRECKING RACING tactical contact zones: all 3 courses passed');
  process.exit(0);
}

globalThis.location={search:`?course=${selected}`};
const racing=await import(`../_site/racing.js?contact=${selected}-${Date.now()}`);
const r3=await import(`../_site/racing3d.js?contact=${selected}-${Date.now()}`);
const {racingTacticalZone,racingTacticalLane}=racing,{race3DFeatureSpec,RACE3D_LENGTH}=r3,spec=race3DFeatureSpec();
assert.equal(typeof racingTacticalZone,'function');assert.equal(typeof racingTacticalLane,'function');

const wrap=s=>(s%RACE3D_LENGTH+RACE3D_LENGTH)%RACE3D_LENGTH;
for(const [i,loop] of spec.loops.entries()){
  const z=racingTacticalZone(wrap(loop.endS+10));
  assert.equal(z.type,'loop-merge',`${selected} loop ${i+1}: exit does not create a merge zone`);
  assert(z.width>1.5&&z.width<2.3,`${selected} loop ${i+1}: unsafe merge width ${z.width}`);
}
const j=spec.jump;
const pre=racingTacticalZone(wrap(j.startS-18)),flight=racingTacticalZone(wrap((j.startS+j.endS)/2)),land=racingTacticalZone(wrap(j.endS+10));
assert.equal(pre.type,'jump-split',`${selected}: jump approach is not a three-line split`);
assert.equal(flight.type,'jump-flight',`${selected}: jump gap lost staged air lanes`);
assert.equal(land.type,'landing-merge',`${selected}: landing does not converge into battle lanes`);
assert(pre.width>=3.5&&pre.width<=4.2,`${selected}: jump lane spacing ${pre.width}`);

let overtake=null;
for(let s=0;s<RACE3D_LENGTH;s+=2){const z=racingTacticalZone(s);if(z.type==='overtake'){overtake=z;break;}}
assert(overtake,`${selected}: no low-curvature overtake line found`);
assert(overtake.width>4.4&&overtake.width<5.3,`${selected}: overtake width ${overtake.width}`);

const ids=Array.from({length:12},(_,i)=>i+1);
const jumpTargets=[...new Set(ids.map(id=>racingTacticalLane(id,0,pre).toFixed(2)))].map(Number).sort((a,b)=>a-b);
assert.equal(jumpTargets.length,3,`${selected}: jump should stage exactly three lanes`);
assert(jumpTargets[0]<-3.4&&jumpTargets[2]>3.4&&Math.abs(jumpTargets[1])<.01,`${selected}: jump lanes ${jumpTargets}`);
const mergeZone=racingTacticalZone(wrap(spec.loops[0].endS+10)),mergeTargets=[...new Set(ids.map(id=>racingTacticalLane(id,0,mergeZone).toFixed(2)))].map(Number).sort((a,b)=>a-b);
assert.equal(mergeTargets.length,2,`${selected}: merge should produce two close battle channels`);
assert(mergeTargets[0]<-1.5&&mergeTargets[1]>1.5&&mergeTargets[1]-mergeTargets[0]<4.6,`${selected}: merge channels ${mergeTargets}`);
const passTargets=[...new Set(ids.map(id=>racingTacticalLane(id,0,overtake).toFixed(2)))].map(Number).sort((a,b)=>a-b);
assert.equal(passTargets.length,2);assert(passTargets[0]<-4.3&&passTargets[1]>4.3,`${selected}: overtake lines ${passTargets}`);
for(const v of [...jumpTargets,...mergeTargets,...passTargets])assert(Math.abs(v)<spec.halfWidth-2.4,`${selected}: tactical lane ${v} outside safe road envelope`);

console.log(`${selected}: merge=${mergeTargets.join('/')} jump=${jumpTargets.join('/')} pass=${passTargets.join('/')} zones=loop-exit+jump+landing+straight`);
