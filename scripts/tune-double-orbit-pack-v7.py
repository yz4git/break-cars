"""DOUBLE ORBIT pack-flow tuning applied after the shared loop stabilizer.

Keeps both open-helix road meshes unchanged.  This only extends the visible
first-loop runoff/bridge traction zone so dense traffic does not stall before
the second loop, and catches post-contact hops early with force-only guidance.
No position, orientation, velocity, trackS or raceDistance values are written.
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

    # The old 95 m zone ended around the bridge bottleneck (s ~= 223 m).
    # Extend it to just before loop two so the whole inter-loop connector has
    # the same visible tyre-grip/drive support, without touching loop two.
    s = one(
        s,
        "if(after>95||road.kind==='loop'||road.kind==='jump-ramp'||road.kind==='jump-gap'||road.kind==='jump-landing')return;",
        "if(after>142||road.kind==='loop'||road.kind==='jump-ramp'||road.kind==='jump-gap'||road.kind==='jump-landing')return;",
        'runoff extent',
    )

    # Keep broad lanes, but give side-by-side traffic enough slip damping to
    # recover from contact before reaching the narrow elevated connector.
    s = one(
        s,
        "const laneGoal=c.id===0?0:ctx.clamp((c.loopLane??0)*.72,-4.2,4.2),laneError=lateral-laneGoal,sideAccel=ctx.clamp(-laneError*2.75-sideSpeed*3.15,-20,20);",
        "const laneGoal=c.id===0?0:ctx.clamp((c.loopLane??0)*.72,-4.2,4.2),laneError=lateral-laneGoal,sideAccel=ctx.clamp(-laneError*3.35-sideSpeed*4.15,-27,27);",
        'lateral grip',
    )

    # Bridge pile-ups were dropping to 1-6 m/s.  A stronger tyre-drive floor
    # restores flow while still leaving impacts, steering and wheel contact free.
    s = one(
        s,
        "if(forwardSpeed<13.5){const driveAccel=ctx.clamp((13.5-forwardSpeed)*3.7,0,18);addForce(acc,mul(road.forward,driveAccel*b.mass));}",
        "if(forwardSpeed<16){const driveAccel=ctx.clamp((16-forwardSpeed)*4.8,0,26);addForce(acc,mul(road.forward,driveAccel*b.mass));}",
        'traction floor',
    )

    # Catch launch energy while it is still a recoverable suspension hop.  This
    # remains acceleration along the current road normal; cars are never snapped
    # back to the ribbon and genuinely distant wrecks remain free-flight.
    s = one(
        s,
        "if(b.groundedWheels===0&&height>1.5&&height<4.2){const normalSpeed=dot(vel,road.up),downAccel=ctx.clamp((height-1.35)*2.8+Math.max(0,normalSpeed)*3.2,0,24);addForce(acc,mul(road.up,-downAccel*b.mass));}",
        "if(b.groundedWheels===0&&height>1.2&&height<11){const normalSpeed=dot(vel,road.up),downAccel=ctx.clamp((height-1.05)*4.6+Math.max(0,normalSpeed)*6.8,0,72);addForce(acc,mul(road.up,-downAccel*b.mass));}",
        'airborne runoff load',
    )
    physics.write_text(s)

    # Match the physical zone with visible purple runoff pads all the way across
    # the bridge connector.  The actual open-loop mesh is not modified here.
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
