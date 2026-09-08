"""Break SKY FORGE's 180-degree loop attitude deadlock with torque only.

The open photo-shaped loop geometry is left untouched.  At the rare exact
anti-aligned attitude, cross(bodyUp, roadUp) approaches zero even though the
car is on the wrong side of the local road frame, so the ordinary attitude PD
has no axis to act around.  Give only SKY FORGE a deterministic roll-axis
escape moment while that singular state is present.  Position, quaternion,
linear/angular velocity, trackS and raceDistance are never assigned.
"""
from pathlib import Path


def apply_sky_loop_attitude_v6(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    old = """  const align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),tiltK=align<.25?13.5:align<.72?10.5:7.2,tiltD=3.25,maxTilt=12.5*b.mass;\n  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt);"""
    new = """  const align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),errMag=Math.hypot(tiltErr.x,tiltErr.y,tiltErr.z),rollRate=dot(omega,road.forward),sky=activeCourse.id==='sky-forge';\n  // At exactly 180 degrees the cross-product error has no preferred axis.\n  // SKY seed 1 can reach that singular state on the descending crown while\n  // still in physical contact.  Seed a roll direction from existing angular\n  // motion (or deterministic car parity) so the normal PD can resume.\n  if(sky&&align<-.70&&errMag<.72){const dir=Math.abs(rollRate)>.18?Math.sign(rollRate):(c.id%2?-1:1),kick=.98;tiltErr.x+=road.forward.x*dir*kick;tiltErr.y+=road.forward.y*dir*kick;tiltErr.z+=road.forward.z*dir*kick;}\n  const tiltK=sky&&align<.2?15.5:align<.25?13.5:align<.72?10.5:7.2,tiltD=sky&&align<0?3.8:3.25,maxTilt=(sky&&align<0?15.5:12.5)*b.mass;\n  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt);"""
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'SKY loop attitude v6: expected 1 attitude block, found {count}')
    path.write_text(s.replace(old, new, 1))


if __name__ == '__main__':
    apply_sky_loop_attitude_v6(Path('_site'))
