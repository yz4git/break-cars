"""Keep SKY FORGE and RAMPAGE chassis attitude attached to their open loops.

The loop geometry is deliberately untouched here. Both courses use physical
contact attitude torque only; position, quaternion, linear/angular velocity,
trackS and raceDistance are never assigned.
"""
from pathlib import Path


def apply_sky_loop_attitude_v6(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    old = """  const align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),tiltK=align<.25?13.5:align<.72?10.5:7.2,tiltD=3.25,maxTilt=12.5*b.mass;\n  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt);"""
    new = """  const align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),errMag=Math.hypot(tiltErr.x,tiltErr.y,tiltErr.z),rollRate=dot(omega,road.forward),sky=activeCourse.id==='sky-forge',rampageLoop=activeCourse.id==='rampage-3d';\n  // The two large open loops rotate the contact frame quickly. Raise physical\n  // attitude authority continuously while wheel/chassis contact follows the\n  // ribbon, rather than applying a late pose correction.\n  const tiltK=sky?(align<.20?19.0:align<.68?16.5:13.8):rampageLoop?(align<.20?22.0:align<.68?18.5:15.0):(align<.25?13.5:align<.72?10.5:7.2),tiltD=sky?4.7:rampageLoop?4.8:3.25,maxTilt=(sky?19.0:rampageLoop?22.0:12.5)*b.mass;\n  // At exactly 180 degrees cross(bodyUp,roadUp) has no preferred axis. SKY's\n  // small deterministic roll-axis seed only breaks that mathematical deadlock.\n  if(sky&&align<-.90&&errMag<.45){const dir=Math.abs(rollRate)>.20?Math.sign(rollRate):(c.id%2?-1:1),kick=.34;tiltErr.x+=road.forward.x*dir*kick;tiltErr.y+=road.forward.y*dir*kick;tiltErr.z+=road.forward.z*dir*kick;}\n  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt);"""
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'SKY/RAMPAGE loop attitude v6: expected 1 attitude block, found {count}')
    path.write_text(s.replace(old, new, 1))


if __name__ == '__main__':
    apply_sky_loop_attitude_v6(Path('_site'))
