"""Integrate the Works-style full 3D vehicle physics after Wreck Hunt/Rush patches."""
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
    new_camera = """if(mode==='menu'){menuTime+=dt;const a=.35+Math.sin(menuTime*.11)*.25;camTarget.set(p.x+Math.sin(a)*13,7,p.z+Math.cos(a)*13);lookTarget.set(p.x-2.5,1,p.z-2.5);camera.fov=50;camera.up.lerp(physicsWorldUp,1-Math.exp(-6*dt));}else if(p.p3?.active){const b=p.p3,x=b.qx,y=b.qy,z=b.qz,w=b.qw,fx=2*(x*z+w*y),fy=2*(y*z-w*x),fz=1-2*(x*x+y*y),ux=2*(x*y-z*w),uy=1-2*(x*x+z*z),uz=2*(y*z+x*w),speed=Math.hypot(b.vx,b.vy,b.vz);if(view===2){camTarget.set(b.px,42,b.pz-8);lookTarget.set(b.px,b.py,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-6*dt));camera.fov=65;}else{const distance=view===1?16:9.8,lift=view===1?9:4.5+speed*.015;camTarget.set(b.px-fx*distance+ux*lift,b.py-fy*distance+uy*lift,b.pz-fz*distance+uz*lift);lookTarget.set(b.px+fx*4+ux*.55,b.py+fy*4+uy*.55,b.pz+fz*4+uz*.55);physicsCamUp.set(ux,uy,uz);camera.up.lerp(physicsCamUp,1-Math.exp(-6*dt));camera.fov=58+speed*.18;}}else{camHeading+=angle(p.heading-camHeading)*(1-Math.exp(-4*dt));const speed=Math.hypot(p.vx,p.vz);if(view===2){camTarget.set(p.x,42,p.z-8);lookTarget.set(p.x,0,p.z);camera.fov=65;}else{const distance=view===1?16:9.8;camTarget.set(p.x-Math.sin(camHeading)*distance,view===1?10:4.8+speed*.015,p.z-Math.cos(camHeading)*distance);lookTarget.set(p.x+Math.sin(camHeading)*4,1.1,p.z+Math.cos(camHeading)*4);camera.fov=58+speed*.18;}}camera.position.lerp(camTarget"""
    s = once(s, old_camera, new_camera, "3D camera")

    # Full-physics collision events include their world-space height.
    s = s.replace("emit(e.x,.75,e.z,e.power,'spark')", "emit(e.x,e.y??.75,e.z,e.power,'spark')")
    s = s.replace("emit(e.x,.7,e.z,e.power,'debris')", "emit(e.x,e.y??.7,e.z,e.power,'debris')")
    path.write_text(s)


def apply_full_physics3d(target: Path) -> None:
    patch_physics(target / 'physics.js')
    patch_game(target / 'game.js')


if __name__ == '__main__':
    apply_full_physics3d(Path('_site'))
