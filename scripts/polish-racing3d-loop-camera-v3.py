"""Keep the RAMPAGE 3D vertical loop readable from a side-stage camera.

The camera sits on the loop axis instead of following the chassis around the
circle. That prevents the road ribbon and guard rails from passing between the
camera and the car at the entry or inverted crown.
"""
from pathlib import Path


def apply_racing3d_loop_camera(target: Path) -> None:
    path = target / 'game.js'
    s = path.read_text()
    old = """const loopDx=b.px-fullPhysicsSpec.loop.x,loopRad=Math.hypot(b.py-fullPhysicsSpec.loop.y,b.pz-fullPhysicsSpec.loop.z),inArenaLoop=gameMode!=='racing'&&Math.abs(loopDx)<fullPhysicsSpec.loop.halfWidth+1&&loopRad<fullPhysicsSpec.loop.r+1.8,racingLoop=gameMode==='racing'&&Math.abs(uy)<.72,distance=view===1?16:inArenaLoop?8.4:9.8,lift=view===1?9:inArenaLoop?1.85:4.5+speed*.015,camDistance=racingLoop?distance*.72:distance,camLift=racingLoop?lift*.58:lift;camTarget.set(b.px-fx*camDistance+ux*camLift,b.py-fy*camDistance+uy*camLift,b.pz-fz*camDistance+uz*camLift);lookTarget.set(b.px+fx*4+ux*.55,b.py+fy*4+uy*.55,b.pz+fz*4+uz*.55);physicsCamUp.set(ux,uy,uz);camera.up.lerp(physicsCamUp,1-Math.exp(-6*dt));camera.fov=58+speed*.18;"""
    new = """const loopDx=b.px-fullPhysicsSpec.loop.x,loopRad=Math.hypot(b.py-fullPhysicsSpec.loop.y,b.pz-fullPhysicsSpec.loop.z),inArenaLoop=gameMode!=='racing'&&Math.abs(loopDx)<fullPhysicsSpec.loop.halfWidth+1&&loopRad<fullPhysicsSpec.loop.r+1.8,raceLoopSpec=fullPhysicsSpec.race?.loop,racePose=gameMode==='racing'?trackPoint(p.trackS??0,0):null,racingLoop=!!raceLoopSpec&&!!racePose&&p.trackS>=raceLoopSpec.startS-7&&p.trackS<=raceLoopSpec.endS+7,distance=view===1?16:inArenaLoop?8.4:9.8,lift=view===1?9:inArenaLoop?1.85:4.5+speed*.015;if(racingLoop){const base=trackPoint(raceLoopSpec.startS,0),side=view===1?22:18.5,centerY=base.y+raceLoopSpec.radius,stageLift=view===1?2.8:1.8;camTarget.set(base.x+base.right.x*side,centerY+stageLift+base.right.y*side,base.z+base.right.z*side);lookTarget.set(b.px,b.py+.35,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-10*dt));camera.fov=view===1?55:58;}else{const camDistance=distance,camLift=lift;camTarget.set(b.px-fx*camDistance+ux*camLift,b.py-fy*camDistance+uy*camLift,b.pz-fz*camDistance+uz*camLift);lookTarget.set(b.px+fx*4+ux*.55,b.py+fy*4+uy*.55,b.pz+fz*4+uz*.55);physicsCamUp.set(ux,uy,uz);camera.up.lerp(physicsCamUp,1-Math.exp(-6*dt));camera.fov=58+speed*.18;}"""
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE loop camera: expected 1 match, found {count}')
    path.write_text(s.replace(old, new, 1))


if __name__ == '__main__':
    apply_racing3d_loop_camera(Path('_site'))
