import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';

const selected=process.env.WRECK_MATH_COURSE;
if(!selected){
  for(const id of ['rampage-3d','sky-forge','double-orbit']){
    const r=spawnSync(process.execPath,[import.meta.filename],{env:{...process.env,WRECK_MATH_COURSE:id},encoding:'utf8'});
    process.stdout.write(r.stdout||'');process.stderr.write(r.stderr||'');assert.equal(r.status,0,`${id}: mathematical course regression failed`);
  }
  console.log('WRECKING RACING math rebuild: all 3 courses passed');
  process.exit(0);
}

globalThis.location={search:`?course=${selected}`};
const stamp=`${selected}-${Date.now()}`;
const mod=await import(`../_site/racing3d.js?math=${stamp}`);
const {racePointAt,projectRacePoint,race3DFeatureSpec,RACE3D_LENGTH}=mod,spec=race3DFeatureSpec();
const expectedLoops=selected==='double-orbit'?2:1;
assert.equal(spec.courseId,selected);assert.match(spec.id,/wrecking-racing-math/);assert.equal(spec.loops.length,expectedLoops);
assert(spec.length>380&&spec.length<620,`${selected}: unexpected lap length ${spec.length}`);
assert(spec.halfWidth>=8&&spec.halfWidth<=9.2);assert(spec.designSpeed>=24&&spec.designSpeed<=27);
assert.equal(spec.bankModel,'atan(v^2*kappa/g)');assert(spec.bankMax<=spec.designBankMax+.012);assert(spec.bankMax>.42);
assert(spec.maxGrade<.20,`${selected}: ordinary grade ${(spec.maxGrade*100).toFixed(1)}% exceeds 20%`);
assert(spec.minRadius>12,`${selected}: ordinary horizontal radius too tight ${spec.minRadius.toFixed(1)}m`);
assert(spec.jump.gapLength>=7&&spec.jump.gapLength<=11.5,`${selected}: jump gap ${spec.jump.gapLength.toFixed(1)}m`);
assert(spec.jump.designRange/spec.jump.gapLength>1.75,`${selected}: ballistic safety ${(spec.jump.designRange/spec.jump.gapLength).toFixed(2)}x`);
const takeoffDeg=spec.jump.takeoffAngle*180/Math.PI;assert(takeoffDeg>=7&&takeoffDeg<=11.5,`${selected}: takeoff angle ${takeoffDeg.toFixed(1)}deg`);

const dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z,dist=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z);
const sDiff=(a,b)=>{let d=a-b;if(d>RACE3D_LENGTH/2)d-=RACE3D_LENGTH;if(d<-RACE3D_LENGTH/2)d+=RACE3D_LENGTH;return d;};
for(const [i,l] of spec.loops.entries()){
  assert(l.radius>=9&&l.radius<=10.5,`${selected} loop ${i+1}: radius ${l.radius}`);
  assert(l.maxY-l.minY>l.radius*1.92,`${selected} loop ${i+1}: insufficient vertical revolution`);
  const entry=racePointAt(l.startS),exit=racePointAt(l.endS),inside=racePointAt(l.startS+.12),outside=racePointAt(l.endS+.12);
  assert(dist(entry,exit)<.03,`${selected} loop ${i+1}: gate position discontinuity`);
  assert(dot(entry.forward,exit.forward)>.985,`${selected} loop ${i+1}: gate tangent discontinuity`);
  assert(dot(entry.up,exit.up)>.985,`${selected} loop ${i+1}: gate normal discontinuity`);
  assert(dist(entry,inside)<.22&&dist(exit,outside)<.22,`${selected} loop ${i+1}: local road continuity failed`);
}

let worstRoundTrip=0;
for(let i=0;i<360;i++){
 const p=racePointAt(i/360*RACE3D_LENGTH),q=projectRacePoint(p.x,p.y,p.z,p.s,true);assert(q&&Number.isFinite(q.s+q.lane+q.y));
 worstRoundTrip=Math.max(worstRoundTrip,Math.abs(sDiff(q.s,p.s)));
}
assert(worstRoundTrip<.45,`${selected}: projection round-trip error ${worstRoundTrip.toFixed(2)}m`);

// Nonadjacent ordinary road must not create accidental same-height branch traps.
// Collapse inserted loop arc length before measuring graph separation: the road
// immediately before/after a full 2π loop is topologically adjacent even though
// raw race S differs by ~60 m.
const loopSpan=spec.loops.reduce((sum,l)=>sum+(l.endS-l.startS),0),ordinaryLength=RACE3D_LENGTH-loopSpan;
const ordinaryS=s=>{let q=s;for(const l of spec.loops)if(s>=l.endS)q-=l.endS-l.startS;return q;};
const ordinary=[];for(let s=0;s<RACE3D_LENGTH;s+=4){const p=racePointAt(s);if(p.kind!=='loop'&&p.kind!=='jump-gap')ordinary.push(p);}
let min3D=Infinity,minXZ=Infinity,crossPair=null;
for(let i=0;i<ordinary.length;i++)for(let j=i+1;j<ordinary.length;j++){
 let arc=Math.abs(ordinaryS(ordinary[i].s)-ordinaryS(ordinary[j].s));arc=Math.min(arc,ordinaryLength-arc);if(arc<42)continue;
 const xz=Math.hypot(ordinary[i].x-ordinary[j].x,ordinary[i].z-ordinary[j].z),d=dist(ordinary[i],ordinary[j]);min3D=Math.min(min3D,d);
 if(xz<minXZ){minXZ=xz;crossPair=[ordinary[i],ordinary[j]];}
}
if(selected==='sky-forge'){
 assert(minXZ<5,`SKY FORGE: figure-eight crossing disappeared (${minXZ.toFixed(1)}m)`);
 assert(Math.abs(crossPair[0].y-crossPair[1].y)>7.5,`SKY FORGE: crossing vertical separation too small`);
 assert(min3D>7.5,`SKY FORGE: 3D branch clearance ${min3D.toFixed(1)}m`);
}else assert(min3D>9,`${selected}: accidental nonadjacent road proximity ${min3D.toFixed(1)}m`);

// End-to-end branch safety: full-physics surface sampling must honor the car's
// current trackS after a closed loop instead of snapping to the geometrically
// coincident loop gate or inverted arc.
const {samplePhysicsSurface}=await import(`../_site/physics3d.js?math-surface=${stamp}`);
let worstSurfaceBranch=0,minSurfaceAlign=1;
for(const [i,l] of spec.loops.entries())for(const d of [4,8,12,16]){
 const s=l.endS+d,road=racePointAt(s),lift=1.0,px=road.x+road.up.x*lift,py=road.y+road.up.y*lift,pz=road.z+road.up.z*lift;
 const surface=samplePhysicsSurface('racing',px,py,pz,road.up,true,s);
 assert(surface,`${selected} loop ${i+1} +${d}m: no physics surface`);
 const branch=Math.abs(sDiff(surface.s,s)),align=dot(surface.normal,road.up);worstSurfaceBranch=Math.max(worstSurfaceBranch,branch);minSurfaceAlign=Math.min(minSurfaceAlign,align);
 assert(branch<3,`${selected} loop ${i+1} +${d}m: physics branch jumped ${branch.toFixed(1)}m`);
 assert(align>.75,`${selected} loop ${i+1} +${d}m: wrong surface normal align=${align.toFixed(3)}`);
 assert(surface.kind!=='race-loop',`${selected} loop ${i+1} +${d}m: loop surface leaked after exit`);
}

const {makeWorld,step}=await import(`../_site/physics.js?math=${stamp}`);

// A natural solo drive must clear the first loop and its runout without any
// recovery. This is the exact failure mode that exposed the missing branch hint.
const solo=makeWorld(0,2468,'racing');solo.endAt=999;solo.limit=999;solo.done=false;
for(const c of solo.cars.slice(1)){c.finished=true;c.dead=false;}
const player=solo.cars[0],exitTarget=spec.loops[0].endS+24;
let auto=0,recover=0,soloFrames=0;
for(;soloFrames<2400&&!solo.done&&player.raceDistance<exitTarget;soloFrames++){
 step(solo,{},1/60,true);
 assert(Number.isFinite(player.p3.px+player.p3.py+player.p3.pz+player.trackS+player.raceDistance));
 for(const e of solo.events){if(e.type==='auto-upright')auto++;if(e.type==='recover')recover++;}
}
assert(player.raceDistance>=exitTarget,`${selected}: solo stalled after first loop at race=${player.raceDistance.toFixed(1)} target=${exitTarget.toFixed(1)} s=${player.trackS.toFixed(1)}`);
assert.equal(auto,0,`${selected}: first-loop runout needed ${auto} auto-upright events`);
assert.equal(recover,0,`${selected}: first-loop runout needed ${recover} recovery events`);

// Short deterministic pack soak: the calculated surface must remain finite and
// still produce a destructive race rather than a geometry-only demo.
const w=makeWorld(0,144,'racing'),start=w.cars.map(c=>c.raceDistance);w.endAt=999;w.limit=999;w.done=false;let impacts=0;
for(let frame=0;frame<720&&!w.done;frame++){step(w,{},1/60,true);for(const c of w.cars){assert(c.p3?.active);assert(Number.isFinite(c.p3.px+c.p3.py+c.p3.pz+c.trackS+c.raceDistance));}impacts+=w.events.filter(e=>e.type==='impact').length;}
const progress=w.cars.map((c,i)=>c.raceDistance-start[i]).sort((a,b)=>a-b),median=progress[Math.floor(progress.length/2)],leader=progress.at(-1);
assert(leader>55,`${selected}: leader only advanced ${leader.toFixed(1)}m in 12s`);assert(median>18,`${selected}: median pack progress ${median.toFixed(1)}m`);assert(impacts>=3,`${selected}: Wrecking Racing lost contact density (${impacts} impacts)`);
console.log(`${selected}: length=${spec.length.toFixed(1)}m grade=${(spec.maxGrade*100).toFixed(1)}% bank=${(spec.bankMax*180/Math.PI).toFixed(1)}deg loops=${spec.loops.length} jump=${spec.jump.gapLength.toFixed(1)}/${spec.jump.designRange.toFixed(1)}m safety=${(spec.jump.designRange/spec.jump.gapLength).toFixed(2)}x minR=${spec.minRadius.toFixed(1)}m roundTrip=${worstRoundTrip.toFixed(2)}m branch=${worstSurfaceBranch.toFixed(2)}m align=${minSurfaceAlign.toFixed(2)} solo=${(soloFrames/60).toFixed(1)}s progress=${median.toFixed(1)}/${leader.toFixed(1)}m impacts=${impacts}`);
