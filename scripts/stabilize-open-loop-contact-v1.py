"""Physical surface-following support for the new open/twisted race loops.

The old loop was a closed circle whose coincident entry/exit made it unusually
forgiving.  The progressive loop has a real entry and exit and can expose brief
one-wheel suspension gaps while the road normal rotates quickly.  This helper
models the missing high-speed tyre/suspension load with force and torque only:
it never writes position, quaternion, velocity, trackS or raceDistance.
"""
from pathlib import Path


def apply_open_loop_contact_v1(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    anchor = "wheelForces(w,c,u,ctx,dt,acc);rampageExitStabilizer(w,c,acc,ctx);skyForgeExitGuide(w,c,acc,ctx);"
    repl = anchor + "openLoopContactAssist(w,c,acc,ctx);"
    if s.count(anchor) != 1:
        raise RuntimeError(f'open loop contact: expected one physics hook, found {s.count(anchor)}')
    s = s.replace(anchor, repl, 1)

    insert_at = "function skyForgeExitGuide(w,c,acc,ctx){"
    if s.count(insert_at) != 1:
        raise RuntimeError('open loop contact: SKY guide anchor missing')
    helper = """function openLoopContactAssist(w,c,acc,ctx){
  if(w.mode!=='racing'||!c?.p3||(activeCourse.id!=='sky-forge'&&activeCourse.id!=='double-orbit'))return;
  const b=c.p3,q=c.trackS??0,road=racePointAt(q);
  if(road.kind!=='loop')return;
  const loop=raceLoopAt(q),vel={x:b.vx,y:b.vy,z:b.vz},omega={x:b.wx,y:b.wy,z:b.wz},bu=bodyUp(b),rel={x:b.px-road.x,y:b.py-road.y,z:b.pz-road.z},height=dot(rel,road.up),forwardSpeed=Math.max(0,dot(vel,road.forward));
  // Only bridge a small suspension/contact gap. A car that genuinely leaves the
  // structure remains free-flight and is not pulled back to the centreline.
  if(height<.35||height>2.65||forwardSpeed<8)return;

  // High-speed tyres and suspension must supply centripetal load as the road
  // normal rotates.  Scale with v^2/r, but cap it so the car still feels bumps,
  // impacts and one-wheel unloads instead of being magnetically glued down.
  const centripetal=forwardSpeed*forwardSpeed/Math.max(4,loop.radius),load=ctx.clamp((centripetal-4.5)*.30,0,18.5),gapBlend=ctx.clamp((2.75-height)/1.25,.28,1);
  addForce(acc,mul(road.up,load*gapBlend*b.mass));

  // Contact-patch attitude moment: suspension/tyre forces rotate chassis-up
  // toward the local road normal.  This prevents the progressive twist from
  // leaving an otherwise fast car globally upright at the inverted crown.
  const align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),tiltK=align<.25?13.5:align<.72?10.5:7.2,tiltD=3.25,maxTilt=12.5*b.mass;
  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt);
  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt);
  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt);

  // Keep heading tangent to the twisted ribbon only while chassis-up is on the
  // correct side of the surface. This is a modest tyre yaw moment, not steering.
  if(align>.15){
    const bf={x:2*(b.qx*b.qz+b.qy*b.qw),y:2*(b.qy*b.qz-b.qx*b.qw),z:1-2*(b.qx*b.qx+b.qy*b.qy)},yawErr=dot(road.up,cross(bf,road.forward)),yawTorque=ctx.clamp((yawErr*3.0-yawRate*1.45)*b.mass,-4.2*b.mass,4.2*b.mass),yt=mul(road.up,yawTorque);
    acc.tx+=yt.x;acc.ty+=yt.y;acc.tz+=yt.z;
  }
}

"""
    s = s.replace(insert_at, helper + insert_at, 1)
    path.write_text(s)


if __name__ == '__main__':
    apply_open_loop_contact_v1(Path('_site'))
