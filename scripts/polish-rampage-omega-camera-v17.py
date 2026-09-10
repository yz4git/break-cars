"""RAMPAGE v17: stabilize the Omega as a stage while still following the car.

v16 successfully exposes the lower throat, but live WebGL captures show that
using the vehicle itself as the full look target tilts the view too far upward
at the crown and too far downward at the exit. The camera position, distance,
FOV and physical course stay unchanged. Only the look target is blended 24%
toward the player from the geometric loop centre, keeping the whole Omega and
its throat readable throughout the stunt without turning it into a static shot.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE Omega camera v17 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_omega_camera_v17(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    old = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,dx=z.x-a.x,dz=z.z-a.z,dl=Math.hypot(dx,dz)||1,nx=dx/dl,nz=dz/dl,fx=a.forward.x,fz=a.forward.z,outward=(mx*nx+mz*nz)>=0?1:-1,side=-(view===1?2.64:2.45)*raceLoopSpec.radius*outward,back=(view===1?2.17:2.00)*raceLoopSpec.radius,stageLift=view===1?3.5:2.7;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(b.px,b.py+.45,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?54:55;"""
    new = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,dx=z.x-a.x,dz=z.z-a.z,dl=Math.hypot(dx,dz)||1,nx=dx/dl,nz=dz/dl,fx=a.forward.x,fz=a.forward.z,outward=(mx*nx+mz*nz)>=0?1:-1,side=-(view===1?2.64:2.45)*raceLoopSpec.radius*outward,back=(view===1?2.17:2.00)*raceLoopSpec.radius,stageLift=view===1?3.5:2.7,loopFocusY=my+raceLoopSpec.radius,playerFocus=.24;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(mx+(b.px-mx)*playerFocus,loopFocusY+(b.py+.45-loopFocusY)*playerFocus,mz+(b.pz-mz)*playerFocus);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?54:55;"""
    s = one(s, old, new, 'stage-centred look target')
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_omega_camera_v17(Path('_site'))
