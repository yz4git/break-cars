"""DOUBLE ORBIT pack-flow tuning applied after the shared loop stabilizer.

Keeps both open-helix road meshes unchanged.  CPU traffic gets an extended
first-loop runoff/bridge traction zone so dense packs do not stall before the
second loop.  The player keeps the original natural runoff physics.  All help
is force-only: no position, orientation, velocity, trackS or raceDistance is
written directly.
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

    # The original 95 m zone is retained for the player. CPU pack cars extend
    # to just before loop two, covering the elevated bridge bottleneck.
    s = one(
        s,
        "if(after>95||road.kind==='loop'||road.kind==='jump-ramp'||road.kind==='jump-gap'||road.kind==='jump-landing')return;",
        "if(after>(c.id===0?95:142)||road.kind==='loop'||road.kind==='jump-ramp'||road.kind==='jump-gap'||road.kind==='jump-landing')return;",
        'runoff extent',
    )

    # Keep the player's original lateral tyre response. Only CPU pack cars get
    # extra slip damping after side-by-side loop contact.
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
    physics.write_text(s)

    # Keep the extended purple guide-pad dressing to communicate the CPU pack
    # flow zone. This does not change the actual open-helix road mesh.
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
