import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const course=await import(`../_site/racing3d.js?test=${Date.now()}`);
const racing=await import(`../_site/racing.js?test=${Date.now()}`);
const physics=await import(`../_site/physics.js?test=${Date.now()}`);
const {racePointAt,projectRacePoint,race3DFeatureSpec,RACE3D_ID}=course;
const {LENGTH}=racing;
const {makeWorld,step}=physics;

const spec=race3DFeatureSpec();
assert.match(RACE3D_ID,/wrecking-racing-3d/);
assert.ok(spec.length>220,`course too short: ${spec.length}`);
assert.ok(spec.maxY-spec.minY>10,`course needs strong elevation change: ${spec.maxY-spec.minY}`);
assert.ok(spec.bankMax>.28,`banking too weak: ${spec.bankMax}`);
assert.ok(spec.loop.maxY>13,`loop too low: ${spec.loop.maxY}`);
assert.ok(spec.jump.endS>spec.jump.startS);
assert.ok(spec.bridge.y>6,`crossover bridge too low: ${spec.bridge.y}`);

// The rendered road triangles must wind forward x right so their front-face
// normal points along the same +up used by wheel/suspension physics. A reversed
// right x forward winding visually exposes the road underside at loop entry even
// when the centerline and collision surface themselves are continuous.
const trackViewSource=await readFile(new URL('../_site/track-view.js',import.meta.url),'utf8');
assert.match(trackViewSource,/const q=\[offset\(p0a,height\),offset\(p1a,height\),offset\(p0b,height\),offset\(p1a,height\),offset\(p1b,height\),offset\(p0b,height\)\]/,'race road front face must match +up');

const sJump=(a,b)=>{let d=a-b;if(d>LENGTH/2)d-=LENGTH;if(d<-LENGTH/2)d+=LENGTH;return Math.abs(d);};
const dot3=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z;
const dist3=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z);

// Open-loop gates must be literal continuations of the normal road.  A tiny step
// across either gate may change curvature, but must not jump position, reverse the
// tangent or flip the road normal (the old failure looked like entering underside-first).
for(const l of spec.loops||[spec.loop]){
  const pre=racePointAt(l.startS-.08),inside=racePointAt(l.startS+.08),beforeExit=racePointAt(l.endS-.08),post=racePointAt(l.endS+.08);
  assert.ok(dist3(pre,inside)<.30,`loop entry position must be continuous: ${dist3(pre,inside)}`);
  assert.ok(dist3(beforeExit,post)<.30,`loop exit position must be continuous: ${dist3(beforeExit,post)}`);
  assert.ok(dot3(pre.forward,inside.forward)>.94,`loop entry tangent must continue road: ${dot3(pre.forward,inside.forward)}`);
  assert.ok(dot3(beforeExit.forward,post.forward)>.94,`loop exit tangent must continue road: ${dot3(beforeExit.forward,post.forward)}`);
  assert.ok(dot3(pre.up,inside.up)>.90,`loop entry normal must not flip: ${dot3(pre.up,inside.up)}`);
  assert.ok(dot3(beforeExit.up,post.up)>.90,`loop exit normal must not flip: ${dot3(beforeExit.up,post.up)}`);
}

// The two figure-eight passes occupy nearly the same XZ location but are separated vertically.
const low=racePointAt(0,0),high=racePointAt(spec.bridge.s,0);
assert.ok(Math.hypot(low.x-high.x,low.z-high.z)<5,`crossover branches miss each other in XZ`);
assert.ok(high.y-low.y>5.5,`crossover needs vertical separation: ${high.y-low.y}`);
const lowProj=projectRacePoint(low.x,low.y,low.z,0,true),highProj=projectRacePoint(high.x,high.y,high.z,spec.bridge.s,true);
assert.ok(Math.abs(lowProj.y-low.y)<.5);
assert.ok(Math.abs(highProj.y-high.y)<.5);

function isolate(w){for(const c of w.cars.slice(1)){c.dead=true;c.respawnAt=Infinity;c.vx=c.vz=0;}w.endAt=999;w.limit=999;w.done=false;}
function place(w,s,speed=20,lane=0){const c=w.cars[0],p=racePointAt(s,lane);Object.assign(c,{trackS:p.s,raceDistance:s,lane,x:p.x,z:p.z,heading:p.heading,vx:p.forward.x*speed,vz:p.forward.z*speed,dead:false,finished:false});c.p3=null;return c;}
const upY=b=>1-2*(b.qx*b.qx+b.qz*b.qz);

// Jump: leave the authored ramp, spend real time airborne, then reach the landing side.
const jump=makeWorld(0,912,'racing');isolate(jump);const jp=place(jump,spec.jump.startS-9,22);let maxY=0,maxAir=0,maxS=jp.trackS,maxJumpS=0,prevJumpS=jp.trackS;
for(let i=0;i<210&&!jump.done;i++){step(jump,{gas:1,brake:0,hand:0,steer:0},1/60,false);maxY=Math.max(maxY,jp.p3.py);maxAir=Math.max(maxAir,jp.p3.airTime);maxJumpS=Math.max(maxJumpS,sJump(jp.trackS,prevJumpS));prevJumpS=jp.trackS;maxS=jp.trackS;}
assert.ok(maxAir>.18,`jump should become airborne: ${maxAir}`);
assert.ok(maxY>3.2,`jump should gain height: ${maxY}`);
assert.ok(maxS>spec.jump.endS||Math.abs(maxS-spec.jump.endS)<8,`jump should progress toward landing`);
assert.ok(maxJumpS<5.5,`jump projection jumped branches: ${maxJumpS}`);

// Vertical loop: initialize on the bottom tangent with enough entry speed and verify inversion and continuous projection.
const loop=makeWorld(0,733,'racing');isolate(loop);const lp=place(loop,spec.loop.startS+.35,24);let loopMaxY=0,loopMinUp=1,loopWheels=0,loopProgress=lp.trackS,loopMaxSJump=0,prevLoopS=lp.trackS;
for(let i=0;i<300&&!loop.done;i++){step(loop,{gas:1,brake:0,hand:0,steer:0},1/60,false);loopMaxY=Math.max(loopMaxY,lp.p3.py);loopMinUp=Math.min(loopMinUp,upY(lp.p3));loopWheels=Math.max(loopWheels,lp.p3.groundedWheels);loopMaxSJump=Math.max(loopMaxSJump,sJump(lp.trackS,prevLoopS));prevLoopS=lp.trackS;loopProgress=lp.trackS;}
assert.ok(loopMaxY>11,`loop should climb high: ${loopMaxY}`);
assert.ok(loopMinUp<-.6,`loop should invert chassis: ${loopMinUp}`);
assert.ok(loopWheels>=2,`loop should maintain wheel contact`);
assert.ok(Number.isFinite(loopProgress));
assert.ok(loopMaxSJump<5.5,`loop trackS branch jump detected: ${loopMaxSJump}`);

// Full-pack soak catches projection/crossover NaNs, branch jumps and 3D boundary instability.
const pack=makeWorld(1,144,'racing');const prevS=pack.cars.map(c=>c.trackS);let packMaxSJump=0;
for(let i=0;i<900&&!pack.done;i++){
  step(pack,{},1/60,true);
  for(const c of pack.cars){
    if(c.dead)continue;
    packMaxSJump=Math.max(packMaxSJump,sJump(c.trackS,prevS[c.id]));
    prevS[c.id]=c.trackS;
  }
}
for(const c of pack.cars){assert.ok(c.p3?.active);assert.ok(Number.isFinite(c.p3.px+c.p3.py+c.p3.pz+c.raceDistance+c.trackS));}
assert.ok(packMaxSJump<5.5,`pack trackS branch jump detected: ${packMaxSJump}`);

console.log(`Racing 3D OK: length=${spec.length.toFixed(1)}, elevation=${(spec.maxY-spec.minY).toFixed(1)}, bank=${spec.bankMax.toFixed(2)}, jumpAir=${maxAir.toFixed(2)}, jumpY=${maxY.toFixed(2)}, loopY=${loopMaxY.toFixed(2)}, loopUp=${loopMinUp.toFixed(2)}, loopSJump=${loopMaxSJump.toFixed(2)}, packSJump=${packMaxSJump.toFixed(2)}`);
