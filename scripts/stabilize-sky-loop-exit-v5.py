"""SKY FORGE post-loop physical stabilizer.

The vertical loop remains fully free 6DoF. On the normal-road section after the
loop, visible magnetic guide pads apply only forces/torques: they damp residual
roll/yaw and keep a roof-bounce from launching the car far above the road. The
guide never writes position, quaternion, velocity, trackS, or raceDistance.
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
  const bu=bodyUp(b),align=dot(bu,road.up),vel={x:b.vx,y:b.vy,z:b.vz},omega={x:b.wx,y:b.wy,z:b.wz},forwardSpeed=dot(vel,road.forward),rel={x:b.px-road.x,y:b.py-road.y,z:b.pz-road.z},height=dot(rel,road.up),normalSpeed=dot(vel,road.up),lateral=dot(rel,road.right),sideSpeed=dot(vel,road.right);
  c.skyForgeExitGuide=true;

  // Magnetic downforce is a real force, not a position correction. The roof can
  // still bounce on loop exit, but the guide absorbs the upward launch before
  // it turns into a 30-50 m unintended flight. Airborne lateral damping keeps
  // the chassis above the visible road without locking it to a lane.
  if(height>1.8||b.groundedWheels===0){
    const downAccel=ctx.clamp(Math.max(0,height-1.35)*3.15+Math.max(0,normalSpeed)*5.6,0,82),sideAccel=ctx.clamp(-lateral*1.55-sideSpeed*2.15,-16,16);
    addForce(acc,mul(road.up,-downAccel*b.mass));
    addForce(acc,mul(road.right,sideAccel*b.mass));
  }

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

  // The loop can also eject the car with substantial yaw while all wheels are
  // airborne. First damp that spin, then—once mostly upright—gently point the
  // chassis down-track. This remains torque-only and still permits free flight.
  const bf={x:2*(b.qx*b.qz+b.qy*b.qw),y:2*(b.qy*b.qz-b.qx*b.qw),z:1-2*(b.qx*b.qx+b.qy*b.qy)},forwardAlign=dot(bf,road.forward),yawRate=dot(omega,road.up),yawErr=dot(road.up,cross(bf,road.forward));
  const desiredYaw=align>.35?ctx.clamp(yawErr*2.1,-1.55,1.55):0,yawTorque=ctx.clamp((desiredYaw-yawRate)*b.mass*(align>.35?1.35:.82),-3.0*b.mass,3.0*b.mass),yawT=mul(road.up,yawTorque);
  acc.tx+=yawT.x;acc.ty+=yawT.y;acc.tz+=yawT.z;
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
  // Cyan magnetic guide pads communicate the post-loop downforce zone without
  // placing any billboard in the chase-camera sightline.
  for(let ss=spec.loop.endS+2;ss<=spec.loop.endS+86;ss+=4.0)for(const lane of [-5.6,-2.8,0,2.8,5.6]){const p=trackPoint(ss,lane),pad=box(group,p.x,p.y,p.z,.72,.025,.82,(Math.floor((ss-spec.loop.endS)/4)%2)?0xbffbff:0x64e8f2,true);align(pad,p);pad.position.add(new THREE.Vector3(p.up.x*.075,p.up.y*.075,p.up.z*.075));}
 }
""" + marker
    s = one(s, marker, visual, 'guide pads')
    view.write_text(s)


if __name__ == '__main__':
    apply_sky_loop_exit_v5(Path('_site'))
