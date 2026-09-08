"""Make stunt loops read like a real open/twisted loop in actual WebGL.

The incoming road must become the loop itself. In particular, no elevated part
of the same stunt may lie back across the approach and read as a black road
underside that the car drives underneath before entering.

RAMPAGE and SKY therefore use a true spatially-open loop:
- cut a longer section out of the authored road so entry and exit gates are
  physically separated;
- narrow the loop ribbon relative to the normal road;
- move the stunt into an OUTBOARD loop bay, away from the figure-eight body;
- keep the lower entry leg mostly in the incoming road direction;
- push the upper arc forward so the loop does not close back over its entrance;
- place the ring exit behind the outgoing gate, then merge forward into the road;
- keep the descending half displaced toward the outgoing side;
- let a separate long-tangent exit leg converge onto the outgoing authored road.

DOUBLE ORBIT keeps its proven short-gate closed-planar tuning because its two
successive loops are tightly tuned around that geometry. Rendering and collision
always consume the same centerline and width. No hidden base road is left under
the loop and no position/orientation teleport is introduced.

This file is also one of the live-WebGL audit trigger paths, so any accepted
reference-loop geometry is captured against the exact Pages build that contains
it rather than being inferred from centerline-only regression tests.
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
    s = one(s, "const LOOP_HALF_T=.10,LOOP_OPEN_ANGLE=.42;", "const LOOP_HALF_T=doubleOrbit?.10:.24,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=.60;", 'open gate spacing and loop lane scale')

    # Choose the outboard side in the HORIZONTAL plane. Using the banked road
    # right vector here also moved the loop vertically (by several metres on a
    # heavily banked entry), which both flattened the first part of the approach
    # and left half of the ring visually mixed into the figure-eight road body.
    s = one(
        s,
        "const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),ringForward=startH;\n  let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=startFrame.right;const ringUp=norm(cross(ringForward,ringRight));",
        "const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),flatRight=norm(cross(worldUp,startH)),outwardSign=(startFrame.p.x*flatRight.x+startFrame.p.z*flatRight.z)>=0?1:-1,yawSign=outwardSign,ringYaw=doubleOrbit?.52:skyForge?.36:.38,ringForward=norm(rotateAround(startH,worldUp,yawSign*ringYaw));\n  let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=flatRight;const ringUp=norm(cross(ringForward,ringRight));",
        'outboard ring orientation',
    )

    s = one(
        s,
        "const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=clamp(gateChord*.22,1.8,3.6),legRise=.85;\n  const desiredEntry=add(add(startFrame.p,mul(startH,legLead)),mul(ringUp,legRise));",
        "const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=doubleOrbit?clamp(gateChord*.30,3.2,4.8):clamp(gateChord*.48,6.0,9.5),legRise=doubleOrbit?.95:1.45,ringSideShift=doubleOrbit?0:skyForge?12.5:13.5;\n  const desiredEntry=add(add(add(startFrame.p,mul(startH,legLead)),mul(ringUp,legRise)),mul(flatRight,outwardSign*ringSideShift));",
        'continuous outboard entry leg and ring',
    )

    # Keep the whole ring in that same horizontal outboard bay. The previous
    # banked-right offset could bring the high arc back over the course in 3D
    # even though its centerline looked laterally separated in XZ calculations.
    s = one(
        s,
        "const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),pos=add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),tangent=norm(add(mul(ringForward,c),mul(ringUp,sn))),up=norm(add(mul(ringUp,c),mul(ringForward,-sn)));return{pos,tangent,up};};",
        "const sepSign=outwardSign,ringSep=doubleOrbit?2.2:skyForge?14.0:14.5,planarExit=add(add(add(ringBase,mul(ringForward,-gapAlong)),mul(ringUp,joinRise)),mul(flatRight,sepSign*ringSep)),endpointAdvance=doubleOrbit?0:clamp(dot(sub(endFrame.p,planarExit),ringForward),0,22),crownPush=doubleOrbit?0:skyForge?15.0:14.5,exitLead=doubleOrbit?0:clamp(gateChord*.42,7.0,10.5),exitTarget=doubleOrbit?endFrame.p:add(sub(endFrame.p,mul(endFrame.forward,exitLead)),mul(endFrame.up,1.2));\n  const baseCirclePos=th=>{const c=Math.cos(th),sn=Math.sin(th),q=clamp((th-open)/(TAU-open*2),0,1),engage=smooth01((q-.24)/.24),release=doubleOrbit?1-smooth01((q-.84)/.16):1,lat=sepSign*ringSep*engage*release,crown=Math.sin(Math.PI*q),advance=endpointAdvance*smooth01(q)+crownPush*crown*crown;return add(add(add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lat)),mul(ringForward,advance));};\n  const rawExit=baseCirclePos(TAU-open),exitCorrection=doubleOrbit?{x:0,y:0,z:0}:sub(exitTarget,rawExit);\n  const circlePos=th=>{const q=clamp((th-open)/(TAU-open*2),0,1),exitBlend=doubleOrbit?0:smooth01((q-.62)/.38);return add(baseCirclePos(th),mul(exitCorrection,exitBlend));};\n  const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),h=.0025,a=circlePos(Math.max(open,th-h)),b=circlePos(Math.min(TAU-open,th+h)),pos=circlePos(th),tangent=norm(sub(b,a)),seed=norm(add(mul(ringUp,c),mul(ringForward,-sn))),up=orthoUp(seed,tangent,ringUp);return{pos,tangent,up};};",
        'outboard open-loop clearance',
    )

    s = one(
        s,
        "entryScale=clamp(entryDist*.46,2.1,4.2),exitScale=clamp(exitDist*.42,2.2,5.0);",
        "entryScale=doubleOrbit?clamp(entryDist*.46,2.1,4.2):clamp(entryDist*1.02,10.0,18.0),exitScale=doubleOrbit?clamp(exitDist*.42,2.2,5.0):clamp(exitDist*.78,5.0,10.0);",
        'long outboard entry and outgoing tangent handles',
    )

    # Start climbing immediately while staying close enough to the authored road
    # tangent to preserve the literal road->loop gate continuity checks.
    s = one(
        s,
        "pushLeg(startFrame.p,startFrame.forward,startFrame.up,ringEntry.pos,ringEntry.tangent,ringEntry.up,entryScale,LEG_STEPS,false);",
        "const entryForward=doubleOrbit?startFrame.forward:norm(add(startFrame.forward,mul(startFrame.up,.22)));\n  pushLeg(startFrame.p,entryForward,startFrame.up,ringEntry.pos,ringEntry.tangent,ringEntry.up,entryScale,LEG_STEPS,false);",
        'rising outboard entry tangent',
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
