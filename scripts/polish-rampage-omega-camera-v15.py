"""RAMPAGE v15: reveal the real open Omega throat in gameplay.

The v12 road/physics geometry is left completely unchanged.  Its two lower legs
are physically separated along depth, but the near-perfect side camera collapses
that separation and makes the open Omega read like a closed hoop with an X at
the bottom.  View the same geometry about 29 degrees off-axis so both lower legs
remain distinct on screen, and tighten the framing to reduce unrelated figure-
eight road clutter around the stunt.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE Omega camera v15 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_omega_camera_v15(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    old = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,dx=z.x-a.x,dz=z.z-a.z,dl=Math.hypot(dx,dz)||1,nx=dx/dl,nz=dz/dl,fx=a.forward.x,fz=a.forward.z,outward=(mx*nx+mz*nz)>=0?1:-1,side=-(view===1?3.35:3.15)*raceLoopSpec.radius*outward,back=(view===1?.72:.62)*raceLoopSpec.radius,stageLift=view===1?4.0:3.0;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(b.px,b.py+.45,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?58:60;"""
    new = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,dx=z.x-a.x,dz=z.z-a.z,dl=Math.hypot(dx,dz)||1,nx=dx/dl,nz=dz/dl,fx=a.forward.x,fz=a.forward.z,outward=(mx*nx+mz*nz)>=0?1:-1,side=-(view===1?2.95:2.75)*raceLoopSpec.radius*outward,back=(view===1?1.72:1.55)*raceLoopSpec.radius,stageLift=view===1?3.5:2.7;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(b.px,b.py+.45,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?54:55;"""
    s = one(s, old, new, 'oblique whole-loop framing')
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_omega_camera_v15(Path('_site'))
