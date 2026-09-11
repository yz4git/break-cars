"""DOUBLE ORBIT v29: replace the tangled lower lobe with one broad U return.

The supplied toy-track reference reads as one clear path: approach -> two side-by-
side vertical loops -> a large low outer U -> back to the start.  v27 already
solved the two loop throats and keeps their entry/exit roads one road width apart.
This late geometry-only pass leaves every point through loop two unchanged, adds
a short straight runout after the second ring, then routes the rest of DOUBLE
ORBIT around a stadium-like U: a rounded right turn, a long lower return parallel
to the loop travel axis, and a rounded left turn into the lap seam.

The authored vertical profile and banking are retained on that return, so the
existing bridge, banked feature and final jump remain functional and the DOUBLE
ORBIT physics/test contract does not lose features. No other course, loop
geometry, controls, progress, or physics helpers are changed.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT U return v29 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_u_return_v29(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()

    old = """const doubleOrbitA=baseAt(loopCenters[0]),doubleOrbitB=baseAt(loopCenters[1]),doubleOrbitSpan=Math.max(.001,loopCenters[1]-loopCenters[0]),doubleOrbitBlendIn0=loopCenters[0]-.30,doubleOrbitBlendIn1=loopCenters[0]-.18,doubleOrbitMergeT0=loopCenters[1]+.30,doubleOrbitMergeT1=1.70;
const doubleOrbitSmooth=q=>{q=clamp(q,0,1);return q*q*q*(10+q*(-15+6*q));};
const DOUBLE_ORBIT_RING_R=LOOP_R*1.38,DOUBLE_ORBIT_SPLIT=RACE3D_TRACK.halfWidth*2+.8;
const doubleOrbitLineAt=t=>{const q=(t-loopCenters[0])/doubleOrbitSpan;return{x:doubleOrbitA.x+(doubleOrbitB.x-doubleOrbitA.x)*q,y:doubleOrbitA.y+(doubleOrbitB.y-doubleOrbitA.y)*q,z:doubleOrbitA.z+(doubleOrbitB.z-doubleOrbitA.z)*q};};
const doubleOrbitDX=doubleOrbitB.x-doubleOrbitA.x,doubleOrbitDY=doubleOrbitB.y-doubleOrbitA.y,doubleOrbitDZ=doubleOrbitB.z-doubleOrbitA.z,doubleOrbitDL=Math.hypot(doubleOrbitDX,doubleOrbitDY,doubleOrbitDZ)||1,doubleOrbitAxis={x:doubleOrbitDX/doubleOrbitDL,y:doubleOrbitDY/doubleOrbitDL,z:doubleOrbitDZ/doubleOrbitDL},doubleOrbitRight0={x:-doubleOrbitAxis.z,y:0,z:doubleOrbitAxis.x},doubleOrbitRightL=Math.hypot(doubleOrbitRight0.x,doubleOrbitRight0.z)||1,doubleOrbitRight={x:doubleOrbitRight0.x/doubleOrbitRightL,y:0,z:doubleOrbitRight0.z/doubleOrbitRightL};
const doubleOrbitLaneAt=t=>{const a0=loopCenters[0]-LOOP_HALF_T,a1=loopCenters[0]+LOOP_HALF_T,b0=loopCenters[1]-LOOP_HALF_T,b1=loopCenters[1]+LOOP_HALF_T;if(t<=a0)return 0;if(t<a1)return DOUBLE_ORBIT_SPLIT*doubleOrbitSmooth((t-a0)/(a1-a0));if(t<=b0)return DOUBLE_ORBIT_SPLIT;if(t<b1)return DOUBLE_ORBIT_SPLIT*(1-doubleOrbitSmooth((t-b0)/(b1-b0)));return 0;};
const doubleOrbitMergeStart=doubleOrbit?doubleOrbitLineAt(doubleOrbitMergeT0):{x:0,y:0,z:0},doubleOrbitMergeEnd=doubleOrbit?rampageCourseRoadAt(doubleOrbitMergeT1):{x:0,y:0,z:0},doubleOrbitMergeBefore=doubleOrbit?rampageCourseRoadAt(doubleOrbitMergeT1-.002):{x:0,y:0,z:0},doubleOrbitMergeAfter=doubleOrbit?rampageCourseRoadAt(doubleOrbitMergeT1+.002):{x:1,y:0,z:0},doubleOrbitEndDX=doubleOrbitMergeAfter.x-doubleOrbitMergeBefore.x,doubleOrbitEndDY=doubleOrbitMergeAfter.y-doubleOrbitMergeBefore.y,doubleOrbitEndDZ=doubleOrbitMergeAfter.z-doubleOrbitMergeBefore.z,doubleOrbitEndDL=Math.hypot(doubleOrbitEndDX,doubleOrbitEndDY,doubleOrbitEndDZ)||1,doubleOrbitEndForward={x:doubleOrbitEndDX/doubleOrbitEndDL,y:doubleOrbitEndDY/doubleOrbitEndDL,z:doubleOrbitEndDZ/doubleOrbitEndDL},doubleOrbitMergeChord=Math.hypot(doubleOrbitMergeEnd.x-doubleOrbitMergeStart.x,doubleOrbitMergeEnd.y-doubleOrbitMergeStart.y,doubleOrbitMergeEnd.z-doubleOrbitMergeStart.z)||1,doubleOrbitMergeScale=doubleOrbitMergeChord*.92;
const doubleOrbitMergeAt=t=>{const q=clamp((t-doubleOrbitMergeT0)/(doubleOrbitMergeT1-doubleOrbitMergeT0),0,1),q2=q*q,q3=q2*q,h00=2*q3-3*q2+1,h10=q3-2*q2+q,h01=-2*q3+3*q2,h11=q3-q2;return{x:doubleOrbitMergeStart.x*h00+doubleOrbitAxis.x*doubleOrbitMergeScale*h10+doubleOrbitMergeEnd.x*h01+doubleOrbitEndForward.x*doubleOrbitMergeScale*h11,y:doubleOrbitMergeStart.y*h00+doubleOrbitAxis.y*doubleOrbitMergeScale*h10+doubleOrbitMergeEnd.y*h01+doubleOrbitEndForward.y*doubleOrbitMergeScale*h11,z:doubleOrbitMergeStart.z*h00+doubleOrbitAxis.z*doubleOrbitMergeScale*h10+doubleOrbitMergeEnd.z*h01+doubleOrbitEndForward.z*doubleOrbitMergeScale*h11};};
const doubleOrbitCourseRoadAt=t=>{
 const base=rampageCourseRoadAt(t);if(!doubleOrbit)return base;
 if(t<=doubleOrbitBlendIn0||t>=doubleOrbitMergeT1)return base;
 if(t<doubleOrbitBlendIn1){const w=doubleOrbitSmooth((t-doubleOrbitBlendIn0)/(doubleOrbitBlendIn1-doubleOrbitBlendIn0)),line=doubleOrbitLineAt(t),lane=doubleOrbitLaneAt(t);return{...base,x:base.x+(line.x+doubleOrbitRight.x*lane-base.x)*w,y:base.y+(line.y+doubleOrbitRight.y*lane-base.y)*w,z:base.z+(line.z+doubleOrbitRight.z*lane-base.z)*w,bank:(base.bank||0)*(1-w)};}
 if(t<=doubleOrbitMergeT0){const line=doubleOrbitLineAt(t),lane=doubleOrbitLaneAt(t);return{...base,x:line.x+doubleOrbitRight.x*lane,y:line.y+doubleOrbitRight.y*lane,z:line.z+doubleOrbitRight.z*lane,bank:0};}
 const p=doubleOrbitMergeAt(t),q=clamp((t-doubleOrbitMergeT0)/(doubleOrbitMergeT1-doubleOrbitMergeT0),0,1);return{...base,x:p.x,y:p.y,z:p.z,bank:(base.bank||0)*doubleOrbitSmooth(q)};
};
"""

    new = """const doubleOrbitA=baseAt(loopCenters[0]),doubleOrbitB=baseAt(loopCenters[1]),doubleOrbitSpan=Math.max(.001,loopCenters[1]-loopCenters[0]),doubleOrbitBlendIn0=loopCenters[0]-.30,doubleOrbitBlendIn1=loopCenters[0]-.18;
const doubleOrbitSmooth=q=>{q=clamp(q,0,1);return q*q*q*(10+q*(-15+6*q));};
const DOUBLE_ORBIT_RING_R=LOOP_R*1.38,DOUBLE_ORBIT_SPLIT=RACE3D_TRACK.halfWidth*2+.8;
const doubleOrbitLineAt=t=>{const q=(t-loopCenters[0])/doubleOrbitSpan;return{x:doubleOrbitA.x+(doubleOrbitB.x-doubleOrbitA.x)*q,y:doubleOrbitA.y+(doubleOrbitB.y-doubleOrbitA.y)*q,z:doubleOrbitA.z+(doubleOrbitB.z-doubleOrbitA.z)*q};};
const doubleOrbitDX=doubleOrbitB.x-doubleOrbitA.x,doubleOrbitDY=doubleOrbitB.y-doubleOrbitA.y,doubleOrbitDZ=doubleOrbitB.z-doubleOrbitA.z,doubleOrbitDL=Math.hypot(doubleOrbitDX,doubleOrbitDY,doubleOrbitDZ)||1,doubleOrbitAxis={x:doubleOrbitDX/doubleOrbitDL,y:doubleOrbitDY/doubleOrbitDL,z:doubleOrbitDZ/doubleOrbitDL},doubleOrbitRight0={x:-doubleOrbitAxis.z,y:0,z:doubleOrbitAxis.x},doubleOrbitRightL=Math.hypot(doubleOrbitRight0.x,doubleOrbitRight0.z)||1,doubleOrbitRight={x:doubleOrbitRight0.x/doubleOrbitRightL,y:0,z:doubleOrbitRight0.z/doubleOrbitRightL};
const doubleOrbitLaneAt=t=>{const a0=loopCenters[0]-LOOP_HALF_T,a1=loopCenters[0]+LOOP_HALF_T,b0=loopCenters[1]-LOOP_HALF_T,b1=loopCenters[1]+LOOP_HALF_T;if(t<=a0)return 0;if(t<a1)return DOUBLE_ORBIT_SPLIT*doubleOrbitSmooth((t-a0)/(a1-a0));if(t<=b0)return DOUBLE_ORBIT_SPLIT;if(t<b1)return DOUBLE_ORBIT_SPLIT*(1-doubleOrbitSmooth((t-b0)/(b1-b0)));return 0;};
const doubleOrbitReturnT0=loopCenters[1]+.30,doubleOrbitReturnT1=2.28,doubleOrbitReturnT2=5.02,DOUBLE_ORBIT_RETURN_DEPTH=RACE3D_TRACK.halfWidth*2.85;
const doubleOrbitReturnTop=doubleOrbit?doubleOrbitLineAt(doubleOrbitReturnT0):{x:0,y:0,z:0},doubleOrbitStart=doubleOrbit?baseAt(0):{x:0,y:0,z:0},doubleOrbitStartBefore=doubleOrbit?baseAt(-.002):{x:-1,y:0,z:0},doubleOrbitStartAfter=doubleOrbit?baseAt(.002):{x:1,y:0,z:0},doubleOrbitStartForward=norm(sub(doubleOrbitStartAfter,doubleOrbitStartBefore)),doubleOrbitReturnBottomRight=add(doubleOrbitReturnTop,mul(doubleOrbitRight,-DOUBLE_ORBIT_RETURN_DEPTH)),doubleOrbitReturnBottomLeft=add(doubleOrbitStart,mul(doubleOrbitRight,-DOUBLE_ORBIT_RETURN_DEPTH));
const doubleOrbitHermite=(p0,t0,p1,t1,s0,s1,q)=>{const q2=q*q,q3=q2*q,h00=2*q3-3*q2+1,h10=q3-2*q2+q,h01=-2*q3+3*q2,h11=q3-q2;return{x:p0.x*h00+t0.x*s0*h10+p1.x*h01+t1.x*s1*h11,y:p0.y*h00+t0.y*s0*h10+p1.y*h01+t1.y*s1*h11,z:p0.z*h00+t0.z*s0*h10+p1.z*h01+t1.z*s1*h11};};
const doubleOrbitReturnAt=t=>{let p;if(t<doubleOrbitReturnT1){const q=clamp((t-doubleOrbitReturnT0)/(doubleOrbitReturnT1-doubleOrbitReturnT0),0,1),s=DOUBLE_ORBIT_RETURN_DEPTH*.86;p=doubleOrbitHermite(doubleOrbitReturnTop,doubleOrbitAxis,doubleOrbitReturnBottomRight,mul(doubleOrbitAxis,-1),s,s,q);}else if(t<doubleOrbitReturnT2){const q=clamp((t-doubleOrbitReturnT1)/(doubleOrbitReturnT2-doubleOrbitReturnT1),0,1),d=len(sub(doubleOrbitReturnBottomLeft,doubleOrbitReturnBottomRight));p=doubleOrbitHermite(doubleOrbitReturnBottomRight,mul(doubleOrbitAxis,-1),doubleOrbitReturnBottomLeft,mul(doubleOrbitAxis,-1),d*.92,d*.92,q);}else{const q=clamp((t-doubleOrbitReturnT2)/(TAU-doubleOrbitReturnT2),0,1),s=DOUBLE_ORBIT_RETURN_DEPTH*.86;p=doubleOrbitHermite(doubleOrbitReturnBottomLeft,mul(doubleOrbitAxis,-1),doubleOrbitStart,doubleOrbitStartForward,s,s,q);}return p;};
const doubleOrbitCourseRoadAt=t=>{
 const base=rampageCourseRoadAt(t);if(!doubleOrbit)return base;
 if(t<=doubleOrbitBlendIn0)return base;
 if(t<doubleOrbitBlendIn1){const w=doubleOrbitSmooth((t-doubleOrbitBlendIn0)/(doubleOrbitBlendIn1-doubleOrbitBlendIn0)),line=doubleOrbitLineAt(t),lane=doubleOrbitLaneAt(t);return{...base,x:base.x+(line.x+doubleOrbitRight.x*lane-base.x)*w,y:base.y+(line.y+doubleOrbitRight.y*lane-base.y)*w,z:base.z+(line.z+doubleOrbitRight.z*lane-base.z)*w,bank:(base.bank||0)*(1-w)};}
 if(t<=doubleOrbitReturnT0){const line=doubleOrbitLineAt(t),lane=doubleOrbitLaneAt(t);return{...base,x:line.x+doubleOrbitRight.x*lane,y:line.y+doubleOrbitRight.y*lane,z:line.z+doubleOrbitRight.z*lane,bank:0};}
 const p=doubleOrbitReturnAt(t);return{...base,x:p.x,y:p.y+base.y,z:p.z,bank:(base.bank||0)};
};
"""

    s = one(s, old, new, 'stadium return corridor')
    path.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_u_return_v29(Path('_site'))
