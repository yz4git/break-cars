"""Prevent loop/crossover projection branch jumps without changing other courses."""
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
        "let delta=p.s-c.trackS;if(delta>LENGTH/2)delta-=LENGTH;if(delta<-LENGTH/2)delta+=LENGTH;\n // A 60 Hz car at 40 m/s advances only ~0.67 m per frame. On RAMPAGE's\n // open Omega, the lower C2 legs are spatially close enough that nearest-point\n // projection can occasionally jump 4-5 m to the wrong branch. Limit loop\n // progress commits to 2.2 m (~3.3x the fastest expected physical step).\n const previousKind=trackPoint(c.trackS).kind,rampageOmega=COURSE_SPEC.id==='rampage-3d'||COURSE_SPEC.id==='classic',continuityLimit=rampageOmega&&(previousKind==='loop'||p.kind==='loop')?2.2:5.5;\n if(Math.abs(delta)>continuityLimit||Math.abs(p.lane)>TRACK.halfWidth+1.5){c.projectionRejects=(c.projectionRejects||0)+1;return;}\n c.trackS=p.s;",
        "advance commit order",
    )
    racing.write_text(s)

    course = target / 'racing3d.js'
    s = course.read_text()
    s = one(
        s,
        "const hint=hintS==null?0:Math.pow(Math.abs(sDelta(s,hintS))/14,2)*.06,cost=dist2+hint;",
        # RAMPAGE's open Omega has two lower C2 legs that are close in world
        # space but far apart in ordered path distance. At 60 Hz even 40 m/s is
        # only 0.67 m/frame, so a 2.2 m continuity window still leaves >3x
        # physical headroom while excluding the observed 4.63 m wrong-branch
        # jump. Keep the proven non-RAMPAGE rule for SKY FORGE / DOUBLE ORBIT.
        "const hintGap=hintS==null?0:Math.abs(sDelta(s,hintS)),rampageProjection=projectionCourse.id==='rampage-3d'||projectionCourse.id==='classic',hint=hintS==null?0:(rampageProjection?(hintGap>2.2?1e6:Math.pow(hintGap/1.0,2)*6.0):(hintGap>3.2?1e4:Math.pow(hintGap/1.6,2)*3.2)),cost=dist2+hint;",
        "course-scoped continuity weight",
    )
    s = "import {activeCourse as projectionCourse} from './courses.js';\n" + s
    course.write_text(s)


if __name__ == '__main__':
    apply_racing3d_projection_fix(Path('_site'))
