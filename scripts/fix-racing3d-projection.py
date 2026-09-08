"""Prevent loop/crossover projection branch jumps in the deployed RAMPAGE 3D runtime."""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"Racing3D projection {label}: expected 1 match, found {n}")
    return text.replace(old, new, 1)


def apply_racing3d_projection_fix(target: Path) -> None:
    racing = target / 'racing.js'
    s = racing.read_text()
    s = one(
        s,
        "let delta=p.s-c.trackS;if(delta>LENGTH/2)delta-=LENGTH;if(delta<-LENGTH/2)delta+=LENGTH;c.trackS=p.s;\n // Ordered progress remains continuous through the vertical loop and the upper/lower crossover.\n if(Math.abs(delta)>5.5||Math.abs(p.lane)>TRACK.halfWidth+1.5)return;",
        "let delta=p.s-c.trackS;if(delta>LENGTH/2)delta-=LENGTH;if(delta<-LENGTH/2)delta+=LENGTH;\n // Projection may move only as far as the rigid body could plausibly travel in\n // this frame. The old fixed 5.5m allowance let a 20m/s car jump five metres\n // around the loop in 1/60s, instantly swapping to a very different tangent.\n const bodySpeed=c.p3?Math.hypot(c.p3.vx||0,c.p3.vy||0,c.p3.vz||0):Math.hypot(c.vx||0,c.vz||0),maxProjectionStep=clamp(bodySpeed*dt*2.6+.55,1.2,2.6);\n if(Math.abs(delta)>maxProjectionStep||Math.abs(p.lane)>TRACK.halfWidth+1.5){c.projectionRejects=(c.projectionRejects||0)+1;return;}\n c.trackS=p.s;",
        "advance commit order",
    )
    racing.write_text(s)

    course = target / 'racing3d.js'
    s = course.read_text()
    s = one(
        s,
        "const hint=hintS==null?0:Math.pow(Math.abs(sDelta(s,hintS))/14,2)*.06,cost=dist2+hint;",
        "const hintGap=hintS==null?0:Math.abs(sDelta(s,hintS)),hint=hintS==null?0:Math.pow(hintGap/6,2)*2.4,cost=dist2+hint;",
        "continuity weight",
    )
    course.write_text(s)


if __name__ == '__main__':
    apply_racing3d_projection_fix(Path('_site'))
