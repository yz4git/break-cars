"""Keep SKY FORGE chassis attitude attached to the photo-shaped loop with torque only.

The loop geometry is deliberately untouched.  SKY seed 1 was not failing at
the entrance: it entered the correct front surface, but chassis-up lagged the
rapidly rotating road normal near the crown (while still in wheel contact),
then fell into the 180-degree cross-product singularity.  Give SKY FORGE a
stronger *continuous* contact attitude PD before that singularity is reached,
with only a small deterministic escape moment if it still becomes exactly
anti-aligned.  Position, quaternion, linear/angular velocity, trackS and
raceDistance are never assigned.
"""
from pathlib import Path


def apply_sky_loop_attitude_v6(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    old = """  const align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),tiltK=align<.25?13.5:align<.72?10.5:7.2,tiltD=3.25,maxTilt=12.5*b.mass;\n  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt);"""
    new = """  const align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),errMag=Math.hypot(tiltErr.x,tiltErr.y,tiltErr.z),rollRate=dot(omega,road.forward),sky=activeCourse.id==='sky-forge';\n  // SKY's tighter crown rotates the contact frame quickly enough that the\n  // generic low-gain controller can lag even with wheels still on the ribbon.\n  // Raise contact attitude authority throughout the loop instead of waiting for\n  // the car to become roof-down.  This remains ordinary torque + damping.\n  const tiltK=sky?(align<.20?19.0:align<.68?16.5:13.8):(align<.25?13.5:align<.72?10.5:7.2),tiltD=sky?4.7:3.25,maxTilt=(sky?19.0:12.5)*b.mass;\n  // At exactly 180 degrees cross(bodyUp,roadUp) has no preferred axis.  A small\n  // roll-axis seed only breaks that mathematical deadlock; the continuous PD\n  // does the actual recovery, avoiding the violent late kick used previously.\n  if(sky&&align<-.90&&errMag<.45){const dir=Math.abs(rollRate)>.20?Math.sign(rollRate):(c.id%2?-1:1),kick=.34;tiltErr.x+=road.forward.x*dir*kick;tiltErr.y+=road.forward.y*dir*kick;tiltErr.z+=road.forward.z*dir*kick;}\n  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt);"""
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'SKY loop attitude v6: expected 1 attitude block, found {count}')
    path.write_text(s.replace(old, new, 1))


if __name__ == '__main__':
    apply_sky_loop_attitude_v6(Path('_site'))
