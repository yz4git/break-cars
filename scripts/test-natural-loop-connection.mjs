import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';

const selected=process.env.BREAK_CARS_LOOP_COURSE;
if(!selected){
  for(const course of ['rampage-3d','sky-forge','double-orbit']){
    const r=spawnSync(process.execPath,[new URL(import.meta.url).pathname],{env:{...process.env,BREAK_CARS_LOOP_COURSE:course},encoding:'utf8'});
    process.stdout.write(r.stdout||'');process.stderr.write(r.stderr||'');
    assert.equal(r.status,0,`${course} natural-loop regression failed`);
  }
  console.log('Natural road-connected vertical loops OK');
  process.exit(0);
}

globalThis.location={search:`?course=${selected}`};
const {racePointAt,race3DFeatureSpec}=await import(`../_site/racing3d.js?natural=${Date.now()}`);
const spec=race3DFeatureSpec(),loops=spec.loops||[spec.loop];
assert.equal(loops.length,selected==='double-orbit'?2:1,`${selected}: unexpected loop count`);

const norm=v=>{const l=Math.hypot(v.x,v.y,v.z)||1;return{x:v.x/l,y:v.y/l,z:v.z/l};};
const sub=(a,b)=>({x:a.x-b.x,y:a.y-b.y,z:a.z-b.z});
const dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z;

for(const [index,loop] of loops.entries()){
  const before=racePointAt(loop.startS-.16),after=racePointAt(loop.endS+.16);
  const chord=norm({x:after.x-before.x,y:0,z:after.z-before.z});
  const side=norm({x:-chord.z,y:0,z:chord.x});
  let maxSide=0,maxY=-Infinity,minY=Infinity;
  for(let i=0;i<=64;i++){
    const s=loop.startS+(loop.endS-loop.startS)*i/64,p=racePointAt(s);
    assert.equal(p.kind,'loop',`${selected} loop ${index+1}: ordinary road leaked into loop interval at ${s.toFixed(2)}m`);
    const rel=sub(p,before),lateral=Math.abs(dot(rel,side));
    maxSide=Math.max(maxSide,lateral);maxY=Math.max(maxY,p.y);minY=Math.min(minY,p.y);
  }
  assert.ok(maxSide<3.5,`${selected} loop ${index+1}: loop is still a lateral helix (${maxSide.toFixed(2)}m side excursion)`);
  assert.ok(maxY-minY>10,`${selected} loop ${index+1}: vertical revolution too shallow`);
  console.log(`${selected} loop ${index+1}: vertical-plane side=${maxSide.toFixed(2)}m rise=${(maxY-minY).toFixed(2)}m`);
}
