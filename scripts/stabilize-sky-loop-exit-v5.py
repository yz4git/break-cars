"""SKY FORGE post-loop physical stabilizer and open-loop contact support.

The open twisted loop remains fully free 6DoF. Inside SKY FORGE and DOUBLE
ORBIT loops, tyre/suspension load is represented with forces and torques only so
the chassis follows the rapidly rotating road normal through tiny contact gaps.
After SKY FORGE's loop, visible guide pads absorb roof bounces and restore the
car naturally. No helper writes position, quaternion, velocity, trackS, or
raceDistance directly.
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
    helper = """wheelForces(w,c,u,ctx,dt,acc);rampageExitStabilizer(w,c,acc,ctx);openLoopContactAssist(w,c,acc,ctx);skyForgeExitGuide(w,c,acc,ctx);"""
    s = one(s, anchor, helper, 'physics hook')

    insert_at = "function rampageExitStabilizer(w,c,acc,ctx){"
    if insert_at not in s:
        raise RuntimeError('SKY exit v5 rampage helper anchor missing')
    sky = """function openLoopContactAssist(w,c,acc,ctx){
  if(w.mode!=='racing'||!c?.p3||(activeCourse.id!=='sky-forge'&&activeCourse.id!=='double-orbit'))return;
  const b=c.p3,q=c.trackS??0,road=racePointAt(q);
  if(road.kind!=='loop')return;
  const loop=raceLoopAt(q),vel={x:b.vx,y:b.vy,z:b.vz},omega={x:b.wx,y:b.wy,z:b.wz},bu=bodyUp(b),rel={x:b.px-road.x,y:b.py-road.y,z:b.pz-road.z},height=dot(rel,road.up),forwardSpeed=Math.max(0,dot(vel,road.forward));
  // Bridge only a small suspension gap. A car that truly leaves the structure
  // stays in free flight instead of being magnetically pulled to the road.
  if(height<.35||height>2.65||forwardSpeed<8)return;

  // High-speed tyre/suspension load supplies the centripetal acceleration that
  // keeps the chassis following a vertical ribbon. Scale with v^2/r, capped so
  // bumps, impacts and one-wheel unloads remain visible and physical.
  const centripetal=forwardSpeed*forwardSpeed/Math.max(4,loop.radius),load=ctx.clamp((centripetal-4.5)*.30,0,18.5),gapBlend=ctx.clamp((2.75-height)/1.25,.28,1);
  addForce(acc,mul(road.up,load*gapBlend*b.mass));

  // Contact-patch attitude moment: suspension and tyre forces rotate chassis-up
  // toward the local road normal. This prevents a fast car from remaining
  // globally upright while the open loop itself has already inverted.
  const align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),tiltK=align<.25?13.5:align<.72?10.5:7.2,tiltD=3.25,maxTilt=12.5*b.mass;
  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt);
  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt);
  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt);

  // A modest tyre yaw moment keeps heading tangent to the twisted ribbon. It
  // only acts while chassis-up is on the correct side of the surface.
  if(align>.15){
    const bf={x:2*(b.qx*b.qz+b.qy*b.qw),y:2*(b.qy*b.qz-b.qx*b.qw),z:1-2*(b.qx*b.qx+b.qy*b.qy)},yawErr=dot(road.up,cross(bf,road.forward)),yawTorque=ctx.clamp((yawErr*3.0-yawRate*1.45)*b.mass,-4.2*b.mass,4.2*b.mass),yt=mul(road.up,yawTorque);
    acc.tx+=yt.x;acc.ty+=yt.y;acc.tz+=yt.z;
  }
}

function skyForgeExitGuide(w,c,acc,ctx){
  c.skyForgeExitGuide=false;
  if(w.mode!=='racing'||activeCourse.id!=='sky-forge'||!c?.p3)return;
  const b=c.p3,L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,loop=raceLoopAt(q),after=(q-loop.endS+L)%L,road=racePointAt(q);
  if(after>132||road.kind==='loop')return;
  const bu=bodyUp(b),align=dot(bu,road.up),vel={x:b.vx,y:b.vy,z:b.vz},omega={x:b.wx,y:b.wy,z:b.wz},forwardSpeed=dot(vel,road.forward),rel={x:b.px-road.x,y:b.py-road.y,z:b.pz-road.z},height=dot(rel,road.up),normalSpeed=dot(vel,road.up),lateral=dot(rel,road.right),sideSpeed=dot(vel,road.right);
  c.skyForgeExitGuide=true;

  if(height>1.8||b.groundedWheels===0){
    const downAccel=ctx.clamp(Math.max(0,height-1.35)*3.35+Math.max(0,normalSpeed)*5.9,0,86),sideAccel=ctx.clamp(-lateral*1.65-sideSpeed*2.25,-17,17);
    addForce(acc,mul(road.up,-downAccel*b.mass));
    addForce(acc,mul(road.right,sideAccel*b.mass));
  }

  const target=align<.45?11.5:14.5;
  if(forwardSpeed<target)addForce(acc,mul(road.forward,(target-forwardSpeed)*b.mass*(align<.45?2.4:5.2)));

  const yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),errMag=Math.hypot(tiltErr.x,tiltErr.y,tiltErr.z),rollRate=dot(omega,road.forward),roofDown=align<-.62;
  if(align<-.82&&errMag<.58){const dir=Math.abs(rollRate)>.14?Math.sign(rollRate):(c.id%2?-1:1),kick=roofDown?1.08:.72;tiltErr.x+=road.forward.x*dir*kick;tiltErr.y+=road.forward.y*dir*kick;tiltErr.z+=road.forward.z*dir*kick;}
  const tiltK=roofDown?17.5:(align<0?10.8:7.8),tiltD=roofDown?5.1:3.75,maxTilt=(roofDown?19:11.5)*b.mass;
  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt);
  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt);
  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt);

  if(roofDown&&b.groundedWheels>0&&Math.abs(rollRate)<1.5){
    const dir=Math.abs(rollRate)>.14?Math.sign(rollRate):(c.id%2?-1:1),arm=mul(road.right,1.05*dir),lift=mul(road.up,8.5*b.mass);
    addForce(acc,lift,arm);addForce(acc,mul(lift,-1),mul(arm,-1));
  }

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
  for(let ss=spec.loop.endS+2;ss<=spec.loop.endS+128;ss+=4.0)for(const lane of [-5.6,-2.8,0,2.8,5.6]){const p=trackPoint(ss,lane),pad=box(group,p.x,p.y,p.z,.72,.025,.82,(Math.floor((ss-spec.loop.endS)/4)%2)?0xbffbff:0x64e8f2,true);align(pad,p);pad.position.add(new THREE.Vector3(p.up.x*.075,p.up.y*.075,p.up.z*.075));}
 }
""" + marker
    s = one(s, marker, visual, 'guide pads')
    view.write_text(s)


if __name__ == '__main__':
    apply_sky_loop_exit_v5(Path('_site'))
