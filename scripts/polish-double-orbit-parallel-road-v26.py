"""DOUBLE ORBIT v26: keep ordinary road parallel through the twin-loop stage.

The toy reference does not turn the road away immediately after a loop.  Both
lower loop joins sit on one straight travel axis, with the ordinary road before,
between and after the rings parallel.  v24 already made the rings open and
planar; this late geometry-only pass straightens the local base-road corridor
under those rings and blends back to the authored lobe outside the stunt.

No physics, controls, progress, loop radius, opening angle, or other courses are
changed.  The existing force-only DOUBLE ORBIT guide continues to consume the
same generated centreline.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT parallel road v26 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_parallel_road_v26(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()

    # v12 has already installed rampageCourseRoadAt.  For DOUBLE ORBIT that
    # helper is currently just baseAt(), so wrap it with one local straight
    # corridor.  The centres themselves stay exactly where v23 placed them.
    anchor = "const raw=[];\n"
    corridor = """const doubleOrbitA=baseAt(loopCenters[0]),doubleOrbitB=baseAt(loopCenters[1]),doubleOrbitSpan=Math.max(.001,loopCenters[1]-loopCenters[0]),doubleOrbitBlendIn0=loopCenters[0]-.20,doubleOrbitBlendIn1=loopCenters[0]-.11,doubleOrbitBlendOut0=loopCenters[1]+.11,doubleOrbitBlendOut1=loopCenters[1]+.20;
const doubleOrbitSmooth=q=>{q=clamp(q,0,1);return q*q*q*(10+q*(-15+6*q));};
const doubleOrbitLineAt=t=>{const q=(t-loopCenters[0])/doubleOrbitSpan;return{x:doubleOrbitA.x+(doubleOrbitB.x-doubleOrbitA.x)*q,y:doubleOrbitA.y+(doubleOrbitB.y-doubleOrbitA.y)*q,z:doubleOrbitA.z+(doubleOrbitB.z-doubleOrbitA.z)*q};};
const doubleOrbitCourseRoadAt=t=>{
 const base=rampageCourseRoadAt(t);if(!doubleOrbit)return base;
 if(t<=doubleOrbitBlendIn0||t>=doubleOrbitBlendOut1)return base;
 let w=1;if(t<doubleOrbitBlendIn1)w=doubleOrbitSmooth((t-doubleOrbitBlendIn0)/(doubleOrbitBlendIn1-doubleOrbitBlendIn0));else if(t>doubleOrbitBlendOut0)w=1-doubleOrbitSmooth((t-doubleOrbitBlendOut0)/(doubleOrbitBlendOut1-doubleOrbitBlendOut0));
 const line=doubleOrbitLineAt(t);return{...base,x:base.x+(line.x-base.x)*w,y:base.y+(line.y-base.y)*w,z:base.z+(line.z-base.z)*w,bank:(base.bank||0)*(1-w)};
};
const raw=[];
"""
    s = one(s, anchor, corridor, 'straight corridor helper')

    s = one(
        s,
        "const dt=.0015,p=rampageCourseRoadAt(t),a=rampageCourseRoadAt(t-dt),b=rampageCourseRoadAt(t+dt),forward=norm(sub(b,a));",
        "const dt=.0015,p=doubleOrbitCourseRoadAt(t),a=doubleOrbitCourseRoadAt(t-dt),b=doubleOrbitCourseRoadAt(t+dt),forward=norm(sub(b,a));",
        'road frame follows straight corridor',
    )
    s = one(
        s,
        "const p=rampageCourseRoadAt(t);raw.push({...p,explicitUp:null});",
        "const p=doubleOrbitCourseRoadAt(t);raw.push({...p,explicitUp:null});",
        'ordinary road follows straight corridor',
    )
    s = one(
        s,
        "const open=.58,ringBottom=baseAt(startCenter),circleAt=th=>",
        "const open=.58,ringBottom=doubleOrbitCourseRoadAt(startCenter),circleAt=th=>",
        'ring base follows straight corridor',
    )
    path.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_parallel_road_v26(Path('_site'))
