"""DOUBLE ORBIT v27: split each loop's entry/exit roads by one road width.

A vertical loop that comes back down onto the same centreline visually lays its
returning ribbon over the incoming road.  Keep the approach and exit tangents
parallel, but move the exit centreline sideways by one full road width.  Loop 1
moves onto the offset line and loop 2 moves back, so the course does not drift
sideways overall.

The lateral transfer is distributed with a zero-slope quintic through the full
loop instead of being hidden in a sharp S-bend at the throat.  The rings are
also larger and farther apart, and each loop gets a wider gate span so its two
lower legs have enough longitudinal room to stay visibly separate.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT split loop v27 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_split_loop_v27(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()

    # Give the two enlarged loops more room along the straightened stage.
    s = one(
        s,
        "const RAMPAGE_LOOP_T=.44,loopCenters=doubleOrbit?[.40,.75]:skyForge?[LOOP_T]:[RAMPAGE_LOOP_T];",
        "const RAMPAGE_LOOP_T=.44,loopCenters=doubleOrbit?[.32,.88]:skyForge?[LOOP_T]:[RAMPAGE_LOOP_T];",
        'loop spacing',
    )

    # v26 made the local base road straight, so a wider gate no longer rotates
    # the approach/exit headings.  Doubling this span gives both lower legs a
    # visibly longer run before they meet the circular section.
    s = one(
        s,
        "const LOOP_HALF_T=doubleOrbit?.05:skyForge?.18:.19,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=doubleOrbit?.50:skyForge?1:.44;",
        "const LOOP_HALF_T=doubleOrbit?.10:skyForge?.18:.19,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=doubleOrbit?.50:skyForge?1:.44;",
        'gate span',
    )

    old_corridor = """const doubleOrbitA=baseAt(loopCenters[0]),doubleOrbitB=baseAt(loopCenters[1]),doubleOrbitSpan=Math.max(.001,loopCenters[1]-loopCenters[0]),doubleOrbitBlendIn0=loopCenters[0]-.20,doubleOrbitBlendIn1=loopCenters[0]-.11,doubleOrbitBlendOut0=loopCenters[1]+.11,doubleOrbitBlendOut1=loopCenters[1]+.20;
const doubleOrbitSmooth=q=>{q=clamp(q,0,1);return q*q*q*(10+q*(-15+6*q));};
const doubleOrbitLineAt=t=>{const q=(t-loopCenters[0])/doubleOrbitSpan;return{x:doubleOrbitA.x+(doubleOrbitB.x-doubleOrbitA.x)*q,y:doubleOrbitA.y+(doubleOrbitB.y-doubleOrbitA.y)*q,z:doubleOrbitA.z+(doubleOrbitB.z-doubleOrbitA.z)*q};};
const doubleOrbitCourseRoadAt=t=>{
 const base=rampageCourseRoadAt(t);if(!doubleOrbit)return base;
 if(t<=doubleOrbitBlendIn0||t>=doubleOrbitBlendOut1)return base;
 let w=1;if(t<doubleOrbitBlendIn1)w=doubleOrbitSmooth((t-doubleOrbitBlendIn0)/(doubleOrbitBlendIn1-doubleOrbitBlendIn0));else if(t>doubleOrbitBlendOut0)w=1-doubleOrbitSmooth((t-doubleOrbitBlendOut0)/(doubleOrbitBlendOut1-doubleOrbitBlendOut0));
 const line=doubleOrbitLineAt(t);return{...base,x:base.x+(line.x-base.x)*w,y:base.y+(line.y-base.y)*w,z:base.z+(line.z-base.z)*w,bank:(base.bank||0)*(1-w)};
};
"""
    new_corridor = """const doubleOrbitA=baseAt(loopCenters[0]),doubleOrbitB=baseAt(loopCenters[1]),doubleOrbitSpan=Math.max(.001,loopCenters[1]-loopCenters[0]),doubleOrbitBlendIn0=loopCenters[0]-.20,doubleOrbitBlendIn1=loopCenters[0]-.11,doubleOrbitBlendOut0=loopCenters[1]+.11,doubleOrbitBlendOut1=loopCenters[1]+.20;
const doubleOrbitSmooth=q=>{q=clamp(q,0,1);return q*q*q*(10+q*(-15+6*q));};
const DOUBLE_ORBIT_RING_R=LOOP_R*1.38,DOUBLE_ORBIT_SPLIT=RACE3D_TRACK.halfWidth*2+.8;
const doubleOrbitLineAt=t=>{const q=(t-loopCenters[0])/doubleOrbitSpan;return{x:doubleOrbitA.x+(doubleOrbitB.x-doubleOrbitA.x)*q,y:doubleOrbitA.y+(doubleOrbitB.y-doubleOrbitA.y)*q,z:doubleOrbitA.z+(doubleOrbitB.z-doubleOrbitA.z)*q};};
const doubleOrbitAxis=horizontal(sub(doubleOrbitB,doubleOrbitA))||{x:1,y:0,z:0},doubleOrbitRight=norm(cross({x:0,y:1,z:0},doubleOrbitAxis));
const doubleOrbitLaneAt=t=>{const a0=loopCenters[0]-LOOP_HALF_T,a1=loopCenters[0]+LOOP_HALF_T,b0=loopCenters[1]-LOOP_HALF_T,b1=loopCenters[1]+LOOP_HALF_T;if(t<=a0)return 0;if(t<a1)return DOUBLE_ORBIT_SPLIT*doubleOrbitSmooth((t-a0)/(a1-a0));if(t<=b0)return DOUBLE_ORBIT_SPLIT;if(t<b1)return DOUBLE_ORBIT_SPLIT*(1-doubleOrbitSmooth((t-b0)/(b1-b0)));return 0;};
const doubleOrbitCourseRoadAt=t=>{
 const base=rampageCourseRoadAt(t);if(!doubleOrbit)return base;
 if(t<=doubleOrbitBlendIn0||t>=doubleOrbitBlendOut1)return base;
 let w=1;if(t<doubleOrbitBlendIn1)w=doubleOrbitSmooth((t-doubleOrbitBlendIn0)/(doubleOrbitBlendIn1-doubleOrbitBlendIn0));else if(t>doubleOrbitBlendOut0)w=1-doubleOrbitSmooth((t-doubleOrbitBlendOut0)/(doubleOrbitBlendOut1-doubleOrbitBlendOut0));
 const line=doubleOrbitLineAt(t),lane=doubleOrbitLaneAt(t),cx=base.x+(line.x-base.x)*w,cy=base.y+(line.y-base.y)*w,cz=base.z+(line.z-base.z)*w;return{...base,x:cx+doubleOrbitRight.x*lane,y:cy+doubleOrbitRight.y*lane,z:cz+doubleOrbitRight.z*lane,bank:(base.bank||0)*(1-w)};
};
"""
    s = one(s, old_corridor, new_corridor, 'split corridor')

    # The circular part carries the same lateral transfer as the road helper.
    # Quintic shift has zero derivative at both endpoints, so the entry and exit
    # tangents stay parallel to their ordinary roads while the returning lower
    # branch lands one full road width away from the incoming branch.
    old_circle = "const open=.58,ringBottom=doubleOrbitCourseRoadAt(startCenter),circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),pos=add(add(ringBottom,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),tangent=norm(add(mul(ringForward,c),mul(ringUp,sn))),up=norm(add(mul(ringUp,c),mul(ringForward,-sn)));return{pos,tangent,up};};"
    new_circle = "const open=.58,ringIndex=loopCenters.indexOf(startCenter),lane0=ringIndex===0?0:DOUBLE_ORBIT_SPLIT,lane1=ringIndex===0?DOUBLE_ORBIT_SPLIT:0,laneMid=(lane0+lane1)*.5,ringBottom=add(doubleOrbitLineAt(startCenter),mul(doubleOrbitRight,laneMid)),circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),q=clamp((th-open)/(TAU-open*2),0,1),sw=doubleOrbitSmooth(q),lane=lane0+(lane1-lane0)*sw,dLane=(lane1-lane0)*30*q*q*(1-q)*(1-q)/(TAU-open*2),pos=add(add(add(ringBottom,mul(ringForward,DOUBLE_ORBIT_RING_R*sn)),mul(ringUp,DOUBLE_ORBIT_RING_R*(1-c))),mul(doubleOrbitRight,lane-laneMid)),tangent=norm(add(add(mul(ringForward,DOUBLE_ORBIT_RING_R*c),mul(ringUp,DOUBLE_ORBIT_RING_R*sn)),mul(doubleOrbitRight,dLane))),radial=norm(add(mul(ringUp,c),mul(ringForward,-sn))),up=orthoUp(radial,tangent,ringUp);return{pos,tangent,up};};"
    s = one(s, old_circle, new_circle, 'wide laterally split ring')

    s = one(
        s,
        "const entryDist=len(sub(ringEntry.pos,startFrame.p)),exitDist=len(sub(endFrame.p,ringExit.pos)),entryScale=clamp(entryDist*.72,4.5,10.5),exitScale=clamp(exitDist*.72,4.5,10.5),LEG_STEPS=Math.max(18,Math.round(LOOP_STEPS*.23)),RING_STEPS=Math.max(68,LOOP_STEPS);",
        "const entryDist=len(sub(ringEntry.pos,startFrame.p)),exitDist=len(sub(endFrame.p,ringExit.pos)),entryScale=clamp(entryDist*.68,5.5,15.0),exitScale=clamp(exitDist*.68,5.5,15.0),LEG_STEPS=Math.max(22,Math.round(LOOP_STEPS*.28)),RING_STEPS=Math.max(84,Math.round(LOOP_STEPS*1.18));",
        'longer lower legs',
    )

    # Keep all camera and force calculations honest about the larger radius.
    s = one(
        s,
        "return{radius:LOOP_R,startS:a[0].s,endS:a.at(-1).s,maxY:Math.max(...a.map(p=>p.y))};",
        "return{radius:doubleOrbit?DOUBLE_ORBIT_RING_R:LOOP_R,startS:a[0].s,endS:a.at(-1).s,maxY:Math.max(...a.map(p=>p.y))};",
        'feature radius',
    )

    path.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_split_loop_v27(Path('_site'))
