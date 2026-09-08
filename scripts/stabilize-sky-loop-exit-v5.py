"""SKY FORGE post-loop physical stabilizer.

The vertical loop remains fully free 6DoF. On the normal-road section after the
loop, a visible guide strip applies only forces/torques: it damps residual roll,
then gently aligns heading after the wheels return. It never writes position,
quaternion, velocity, trackS, or raceDistance directly.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'SKY exit v5 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_sky_loop_exit_v5(target: Path) -> None:
    physics = target / 'physics3d.js'
    s = physics.read_text()
    anchor = "wheelForces(w,c,u,ctx,dt,acc);rampageExitStabilizer(w,c,acc,ctx);"
    helper = """wheelForces(w,c,u,ctx,dt,acc);rampageExitStabilizer(w,c,acc,ctx);skyForgeExitGuide(w,c,acc,ctx);"""
    s = one(s, anchor, helper, 'physics hook')

    insert_at = "function rampageExitStabilizer(w,c,acc,ctx){"
    if insert_at not in s:
        raise RuntimeError('SKY exit v5 rampage helper anchor missing')
    sky = """function skyForgeExitGuide(w,c,acc,ctx){
  c.skyForgeExitGuide=false;
  if(w.mode!=='racing'||activeCourse.id!=='sky-forge'||!c?.p3)return;
  const b=c.p3,L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,loop=raceLoopAt(q),after=(q-loop.endS+L)%L,road=racePointAt(q);
  if(after>90||road.kind==='loop')return;
  const bu=bodyUp(b),align=dot(bu,road.up),vel={x:b.vx,y:b.vy,z:b.vz},omega={x:b.wx,y:b.wy,z:b.wz},forwardSpeed=dot(vel,road.forward);
  c.skyForgeExitGuide=true;
  // Preserve momentum through the recovery zone using force only. Stronger
  // acceleration is withheld until the chassis is at least halfway upright.
  const target=align<.45?11.5:14.5;
  if(forwardSpeed<target)addForce(acc,mul(road.forward,(target-forwardSpeed)*b.mass*(align<.45?2.4:5.2)));

  // Roll controller: restore the road-up direction, then continue damping the
  // angular velocity instead of switching off with a large residual spin.
  const rollRate=dot(omega,road.forward),gradient=dot(road.forward,cross(bu,road.up));
  let dir=Math.abs(gradient)>.025?Math.sign(gradient):(Math.abs(rollRate)>.12?Math.sign(rollRate):(c.id%2?-1:1));
  const urgency=ctx.clamp((.86-align)/1.86,0,1),desiredRoll=align<.82?dir*(1.35+urgency*1.45):0;
  const rollTorque=ctx.clamp((desiredRoll-rollRate)*b.mass*2.05,-5.2*b.mass,5.2*b.mass),rollT=mul(road.forward,rollTorque);
  acc.tx+=rollT.x;acc.ty+=rollT.y;acc.tz+=rollT.z;

  // Once the chassis is mostly upright and has real wheel contact, use a mild
  // yaw PD controller to point the vehicle down-track. This prevents the roll
  // recovery from leaving the car travelling sideways at the end of the pads.
  if(align>.48&&b.groundedWheels>=2){
    const bf={x:2*(b.qx*b.qz+b.qy*b.qw),y:2*(b.qy*b.qz-b.qx*b.qw),z:1-2*(b.qx*b.qx+b.qy*b.qy)},forwardAlign=dot(bf,road.forward),yawRate=dot(omega,road.up),yawErr=dot(road.up,cross(bf,road.forward));
    if(forwardAlign<.985||Math.abs(yawRate)>.12){
      const desiredYaw=ctx.clamp(yawErr*2.35,-1.65,1.65),yawTorque=ctx.clamp((desiredYaw-yawRate)*b.mass*1.45,-3.2*b.mass,3.2*b.mass),yawT=mul(road.up,yawTorque);
      acc.tx+=yawT.x;acc.ty+=yawT.y;acc.tz+=yawT.z;
    }
  }
}

"""
    s = s.replace(insert_at, sky + insert_at, 1)
    physics.write_text(s)

    view = target / 'track-view.js'
    s = view.read_text()
    marker = ' // Jump take-off'
    if marker not in s:
        raise RuntimeError('SKY exit v5 visual anchor missing')
    visual = """ if(activeCourse.id==='sky-forge'){
  // Low-profile guide pads make the post-loop assist legible without adding a
  // billboard to the chase-camera sightline.
  for(let ss=spec.loop.endS+2;ss<=spec.loop.endS+86;ss+=4.0)for(const lane of [-5.6,-2.8,0,2.8,5.6]){const p=trackPoint(ss,lane),pad=box(group,p.x,p.y,p.z,.72,.025,.82,(Math.floor((ss-spec.loop.endS)/4)%2)?0xbffbff:0x64e8f2,true);align(pad,p);pad.position.add(new THREE.Vector3(p.up.x*.075,p.up.y*.075,p.up.z*.075));}
 }
""" + marker
    s = one(s, marker, visual, 'guide pads')
    view.write_text(s)


if __name__ == '__main__':
    apply_sky_loop_exit_v5(Path('_site'))
