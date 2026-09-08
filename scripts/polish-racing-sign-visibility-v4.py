"""Final racing visibility polish.

Move the large loop billboard away from the loop/jump/chase-camera centerline.
The sign remains as track dressing, but is smaller and sits outside the road at
loop entry so it cannot cover the player's car during vertical stunts.
"""
from pathlib import Path


def apply_racing_sign_visibility_v4(target: Path) -> None:
    p = target / 'track-view.js'
    s = p.read_text()
    old = "const loopBoard=sign('VERTICAL WRECK LOOP',18,2);const loopP=trackPoint((loop.startS+loop.endS)*.5,0);loopBoard.position.set(loopP.x,loopP.y+2.5,loopP.z-5);loopBoard.rotation.y=loopP.heading+Math.PI/2;group.add(loopBoard);"
    new = "const loopP=trackPoint(loop.startS-7,TRACK.halfWidth+4.2),loopBoard=sign('WRECK LOOP',10.5,1.25);loopBoard.position.set(loopP.x,loopP.y+3.4,loopP.z);loopBoard.rotation.y=loopP.heading+Math.PI/2;group.add(loopBoard);"
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f'racing visibility v4: expected 1 loop-board template, found {n}')
    p.write_text(s.replace(old, new, 1))


if __name__ == '__main__':
    apply_racing_sign_visibility_v4(Path('_site'))
