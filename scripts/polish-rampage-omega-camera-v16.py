"""RAMPAGE v16: rotate the whole-loop camera to expose the Omega throat.

v15 moved the camera off-axis without changing the physical Omega. Live WebGL
captures still foreshorten the two lower C2 legs enough that the stunt reads
more like a closed circular hoop than the intended open Omega.

This pass changes presentation only. It rotates the camera orbit from roughly
29 degrees to roughly 39 degrees while keeping almost exactly the same camera
radius, elevation, FOV, and player-follow target. Geometry, physics, input,
boost, AI, and collision behavior are unchanged.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE Omega camera v16 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_omega_camera_v16(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    old = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,dx=z.x-a.x,dz=z.z-a.z,dl=Math.hypot(dx,dz)||1,nx=dx/dl,nz=dz/dl,fx=a.forward.x,fz=a.forward.z,outward=(mx*nx+mz*nz)>=0?1:-1,side=-(view===1?2.95:2.75)*raceLoopSpec.radius*outward,back=(view===1?1.72:1.55)*raceLoopSpec.radius,stageLift=view===1?3.5:2.7;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(b.px,b.py+.45,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?54:55;"""
    new = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,dx=z.x-a.x,dz=z.z-a.z,dl=Math.hypot(dx,dz)||1,nx=dx/dl,nz=dz/dl,fx=a.forward.x,fz=a.forward.z,outward=(mx*nx+mz*nz)>=0?1:-1,side=-(view===1?2.64:2.45)*raceLoopSpec.radius*outward,back=(view===1?2.17:2.00)*raceLoopSpec.radius,stageLift=view===1?3.5:2.7;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(b.px,b.py+.45,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?54:55;"""
    s = one(s, old, new, '39-degree same-distance orbit')
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_omega_camera_v16(Path('_site'))
