"""DOUBLE ORBIT v25: match the reference sightline around both open loops.

The reference has clean open throats with no billboard hanging across the lower
arc. Hide the generic WRECK LOOP and BOOST LOOP boards only when the generated
course exposes two loops. Also place the active-loop camera on the side of that
ring opposite the other ring, so loop two is never viewed through loop one.
After that final authored composition, chain the global Camera 2.0 visibility
resolver. Vehicle physics, controls and progress remain unchanged.
"""
from pathlib import Path
import importlib.util


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT reference view v25 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_camera2(target: Path) -> None:
    module_path = Path(__file__).with_name('polish-camera2-v1.py')
    spec = importlib.util.spec_from_file_location('break_cars_camera2_v1', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_camera2_v1(target)


def apply_double_orbit_reference_view_v25(target: Path) -> None:
    track = target / 'track-view.js'
    s = track.read_text()
    board = "const loopP=trackPoint(spec.loop.startS-7,TRACK.halfWidth+4.2),loopBoard=sign('WRECK LOOP',10.5,1.25);loopBoard.position.set(loopP.x,loopP.y+3.4,loopP.z);loopBoard.rotation.y=loopP.heading+Math.PI/2;group.add(loopBoard);"
    clean_board = "if((spec.loops||[]).length<2){const loopP=trackPoint(spec.loop.startS-7,TRACK.halfWidth+4.2),loopBoard=sign('WRECK LOOP',10.5,1.25);loopBoard.position.set(loopP.x,loopP.y+3.4,loopP.z);loopBoard.rotation.y=loopP.heading+Math.PI/2;group.add(loopBoard);}"
    s = one(s, board, clean_board, 'remove DOUBLE ORBIT loop billboard')
    # apply-extreme-courses wraps the original loop dressing in a per-loop
    # loop, so the final template uses loop.startS rather than spec.loop.startS.
    boost = "const boostSignP=trackPoint(loop.startS-28,0),boostSign=sign('BOOST LOOP',16,2);boostSign.position.set(boostSignP.x,boostSignP.y+3.1,boostSignP.z);boostSign.rotation.y=boostSignP.heading+Math.PI/2;group.add(boostSign);"
    clean_boost = "if((spec.loops||[]).length<2){const boostSignP=trackPoint(loop.startS-28,0),boostSign=sign('BOOST LOOP',16,2);boostSign.position.set(boostSignP.x,boostSignP.y+3.1,boostSignP.z);boostSign.rotation.y=boostSignP.heading+Math.PI/2;group.add(boostSign);}"
    s = one(s, boost, clean_boost, 'remove DOUBLE ORBIT boost billboard')
    track.write_text(s)

    game = target / 'game.js'
    s = game.read_text()
    old = "side=(view===1?2.85:2.55)*doubleOrbitLoop.radius*outward,back=(view===1?1.55:1.28)*doubleOrbitLoop.radius,stageLift=view===1?2.8:2.1,loopFocusY=my+doubleOrbitLoop.radius-1.35,playerFocus=.30;camTarget.set(mx+rx*side-fx*back,my+doubleOrbitLoop.radius+stageLift,mz+rz*side-fz*back);"
    new = "side=(view===1?3.05:2.75)*doubleOrbitLoop.radius*outward,back=(view===1?1.62:1.38)*doubleOrbitLoop.radius,stageLift=view===1?2.8:2.1,pair=fullPhysicsSpec.race?.loops||[],loopIndex=pair.indexOf(doubleOrbitLoop),other=pair.length>1?pair[loopIndex===0?1:0]:null,otherP=other?trackPoint((other.startS+other.endS)*.5,0):null,away=otherP&&((otherP.x-mx)*fx+(otherP.z-mz)*fz)>0?-1:1,loopFocusY=my+doubleOrbitLoop.radius-1.35,playerFocus=.30;camTarget.set(mx+rx*side+fx*back*away,my+doubleOrbitLoop.radius+stageLift,mz+rz*side+fz*back*away);"
    s = one(s, old, new, 'camera away from sibling ring')
    game.write_text(s)
    apply_camera2(target)


if __name__ == '__main__':
    apply_double_orbit_reference_view_v25(Path('_site'))