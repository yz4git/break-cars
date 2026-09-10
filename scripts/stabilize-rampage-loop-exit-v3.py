"""RAMPAGE 3D loop-exit stabilizer.

The loop itself remains unconstrained 6DoF. A visible post-loop stabilizer strip
provides forward force and a physical roll-righting moment after the stunt. It
never overwrites position, quaternion, velocity, trackS or raceDistance.  The
new spatially-open loop can leave a chassis with residual roll for much longer
than the old compact loop, so the force-only settling zone now continues through
the following road instead of ending while the car is still leaning over.
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
  if(after>82||road.kind==='loop')return;
  const bu=bodyUp(b),align=dot(bu,road.up),v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),target=align<.35?16.5:13.5;
  if(v<target)addForce(acc,mul(road.forward,(target-v)*b.mass*7.2));
  c.rampageExitStabilizer=true;
  if(align>.72)return;

  // A direct physical roll moment is well-defined even at exactly 180 degrees,
  // where cross(chassisUp, roadUp) becomes zero. Preserve an existing roll
  // direction; otherwise choose the shortest visible escape side deterministically.
  const omega={x:b.wx,y:b.wy,z:b.wz},rollRate=dot(omega,road.forward),gradient=dot(road.forward,cross(bu,road.up));
  let dir=Math.abs(gradient)>.025?Math.sign(gradient):(Math.abs(rollRate)>.12?Math.sign(rollRate):(c.id%2?-1:1));
  const urgency=ctx.clamp((.75-align)/1.75,0,1),desiredRoll=dir*(2.35+urgency*1.95),rollTorque=ctx.clamp((desiredRoll-rollRate)*b.mass*3.6,-10.5*b.mass,10.5*b.mass),T=mul(road.forward,rollTorque);
  acc.tx+=T.x;acc.ty+=T.y;acc.tz+=T.z;

  // When the roof is resting on the road, wheel count is naturally zero and a
  // pure torque can be resisted by the broad roof contact. An equal/opposite
  // vertical force pair across the chassis creates a real rocking couple with
  // zero net lift, breaking that static contact without teleporting the body.
  if(align<-.55&&Math.abs(rollRate)<2.05){
    const arm=mul(road.right,1.02*dir),lift=mul(road.up,11.8*b.mass);
    addForce(acc,lift,arm);addForce(acc,mul(lift,-1),mul(arm,-1));
  }
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
  // Visible pads correspond exactly to the physical acceleration/stability zone.
  for(let ss=spec.loop.endS+2;ss<=spec.loop.endS+78;ss+=3.2)for(const lane of [-5.8,-2.9,0,2.9,5.8]){const p=trackPoint(ss,lane),pad=box(group,p.x,p.y,p.z,1.0,.035,1.12,(Math.floor((ss-spec.loop.endS)/3.2)%2)?0xa8f7ff:0x42ddeb,true);align(pad,p);pad.position.add(new THREE.Vector3(p.up.x*.09,p.up.y*.09,p.up.z*.09));}
  // Keep the label as track dressing, but never place a billboard across the
  // player's post-loop chase line.
  const ep=trackPoint(spec.loop.endS+34,TRACK.halfWidth+4.2),es=sign('EXIT STABILIZER',9.5,1.15);es.position.set(ep.x,ep.y+2.6,ep.z);es.rotation.y=ep.heading+Math.PI/2;group.add(es);
 }
""" + marker
    s = one(s, marker, visual, 'visible strip')
    view.write_text(s)


if __name__ == '__main__':
    apply_rampage_exit_stabilizer_v3(Path('_site'))
