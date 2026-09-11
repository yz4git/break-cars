import assert from 'node:assert/strict';
import fs from 'node:fs';

globalThis.location={search:'?course=double-orbit'};
const version=fs.readFileSync(new URL('../_site/index.html',import.meta.url),'utf8').match(/game.js\?v=([^"']+)/)[1];
const {makeWorld,step}=await import(`../_site/physics.js?v=${version}`);
const {race3DFeatureSpec,racePointAt}=await import(`../_site/racing3d.js?v=${version}`);
const spec=race3DFeatureSpec();
assert.equal(spec.loops.length,2);
assert(spec.bridge.y>14);
assert(spec.bankMax>.6);

const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const horizontal=v=>{const l=Math.hypot(v.x,v.z);return{x:v.x/l,z:v.z/l};};
const joinAngleDeg=(a,b)=>Math.acos(clamp(a.x*b.x+a.z*b.z,-1,1))*180/Math.PI;
const joinMetrics=[];
for(let i=0;i<spec.loops.length;i++){
  const loop=spec.loops[i],before=racePointAt(loop.startS-2.5),after=racePointAt(loop.endS+2.5);
  assert.notEqual(before.kind,'loop',`loop ${i+1} approach must be ordinary road`);
  assert.notEqual(after.kind,'loop',`loop ${i+1} exit must be ordinary road`);
  const angle=joinAngleDeg(horizontal(before.forward),horizontal(after.forward));
  joinMetrics.push({loop:i+1,angleDeg:+angle.toFixed(2),beforeS:+(loop.startS-2.5).toFixed(2),afterS:+(loop.endS+2.5).toFixed(2)});
  assert(angle<=12,`loop ${i+1} approach/exit roads must stay near-parallel; got ${angle.toFixed(2)} deg`);
}

const bodyUpY=b=>1-2*(b.qx*b.qx+b.qz*b.qz);
const w=makeWorld(0,2468,'racing');
w.endAt=999;
for(const c of w.cars.slice(1))c.finished=true;
const p=w.cars[0],start=p.raceDistance,inverted=new Set();
let recovery=0,firstRecovery=null,air=0,frames=0,maxRace=p.raceDistance,maxS=p.trackS,lastAdvanceFrame=0;
for(;frames<3600&&p.raceDistance<start+spec.length;frames++){
  step(w,{},1/60,true);
  const b=p.p3;
  assert(Number.isFinite(b.px+b.py+b.pz));
  air=Math.max(air,b.airTime);
  if(p.raceDistance>maxRace+.1){maxRace=p.raceDistance;maxS=p.trackS;lastAdvanceFrame=frames;}
  for(let n=0;n<2;n++)if(p.trackS>=spec.loops[n].startS&&p.trackS<=spec.loops[n].endS&&bodyUpY(b)<-.7)inverted.add(n);
  for(const e of w.events)if(e.type==='recover'||e.type==='auto-upright'){
    recovery++;
    if(!firstRecovery){
      const road=racePointAt(p.trackS),speed=Math.hypot(b.vx,b.vy,b.vz);
      firstRecovery={type:e.type,frame:frames,s:+p.trackS.toFixed(2),race:+p.raceDistance.toFixed(2),kind:road.kind,x:+b.px.toFixed(2),y:+b.py.toFixed(2),z:+b.pz.toFixed(2),upY:+bodyUpY(b).toFixed(3),speed:+speed.toFixed(2),wheels:b.groundedWheels,air:+(b.airTime||0).toFixed(2),timer:+(p.autoUprightTime||0).toFixed(2)};
    }
  }
}
if(p.raceDistance<start+spec.length){
  const b=p.p3,road=racePointAt(p.trackS),speed=Math.hypot(b.vx,b.vy,b.vz);
  console.log('DOUBLE ORBIT natural-lap stall',JSON.stringify({frames,race:+p.raceDistance.toFixed(2),target:+(start+spec.length).toFixed(2),maxRace:+maxRace.toFixed(2),s:+p.trackS.toFixed(2),maxS:+maxS.toFixed(2),kind:road.kind,speed:+speed.toFixed(2),upY:+bodyUpY(b).toFixed(3),wheels:b.groundedWheels,air:+(b.airTime||0).toFixed(2),lastAdvanceAgo:+((frames-lastAdvanceFrame)/60).toFixed(2),inverted:[...inverted],recovery,firstRecovery}));
}
assert(p.raceDistance>=start+spec.length,'complete a natural lap');
assert.equal(inverted.size,2,'natural lap must invert through both open loops');
assert.equal(recovery,0,`natural lap must not need recovery; first=${JSON.stringify(firstRecovery)}`);
assert(air>.5);

const pack=makeWorld(0,144,'racing');
let impacts=0;
for(let i=0;i<3600&&!pack.done;i++){
  step(pack,{},1/60,true);
  for(const c of pack.cars)assert(Number.isFinite(c.p3.py+c.p3.px+c.p3.pz));
  impacts+=pack.events.filter(e=>e.type==='impact').length;
}
const clear=pack.cars.filter(c=>c.raceDistance>spec.loops[1].endS+8).length;
console.log(`DOUBLE ORBIT: joins=${joinMetrics.map(j=>`L${j.loop}:${j.angleDeg}deg`).join(', ')}, natural lap ${(frames/60).toFixed(1)}s, inverted loops=${inverted.size}, air=${air.toFixed(2)}s, cleared both loops=${clear}/12, impacts=${impacts}`);
assert(clear>=7,'pack must flow through both loops');
assert(impacts>10);
