"""Make stunt loops read like a real open/twisted loop in actual WebGL.

The incoming road must become the loop itself. In particular, no elevated part
of the same stunt may lie back across the approach and read as a black road
underside that the car drives underneath before entering.

RAMPAGE and SKY therefore use a true spatially-open loop:
- cut a longer section out of the authored road so entry and exit gates are
  physically separated;
- narrow the loop ribbon relative to the normal road;
- keep the lower entry leg mostly in the incoming road direction;
- advance the ring longitudinally as it rotates, producing a corkscrew/open
  revolution instead of a circle that closes back above the entry gate;
- keep the descending half displaced toward the outgoing side;
- let a separate long-tangent exit leg converge onto the outgoing authored road.

DOUBLE ORBIT keeps its proven short-gate closed-planar tuning because its two
successive loops are tightly tuned around that geometry. Rendering and collision
always consume the same centerline and width. No hidden base road is left under
the loop and no position/orientation teleport is introduced.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'reference loop v8 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_reference_loop_geometry_v8(target: Path) -> None:
    racing3d = target / 'racing3d.js'
    s = racing3d.read_text()

    s = one(s, "loopRadius:doubleOrbit?8.6:skyForge?7.5:7.2", "loopRadius:doubleOrbit?8.6:skyForge?12.5:11.5", 'loop radii')
    s = one(s, "const LOOP_HALF_T=.10,LOOP_OPEN_ANGLE=.42;", "const LOOP_HALF_T=doubleOrbit?.10:.20,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=.60;", 'open gate spacing and loop lane scale')

    # Keep the initial ring heading close to the road. Spatial openness is
    # created by the longitudinal corkscrew advance below rather than by forcing
    # the entrance to yaw sideways before it can climb.
    s = one(
        s,
        "const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),ringForward=startH;\n  let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=startFrame.right;const ringUp=norm(cross(ringForward,ringRight));",
        "const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),exitSide=dot(gateVec,startFrame.right),yawSign=exitSide>=0?-1:1,ringYaw=doubleOrbit?.52:skyForge?.32:.34,ringForward=norm(rotateAround(startH,worldUp,yawSign*ringYaw));\n  let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=startFrame.right;const ringUp=norm(cross(ringForward,ringRight));",
        'open ring orientation',
    )

    s = one(
        s,
        "const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=clamp(gateChord*.22,1.8,3.6),legRise=.85;\n  const desiredEntry=add(add(startFrame.p,mul(startH,legLead)),mul(ringUp,legRise));",
        "const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=doubleOrbit?clamp(gateChord*.30,3.2,4.8):clamp(gateChord*.42,4.8,7.6),legRise=doubleOrbit?.95:1.15,ringSideShift=doubleOrbit?0:skyForge?3.2:3.6;\n  const desiredEntry=add(add(add(startFrame.p,mul(startH,legLead)),mul(ringUp,legRise)),mul(startFrame.right,(exitSide>=0?1:-1)*ringSideShift));",
        'continuous entry leg and ring',
    )

    # A planar vertical circle inevitably comes back directly above its own
    # entrance at the crown, which is exactly the black underside/canopy seen in
    # the real WebGL captures. For the two single-loop courses, advance the ring
    # monotonically along its travel axis while it rotates. At q=0 the advance
    # and its derivative are zero, so the incoming leg remains tangent-continuous;
    # at q=1 the advance is roughly the authored gate chord, putting ringExit
    # near the outgoing gate instead of behind the entrance. This is a genuine
    # open corkscrew loop rather than a closed ring superimposed over a road.
    s = one(
        s,
        "const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),pos=add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),tangent=norm(add(mul(ringForward,c),mul(ringUp,sn))),up=norm(add(mul(ringUp,c),mul(ringForward,-sn)));return{pos,tangent,up};};",
        "const sepSign=exitSide>=0?1:-1,ringSep=doubleOrbit?2.2:skyForge?7.5:7.2,ringAdvance=doubleOrbit?0:clamp(gateChord*1.18,14.0,22.0);\n  const circlePos=th=>{const c=Math.cos(th),sn=Math.sin(th),q=clamp((th-open)/(TAU-open*2),0,1),engage=smooth01((q-.32)/.22),release=doubleOrbit?1-smooth01((q-.84)/.16):1,lat=sepSign*ringSep*engage*release,advance=ringAdvance*smooth01(q);return add(add(add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),mul(startFrame.right,lat)),mul(ringForward,advance));};\n  const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),h=.0025,a=circlePos(Math.max(open,th-h)),b=circlePos(Math.min(TAU-open,th+h)),pos=circlePos(th),tangent=norm(sub(b,a)),seed=norm(add(mul(ringUp,c),mul(ringForward,-sn))),up=orthoUp(seed,tangent,ringUp);return{pos,tangent,up};};",
        'longitudinal open-loop clearance',
    )

    s = one(
        s,
        "entryScale=clamp(entryDist*.46,2.1,4.2),exitScale=clamp(exitDist*.42,2.2,5.0);",
        "entryScale=doubleOrbit?clamp(entryDist*.46,2.1,4.2):clamp(entryDist*.92,7.0,14.0),exitScale=doubleOrbit?clamp(exitDist*.42,2.2,5.0):clamp(exitDist*1.20,6.0,30.0);",
        'long entry and outgoing tangent handles',
    )

    s = one(
        s,
        "const pos=add(center,mul(f.right,lane)),kind=kindBetween(a,b,u),bank=(a.bank||0)+((b.bank||0)-(a.bank||0))*u;",
        "const kind=kindBetween(a,b,u),laneScale=kind==='loop'?LOOP_LANE_SCALE:1,pos=add(center,mul(f.right,lane*laneScale)),bank=(a.bank||0)+((b.bank||0)-(a.bank||0))*u;",
        'render lane taper',
    )
    s = one(
        s,
        "const allowance=RACE3D_TRACK.halfWidth+(forChassis?2.1:1.35);if(Math.abs(p.lane)>allowance||p.kind==='jump-gap')return null;\n const lane=clamp(p.lane,-RACE3D_TRACK.halfWidth,RACE3D_TRACK.halfWidth),point={x:p.x+p.right.x*lane,y:p.y+p.right.y*lane,z:p.z+p.right.z*lane};",
        "const surfaceHalf=p.kind==='loop'?RACE3D_TRACK.halfWidth*LOOP_LANE_SCALE:RACE3D_TRACK.halfWidth,allowance=surfaceHalf+(forChassis?2.1:1.35);if(Math.abs(p.lane)>allowance||p.kind==='jump-gap')return null;\n const lane=clamp(p.lane,-surfaceHalf,surfaceHalf),point={x:p.x+p.right.x*lane,y:p.y+p.right.y*lane,z:p.z+p.right.z*lane};",
        'collision lane taper',
    )
    s = one(s, "halfWidth:RACE3D_TRACK.halfWidth,loop:loopGroups[0],loops:loopGroups", "halfWidth:RACE3D_TRACK.halfWidth,loopHalfWidth:RACE3D_TRACK.halfWidth*LOOP_LANE_SCALE,loop:loopGroups[0],loops:loopGroups", 'feature loop width')
    racing3d.write_text(s)

    view = target / 'track-view.js'
    s = view.read_text()
    s = one(s, "TRACK.halfWidth*2+.35", "(spec.loopHalfWidth||TRACK.halfWidth)*2+.35", 'loop rib width')
    view.write_text(s)


if __name__ == '__main__':
    apply_reference_loop_geometry_v8(Path('_site'))
