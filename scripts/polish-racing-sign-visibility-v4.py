"""Final racing visibility and stability polish.

Move the large loop billboard away from the loop/jump/chase-camera centerline.
The sign remains as track dressing, but is smaller and sits outside the road at
loop entry so it cannot cover the player's car during vertical stunts.

This transform intentionally runs after the SKY FORGE exit-guide transform, so
it also gives that physical guide a small recovery margin for rare roof-down
landings. The adjustment remains force/torque-only: no position, rotation,
velocity, track progress, recovery event, or auto-upright state is overwritten.
"""
from pathlib import Path


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'racing visibility v4 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_racing_sign_visibility_v4(target: Path) -> None:
    p = target / 'track-view.js'
    s = p.read_text()
    old = "const loopBoard=sign('VERTICAL WRECK LOOP',18,2);const loopP=trackPoint((spec.loop.startS+spec.loop.endS)*.5,0);loopBoard.position.set(loopP.x,loopP.y+2.5,loopP.z-5);loopBoard.rotation.y=loopP.heading+Math.PI/2;group.add(loopBoard);"
    new = "const loopP=trackPoint(spec.loop.startS-7,TRACK.halfWidth+4.2),loopBoard=sign('WRECK LOOP',10.5,1.25);loopBoard.position.set(loopP.x,loopP.y+3.4,loopP.z);loopBoard.rotation.y=loopP.heading+Math.PI/2;group.add(loopBoard);"
    p.write_text(_replace_once(s, old, new, 'loop-board template'))

    # The open-loop projection is now locally continuous, which means SKY FORGE
    # reaches the exit guide with more varied but physically correct attitudes.
    # Start assisting a roof-down chassis slightly earlier and add modest torque
    # headroom so it rolls onto its wheels before the normal player safety timer
    # becomes relevant. Impacts and free-flight rotation remain fully simulated.
    p = target / 'physics3d.js'
    s = p.read_text()
    s = _replace_once(
        s,
        "rollRate=dot(omega,road.forward),roofDown=align<-.62;",
        "rollRate=dot(omega,road.forward),roofDown=align<-.58;",
        'SKY roof-down threshold',
    )
    s = _replace_once(
        s,
        "if(align<-.82&&errMag<.58){const dir=Math.abs(rollRate)>.14?Math.sign(rollRate):(c.id%2?-1:1),kick=roofDown?1.08:.72;",
        "if(align<-.76&&errMag<.68){const dir=Math.abs(rollRate)>.14?Math.sign(rollRate):(c.id%2?-1:1),kick=roofDown?1.20:.72;",
        'SKY roll escape kick',
    )
    s = _replace_once(
        s,
        "const tiltK=roofDown?17.5:(align<0?10.8:7.8),tiltD=roofDown?5.1:3.75,maxTilt=(roofDown?19:11.5)*b.mass;",
        "const tiltK=roofDown?20.5:(align<0?10.8:7.8),tiltD=roofDown?5.4:3.75,maxTilt=(roofDown?22:11.5)*b.mass;",
        'SKY recovery torque',
    )
    s = _replace_once(
        s,
        "if(roofDown&&b.groundedWheels>0&&Math.abs(rollRate)<1.5){\n    const dir=Math.abs(rollRate)>.14?Math.sign(rollRate):(c.id%2?-1:1),arm=mul(road.right,1.05*dir),lift=mul(road.up,8.5*b.mass);",
        "if(roofDown&&b.groundedWheels>0&&Math.abs(rollRate)<1.8){\n    const dir=Math.abs(rollRate)>.14?Math.sign(rollRate):(c.id%2?-1:1),arm=mul(road.right,1.05*dir),lift=mul(road.up,10.0*b.mass);",
        'SKY grounded rocking couple',
    )
    p.write_text(s)


if __name__ == '__main__':
    apply_racing_sign_visibility_v4(Path('_site'))
