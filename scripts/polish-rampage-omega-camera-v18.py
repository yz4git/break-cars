"""RAMPAGE/SKY v19 framing: keep the car readable inside the Omega stage.

The v17/v18 side-stage camera made the complete loop readable, but live iPhone
captures showed the controllable car shrinking to a tiny subject or drifting to
a screen edge. Move the stage camera materially closer and bias the look target
toward the player while preserving the world-up side-stage composition.

Vehicle physics, loop geometry, progress, input, damage and scoring are unchanged.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE Omega camera v19 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_omega_camera_v18(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    old = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,dx=z.x-a.x,dz=z.z-a.z,dl=Math.hypot(dx,dz)||1,nx=dx/dl,nz=dz/dl,fx=a.forward.x,fz=a.forward.z,outward=(mx*nx+mz*nz)>=0?1:-1,side=-(view===1?2.64:2.45)*raceLoopSpec.radius*outward,back=(view===1?2.17:2.00)*raceLoopSpec.radius,stageLift=view===1?3.5:2.7,loopFocusY=my+raceLoopSpec.radius,playerFocus=.24;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(mx+(b.px-mx)*playerFocus,loopFocusY+(b.py+.45-loopFocusY)*playerFocus,mz+(b.pz-mz)*playerFocus);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?54:55;"""
    new = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,dx=z.x-a.x,dz=z.z-a.z,dl=Math.hypot(dx,dz)||1,nx=dx/dl,nz=dz/dl,fx=a.forward.x,fz=a.forward.z,outward=(mx*nx+mz*nz)>=0?1:-1,side=-(view===1?2.05:1.82)*raceLoopSpec.radius*outward,back=(view===1?1.48:1.30)*raceLoopSpec.radius,stageLift=view===1?3.5:2.7,loopFocusY=my+raceLoopSpec.radius-2.0,playerFocus=view===1?.48:.58;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(mx+(b.px-mx)*playerFocus,loopFocusY+(b.py+.45-loopFocusY)*playerFocus,mz+(b.pz-mz)*playerFocus);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?56:58;"""
    s = one(s, old, new, 'player-readable loop framing')
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_omega_camera_v18(Path('_site'))
