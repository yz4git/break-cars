import assert from 'node:assert/strict';

const course=await import(`../_site/racing3d.js?boost=${Date.now()}`);
const physics=await import(`../_site/physics.js?boost=${Date.now()}`);
const {racePointAt}=course;
const {makeWorld,step}=physics;
const dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z;
const upY=b=>1-2*(b.qx*b.qx+b.qz*b.qz);

// Natural grid-start verification.  The BOOST LOOP should give enough margin
// that the car reaches the loop fast, stays decisively forward at the crown,
// and exits without a recovery or a near-stall.
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
assert.ok(crownForward>24,`inverted crown should retain generous speed: ${crownForward.toFixed(2)}m/s`);
assert.ok(minLoopForward>22,`loop should never approach a stall: min ${minLoopForward.toFixed(2)}m/s`);
assert.ok(maxLoopForward<36,`boost should remain controlled, not runaway: max ${maxLoopForward.toFixed(2)}m/s`);
assert.equal(recover,0,'strong boost loop must not require manual recovery');
assert.equal(auto,0,'strong boost loop must not trigger auto-upright');

console.log(`RAMPAGE boost OK: entry=${entryForward.toFixed(2)}m/s, crown=${crownForward.toFixed(2)}m/s, minLoop=${minLoopForward.toFixed(2)}m/s, maxLoop=${maxLoopForward.toFixed(2)}m/s`);
