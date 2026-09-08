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

const bodyUpY=b=>1-2*(b.qx*b.qx+b.qz*b.qz);
const w=makeWorld(0,2468,'racing');
w.endAt=999;
for(const c of w.cars.slice(1))c.finished=true;
const p=w.cars[0],start=p.raceDistance,inverted=new Set();
let recovery=0,firstRecovery=null,air=0,frames=0;
for(;frames<3600&&p.raceDistance<start+spec.length;frames++){
  step(w,{},1/60,true);
  const b=p.p3;
  assert(Number.isFinite(b.px+b.py+b.pz));
  air=Math.max(air,b.airTime);
  for(let n=0;n<2;n++)if(p.trackS>=spec.loops[n].startS&&p.trackS<=spec.loops[n].endS&&bodyUpY(b)<-.7)inverted.add(n);
  for(const e of w.events)if(e.type==='recover'||e.type==='auto-upright'){
    recovery++;
    if(!firstRecovery){
      const road=racePointAt(p.trackS),speed=Math.hypot(b.vx,b.vy,b.vz);
      firstRecovery={type:e.type,frame:frames,s:+p.trackS.toFixed(2),race:+p.raceDistance.toFixed(2),kind:road.kind,x:+b.px.toFixed(2),y:+b.py.toFixed(2),z:+b.pz.toFixed(2),upY:+bodyUpY(b).toFixed(3),speed:+speed.toFixed(2),wheels:b.groundedWheels,air:+(b.airTime||0).toFixed(2),timer:+(p.autoUprightTime||0).toFixed(2)};
    }
  }
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
console.log(`DOUBLE ORBIT: natural lap ${(frames/60).toFixed(1)}s, inverted loops=${inverted.size}, air=${air.toFixed(2)}s, cleared both loops=${clear}/12, impacts=${impacts}`);
assert(clear>=7,'pack must flow through both loops');
assert(impacts>10);
