"""Keep SKY FORGE and RAMPAGE chassis attitude attached to their open loops.

The loop geometry is deliberately untouched here. Both courses use physical
contact attitude torque only; position, quaternion, linear/angular velocity,
trackS and raceDistance are never assigned. RAMPAGE additionally follows the
measured road-curvature pitch rate so its conventional vertical loop does not
hit the 180-degree shortest-path singularity at the crown.
"""
from pathlib import Path


def apply_sky_loop_attitude_v6(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    old = """  const align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),tiltK=align<.25?13.5:align<.72?10.5:7.2,tiltD=3.25,maxTilt=12.5*b.mass;\n  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt);\n  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt);"""
    new = """  const align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),errMag=Math.hypot(tiltErr.x,tiltErr.y,tiltErr.z),rollRate=dot(omega,road.forward),sky=activeCourse.id==='sky-forge',rampageLoop=activeCourse.id==='rampage-3d';\n  // SKY keeps the proven general attitude spring. RAMPAGE's reference-style\n  // vertical loop is driven primarily by a curvature-directed physical pitch\n  // moment so the chassis cannot choose the wrong shortest path at 180deg.\n  const tiltK=sky?(align<.20?19.0:align<.68?16.5:13.8):rampageLoop?12.0:(align<.25?13.5:align<.72?10.5:7.2),tiltD=sky?4.7:rampageLoop?3.8:3.25,maxTilt=(sky?19.0:rampageLoop?14.0:12.5)*b.mass;\n  if(sky&&align<-.90&&errMag<.45){const dir=Math.abs(rollRate)>.20?Math.sign(rollRate):(c.id%2?-1:1),kick=.34;tiltErr.x+=road.forward.x*dir*kick;tiltErr.y+=road.forward.y*dir*kick;tiltErr.z+=road.forward.z*dir*kick;}\n  let rampagePitchTorque={x:0,y:0,z:0};\n  if(rampageLoop){\n    const ds=.55,rb=racePointAt(q-ds),ra=racePointAt(q+ds),curve=cross(rb.forward,ra.forward),basePitch=ctx.clamp(dot(curve,road.right)*Math.max(8,forwardSpeed)/(2*ds),-4.5,4.5),turnDir=Math.abs(basePitch)>.08?Math.sign(basePitch):-1,pitchRate=dot(omega,road.right),angleError=Math.acos(ctx.clamp(align,-1,1)),desiredPitch=ctx.clamp(basePitch+turnDir*angleError*5.2,-14.0,14.0),pitchTorque=ctx.clamp((desiredPitch-pitchRate)*b.mass*10.0,-55*b.mass,55*b.mass);rampagePitchTorque=mul(road.right,pitchTorque);\n    if(align<.45){const along=dot(tiltErr,road.right);tiltErr.x-=road.right.x*along;tiltErr.y-=road.right.y*along;tiltErr.z-=road.right.z*along;}\n  }\n  acc.tx+=ctx.clamp((tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass,-maxTilt,maxTilt)+rampagePitchTorque.x;\n  acc.ty+=ctx.clamp((tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass,-maxTilt,maxTilt)+rampagePitchTorque.y;\n  acc.tz+=ctx.clamp((tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass,-maxTilt,maxTilt)+rampagePitchTorque.z;"""
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'SKY/RAMPAGE loop attitude v6: expected 1 attitude block, found {count}')
    s = s.replace(old, new, 1)

    # The broader RAMPAGE loop begins rotating while the chassis can still be a
    # little above nominal suspension height. Keep the contact moment active
    # through that transient so the physical pitch controller engages before
    # the vertical section; other courses retain their previous bridge window.
    contact_old = "if(height<.35||height>(rampage?2.35:2.65))return;"
    contact_new = "if(height<(rampage?.25:.35)||height>(rampage?3.25:2.65))return;"
    count = s.count(contact_old)
    if count != 1:
        raise RuntimeError(f'SKY/RAMPAGE loop attitude v6: expected 1 contact gate, found {count}')
    s = s.replace(contact_old, contact_new, 1)
    path.write_text(s)


if __name__ == '__main__':
    apply_sky_loop_attitude_v6(Path('_site'))