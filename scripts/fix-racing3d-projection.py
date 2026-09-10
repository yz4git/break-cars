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
        "let delta=p.s-c.trackS;if(delta>LENGTH/2)delta-=LENGTH;if(delta<-LENGTH/2)delta+=LENGTH;\n // At 60 Hz a 40 m/s car advances only ~0.67 m per frame. The observed bad\n // Omega projection was a 5.23 m jump between two LOWER throat samples\n // (roughly y=0..2 m). Do not clamp the whole loop: once the car is climbing,\n // trackS may legitimately need to catch up by more than 2.2 m. Tighten only\n // when both old and candidate road samples live in the ambiguous lower throat.\n const previousPoint=trackPoint(c.trackS),rampageOmega=COURSE_SPEC.id==='rampage-3d'||COURSE_SPEC.id==='classic',lowerOmega=rampageOmega&&(previousPoint.kind==='loop'||p.kind==='loop')&&Math.max(previousPoint.y,p.y)<6.0,continuityLimit=lowerOmega?2.2:5.5;\n if(Math.abs(delta)>continuityLimit||Math.abs(p.lane)>TRACK.halfWidth+1.5){c.projectionRejects=(c.projectionRejects||0)+1;return;}\n c.trackS=p.s;",
        "advance commit order",
    )
    racing.write_text(s)

    course = target / 'racing3d.js'
    s = course.read_text()
    s = one(
        s,
        "export function projectRacePoint(x,y,z,hintS=null,use3D=true){\n const p={x,y:Number.isFinite(y)?y:0,z};let best=null,bestCost=Infinity;",
        "export function projectRacePoint(x,y,z,hintS=null,use3D=true){\n const p={x,y:Number.isFinite(y)?y:0,z};let best=null,bestCost=Infinity,hintSeg=hintS==null?null:segmentAtS(hintS),hintKind=hintSeg?kindBetween(hintSeg.a,hintSeg.b,hintSeg.u):null,hintY=hintSeg?hintSeg.a.y+(hintSeg.b.y-hintSeg.a.y)*hintSeg.u:Infinity;",
        "hint segment kind and height",
    )
    s = one(
        s,
        "const hint=hintS==null?0:Math.pow(Math.abs(sDelta(s,hintS))/14,2)*.06,cost=dist2+hint;",
        # RAMPAGE's two lower Omega legs can be close in world space. The bad
        # branch jump happened entirely below y=2 m. A 6 m cutoff includes the
        # complete ambiguous throat while leaving the vertical climb/crown free
        # to catch up normally. Other RAMPAGE track uses the proven 5.25 m rule.
        "const hintGap=hintS==null?0:Math.abs(sDelta(s,hintS)),rampageProjection=projectionCourse.id==='rampage-3d'||projectionCourse.id==='classic',candidateKind=kindBetween(a,b,u),lowerOmegaProjection=rampageProjection&&(hintKind==='loop'||candidateKind==='loop')&&Math.max(hintY,center.y)<6.0,hint=hintS==null?0:(rampageProjection?(lowerOmegaProjection?(hintGap>2.2?1e6:Math.pow(hintGap/1.0,2)*6.0):(hintGap>5.25?1e4:Math.pow(hintGap/2.4,2)*1.55)):(hintGap>3.2?1e4:Math.pow(hintGap/1.6,2)*3.2)),cost=dist2+hint;",
        "lower-throat continuity weight",
    )
    s = one(
        s,
        "kind:kindBetween(a,b,u),segment:seg.i",
        "kind:candidateKind,segment:seg.i",
        "reuse candidate kind",
    )
    s = "import {activeCourse as projectionCourse} from './courses.js';\n" + s
    course.write_text(s)


if __name__ == '__main__':
    apply_racing3d_projection_fix(Path('_site'))
