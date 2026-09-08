"""RAMPAGE 3D loop-exit stabilizer.

The loop itself remains unconstrained 6DoF.  A visible post-loop stabilizer strip
applies only physical forward force + roll torque on RAMPAGE when a chassis
leaves the loop roof-down.  It never overwrites position, quaternion or trackS.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE exit v3 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_exit_stabilizer_v3(target: Path) -> None:
    physics = target / 'physics3d.js'
    s = physics.read_text()
    anchor = "function integrateBody(w,c,u,ctx,dt) {\n  const b=c.p3,acc={fx:0,fy:-9.81*b.mass,fz:0,tx:0,ty:0,tz:0}; wheelForces(w,c,u,ctx,dt,acc);"
    helper = """function rampageExitStabilizer(w,c,acc,ctx){
  c.rampageExitStabilizer=false;
  if(w.mode!=='racing'||activeCourse.id!=='rampage-3d'||!c?.p3)return;
  const b=c.p3,L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,loop=raceLoopAt(q),after=(q-loop.endS+L)%L,road=racePointAt(q);
  if(after>40||road.kind==='loop')return;
  const bu=bodyUp(b),align=dot(bu,road.up);if(align>.55)return;
  const omega={x:b.wx,y:b.wy,z:b.wz},rollRate=dot(omega,road.forward),gradient=dot(road.forward,cross(bu,road.up));
  let dir=Math.abs(gradient)>.035?Math.sign(gradient):(Math.abs(rollRate)>.16?Math.sign(rollRate):1);
  const urgency=ctx.clamp((.55-align)/1.55,0,1),desiredRoll=dir*(1.75+urgency*1.25),rollTorque=ctx.clamp((desiredRoll-rollRate)*b.mass*2.1,-5.2*b.mass,5.2*b.mass),T=mul(road.forward,rollTorque);
  acc.tx+=T.x;acc.ty+=T.y;acc.tz+=T.z;
  const v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),target=align<-.55?14:11;if(v<target)addForce(acc,mul(road.forward,(target-v)*b.mass*4.6));
  c.rampageExitStabilizer=true;
}

function integrateBody(w,c,u,ctx,dt) {
  const b=c.p3,acc={fx:0,fy:-9.81*b.mass,fz:0,tx:0,ty:0,tz:0}; wheelForces(w,c,u,ctx,dt,acc);rampageExitStabilizer(w,c,acc,ctx);"""
    s = one(s, anchor, helper, 'physics hook')
    physics.write_text(s)

    view = target / 'track-view.js'
    s = view.read_text()
    marker = ' // Jump take-off'
    if marker not in s:
        raise RuntimeError('RAMPAGE exit v3 visual anchor missing')
    visual = """ if(activeCourse.id==='rampage-3d'){
  // The physical loop-exit stabilizer is visible: cyan pads mark the exact
  // region where a roof-down loop exit receives roll torque / forward force.
  for(let ss=spec.loop.endS+2;ss<=spec.loop.endS+38;ss+=3.2)for(const lane of [-5.8,-2.9,0,2.9,5.8]){const p=trackPoint(ss,lane),pad=box(group,p.x,p.y,p.z,1.0,.035,1.12,(Math.floor((ss-spec.loop.endS)/3.2)%2)?0xa8f7ff:0x42ddeb,true);align(pad,p);pad.position.add(new THREE.Vector3(p.up.x*.09,p.up.y*.09,p.up.z*.09));}
  const ep=trackPoint(spec.loop.endS+18,0),es=sign('EXIT STABILIZER',15,1.8);es.position.set(ep.x,ep.y+3.0,ep.z);es.rotation.y=ep.heading+Math.PI/2;group.add(es);
 }
""" + marker
    s = one(s, marker, visual, 'visible strip')
    view.write_text(s)


if __name__ == '__main__':
    apply_rampage_exit_stabilizer_v3(Path('_site'))
