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
        "let delta=p.s-c.trackS;if(delta>LENGTH/2)delta-=LENGTH;if(delta<-LENGTH/2)delta+=LENGTH;\n // The bad Omega branch switch is local to the low throat. At 40 m/s a 60 Hz\n // step is only ~0.67 m, so 2.2 m is generous while both road samples are low.\n // If the rigid body has already climbed >6 m away from its hinted road sample,\n // that hint is stale: allow a one-shot catch-up to the true 3D projection.\n const previousPoint=trackPoint(c.trackS),rampageOmega=COURSE_SPEC.id==='rampage-3d'||COURSE_SPEC.id==='classic',bodyY=carY(c)??previousPoint.y,detachedHint=rampageOmega&&Math.abs(bodyY-previousPoint.y)>6.0,lowerOmega=rampageOmega&&!detachedHint&&(previousPoint.kind==='loop'||p.kind==='loop')&&Math.max(previousPoint.y,p.y)<6.0,continuityLimit=detachedHint?48:lowerOmega?2.2:5.5;\n if(Math.abs(delta)>continuityLimit||Math.abs(p.lane)>TRACK.halfWidth+1.5){c.projectionRejects=(c.projectionRejects||0)+1;return;}\n c.trackS=p.s;",
        "advance commit order",
    )
    racing.write_text(s)

    course = target / 'racing3d.js'
    s = course.read_text()
    s = one(
        s,
        "export function projectRacePoint(x,y,z,hintS=null,use3D=true){\n const p={x,y:Number.isFinite(y)?y:0,z};let best=null,bestCost=Infinity;",
        "export function projectRacePoint(x,y,z,hintS=null,use3D=true){\n const p={x,y:Number.isFinite(y)?y:0,z};let best=null,bestCost=Infinity,hintSeg=hintS==null?null:segmentAtS(hintS),hintKind=hintSeg?kindBetween(hintSeg.a,hintSeg.b,hintSeg.u):null,hintY=hintSeg?hintSeg.a.y+(hintSeg.b.y-hintSeg.a.y)*hintSeg.u:Infinity,detachedHint=hintSeg&&use3D&&Math.abs(p.y-hintY)>6.0;",
        "hint segment kind height and detachment",
    )
    s = one(
        s,
        "const hint=hintS==null?0:Math.pow(Math.abs(sDelta(s,hintS))/14,2)*.06,cost=dist2+hint;",
        # Tight continuity is needed only while the car and hinted road are both
        # in the low ambiguous throat. If the chassis has climbed >6 m away from
        # hintY, use the old very soft hint so true 3D distance can reacquire the
        # vertical arc instead of remaining locked to the lower road forever.
        "const hintGap=hintS==null?0:Math.abs(sDelta(s,hintS)),rampageProjection=projectionCourse.id==='rampage-3d'||projectionCourse.id==='classic',candidateKind=kindBetween(a,b,u),lowerOmegaProjection=rampageProjection&&!detachedHint&&(hintKind==='loop'||candidateKind==='loop')&&Math.max(hintY,center.y)<6.0,hint=hintS==null?0:(rampageProjection?(detachedHint?Math.pow(hintGap/14,2)*.06:lowerOmegaProjection?(hintGap>2.2?1e6:Math.pow(hintGap/1.0,2)*6.0):(hintGap>5.25?1e4:Math.pow(hintGap/2.4,2)*1.55)):(hintGap>3.2?1e4:Math.pow(hintGap/1.6,2)*3.2)),cost=dist2+hint;",
        "lower-throat continuity and stale-hint recovery",
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
