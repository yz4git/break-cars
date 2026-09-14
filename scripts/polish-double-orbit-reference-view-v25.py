"""WRECKING RACING loop-view v27: side-stage the player clear of loop surfaces.

Live iPhone captures from v26 proved that distance alone was not the problem:
RAMPAGE could hide the player completely behind the loop ribbon, SKY FORGE
partly buried the car under the loop deck, and DOUBLE ORBIT could still look
through the ring on exit. Keep the stable v18 -> v24 generation contract, then
apply this final camera pass after v24: while the player is in a loop, follow
from a fixed horizontal axis perpendicular to the loop plane and look directly
at the car. That keeps the player large enough to drive while still showing the
loop as a set piece instead of placing the camera in the road surface.

DOUBLE ORBIT adds a small along-track bias away from the sibling ring. Camera
2.0 is chained last and continues to yield while an authored loop camera owns
the composition. Vehicle physics, controls, progress, damage, AI and course
geometry remain unchanged.
"""
from pathlib import Path
import importlib.util


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'WRECKING RACING loop-view v27 {label}: expected 1 match, found {n}')
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
    double_new = "sideDist=view===1?17.5:15.5,stageLift=view===1?3.1:2.4,pair=fullPhysicsSpec.race?.loops||[],loopIndex=pair.indexOf(doubleOrbitLoop),other=pair.length>1?pair[loopIndex===0?1:0]:null,otherP=other?trackPoint((other.startS+other.endS)*.5,0):null,away=otherP&&((otherP.x-mx)*fx+(otherP.z-mz)*fz)>0?-1:1,camSide=(mx*rx+mz*rz)>=0?1:-1,loopFocusY=b.py+.45,playerFocus=1;camTarget.set(b.px+rx*camSide*sideDist+fx*away*2.8,b.py+stageLift,b.pz+rz*camSide*sideDist+fz*away*2.8);"
    s = one(s, double_old, double_new, 'side-stage DOUBLE ORBIT camera')

    generic_old = "side=-(view===1?2.64:2.45)*raceLoopSpec.radius*outward,back=(view===1?2.17:2.00)*raceLoopSpec.radius,stageLift=view===1?3.5:2.7,loopFocusY=my+raceLoopSpec.radius-2.6,playerFocus=.24;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(mx+(b.px-mx)*playerFocus,loopFocusY+(b.py+.45-loopFocusY)*playerFocus,mz+(b.pz-mz)*playerFocus);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?54:55;"
    generic_new = "rd2=Math.hypot(a.right.x,a.right.z)||1,rx2=a.right.x/rd2,rz2=a.right.z/rd2,camSide=(mx*rx2+mz*rz2)>=0?1:-1,sideDist=view===1?17:15,stageLift=view===1?3.2:2.5,loopFocusY=b.py+.45,playerFocus=1;camTarget.set(b.px+rx2*camSide*sideDist,b.py+stageLift,b.pz+rz2*camSide*sideDist);lookTarget.set(mx+(b.px-mx)*playerFocus,loopFocusY+(b.py+.45-loopFocusY)*playerFocus,mz+(b.pz-mz)*playerFocus);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?56:58;"
    s = one(s, generic_old, generic_new, 'side-stage RAMPAGE/SKY camera')

    game.write_text(s)
    apply_clean_throat(target)
    apply_camera2(target)


if __name__ == '__main__':
    apply_double_orbit_reference_view_v25(Path('_site'))
