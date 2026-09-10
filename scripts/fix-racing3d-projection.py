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
        "let delta=p.s-c.trackS;if(delta>LENGTH/2)delta-=LENGTH;if(delta<-LENGTH/2)delta+=LENGTH;\n // RAMPAGE's open Omega has two close lower branches. Do not reject a valid\n // projection merely because the nearest point advances farther than one frame;\n // instead clamp ordered progress while keeping the true projected road point.\n // Low throat: max 2.2 m/step, enough for >3x a 40 m/s physical frame.\n // Detached stale hint: max 4.5 m/step, so the correct high arc is reacquired\n // over several frames without ever producing the old 47 m branch jump.\n const previousPoint=trackPoint(c.trackS),rampageOmega=w.raceCourse==='rampage-3d',bodyY=carY(c)??previousPoint.y,detachedHint=rampageOmega&&Math.abs(bodyY-previousPoint.y)>6.0,lowerOmega=rampageOmega&&!detachedHint&&(previousPoint.kind==='loop'||p.kind==='loop')&&Math.max(previousPoint.y,p.y)<6.0;\n if(Math.abs(p.lane)>TRACK.halfWidth+1.5){c.projectionRejects=(c.projectionRejects||0)+1;return;}\n let committedDelta=delta;if(lowerOmega&&Math.abs(committedDelta)>2.2){committedDelta=Math.sign(committedDelta)*2.2;c.projectionClamps=(c.projectionClamps||0)+1;}else if(detachedHint&&Math.abs(committedDelta)>4.5){committedDelta=Math.sign(committedDelta)*4.5;c.projectionClamps=(c.projectionClamps||0)+1;}else if(Math.abs(committedDelta)>5.5){c.projectionRejects=(c.projectionRejects||0)+1;return;}\n c.trackS=Math.abs(committedDelta-delta)<1e-6?p.s:wrap(c.trackS+committedDelta);delta=committedDelta;",
        "smooth advance commit",
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
        # Let the projector report the real nearest lower-throat candidate up to
        # the previously proven 5.25 m neighborhood. Ordered progress limiting
        # now belongs in advanceRace, where a 5.23 m candidate is smoothly
        # consumed as 2.2 m steps instead of being mistaken for a teleport.
        "const hintGap=hintS==null?0:Math.abs(sDelta(s,hintS)),rampageProjection=projectionCourse.id==='rampage-3d'||projectionCourse.id==='classic',candidateKind=kindBetween(a,b,u),lowerOmegaProjection=rampageProjection&&!detachedHint&&(hintKind==='loop'||candidateKind==='loop')&&Math.max(hintY,center.y)<6.0,hint=hintS==null?0:(rampageProjection?(detachedHint?Math.pow(hintGap/14,2)*.06:lowerOmegaProjection?(hintGap>5.25?1e4:Math.pow(hintGap/2.4,2)*1.55):(hintGap>5.25?1e4:Math.pow(hintGap/2.4,2)*1.55)):(hintGap>3.2?1e4:Math.pow(hintGap/1.6,2)*3.2)),cost=dist2+hint;",
        "projection candidate continuity",
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
