"""Integrate full 3D vehicle physics after Wreck Hunt/Rush patches, including the dedicated 3D race course."""
from pathlib import Path
import re


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"Full physics {label}: expected 1 match, found {n}")
    return text.replace(old, new, 1)


def regex_once(text: str, pattern: str, repl: str, label: str, flags=0) -> str:
    out, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise RuntimeError(f"Full physics {label}: expected 1 regex match, found {n}")
    return out


def patch_physics3d(path: Path) -> None:
    s = path.read_text()
    s = "import {sampleRaceSurface,racePointAt,race3DFeatureSpec} from './racing3d.js?v=wr3d-v1';\n" + s
    s = once(s, "works-full-physics3d-v4", "works-full-physics3d-v5-racing3d", "physics id")

    surface = """export function samplePhysicsSurface(mode,x,y,z,up={x:0,y:1,z:0},forChassis=false) {
  if (mode==='racing') {
    const race=sampleRaceSurface(x,y,z,up,forChassis);
    if (race) return race;
    const point={x,y:-7.5,z},normal={x:0,y:1,z:0};
    return {point,normal,kind:'race-void',d:y+7.5,align:up.y};
  }
  const floor=floorSurface(x,z),surfaces=[floor];
  const ramp=rampSurface(x,z); if (ramp) surfaces.push(ramp);
  const loop=loopSurface(x,y,z); if (loop && loop.radialError<2.3) surfaces.push(loop);
  let best=null,bestScore=Infinity; const p={x,y,z};
  for (const s of surfaces) {
    const d=dot(sub(p,s.point),s.normal),align=dot(up,s.normal);
    if (!forChassis && align<.10) continue;
    const score=Math.abs(d) + (s.kind==='loop' ? .015 : 0) + (align<0 ? .8 : 0);
    if (score<bestScore) { bestScore=score; best={...s,d,align}; }
  }
  return best || {...floor,d:y-floor.point.y,align:up.y};
}

function inertia"""
    s = regex_once(
        s,
        r"export function samplePhysicsSurface\(mode,x,y,z,up=\{x:0,y:1,z:0\},forChassis=false\) \{.*?\n\}\n\nfunction inertia",
        surface,
        "race surface",
        re.S,
    )

    body = """function frameQuat(forward,up,right) {
  const m00=right.x,m01=up.x,m02=forward.x,m10=right.y,m11=up.y,m12=forward.y,m20=right.z,m21=up.z,m22=forward.z,tr=m00+m11+m22;let x,y,z,w,s;
  if(tr>0){s=Math.sqrt(tr+1)*2;w=.25*s;x=(m21-m12)/s;y=(m02-m20)/s;z=(m10-m01)/s;}
  else if(m00>m11&&m00>m22){s=Math.sqrt(1+m00-m11-m22)*2;w=(m21-m12)/s;x=.25*s;y=(m01+m10)/s;z=(m02+m20)/s;}
  else if(m11>m22){s=Math.sqrt(1+m11-m00-m22)*2;w=(m02-m20)/s;x=(m01+m10)/s;y=.25*s;z=(m12+m21)/s;}
  else{s=Math.sqrt(1+m22-m00-m11)*2;w=(m10-m01)/s;x=(m02+m20)/s;y=(m12+m21)/s;z=.25*s;}
  const l=Math.hypot(x,y,z,w)||1;return{x:x/l,y:y/l,z:z/l,w:w/l};
}
function makeBody(c,type,mode='colosseum') {
  const mass=Math.max(.65,type.mass||1),I=inertia(mass);let q,px=c.x,py,pz=c.z;
  if(mode==='racing'){
    const p=racePointAt(c.trackS??0,c.lane??0);q=frameQuat(p.forward,p.up,p.right);px=p.x+p.up.x*COM_VISUAL_Y;py=p.y+p.up.y*COM_VISUAL_Y;pz=p.z+p.up.z*COM_VISUAL_Y;
  }else{q=yawQuat(c.heading||0);py=baseHeight(c.x,c.z).h+COM_VISUAL_Y;}
  return {active:true,px,py,pz,qx:q.x,qy:q.y,qz:q.z,qw:q.w,vx:c.vx||0,vy:0,vz:c.vz||0,wx:0,wy:c.omega||0,wz:0,mass,invMass:1/mass,invIx:1/I.x,invIy:1/I.y,invIz:1/I.z,grounded:false,groundedWheels:0,wheelCompression:[0,0,0,0],wheelNormal:[0,0,0,0],airTime:0,lastLandingAt:-99,lastSyncX:c.x,lastSyncZ:c.z,lastSyncVx:c.vx||0,lastSyncVz:c.vz||0};
}
export function ensureFullPhysics(w,types) { if (!w.fullPhysics) w.fullPhysics={id:FULL_PHYSICS_ID,enabled:true}; for (const c of w.cars) if (!c.p3 || !c.p3.active) c.p3=makeBody(c,types[c.type],w.mode); return w.fullPhysics; }
export function resetFullPhysicsBody(w,c,types) { c.p3=makeBody(c,types[c.type],w.mode); return c.p3; }

function bodyUp"""
    s = regex_once(
        s,
        r"function makeBody\(c,type\) \{.*?export function resetFullPhysicsBody\(w,c,types\) \{.*?\n\}\n\nfunction bodyUp",
        body,
        "race spawn frame",
        re.S,
    )
    s = once(s, "function adoptExternal(c,types) {", "function adoptExternal(c,types,mode) {", "adopt mode signature")
    s = once(s, "c.p3=makeBody(c,types[c.type]); return;", "c.p3=makeBody(c,types[c.type],mode); return;", "adopt race pose")

    boundary = """function raceBoundary(w,c,ctx) {
  if (w.mode!=='racing') return; syncLegacy(c); const ox=c.x,oz=c.z,wall=ctx.constrainTrack(c),b=c.p3;
  if (wall?.correction) { b.px+=wall.correction.x; b.py+=wall.correction.y; b.pz+=wall.correction.z; c.x=b.px;c.z=b.pz; }
  else if (c.x!==ox||c.z!==oz) { b.px=c.x; b.pz=c.z; }
  if (wall&&wall.speed>0) { const {nx,ny=0,nz,speed:v}=wall; b.vx-=nx*v*1.28; b.vy-=ny*v*1.28; b.vz-=nz*v*1.28; if (v>6&&w.time-c.hitAt>.4) { ctx.hit(w,c,(v-5)*.30,nx,nz); w.events.push({type:'wall',car:c.id,x:b.px,y:b.py,z:b.pz,power:v,nx,ny,nz}); } }
}

function sphereWorld"""
    s = regex_once(s, r"function raceBoundary\(w,c,ctx\) \{.*?\n\}\n\nfunction sphereWorld", boundary, "3D race boundary", re.S)
    s = once(s, "for (const c of w.cars) { adoptExternal(c,ctx.TYPES); syncLegacy(c); }", "for (const c of w.cars) { adoptExternal(c,ctx.TYPES,w.mode); syncLegacy(c); }", "adopt mode call")
    s = once(s, "export function fullPhysicsFeatureSpec() { return {loop:{...LOOP},ramp:{...RAMP},bumps:BUMPS.map(v=>[...v])}; }", "export function fullPhysicsFeatureSpec() { return {loop:{...LOOP},ramp:{...RAMP},bumps:BUMPS.map(v=>[...v]),race:race3DFeatureSpec()}; }", "feature spec")
    path.write_text(s)


def patch_physics(path: Path) -> None:
    s = path.read_text()
    s = "import {stepFullPhysics} from './physics3d.js?v=works-full3d';\n" + s
    s = regex_once(s, r"\nfunction hit\(", "\nexport function hit(", "export hit")
    s = regex_once(s, r"\nfunction ai\(", "\nexport function ai(", "export ai")
    s = regex_once(s, r"\nfunction chooseHuntFocus\(", "\nexport function chooseHuntFocus(", "export hunt focus")
    s = regex_once(s, r"\nfunction respawnHuntCar\(", "\nexport function respawnHuntCar(", "export hunt respawn")
    s = once(s, "export function step(w,input,dt=1/60,autoplay=false){", "export function legacyStep(w,input,dt=1/60,autoplay=false){", "preserve legacy step")
    s += """

export function step(w,input,dt=1/60,autoplay=false){
 return stepFullPhysics(w,input,dt,autoplay,{TYPES,RADIUS,DURATION,COUNT,clamp,angle,hit,ai,racingAI,constrainTrack,advanceRace,respawnHuntCar,chooseHuntFocus});
}
"""
    path.write_text(s)


def patch_game(path: Path) -> None:
    s = path.read_text()
    s = "import {fullPhysicsFeatureSpec} from './physics3d.js?v=works-full3d';\n" + s

    course = """const fullPhysicsSpec=fullPhysicsFeatureSpec();const fullPhysicsCourse=new THREE.Group();arena.add(fullPhysicsCourse);
for(const [x,z,amp,rad] of fullPhysicsSpec.bumps){const mound=new THREE.Mesh(new THREE.SphereGeometry(rad,14,8),mat(0x6d685e));mound.scale.y=amp/rad;mound.position.set(x,0,z);mound.receiveShadow=true;fullPhysicsCourse.add(mound);}
{const r=fullPhysicsSpec.ramp,len=r.halfLength*2;const ramp=box(fullPhysicsCourse,r.x,r.halfLength*Math.tan(r.angle)-.12,r.z,r.halfWidth*2,.24,len,0x5d6466,true);ramp.rotation.x=-r.angle;}
{const l=fullPhysicsSpec.loop;for(const xo of [-3.45,0,3.45]){const rail=new THREE.Mesh(new THREE.TorusGeometry(l.r,.12,6,72),mat(xo===0?0xff7545:0x555f63,.7,.25));rail.rotation.y=Math.PI/2;rail.position.set(l.x+xo,l.y,l.z);rail.castShadow=true;rail.receiveShadow=true;fullPhysicsCourse.add(rail);}for(let i=0;i<36;i++){const a=i/36*Math.PI*2,slat=box(fullPhysicsCourse,l.x,l.y-l.r*Math.cos(a),l.z+l.r*Math.sin(a),l.halfWidth*2,.10,.32,i%6===0?0xd56a42:0x72736c,true);slat.rotation.x=-a;}}
"""
    s = once(s, "const raceTrack=buildRaceTrack({box,sign});scene.add(raceTrack);raceTrack.visible=false;", "const raceTrack=buildRaceTrack({box,sign});scene.add(raceTrack);raceTrack.visible=false;\n" + course, "stunt course")

    helper = """function applyFullPhysicsTransform(m,c){const b=c.p3;if(!b?.active)return false;const x=b.qx,y=b.qy,z=b.qz,w=b.qw,ux=2*(x*y-z*w),uy=1-2*(x*x+z*z),uz=2*(y*z+x*w);m.g.position.set(b.px-ux*.90,b.py-uy*.90,b.pz-uz*.90);m.g.quaternion.set(x,y,z,w);for(let i=0;i<m.wheels.length;i++)m.wheels[i].pivot.position.y=.52+(b.wheelCompression?.[i]||0)*.52;return true;}
"""
    s = once(s, "function visuals(dt){", helper + "function visuals(dt){", "physics transform helper")
    s = once(
        s,
        "m.g.rotation.order='YXZ';m.g.position.set(c.x,rxn.lift+groundClear+.025,c.z);m.g.rotation.set(rxn.pitch,c.heading+rxn.yaw,rxn.roll);",
        "if(!applyFullPhysicsTransform(m,c)){m.g.rotation.order='YXZ';m.g.position.set(c.x,rxn.lift+groundClear+.025,c.z);m.g.rotation.set(rxn.pitch,c.heading+rxn.yaw,rxn.roll);}",
        "car rigid transform",
    )
    s = once(s, "m.body.rotation.z=c.dead?(c.id%2?.12:-.12):-c.omega*Math.hypot(c.vx,c.vz)*.0025;", "m.body.rotation.z=c.p3?.active?0:c.dead?(c.id%2?.12:-.12):-c.omega*Math.hypot(c.vx,c.vz)*.0025;", "remove fake body roll")
    s = once(s, "m.body.rotation.x=c.dead?-.05:c.throttle*.016+Math.sin(world.time*23+c.id)*Math.hypot(c.vx,c.vz)*.0011;", "m.body.rotation.x=c.p3?.active?0:c.dead?-.05:c.throttle*.016+Math.sin(world.time*23+c.id)*Math.hypot(c.vx,c.vz)*.0011;", "remove fake body pitch")
    s = once(s, "if(skidClock>.06&&!c.dead&&Math.hypot(c.vx,c.vz)>8&&Math.abs(c.omega)>.7)addSkids(c);", "if(skidClock>.06&&!c.dead&&Math.hypot(c.vx,c.vz)>8&&Math.abs(c.omega)>.7&&(!c.p3?.active||c.p3.py<1.4))addSkids(c);", "airborne skid suppression")

    s = once(s, "const camTarget=new THREE.Vector3(),lookTarget=new THREE.Vector3(),smoothLook=new THREE.Vector3();let uiClock=0;", "const camTarget=new THREE.Vector3(),lookTarget=new THREE.Vector3(),smoothLook=new THREE.Vector3(),physicsCamUp=new THREE.Vector3(0,1,0),physicsWorldUp=new THREE.Vector3(0,1,0);let uiClock=0;", "camera vectors")
    old_camera = """if(mode==='menu'){menuTime+=dt;const a=.35+Math.sin(menuTime*.11)*.25;camTarget.set(p.x+Math.sin(a)*13,7,p.z+Math.cos(a)*13);lookTarget.set(p.x-2.5,1,p.z-2.5);camera.fov=50;}else{camHeading+=angle(p.heading-camHeading)*(1-Math.exp(-4*dt));const speed=Math.hypot(p.vx,p.vz);if(view===2){camTarget.set(p.x,42,p.z-8);lookTarget.set(p.x,0,p.z);camera.fov=65;}else{const distance=view===1?16:9.8;camTarget.set(p.x-Math.sin(camHeading)*distance,view===1?10:4.8+speed*.015,p.z-Math.cos(camHeading)*distance);lookTarget.set(p.x+Math.sin(camHeading)*4,1.1,p.z+Math.cos(camHeading)*4);camera.fov=58+speed*.18;}}camera.position.lerp(camTarget"""
    new_camera = """if(mode==='menu'){menuTime+=dt;const a=.35+Math.sin(menuTime*.11)*.25;camTarget.set(p.x+Math.sin(a)*13,7,p.z+Math.cos(a)*13);lookTarget.set(p.x-2.5,1,p.z-2.5);camera.fov=50;camera.up.lerp(physicsWorldUp,1-Math.exp(-6*dt));}else if(p.p3?.active){const b=p.p3,x=b.qx,y=b.qy,z=b.qz,w=b.qw,fx=2*(x*z+w*y),fy=2*(y*z-w*x),fz=1-2*(x*x+y*y),ux=2*(x*y-z*w),uy=1-2*(x*x+z*z),uz=2*(y*z+x*w),speed=Math.hypot(b.vx,b.vy,b.vz);if(view===2){camTarget.set(b.px,42,b.pz-8);lookTarget.set(b.px,b.py,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-6*dt));camera.fov=65;}else{const distance=view===1?16:9.8,lift=view===1?9:4.5+speed*.015,looping=gameMode==='racing'&&Math.abs(uy)<.72,camDistance=looping?distance*.72:distance,camLift=looping?lift*.58:lift;camTarget.set(b.px-fx*camDistance+ux*camLift,b.py-fy*camDistance+uy*camLift,b.pz-fz*camDistance+uz*camLift);lookTarget.set(b.px+fx*4+ux*.55,b.py+fy*4+uy*.55,b.pz+fz*4+uz*.55);physicsCamUp.set(ux,uy,uz);camera.up.lerp(physicsCamUp,1-Math.exp(-6*dt));camera.fov=58+speed*.18;}}else{camHeading+=angle(p.heading-camHeading)*(1-Math.exp(-4*dt));const speed=Math.hypot(p.vx,p.vz);if(view===2){camTarget.set(p.x,42,p.z-8);lookTarget.set(p.x,0,p.z);camera.fov=65;}else{const distance=view===1?16:9.8;camTarget.set(p.x-Math.sin(camHeading)*distance,view===1?10:4.8+speed*.015,p.z-Math.cos(camHeading)*distance);lookTarget.set(p.x+Math.sin(camHeading)*4,1.1,p.z+Math.cos(camHeading)*4);camera.fov=58+speed*.18;}}camera.position.lerp(camTarget"""
    s = once(s, old_camera, new_camera, "3D camera")

    s = s.replace("emit(e.x,.75,e.z,e.power,'spark')", "emit(e.x,e.y??.75,e.z,e.power,'spark')")
    s = s.replace("emit(e.x,.7,e.z,e.power,'debris')", "emit(e.x,e.y??.7,e.z,e.power,'debris')")
    path.write_text(s)


def apply_full_physics3d(target: Path) -> None:
    patch_physics3d(target / 'physics3d.js')
    patch_physics(target / 'physics.js')
    patch_game(target / 'game.js')


if __name__ == '__main__':
    apply_full_physics3d(Path('_site'))
