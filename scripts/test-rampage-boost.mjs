import assert from 'node:assert/strict';

// This test is specifically for the RAMPAGE 3D BOOST LOOP. Select the real
// course before importing runtime modules so course-specific physical tyre /
// suspension support is exercised exactly as it is in the playable game.
if(!globalThis.location)globalThis.location={search:'?course=rampage-3d'};

const course=await import(`../_site/racing3d.js?boost=${Date.now()}`);
const physics=await import(`../_site/physics.js?boost=${Date.now()}`);
const {racePointAt,race3DFeatureSpec}=course;
const {makeWorld,step}=physics;
const dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z;
const upY=b=>1-2*(b.qx*b.qx+b.qz*b.qz);
const spec=race3DFeatureSpec();

// The open twist loop must have genuinely separate entry and exit gates rather
// than returning to the same point like the legacy closed-circle insertion.
const gateA=racePointAt(spec.loop.startS+.02,0),gateB=racePointAt(spec.loop.endS-.02,0);
const gateSeparation=Math.hypot(gateA.x-gateB.x,gateA.y-gateB.y,gateA.z-gateB.z);
assert.ok(gateSeparation>6,`open loop entry/exit too close: ${gateSeparation.toFixed(2)}m`);

// Natural grid-start verification.  The BOOST LOOP still gives a generous
// entry speed, but the inverted section is judged against the physical
// centripetal-speed requirement instead of the old closed-loop arcade target.
// sqrt(g*r) is the gravity-only crown contact threshold for a vertical loop;
// retain a healthy margin over it while also preventing runaway boost speed.
const criticalCrownSpeed=Math.sqrt(9.81*spec.loop.radius);
const w=makeWorld(0,2468,'racing');
w.endAt=999;w.limit=999;w.done=false;
for(const c of w.cars.slice(1)){c.finished=true;c.dead=false;c.vx=c.vz=0;}
const c=w.cars[0];
let entered=false,exited=false,boostSeen=false,entryForward=0,crownForward=0;
let minLoopForward=Infinity,maxLoopForward=0,recover=0,auto=0;
for(let frame=0;frame<1200&&!w.done&&!exited;frame++){
  step(w,{},1/60,true);
  const b=c.p3,road=racePointAt(c.trackS),forward=dot({x:b.vx,y:b.vy,z:b.vz},road.forward);
  if(c.rampageBoost)boostSeen=true;
  if(road.kind==='loop'){
    if(!entered){entered=true;entryForward=forward;}
    minLoopForward=Math.min(minLoopForward,forward);
    maxLoopForward=Math.max(maxLoopForward,forward);
    if(upY(b)<-.70)crownForward=Math.max(crownForward,forward);
  }else if(entered){exited=true;}
  for(const e of w.events){if(e.type==='recover')recover++;if(e.type==='auto-upright')auto++;}
}
assert.ok(boostSeen,'BOOST LOOP force must engage on a natural start');
assert.ok(entered&&exited,'car must enter and exit the physical loop');
assert.ok(entryForward>26,`loop entry should have generous speed margin: ${entryForward.toFixed(2)}m/s`);
assert.ok(crownForward>criticalCrownSpeed*1.45,`inverted crown lacks physical contact margin: ${crownForward.toFixed(2)}m/s (critical ${criticalCrownSpeed.toFixed(2)})`);
assert.ok(minLoopForward>criticalCrownSpeed*1.20,`loop speed fell below safe contact margin: min ${minLoopForward.toFixed(2)}m/s (critical ${criticalCrownSpeed.toFixed(2)})`);
assert.ok(maxLoopForward<36,`boost should remain controlled, not runaway: max ${maxLoopForward.toFixed(2)}m/s`);
assert.equal(recover,0,'open boost loop must not require manual recovery');
assert.equal(auto,0,'open boost loop must not trigger auto-upright');

console.log(`RAMPAGE open-loop boost OK: gates=${gateSeparation.toFixed(1)}m, critical=${criticalCrownSpeed.toFixed(2)}m/s, entry=${entryForward.toFixed(2)}m/s, crown=${crownForward.toFixed(2)}m/s, minLoop=${minLoopForward.toFixed(2)}m/s, maxLoop=${maxLoopForward.toFixed(2)}m/s`);
