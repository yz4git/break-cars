import { strict as assert } from 'node:assert';

globalThis.location={search:'?course=rampage-3d'};
const stamp=Date.now();
const course=await import(`../_site/racing3d.js?diag=${stamp}`);
const physics=await import(`../_site/physics.js?diag=${stamp}`);
const {race3DFeatureSpec,racePointAt,raceCourseSamples,projectRacePoint,RACE3D_LENGTH}=course;
const {makeWorld,step}=physics;
const spec=race3DFeatureSpec();
const loop=spec.loop;
const loopHalf=spec.loopHalfWidth||spec.halfWidth;
const signedDelta=(a,b)=>{let d=a-b;if(d>RACE3D_LENGTH/2)d-=RACE3D_LENGTH;if(d<-RACE3D_LENGTH/2)d+=RACE3D_LENGTH;return d;};
const wrapDelta=(a,b)=>Math.abs(signedDelta(a,b));

console.log(`RAMPAGE geom length=${spec.length.toFixed(2)} loop=${loop.startS.toFixed(2)}..${loop.endS.toFixed(2)} half=${loopHalf.toFixed(2)} roadHalf=${spec.halfWidth.toFixed(2)}`);

const all=raceCourseSamples(2200);
const nonLoop=all.filter(p=>p.kind!=='loop');
let worst={clear:1e9};
for(let s=loop.startS+5;s<=loop.endS-5;s+=2){
  const p=racePointAt(s);
  let nearest=null;
  for(const q of nonLoop){
    if(wrapDelta(s,q.s)<28) continue;
    const flat=Math.hypot(p.x-q.x,p.z-q.z);
    const dy=Math.abs(p.y-q.y);
    if(!nearest||flat<nearest.flat)nearest={q,flat,dy};
  }
  if(nearest){
    const clear=nearest.flat-(loopHalf+spec.halfWidth);
    if(clear<worst.clear)worst={clear,s,p,nearest};
    if(clear<3)console.log(`CLEAR s=${s.toFixed(1)} flat=${nearest.flat.toFixed(2)} edgeClear=${clear.toFixed(2)} dy=${nearest.dy.toFixed(2)} other=${nearest.q.s.toFixed(1)} kind=${nearest.q.kind}`);
  }
}
console.log(`WORST edgeClear=${worst.clear.toFixed(2)} at loopS=${worst.s?.toFixed(2)} otherS=${worst.nearest?.q.s.toFixed(2)} flat=${worst.nearest?.flat.toFixed(2)} dy=${worst.nearest?.dy.toFixed(2)}`);

for(let s=loop.startS;s<=loop.endS;s+=(loop.endS-loop.startS)/16){
  const p=racePointAt(s);
  console.log(`ROAD s=${s.toFixed(2)} p=(${p.x.toFixed(2)},${p.y.toFixed(2)},${p.z.toFixed(2)}) f=(${p.forward.x.toFixed(2)},${p.forward.y.toFixed(2)},${p.forward.z.toFixed(2)}) upY=${p.up.y.toFixed(2)}`);
}

const w=makeWorld(0,2468,'racing');w.endAt=999;w.limit=999;w.done=false;
for(const c of w.cars.slice(1)){c.finished=true;c.dead=false;c.vx=c.vz=0;}
const c=w.cars[0];
let lastBucket=-1,lastProjectionBucket=-1,maxRace=c.raceDistance;
for(let frame=0;frame<1900&&!w.done;frame++){
  step(w,{},1/60,true);
  maxRace=Math.max(maxRace,c.raceDistance);
  const b=c.p3,road=racePointAt(c.trackS),bucket=Math.floor(frame/12),inWindow=c.trackS>loop.startS-15&&c.trackS<loop.endS+25;
  if(inWindow&&bucket!==lastBucket){
    lastBucket=bucket;
    const d={x:b.px-road.x,y:b.py-road.y,z:b.pz-road.z};
    const side=d.x*road.right.x+d.y*road.right.y+d.z*road.right.z;
    const normal=d.x*road.up.x+d.y*road.up.y+d.z*road.up.z;
    const fv=b.vx*road.forward.x+b.vy*road.forward.y+b.vz*road.forward.z;
    const sv=b.vx*road.right.x+b.vy*road.right.y+b.vz*road.right.z;
    console.log(`CAR f=${frame} s=${c.trackS.toFixed(2)} race=${c.raceDistance.toFixed(2)} kind=${road.kind} pos=(${b.px.toFixed(2)},${b.py.toFixed(2)},${b.pz.toFixed(2)}) v=${Math.hypot(b.vx,b.vy,b.vz).toFixed(2)} fv=${fv.toFixed(2)} side=${side.toFixed(2)} sv=${sv.toFixed(2)} normal=${normal.toFixed(2)} wheels=${b.groundedWheels} upY=${(1-2*(b.qx*b.qx+b.qz*b.qz)).toFixed(2)} rejects=${c.projectionRejects||0}`);
  }
  const stale=Math.abs(b.py-road.y)>6&&road.kind==='loop';
  const projectionBucket=Math.floor(frame/6);
  if(stale&&projectionBucket!==lastProjectionBucket){
    lastProjectionBucket=projectionBucket;
    const hinted=projectRacePoint(b.px,b.py,b.pz,c.trackS,true);
    const free=projectRacePoint(b.px,b.py,b.pz,null,true);
    const fmt=p=>p?`s=${p.s.toFixed(2)} ds=${signedDelta(p.s,c.trackS).toFixed(2)} y=${p.y.toFixed(2)} lane=${p.lane.toFixed(2)} dist=${p.distance.toFixed(2)} kind=${p.kind}`:'null';
    console.log(`PROJ f=${frame} hintS=${c.trackS.toFixed(2)} bodyY=${b.py.toFixed(2)} hinted[${fmt(hinted)}] free[${fmt(free)}]`);
  }
}
console.log(`END race=${c.raceDistance.toFixed(2)} maxRace=${maxRace.toFixed(2)} s=${c.trackS.toFixed(2)} speed=${Math.hypot(c.p3.vx,c.p3.vy,c.p3.vz).toFixed(2)} rejects=${c.projectionRejects||0}`);
assert.ok(Number.isFinite(worst.clear));
