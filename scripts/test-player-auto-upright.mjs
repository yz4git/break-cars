import assert from 'node:assert/strict';

const core = await import(`../_site/physics3d.js?upright=${Date.now()}`);
const physics = await import(`../_site/physics.js?upright=${Date.now()}`);
const course = await import(`../_site/racing3d.js?upright=${Date.now()}`);
const { ensureFullPhysics, resetFullPhysicsBody, updatePlayerAutoUpright } = core;
const { makeWorld, TYPES } = physics;
const { race3DFeatureSpec } = course;

function upY(b){return 1-2*(b.qx*b.qx+b.qz*b.qz);}
function forceRoofDown(c,groundedWheels=0){
  const b=c.p3;
  Object.assign(b,{qx:0,qy:0,qz:1,qw:0,vx:0,vy:0,vz:0,wx:0,wy:0,wz:0,grounded:groundedWheels>0,groundedWheels});
}

for(const [mode,seed] of [['colosseum',101],['wreck-hunt',202],['racing',303]]){
  const w=makeWorld(0,seed,mode);ensureFullPhysics(w,TYPES);const p=w.cars[0];forceRoofDown(p);
  let recovered=false;
  for(let i=0;i<299;i++){
    forceRoofDown(p);
    recovered=updatePlayerAutoUpright(w,1/60);
    assert.equal(recovered,false,`${mode} recovered before five seconds at frame ${i}`);
  }
  forceRoofDown(p);
  for(let i=299;i<305&&!recovered;i++)recovered=updatePlayerAutoUpright(w,1/60);
  assert.equal(recovered,true,`${mode} should recover after five seconds roof-down`);
  assert.ok(upY(p.p3)>.55,`${mode} player should be upright after recovery, upY=${upY(p.p3)}`);
  assert.equal(p.autoUprightTime,0);
  assert.ok(w.events.some(e=>e.type==='auto-upright'&&e.car===0));
}

// A false four-wheel contact while roof-down on a flat/slope must not suppress
// the requested five-second player recovery.
{
  const w=makeWorld(0,313,'wreck-hunt');ensureFullPhysics(w,TYPES);const p=w.cars[0];forceRoofDown(p,4);
  let recovered=false;
  for(let i=0;i<310&&!recovered;i++){forceRoofDown(p,4);recovered=updatePlayerAutoUpright(w,1/60);}
  assert.equal(recovered,true,'roof-down player must recover even if simplified suspension reports 4 wheels');
  assert.ok(upY(p.p3)>.55);
}

// CPU cars must never be touched by the player-only recovery helper.
{
  const w=makeWorld(0,404,'colosseum');ensureFullPhysics(w,TYPES);const cpu=w.cars[1];forceRoofDown(cpu);
  for(let i=0;i<420;i++)updatePlayerAutoUpright(w,1/60);
  assert.ok(upY(cpu.p3)<-.9,'CPU car must remain upside down; recovery is player-only');
}

// A real inverted loop crown has an inverted road normal too, so the body is
// correctly aligned to its drivable surface and must not auto-recover.
{
  const w=makeWorld(0,505,'racing');ensureFullPhysics(w,TYPES);const p=w.cars[0],spec=race3DFeatureSpec(),crown=(spec.loop.startS+spec.loop.endS)*.5;
  p.trackS=crown;p.lane=0;resetFullPhysicsBody(w,p,TYPES);p.p3.grounded=true;p.p3.groundedWheels=4;
  assert.ok(upY(p.p3)<-.65,`test must place car inverted at loop crown, upY=${upY(p.p3)}`);
  for(let i=0;i<420;i++)assert.equal(updatePlayerAutoUpright(w,1/60),false,'aligned inverted loop state must not auto-recover');
  assert.equal(p.autoUprightTime,0);
}

console.log('Player auto upright OK: 5s delay, false wheel-contact tolerant, CPU excluded, real loop surface safe');
