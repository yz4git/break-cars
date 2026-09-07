import assert from 'node:assert/strict';

const core = await import(`../_site/physics3d.js?upright=${Date.now()}`);
const physics = await import(`../_site/physics.js?upright=${Date.now()}`);
const { ensureFullPhysics, updatePlayerAutoUpright } = core;
const { makeWorld, TYPES } = physics;

function upY(b){return 1-2*(b.qx*b.qx+b.qz*b.qz);}
function forceRoofDown(c){
  const b=c.p3;
  Object.assign(b,{qx:0,qy:0,qz:1,qw:0,vx:0,vy:0,vz:0,wx:0,wy:0,wz:0,grounded:false,groundedWheels:0});
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

// CPU cars must never be touched by the player-only recovery helper.
{
  const w=makeWorld(0,404,'colosseum');ensureFullPhysics(w,TYPES);const cpu=w.cars[1];forceRoofDown(cpu);
  for(let i=0;i<420;i++)updatePlayerAutoUpright(w,1/60);
  assert.ok(upY(cpu.p3)<-.9,'CPU car must remain upside down; recovery is player-only');
}

// An inverted vehicle with loaded wheels is a legitimate loop state, not a wreck.
{
  const w=makeWorld(0,505,'racing');ensureFullPhysics(w,TYPES);const p=w.cars[0];forceRoofDown(p);p.p3.groundedWheels=4;
  for(let i=0;i<420;i++)assert.equal(updatePlayerAutoUpright(w,1/60),false,'loaded inverted loop state must not auto-recover');
  assert.equal(p.autoUprightTime,0);
}

console.log('Player auto upright OK: colosseum + wreck-hunt + racing, 5s delay, CPU excluded, loop-safe');
