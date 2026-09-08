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
        "let delta=p.s-c.trackS;if(delta>LENGTH/2)delta-=LENGTH;if(delta<-LENGTH/2)delta+=LENGTH;\n // The projector is continuity-biased below, so a normal local projection can\n // commit directly. Keep this final guard only for genuinely impossible jumps.\n if(Math.abs(delta)>5.5||Math.abs(p.lane)>TRACK.halfWidth+1.5){c.projectionRejects=(c.projectionRejects||0)+1;return;}\n c.trackS=p.s;",
        "advance commit order",
    )
    racing.write_text(s)

    course = target / 'racing3d.js'
    s = course.read_text()
    s = one(
        s,
        "const hint=hintS==null?0:Math.pow(Math.abs(sDelta(s,hintS))/14,2)*.06,cost=dist2+hint;",
        # The previous 3.2 m hard window could permanently pin trackS when the
        # chassis briefly went airborne at the loop exit: once the body got a
        # little more than one car-length ahead, every genuinely-forward sample
        # was assigned the 1e4 branch-jump penalty.  Keep the final 5.5 m commit
        # guard in racing.js as the real branch-safety limit, but let the nearest
        # same-branch sample catch up anywhere inside that window.
        "const hintGap=hintS==null?0:Math.abs(sDelta(s,hintS)),hint=hintS==null?0:(hintGap>5.25?1e4:Math.pow(hintGap/2.4,2)*1.55),cost=dist2+hint;",
        "continuity weight",
    )
    course.write_text(s)


if __name__ == '__main__':
    apply_racing3d_projection_fix(Path('_site'))
