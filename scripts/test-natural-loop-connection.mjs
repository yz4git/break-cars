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
const flatNorm=v=>{const n=Math.hypot(v.x,v.z)||1;return{x:v.x/n,y:0,z:v.z/n};};

for(const [index,loop] of loops.entries()){
  const span=loop.endS-loop.startS,before=racePointAt(loop.startS-.18),after=racePointAt(loop.endS+.18);
  let maxY=-Infinity,minY=Infinity,minUpDot=1,minEarlyAdvance=Infinity,minEarlyFacing=1;

  for(let i=0;i<=80;i++){
    const s=loop.startS+span*i/80,p=racePointAt(s);
    assert.equal(p.kind,'loop',`${selected} loop ${index+1}: ordinary road leaked into loop interval at ${s.toFixed(2)}m`);
    maxY=Math.max(maxY,p.y);minY=Math.min(minY,p.y);minUpDot=Math.min(minUpDot,dot(p.up,before.up));
  }

  for(let i=1;i<=8;i++){
    const d=.25*i,p=racePointAt(loop.startS+d),rel=sub(p,before),advance=dot(rel,before.forward),facing=dot(p.forward,before.forward);
    minEarlyAdvance=Math.min(minEarlyAdvance,advance);minEarlyFacing=Math.min(minEarlyFacing,facing);
  }
  assert.ok(minEarlyAdvance>-.15,`${selected} loop ${index+1}: entry bends behind incoming road (${minEarlyAdvance.toFixed(2)}m)`);
  assert.ok(minEarlyFacing>.75,`${selected} loop ${index+1}: entry turns too far toward loop back face (dot=${minEarlyFacing.toFixed(2)})`);

  const gate=racePointAt(loop.startS+.04),gateNormal=dot(gate.up,before.up),early=racePointAt(loop.startS+2.0);
  assert.ok(gateNormal>.72,`${selected} loop ${index+1}: road face flips at entry (up dot=${gateNormal.toFixed(2)})`);
  assert.ok(early.y>before.y+.10,`${selected} loop ${index+1}: front entry leg does not rise smoothly into loop`);
  assert.ok(maxY-minY>10,`${selected} loop ${index+1}: vertical revolution too shallow`);
  assert.ok(minUpDot<-.72,`${selected} loop ${index+1}: loop never reaches a true inverted surface`);

  let lowerClearance=Infinity;
  if(selected==='rampage-3d'&&index===0){
    const roadWidth=(spec.loopHalfWidth||spec.halfWidth)*2;
    const entryGate=racePointAt(loop.startS+.04),exitGate=racePointAt(loop.endS-.04),gateForward=flatNorm(before.forward),gateRight=flatNorm(before.right),delta=sub(exitGate,entryGate);
    const along=Math.abs(dot(delta,gateForward)),across=Math.abs(dot(delta,gateRight)),parallel=dot(flatNorm(before.forward),flatNorm(after.forward)),entryStraight=dot(entryGate.forward,before.forward),exitStraight=dot(exitGate.forward,after.forward);
    console.log(`RAMPAGE parallel gates: width=${roadWidth.toFixed(2)}m across=${across.toFixed(2)}m along=${along.toFixed(2)}m parallel=${parallel.toFixed(3)} entryStraight=${entryStraight.toFixed(3)} exitStraight=${exitStraight.toFixed(3)}`);
    assert.ok(Math.abs(across-roadWidth)<.85,`${selected}: entry/exit road centerlines are not separated by one road width (across=${across.toFixed(2)}m width=${roadWidth.toFixed(2)}m)`);
    assert.ok(along<.85,`${selected}: entry/exit gates are staggered along the road instead of side-by-side (${along.toFixed(2)}m)`);
    assert.ok(parallel>.97,`${selected}: roads before and after loop are not parallel (dot=${parallel.toFixed(3)})`);
    assert.ok(entryStraight>.96,`${selected}: loop entry does not connect straight to incoming road (dot=${entryStraight.toFixed(3)})`);
    assert.ok(exitStraight>.96,`${selected}: loop exit does not connect straight to outgoing road (dot=${exitStraight.toFixed(3)})`);

    const N=360,points=[];
    for(let i=0;i<=N;i++){
      const s=loop.startS+span*i/N,p=racePointAt(s);
      if(p.y<minY+4.2)points.push({i,s,p});
    }
    for(let a=0;a<points.length;a++)for(let b=a+1;b<points.length;b++){
      if(points[b].i-points[a].i<N*.22)continue;
      const p=points[a].p,q=points[b].p,d=Math.hypot(p.x-q.x,p.z-q.z);
      lowerClearance=Math.min(lowerClearance,d);
    }
    // The reference geometry intentionally puts the two straight centrelines
    // one road width apart.  The curved lower shoulders may be slightly closer,
    // but must not collapse back into the old overlapping-throat shape.
    assert.ok(lowerClearance>roadWidth*.72,`${selected}: lower loop collapses despite parallel gate spacing (clearance=${lowerClearance.toFixed(2)}m width=${roadWidth.toFixed(2)}m)`);
  }

  const late=racePointAt(loop.endS-2.0),exitFacing=dot(late.forward,after.forward),exitNormal=dot(racePointAt(loop.endS-.04).up,after.up);
  assert.ok(exitFacing>.58,`${selected} loop ${index+1}: exit leg faces against outgoing road (dot=${exitFacing.toFixed(2)})`);
  assert.ok(exitNormal>.68,`${selected} loop ${index+1}: road face flips at exit (up dot=${exitNormal.toFixed(2)})`);

  const clearText=Number.isFinite(lowerClearance)?` clearance=${lowerClearance.toFixed(2)}m`:'';
  console.log(`${selected} loop ${index+1}: front-leg advance=${minEarlyAdvance.toFixed(2)} facing=${minEarlyFacing.toFixed(2)} rise=${(maxY-minY).toFixed(2)}m inverted=${minUpDot.toFixed(2)}${clearText}`);
}
