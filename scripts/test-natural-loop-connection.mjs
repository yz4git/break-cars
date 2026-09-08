import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';

const selected=process.env.BREAK_CARS_LOOP_COURSE;
if(!selected){
  for(const course of ['rampage-3d','sky-forge','double-orbit']){
    const r=spawnSync(process.execPath,[new URL(import.meta.url).pathname],{env:{...process.env,BREAK_CARS_LOOP_COURSE:course},encoding:'utf8'});
    process.stdout.write(r.stdout||'');process.stderr.write(r.stderr||'');
    assert.equal(r.status,0,`${course} natural-loop regression failed`);
  }
  console.log('Natural front-entry open loops OK');
  process.exit(0);
}

globalThis.location={search:`?course=${selected}`};
const {racePointAt,race3DFeatureSpec}=await import(`../_site/racing3d.js?natural=${Date.now()}`);
const spec=race3DFeatureSpec(),loops=spec.loops||[spec.loop];
assert.equal(loops.length,selected==='double-orbit'?2:1,`${selected}: unexpected loop count`);

const sub=(a,b)=>({x:a.x-b.x,y:a.y-b.y,z:a.z-b.z});
const dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z;

for(const [index,loop] of loops.entries()){
  const span=loop.endS-loop.startS,before=racePointAt(loop.startS-.18),after=racePointAt(loop.endS+.18);
  let maxY=-Infinity,minY=Infinity,minUpDot=1,minEarlyAdvance=Infinity,minEarlyFacing=1;

  for(let i=0;i<=80;i++){
    const s=loop.startS+span*i/80,p=racePointAt(s);
    assert.equal(p.kind,'loop',`${selected} loop ${index+1}: ordinary road leaked into loop interval at ${s.toFixed(2)}m`);
    maxY=Math.max(maxY,p.y);minY=Math.min(minY,p.y);minUpDot=Math.min(minUpDot,dot(p.up,before.up));
  }

  // The first part of the loop must remain on the FRONT side of the incoming
  // road.  A negative signed advance here is the exact "drive into the back of
  // the loop" failure the reference photo rules out.
  for(let i=1;i<=7;i++){
    const p=racePointAt(loop.startS+span*(i/80)),rel=sub(p,before),advance=dot(rel,before.forward),facing=dot(p.forward,before.forward);
    minEarlyAdvance=Math.min(minEarlyAdvance,advance);minEarlyFacing=Math.min(minEarlyFacing,facing);
  }
  assert.ok(minEarlyAdvance>-.15,`${selected} loop ${index+1}: entry bends behind incoming road (${minEarlyAdvance.toFixed(2)}m)`);
  assert.ok(minEarlyFacing>.58,`${selected} loop ${index+1}: entry turns toward loop back face (dot=${minEarlyFacing.toFixed(2)})`);

  // Surface front face must be continuous at the gate. The loop can twist only
  // after the incoming road has already become the ascending leg.
  const gate=racePointAt(loop.startS+.04),gateNormal=dot(gate.up,before.up),early=racePointAt(loop.startS+span*.10);
  assert.ok(gateNormal>.72,`${selected} loop ${index+1}: road face flips at entry (up dot=${gateNormal.toFixed(2)})`);
  assert.ok(early.y>before.y+.18,`${selected} loop ${index+1}: front entry does not rise into loop`);

  // A real loop still turns the car fully upside-down at the crown.
  assert.ok(maxY-minY>10,`${selected} loop ${index+1}: vertical revolution too shallow`);
  assert.ok(minUpDot<-.72,`${selected} loop ${index+1}: loop never reaches a true inverted surface`);

  // The separate descending leg must merge into the outgoing road in the same
  // driving direction instead of meeting it nose-to-nose.
  const late=racePointAt(loop.endS-span*.035),exitFacing=dot(late.forward,after.forward),exitNormal=dot(racePointAt(loop.endS-.04).up,after.up);
  assert.ok(exitFacing>.58,`${selected} loop ${index+1}: exit leg faces against outgoing road (dot=${exitFacing.toFixed(2)})`);
  assert.ok(exitNormal>.68,`${selected} loop ${index+1}: road face flips at exit (up dot=${exitNormal.toFixed(2)})`);

  console.log(`${selected} loop ${index+1}: front-entry advance=${minEarlyAdvance.toFixed(2)} facing=${minEarlyFacing.toFixed(2)} rise=${(maxY-minY).toFixed(2)}m inverted=${minUpDot.toFixed(2)}`);
}
