"""Keep DOUBLE ORBIT upright through the actual final jump and landing runoff.

The original v8 gated its attitude helper by a fixed distance after loop two.
Later reference-geometry passes changed DOUBLE ORBIT path length, so the real
jump could fall outside that stale window.  Bind the helper to the generated
jump feature itself instead, then continue a short force/torque-only settling
run after landing.  No position, quaternion, velocity, trackS or raceDistance
is assigned directly.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT final jump v8 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_final_jump_v8(target: Path) -> None:
    physics = target / 'physics3d.js'
    s = physics.read_text()

    anchor = "function doubleOrbitExitRunoff"
    idx = s.find(anchor)
    if idx < 0:
        raise RuntimeError('DOUBLE ORBIT final jump v8: exit runoff helper not found')

    helper = r"""function doubleOrbitFinalJumpAttitude(w,c,ctx,acc){
 const loops=RAMPAGE_RACE_SPEC.loops;if(activeCourse.id!=='double-orbit'||!loops||loops.length<2)return;
 const b=c.p3,L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,road=racePointAt(q),jump=RAMPAGE_RACE_SPEC.jump,onJump=road.kind==='jump-ramp'||road.kind==='jump-gap'||road.kind==='jump-landing',afterJump=jump?((q-jump.endS+L)%L):L,postJump=!!jump&&afterJump<46&&road.kind==='track';
 if(!onJump&&!postJump)return;
 const vel={x:b.vx,y:b.vy,z:b.vz},bu=bodyUp(b),omega={x:b.wx,y:b.wy,z:b.wz},align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},err=cross(bu,road.up),errMag=Math.hypot(err.x,err.y,err.z);
 if(align<-.82&&errMag<.35){const rollRate=dot(omega,road.forward),dir=Math.abs(rollRate)>.12?Math.sign(rollRate):(c.id%2?-1:1),kick=.34;err.x+=road.forward.x*dir*kick;err.y+=road.forward.y*dir*kick;err.z+=road.forward.z*dir*kick;}
 const k=onJump?(align<-.35?17.5:align<.35?13.0:9.0):(align<0?11.5:7.2),d=onJump?4.4:4.8,maxT=(onJump?(align<-.35?18:14):10)*b.mass;
 acc.tx+=ctx.clamp((err.x*k-tiltRate.x*d)*b.mass,-maxT,maxT);
 acc.ty+=ctx.clamp((err.y*k-tiltRate.y*d)*b.mass,-maxT,maxT);
 acc.tz+=ctx.clamp((err.z*k-tiltRate.z*d)*b.mass,-maxT,maxT);
 if(postJump){
  const rel={x:b.px-road.x,y:b.py-road.y,z:b.pz-road.z},height=dot(rel,road.up),forwardSpeed=dot(vel,road.forward),lateral=dot(rel,road.right),sideSpeed=dot(vel,road.right),normalSpeed=dot(vel,road.up),target=c.id===0?14.5:15.5;
  if(forwardSpeed<target){const drive=ctx.clamp((target-forwardSpeed)*(c.id===0?3.9:4.6),0,c.id===0?20:25);addForce(acc,mul(road.forward,drive*b.mass));}
  const laneGoal=c.id===0?0:ctx.clamp((c.loopLane??0)*.58,-3.2,3.2),side=ctx.clamp((laneGoal-lateral)*3.0-sideSpeed*3.8,-24,24);addForce(acc,mul(road.right,side*b.mass));
  if(height>-.75&&height<3.8){const normal=ctx.clamp((.90-height)*8.5-normalSpeed*4.3,-18,28);addForce(acc,mul(road.up,normal*b.mass));}
 }
}

"""
    s = s[:idx] + helper + s[idx:]

    call = "doubleOrbitExitRunoff(w,c,acc,ctx);"
    s = one(s, call, f"doubleOrbitFinalJumpAttitude(w,c,ctx,acc);{call}", 'attitude call')
    physics.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_final_jump_v8(Path('_site'))
