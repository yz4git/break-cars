"""SKY FORGE post-loop physical stabilizer.

The open twisted loop remains fully free 6DoF. On the normal-road section after
the loop, visible magnetic guide pads apply only forces/torques: they absorb a
roof bounce, damp full 3D tilt, and gently restore down-track heading. The guide
never writes position, quaternion, velocity, trackS, or raceDistance directly.
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
  if(after>132||road.kind==='loop')return;
  const bu=bodyUp(b),align=dot(bu,road.up),vel={x:b.vx,y:b.vy,z:b.vz},omega={x:b.wx,y:b.wy,z:b.wz},forwardSpeed=dot(vel,road.forward),rel={x:b.px-road.x,y:b.py-road.y,z:b.pz-road.z},height=dot(rel,road.up),normalSpeed=dot(vel,road.up),lateral=dot(rel,road.right),sideSpeed=dot(vel,road.right);
  c.skyForgeExitGuide=true;

  // Magnetic downforce is a real force, not a position correction. The roof can
  // still bounce on loop exit, but the guide absorbs the upward launch before
  // it turns into an unintended high-altitude flight. Airborne lateral damping
  // keeps the chassis above the visible road without locking it to a lane.
  if(height>1.8||b.groundedWheels===0){
    const downAccel=ctx.clamp(Math.max(0,height-1.35)*3.35+Math.max(0,normalSpeed)*5.9,0,86),sideAccel=ctx.clamp(-lateral*1.65-sideSpeed*2.25,-17,17);
    addForce(acc,mul(road.up,-downAccel*b.mass));
    addForce(acc,mul(road.right,sideAccel*b.mass));
  }

  // Preserve momentum through the recovery zone using force only. Stronger
  // acceleration is withheld until the chassis is at least halfway upright.
  const target=align<.45?11.5:14.5;
  if(forwardSpeed<target)addForce(acc,mul(road.forward,(target-forwardSpeed)*b.mass*(align<.45?2.4:5.2)));

  // Full 3D attitude PD. The progressive open loop can release more residual
  // roll than the legacy closed circle, so a roof-down chassis receives a
  // stronger deterministic roll moment. Upright/sideways cars retain the old,
  // gentler gains. This is torque-only; no quaternion or position is written.
  const yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),errMag=Math.hypot(tiltErr.x,tiltErr.y,tiltErr.z),rollRate=dot(omega,road.forward),roofDown=align<-.62;
  if(align<-.82&&errMag<.58){const dir=Math.abs(rollRate)>.14?Math.sign(rollRate):(c.id%2?-1:1),kick=roofDown?1.08:.72;tiltErr.x+=road.forward.x*dir*kick;tiltErr.y+=road.forward.y*dir*kick;tiltErr.z+=road.forward.z*dir*kick;}
  const tiltK=roofDown?17.5:(align<0?10.8:7.8),tiltD=roofDown?5.1:3.75,maxTilt=(roofDown?19:11.5)*b.mass;
  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt);
  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt);
  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt);

  // If the car has actually settled roof-down on the road, use a small physical
  // rocking couple to break static contact. It is two equal/opposite forces, so
  // it adds roll torque without translating or snapping the chassis.
  if(roofDown&&b.groundedWheels>0&&Math.abs(rollRate)<1.5){
    const dir=Math.abs(rollRate)>.14?Math.sign(rollRate):(c.id%2?-1:1),arm=mul(road.right,1.05*dir),lift=mul(road.up,8.5*b.mass);
    addForce(acc,lift,arm);addForce(acc,mul(lift,-1),mul(arm,-1));
  }

  // Damp loop-exit yaw even in the air, then gently point the mostly-upright
  // chassis down-track. This remains torque-only and still permits free flight.
  const bf={x:2*(b.qx*b.qz+b.qy*b.qw),y:2*(b.qy*b.qz-b.qx*b.qw),z:1-2*(b.qx*b.qx+b.qy*b.qy)},yawErr=dot(road.up,cross(bf,road.forward)),desiredYaw=align>.35?ctx.clamp(yawErr*2.1,-1.55,1.55):0,yawTorque=ctx.clamp((desiredYaw-yawRate)*b.mass*(align>.35?1.35:.9),-3.2*b.mass,3.2*b.mass),yawT=mul(road.up,yawTorque);
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
  // Cyan magnetic guide pads communicate the post-loop downforce/roll-control
  // zone without placing any billboard in the chase-camera sightline.
  for(let ss=spec.loop.endS+2;ss<=spec.loop.endS+128;ss+=4.0)for(const lane of [-5.6,-2.8,0,2.8,5.6]){const p=trackPoint(ss,lane),pad=box(group,p.x,p.y,p.z,.72,.025,.82,(Math.floor((ss-spec.loop.endS)/4)%2)?0xbffbff:0x64e8f2,true);align(pad,p);pad.position.add(new THREE.Vector3(p.up.x*.075,p.up.y*.075,p.up.z*.075));}
 }
""" + marker
    s = one(s, marker, visual, 'guide pads')
    view.write_text(s)


if __name__ == '__main__':
    apply_sky_loop_exit_v5(Path('_site'))
