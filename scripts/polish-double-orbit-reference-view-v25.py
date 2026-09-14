"""WRECKING RACING loop-view v26: keep loop scale without losing the player.

The clean-throat/reference composition remains, but live iPhone captures showed
the active car becoming too small around all three WRECKING RACING loop stages.
Apply the final camera polish only after DOUBLE ORBIT v24 has consumed the
stable v18 input contract: DOUBLE ORBIT stays on the side away from its sibling
ring, while RAMPAGE/SKY move closer and bias their look target toward the car.
Camera 2.0 is chained last and yields to the authored camera while actually on a
loop. Vehicle physics, controls, progress and course geometry remain unchanged.
"""
from pathlib import Path
import importlib.util


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'WRECKING RACING loop-view v26 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_camera2(target: Path) -> None:
    module_path = Path(__file__).with_name('polish-camera2-v1.py')
    spec = importlib.util.spec_from_file_location('break_cars_camera2_v1', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_camera2_v1(target)


def apply_clean_throat(target: Path) -> None:
    module_path = Path(__file__).with_name('polish-double-orbit-clean-throat-v28.py')
    spec = importlib.util.spec_from_file_location('break_cars_double_orbit_clean_throat_v28', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_double_orbit_clean_throat_v28(target)


def apply_double_orbit_reference_view_v25(target: Path) -> None:
    track = target / 'track-view.js'
    s = track.read_text()
    board = "const loopP=trackPoint(spec.loop.startS-7,TRACK.halfWidth+4.2),loopBoard=sign('WRECK LOOP',10.5,1.25);loopBoard.position.set(loopP.x,loopP.y+3.4,loopP.z);loopBoard.rotation.y=loopP.heading+Math.PI/2;group.add(loopBoard);"
    clean_board = "if((spec.loops||[]).length<2){const loopP=trackPoint(spec.loop.startS-7,TRACK.halfWidth+4.2),loopBoard=sign('WRECK LOOP',10.5,1.25);loopBoard.position.set(loopP.x,loopP.y+3.4,loopP.z);loopBoard.rotation.y=loopP.heading+Math.PI/2;group.add(loopBoard);}"
    s = one(s, board, clean_board, 'remove DOUBLE ORBIT loop billboard')
    boost = "const boostSignP=trackPoint(loop.startS-28,0),boostSign=sign('BOOST LOOP',16,2);boostSign.position.set(boostSignP.x,boostSignP.y+3.1,boostSignP.z);boostSign.rotation.y=boostSignP.heading+Math.PI/2;group.add(boostSign);"
    clean_boost = "if((spec.loops||[]).length<2){const boostSignP=trackPoint(loop.startS-28,0),boostSign=sign('BOOST LOOP',16,2);boostSign.position.set(boostSignP.x,boostSignP.y+3.1,boostSignP.z);boostSign.rotation.y=boostSignP.heading+Math.PI/2;group.add(boostSign);}"
    s = one(s, boost, clean_boost, 'remove DOUBLE ORBIT boost billboard')
    track.write_text(s)

    game = target / 'game.js'
    s = game.read_text()

    double_old = "side=(view===1?2.85:2.55)*doubleOrbitLoop.radius*outward,back=(view===1?1.55:1.28)*doubleOrbitLoop.radius,stageLift=view===1?2.8:2.1,loopFocusY=my+doubleOrbitLoop.radius-1.35,playerFocus=.30;camTarget.set(mx+rx*side-fx*back,my+doubleOrbitLoop.radius+stageLift,mz+rz*side-fz*back);"
    double_new = "side=(view===1?2.15:1.90)*doubleOrbitLoop.radius*outward,back=(view===1?1.20:1.05)*doubleOrbitLoop.radius,stageLift=view===1?2.8:2.1,pair=fullPhysicsSpec.race?.loops||[],loopIndex=pair.indexOf(doubleOrbitLoop),other=pair.length>1?pair[loopIndex===0?1:0]:null,otherP=other?trackPoint((other.startS+other.endS)*.5,0):null,away=otherP&&((otherP.x-mx)*fx+(otherP.z-mz)*fz)>0?-1:1,loopFocusY=my+doubleOrbitLoop.radius-1.15,playerFocus=view===1?.48:.58;camTarget.set(mx+rx*side+fx*back*away,my+doubleOrbitLoop.radius+stageLift,mz+rz*side+fz*back*away);"
    s = one(s, double_old, double_new, 'closer DOUBLE ORBIT camera away from sibling ring')

    generic_old = "side=-(view===1?2.64:2.45)*raceLoopSpec.radius*outward,back=(view===1?2.17:2.00)*raceLoopSpec.radius,stageLift=view===1?3.5:2.7,loopFocusY=my+raceLoopSpec.radius-2.6,playerFocus=.24;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(mx+(b.px-mx)*playerFocus,loopFocusY+(b.py+.45-loopFocusY)*playerFocus,mz+(b.pz-mz)*playerFocus);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?54:55;"
    generic_new = "side=-(view===1?2.05:1.82)*raceLoopSpec.radius*outward,back=(view===1?1.48:1.30)*raceLoopSpec.radius,stageLift=view===1?3.5:2.7,loopFocusY=my+raceLoopSpec.radius-2.0,playerFocus=view===1?.48:.58;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(mx+(b.px-mx)*playerFocus,loopFocusY+(b.py+.45-loopFocusY)*playerFocus,mz+(b.pz-mz)*playerFocus);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?56:58;"
    s = one(s, generic_old, generic_new, 'closer RAMPAGE/SKY camera')

    game.write_text(s)
    apply_clean_throat(target)
    apply_camera2(target)


if __name__ == '__main__':
    apply_double_orbit_reference_view_v25(Path('_site'))
