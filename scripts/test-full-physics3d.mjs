import assert from 'node:assert/strict';
import fs from 'node:fs';

const core = await import(`../_site/physics3d.js?full3d-test=${Date.now()}`);
const physics = await import(`../_site/physics.js?full3d-test=${Date.now()}`);
const { samplePhysicsSurface, fullPhysicsFeatureSpec, FULL_PHYSICS_ID } = core;
const { makeWorld, step } = physics;

assert.match(FULL_PHYSICS_ID, /works-full-physics3d/);
const source = fs.readFileSync(new URL('../_site/physics.js', import.meta.url), 'utf8');
const gameSource = fs.readFileSync(new URL('../_site/game.js', import.meta.url), 'utf8');
assert.match(source, /stepFullPhysics/);
assert.match(source, /export function legacyStep/);
assert.match(gameSource, /applyFullPhysicsTransform/);
assert.match(gameSource, /fullPhysicsFeatureSpec/);
assert.match(gameSource, /physicsCamUp/);
assert.match(gameSource, /TorusGeometry/);

const spec = fullPhysicsFeatureSpec();
assert.equal(spec.loop.r, 5.5);
assert.ok(spec.bumps.length >= 4);

// Loop road normal must rotate a full 360 degrees: up at bottom, down at top,
// horizontal on the side. This is what makes the loop physical rather than an animation.
const bottom = samplePhysicsSurface('colosseum', spec.loop.x, spec.loop.y-spec.loop.r+.7, spec.loop.z, {x:0,y:1,z:0});
assert.equal(bottom.kind, 'loop');
assert.ok(bottom.normal.y > .95);
const top = samplePhysicsSurface('colosseum', spec.loop.x, spec.loop.y+spec.loop.r-.7, spec.loop.z, {x:0,y:-1,z:0});
assert.equal(top.kind, 'loop');
assert.ok(top.normal.y < -.95);
const side = samplePhysicsSurface('colosseum', spec.loop.x, spec.loop.y, spec.loop.z+spec.loop.r-.7, {x:0,y:0,z:-1});
assert.equal(side.kind, 'loop');
assert.ok(side.normal.z < -.95);

// Ramp is an actual sloped contact plane.
const rz = spec.ramp.z;
const ry = spec.ramp.halfLength * Math.tan(spec.ramp.angle);
const ramp = samplePhysicsSurface('colosseum', spec.ramp.x, ry+.6, rz, {x:0,y:1,z:-.35});
assert.equal(ramp.kind, 'ramp');
assert.ok(ramp.normal.y > .9 && ramp.normal.z < -.2);

// Runtime soak: every car owns a normalized quaternion and four suspension states.
const w = makeWorld(0, 411, 'wreck-hunt');
for (let i=0;i<120;i++) step(w, {gas:0,brake:0,hand:0,steer:0}, 1/60, false);
for (const c of w.cars) {
  assert.ok(c.p3?.active, `car ${c.id} missing full physics body`);
  const b=c.p3,qLen=Math.hypot(b.qx,b.qy,b.qz,b.qw);
  assert.ok(Number.isFinite(b.px+b.py+b.pz+b.vx+b.vy+b.vz+b.wx+b.wy+b.wz));
  assert.ok(Math.abs(qLen-1)<1e-3, `car ${c.id} quaternion drifted: ${qLen}`);
  assert.equal(b.wheelCompression.length,4);
  assert.ok(b.wheelCompression.every(v=>Number.isFinite(v)&&v>=0&&v<=.34));
}

// Drive the hunter through the authored jump ramp. Other targets are parked dead
// so this test measures terrain/suspension rather than combat randomness.
const jump = makeWorld(0, 812, 'wreck-hunt');
const p=jump.cars[0];
p.x=spec.ramp.x;p.z=spec.ramp.z-spec.ramp.halfLength-1.4;p.heading=0;p.vx=0;p.vz=0;
for (const c of jump.cars.slice(1)) { c.dead=true;c.respawnAt=Infinity;c.x=35;c.z=35;c.vx=0;c.vz=0; }
jump.hunt.focusId=-1;
let maxY=0,maxAir=0;
for (let i=0;i<240&&!jump.done;i++) {
  step(jump,{gas:1,brake:0,hand:0,steer:0},1/60,false);
  maxY=Math.max(maxY,p.p3.py);maxAir=Math.max(maxAir,p.p3.airTime);
}
assert.ok(maxY>1.55, `jump ramp should lift chassis, maxY=${maxY.toFixed(2)}`);
assert.ok(maxAir>.08, `jump ramp should create airborne time, maxAir=${maxAir.toFixed(2)}`);

console.log(`Full physics OK: id=${FULL_PHYSICS_ID}, maxJumpY=${maxY.toFixed(2)}, maxAir=${maxAir.toFixed(2)}, cars=${w.cars.length}`);
