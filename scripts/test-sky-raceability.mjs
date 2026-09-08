import assert from 'node:assert/strict';

if(!globalThis.location)globalThis.location={search:'?course=sky-forge'};
const course=await import(`../_site/racing3d.js?sky-raceability=${Date.now()}`);
const physics=await import(`../_site/physics.js?sky-raceability=${Date.now()}`);
const {race3DFeatureSpec,racePointAt}=course;
const {makeWorld,step}=physics;
const spec=race3DFeatureSpec();
const seeds=[1,31,77,144,912,2468,12345,2132980000];
const upY=b=>1-2*(b.qx*b.qx+b.qz*b.qz);
const results=[];

for(const seed of seeds){
  const w=makeWorld(0,seed,'racing');w.endAt=999;w.limit=999;w.done=false;
  for(const c of w.cars.slice(1)){c.finished=true;c.dead=false;c.vx=c.vz=0;}
  const p=w.cars[0],start=p.raceDistance,target=start+spec.length*.985;
  let frames=0,auto=0,recover=0,maxTimer=0,longestStuck=0,stuck=0,loopInverted=false,loopExited=false,guideSeen=false;
  for(;frames<2200&&!w.done&&p.raceDistance<target;frames++){
    step(w,{},1/60,true);
    const b=p.p3,kind=racePointAt(p.trackS).kind,speed=Math.hypot(b.vx,b.vy,b.vz);
    if(kind==='loop'&&upY(b)<-.65)loopInverted=true;
    if(loopInverted&&kind!=='loop')loopExited=true;
    if(p.skyForgeExitGuide)guideSeen=true;
    maxTimer=Math.max(maxTimer,p.autoUprightTime||0);
    if(speed<1.4){stuck++;longestStuck=Math.max(longestStuck,stuck);}else stuck=0;
    for(const e of w.events){if(e.type==='auto-upright')auto++;if(e.type==='recover')recover++;}
  }
  const distance=p.raceDistance-start;
  results.push({seed,distance,seconds:frames/60,auto,recover,maxTimer,longestStuck:longestStuck/60,loopInverted,loopExited,guideSeen});
  assert.ok(p.raceDistance>=target,`SKY seed ${seed} should naturally complete lap: ${distance.toFixed(1)}/${spec.length.toFixed(1)}m`);
  assert.ok(loopInverted,`SKY seed ${seed} must reach inverted loop crown`);
  assert.ok(loopExited,`SKY seed ${seed} must exit loop`);
  assert.ok(guideSeen,`SKY seed ${seed} must traverse physical exit guide`);
  assert.equal(auto,0,`SKY seed ${seed} must not need auto-upright`);
  assert.equal(recover,0,`SKY seed ${seed} must not need race recovery`);
  assert.ok(maxTimer<2.0,`SKY seed ${seed} remained roof-down too long: ${maxTimer.toFixed(2)}s`);
  assert.ok(longestStuck/60<2.5,`SKY seed ${seed} stalled too long: ${(longestStuck/60).toFixed(2)}s`);
}
console.log('SKY FORGE raceability OK: '+results.map(r=>`${r.seed}:${r.distance.toFixed(0)}m/${r.seconds.toFixed(1)}s timer=${r.maxTimer.toFixed(2)}`).join(', '));
