import assert from 'node:assert/strict';

const course=await import(`../_site/racing3d.js?raceability=${Date.now()}`);
const physics=await import(`../_site/physics.js?raceability=${Date.now()}`);
const {race3DFeatureSpec,racePointAt,RACE3D_LENGTH}=course;
const {makeWorld,step}=physics;
const spec=race3DFeatureSpec();

const upY=b=>1-2*(b.qx*b.qx+b.qz*b.qz);
const sDelta=(a,b)=>{let d=a-b;if(d>RACE3D_LENGTH/2)d-=RACE3D_LENGTH;if(d<-RACE3D_LENGTH/2)d+=RACE3D_LENGTH;return Math.abs(d);};

// True course-connectivity regression: start on the real grid and drive the
// same rigid body through the loop, bridge, jump and landing for one full lap.
const solo=makeWorld(0,2468,'racing');
solo.endAt=999;solo.limit=999;solo.done=false;
for(const c of solo.cars.slice(1)){c.finished=true;c.dead=false;c.vx=c.vz=0;}
const p=solo.cars[0],start=p.raceDistance,target=start+spec.length*.985;
let loopInverted=false,loopExited=false,jumpAir=0,jumpLanded=false,bridgeSeen=false,recover=0,auto=0,maxSJump=0,prevS=p.trackS,longestStuck=0,stuck=0,frames=0,boostSeen=false;
for(;frames<1900&&!solo.done&&p.raceDistance<target;frames++){
  step(solo,{},1/60,true);
  const kind=racePointAt(p.trackS).kind,b=p.p3,speed=Math.hypot(b.vx,b.vy,b.vz);
  maxSJump=Math.max(maxSJump,sDelta(p.trackS,prevS));prevS=p.trackS;
  if(kind==='loop'&&upY(b)<-.65)loopInverted=true;
  if(loopInverted&&kind!=='loop')loopExited=true;
  if(b.airTime>jumpAir)jumpAir=b.airTime;
  if(kind==='jump-landing')jumpLanded=true;
  if(kind==='bridge')bridgeSeen=true;
  if(p.rampageBoost)boostSeen=true;
  if(speed<1.4){stuck++;longestStuck=Math.max(longestStuck,stuck);}else stuck=0;
  for(const e of solo.events){if(e.type==='recover')recover++;if(e.type==='auto-upright')auto++;}
}
assert.ok(p.raceDistance>=target,`natural grid start should complete a lap: ${p.raceDistance-start}/${spec.length}`);
assert.ok(loopInverted,'natural approach must reach the inverted crown of the loop');
assert.ok(loopExited,'car must exit the loop after inversion');
assert.ok(bridgeSeen,'natural lap must reach the elevated crossover');
assert.ok(jumpAir>.12,`natural lap must become airborne at jump: ${jumpAir}`);
assert.ok(jumpLanded,'natural lap must reach the authored landing section');
assert.ok(boostSeen,'natural lap must traverse the visible BOOST LOOP force zone');
assert.equal(recover,0,'natural lap must not need manual race recovery');
assert.equal(auto,0,'natural lap must not need auto-upright');
assert.ok(maxSJump<5.5,`natural lap projection jump: ${maxSJump}`);
assert.ok(longestStuck/60<2.5,`natural lap stalled too long: ${longestStuck/60}s`);

// Thirty-second representative pack soak. The opening remains full-contact,
// but it must develop into a race: most cars must clear the first loop rather
// than becoming a permanent obstacle field before the rest of RAMPAGE 3D.
const pack=makeWorld(0,144,'racing');pack.endAt=999;pack.limit=999;pack.done=false;
let packMaxSJump=0,packPrev=pack.cars.map(c=>c.trackS),maxLoopCars=0,packImpacts=0,boostCars=new Set();
const stalled=Array(12).fill(0),maxStalled=Array(12).fill(0);
for(let frame=0;frame<1800&&!pack.done;frame++){
  step(pack,{},1/60,true);
  let loopCars=0;
  for(const c of pack.cars){
    if(c.dead||c.finished)continue;
    packMaxSJump=Math.max(packMaxSJump,sDelta(c.trackS,packPrev[c.id]));packPrev[c.id]=c.trackS;
    const kind=racePointAt(c.trackS).kind;
    if(kind==='loop')loopCars++;
    if(c.rampageBoost)boostCars.add(c.id);
    const speed=Math.hypot(c.p3?.vx??c.vx,c.p3?.vy??0,c.p3?.vz??c.vz);
    if(speed<1.2){stalled[c.id]++;maxStalled[c.id]=Math.max(maxStalled[c.id],stalled[c.id]);}else stalled[c.id]=0;
  }
  maxLoopCars=Math.max(maxLoopCars,loopCars);
  packImpacts+=pack.events.filter(e=>e.type==='impact').length;
}
const survivors=pack.cars.filter(c=>!c.dead).length;
const cleared=pack.cars.filter(c=>c.raceDistance>spec.loop.endS+20).length;
const hardStalls=pack.cars.filter(c=>maxStalled[c.id]/60>4).length;
assert.ok(maxLoopCars>=3,`pack should actually traverse the loop, max simultaneous cars=${maxLoopCars}`);
assert.ok(survivors>=8,`opening loop is still too destructive: ${survivors}/12 survivors`);
assert.ok(cleared>=8,`opening loop still blocks race flow: only ${cleared}/12 cleared loop+20m after 30s`);
assert.ok(boostCars.size>=8,`BOOST LOOP should visibly/physically assist most of the pack: ${boostCars.size}/12`);
assert.ok(hardStalls<=2,`too many cars remained stalled >4s: ${hardStalls}`);
assert.ok(!pack.cars[0].dead,'player should survive the representative first-loop pack run');
assert.ok(packMaxSJump<5.5,`pack projection jump: ${packMaxSJump}`);

console.log(`RAMPAGE raceability OK: solo ${(p.raceDistance-start).toFixed(1)}/${spec.length.toFixed(1)}m in ${(frames/60).toFixed(1)}s, loopInverted=${loopInverted}, jumpAir=${jumpAir.toFixed(2)}, pack=${survivors}/12, cleared=${cleared}/12, boosted=${boostCars.size}/12, hardStalls=${hardStalls}, loopCars=${maxLoopCars}, impacts=${packImpacts}`);
