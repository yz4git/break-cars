"""DOUBLE ORBIT pack-flow and bridge recovery tuning.

Keeps both photo-shaped open-loop road meshes unchanged.  The first-loop
runoff/bridge zone uses tyre-like force and torque only so both player and CPU
cars keep flowing toward loop two without an automatic recovery.  No position,
orientation, velocity, trackS or raceDistance is written directly.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT v7 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_pack_v7(target: Path) -> None:
    physics = target / 'physics3d.js'
    s = physics.read_text()

    # Extend the physical runoff through the elevated bridge for the player too.
    # The previous 95 m player cutoff ended just before the seed-2468 roof-down
    # bridge state at trackS~220 m.  This still stops before loop two itself.
    s = one(
        s,
        "if(after>95||road.kind==='loop'||road.kind==='jump-ramp'||road.kind==='jump-gap'||road.kind==='jump-landing')return;",
        "if(after>142||road.kind==='loop'||road.kind==='jump-ramp'||road.kind==='jump-gap'||road.kind==='jump-landing')return;",
        'runoff extent',
    )

    # Keep the player's measured tyre response; CPU pack cars get extra slip
    # damping after side-by-side contact.
    s = one(
        s,
        "const laneGoal=c.id===0?0:ctx.clamp((c.loopLane??0)*.72,-4.2,4.2),laneError=lateral-laneGoal,sideAccel=ctx.clamp(-laneError*2.75-sideSpeed*3.15,-20,20);",
        "const laneGoal=c.id===0?0:ctx.clamp((c.loopLane??0)*.72,-4.2,4.2),laneError=lateral-laneGoal,sideAccel=c.id===0?ctx.clamp(-laneError*2.75-sideSpeed*3.15,-20,20):ctx.clamp(-laneError*3.35-sideSpeed*4.15,-27,27);",
        'lateral grip',
    )

    # Preserve the natural 13.5 m/s player runoff. CPU cars use a stronger
    # traction floor to stop bridge contact from becoming a permanent wall-pile.
    s = one(
        s,
        "if(forwardSpeed<13.5){const driveAccel=ctx.clamp((13.5-forwardSpeed)*3.7,0,18);addForce(acc,mul(road.forward,driveAccel*b.mass));}",
        "const runoffTarget=c.id===0?13.5:16,runoffGain=c.id===0?3.7:4.8,runoffMax=c.id===0?18:26;if(forwardSpeed<runoffTarget){const driveAccel=ctx.clamp((runoffTarget-forwardSpeed)*runoffGain,0,runoffMax);addForce(acc,mul(road.forward,driveAccel*b.mass));}",
        'traction floor',
    )

    # Player keeps the previous suspension-hop window exactly. CPU cars catch
    # higher post-contact launches while they are still close enough to recover.
    s = one(
        s,
        "if(b.groundedWheels===0&&height>1.5&&height<4.2){const normalSpeed=dot(vel,road.up),downAccel=ctx.clamp((height-1.35)*2.8+Math.max(0,normalSpeed)*3.2,0,24);addForce(acc,mul(road.up,-downAccel*b.mass));}",
        "if(b.groundedWheels===0&&height>(c.id===0?1.5:1.2)&&height<(c.id===0?4.2:11)){const normalSpeed=dot(vel,road.up),downAccel=c.id===0?ctx.clamp((height-1.35)*2.8+Math.max(0,normalSpeed)*3.2,0,24):ctx.clamp((height-1.05)*4.6+Math.max(0,normalSpeed)*6.8,0,72);addForce(acc,mul(road.up,-downAccel*b.mass));}",
        'airborne runoff load',
    )

    # A car can leave loop one with the roof facing the bridge while still
    # carrying healthy forward speed.  The generic 5 s safety recovery then
    # fires even though the car is still on the intended route.  Model the
    # missing tyre/chassis roll response with a bounded torque around the road
    # tangent.  It acts only in this runoff/bridge helper and never snaps pose.
    anchor = """  if(b.groundedWheels===0&&height>(c.id===0?1.5:1.2)&&height<(c.id===0?4.2:11)){const normalSpeed=dot(vel,road.up),downAccel=c.id===0?ctx.clamp((height-1.35)*2.8+Math.max(0,normalSpeed)*3.2,0,24):ctx.clamp((height-1.05)*4.6+Math.max(0,normalSpeed)*6.8,0,72);addForce(acc,mul(road.up,-downAccel*b.mass));}\n}"""
    replacement = """  if(b.groundedWheels===0&&height>(c.id===0?1.5:1.2)&&height<(c.id===0?4.2:11)){const normalSpeed=dot(vel,road.up),downAccel=c.id===0?ctx.clamp((height-1.35)*2.8+Math.max(0,normalSpeed)*3.2,0,24):ctx.clamp((height-1.05)*4.6+Math.max(0,normalSpeed)*6.8,0,72);addForce(acc,mul(road.up,-downAccel*b.mass));}\n\n  const bu=bodyUp(b),align=dot(bu,road.up);\n  if(align<.58){\n    const omega={x:b.wx,y:b.wy,z:b.wz},rollRate=dot(omega,road.forward),gradient=dot(road.forward,cross(bu,road.up));\n    let dir=Math.abs(gradient)>.035?Math.sign(gradient):(Math.abs(rollRate)>.16?Math.sign(rollRate):(c.id%2?-1:1));\n    const urgency=ctx.clamp((.58-align)/1.58,0,1),desiredRoll=dir*(1.45+urgency*1.45),rollTorque=ctx.clamp((desiredRoll-rollRate)*b.mass*1.95,-5.0*b.mass,5.0*b.mass),T=mul(road.forward,rollTorque);\n    acc.tx+=T.x;acc.ty+=T.y;acc.tz+=T.z;\n    // If the roof is resting on the bridge, a small equal-and-opposite force\n    // couple supplies the lever arm a real chassis/tyre contact patch would.\n    if(align<-.58&&b.groundedWheels>0&&Math.abs(rollRate)<1.55){\n      const arm=mul(road.right,1.0*dir),lift=mul(road.up,8.8*b.mass);addForce(acc,lift,arm);addForce(acc,mul(lift,-1),mul(arm,-1));\n    }\n  }\n}"""
    s = one(s, anchor, replacement, 'bridge roll recovery')
    physics.write_text(s)

    # Extended purple guide pads communicate the physical runoff/bridge zone.
    # They are dressing only and do not alter the loop road mesh.
    view = target / 'track-view.js'
    s = view.read_text()
    s = one(
        s,
        "for(let ss=first.endS+4;ss<=first.endS+90;ss+=5.0)",
        "for(let ss=first.endS+4;ss<=first.endS+137;ss+=5.0)",
        'visible runoff pads',
    )
    view.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_pack_v7(Path('_site'))
