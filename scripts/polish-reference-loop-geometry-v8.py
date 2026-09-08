"""Make stunt loops read like a real open/twisted loop in actual WebGL.

The original topology was continuous, but a broad descending branch sat only a
couple of metres above the approach ribbon. From the chase camera that still
looked like the car drove underneath/backside of a road before entering.

RAMPAGE and SKY therefore use a true two-leg open loop:
- cut a longer section out of the authored road so entry and exit gates are
  physically separated;
- narrow the loop ribbon relative to the normal road;
- curve the entry leg laterally into an oblique ring;
- keep the descending half displaced to the outgoing side all the way to the
  ring exit instead of folding it back over the approach;
- let a separate, long-tangent exit leg converge onto the outgoing authored road.

DOUBLE ORBIT keeps its proven 8.6 m radius and short gate interval because its
two-loop physics pack is tightly tuned around that geometry. It still gets the
narrow ribbon, milder yaw and mild temporary lateral separation.

Rendering and collision consume the same geometry/width. No hidden base road is
left under the loop and no position/orientation teleport is introduced.
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

    # RAMPAGE/SKY need a visibly larger ring. DOUBLE ORBIT retains the radius
    # its two-loop force/recovery tuning was authored against.
    s = one(
        s,
        "loopRadius:doubleOrbit?8.6:skyForge?7.5:7.2",
        "loopRadius:doubleOrbit?8.6:skyForge?12.5:11.5",
        'loop radii',
    )

    # Real-WebGL review showed the old +/- .10 rad gates were too close for a
    # 17 m normal road. Widen the removed authored-road interval on the two
    # single-loop courses so their entry and exit legs can be genuinely separate.
    s = one(
        s,
        "const LOOP_HALF_T=.10,LOOP_OPEN_ANGLE=.42;",
        "const LOOP_HALF_T=doubleOrbit?.10:.20,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=.60;",
        'open gate spacing and loop lane scale',
    )

    # Aim the ring obliquely so its far/descending side is not directly above
    # the approach. DOUBLE ORBIT uses a milder yaw to preserve its tuned flow.
    s = one(
        s,
        "const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),ringForward=startH;\n  let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=startFrame.right;const ringUp=norm(cross(ringForward,ringRight));",
        "const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),exitSide=dot(gateVec,startFrame.right),yawSign=exitSide>=0?-1:1,ringYaw=doubleOrbit?.52:skyForge?.80:.82,ringForward=norm(rotateAround(startH,worldUp,yawSign*ringYaw));\n  let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=startFrame.right;const ringUp=norm(cross(ringForward,ringRight));",
        'oblique ring orientation',
    )

    # Give the road enough visible transition length to turn/rise before the
    # circular section. The two single-loop courses also move the ring itself
    # sideways by one road-width-ish amount: the approach road now visibly bends
    # into the ring instead of running underneath its lower descending branch.
    s = one(
        s,
        "const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=clamp(gateChord*.22,1.8,3.6),legRise=.85;\n  const desiredEntry=add(add(startFrame.p,mul(startH,legLead)),mul(ringUp,legRise));",
        "const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=doubleOrbit?clamp(gateChord*.30,3.2,4.8):clamp(gateChord*.42,4.8,7.6),legRise=doubleOrbit?.95:1.15,ringSideShift=doubleOrbit?0:skyForge?7.0:8.0;\n  const desiredEntry=add(add(add(startFrame.p,mul(startH,legLead)),mul(ringUp,legRise)),mul(startFrame.right,(exitSide>=0?1:-1)*ringSideShift));",
        'separate entry leg and ring',
    )

    # Keep the ascending side close to a clean vertical ring. Starting before
    # the crown, smoothly displace the descending half toward the outgoing side.
    # Crucially, RAMPAGE/SKY DO NOT release that displacement before ringExit;
    # their separate exit leg is responsible for converging back to the road.
    # This removes the low black canopy seen over the approach in real WebGL.
    s = one(
        s,
        "const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),pos=add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),tangent=norm(add(mul(ringForward,c),mul(ringUp,sn))),up=norm(add(mul(ringUp,c),mul(ringForward,-sn)));return{pos,tangent,up};};",
        "const sepSign=exitSide>=0?1:-1,ringSep=doubleOrbit?2.2:skyForge?5.9:5.5;\n  const circlePos=th=>{const c=Math.cos(th),sn=Math.sin(th),q=clamp((th-open)/(TAU-open*2),0,1),engage=smooth01((q-.32)/.22),release=doubleOrbit?1-smooth01((q-.84)/.16):1,lat=sepSign*ringSep*engage*release;return add(add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),mul(startFrame.right,lat));};\n  const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),h=.0025,a=circlePos(Math.max(open,th-h)),b=circlePos(Math.min(TAU-open,th+h)),pos=circlePos(th),tangent=norm(sub(b,a)),seed=norm(add(mul(ringUp,c),mul(ringForward,-sn))),up=orthoUp(seed,tangent,ringUp);return{pos,tangent,up};};",
        'descending-side separation',
    )

    # Relocating the ring makes ringExit->road much longer. The old 5 m Hermite
    # tangent handle only aligned during the final few centimetres, so the exit
    # still looked like a crossing. Stretch the single-loop outgoing handle so
    # the final metres already face the authored road; leave DOUBLE ORBIT alone.
    s = one(
        s,
        "entryScale=clamp(entryDist*.46,2.1,4.2),exitScale=clamp(exitDist*.42,2.2,5.0);",
        "entryScale=clamp(entryDist*.46,2.1,4.2),exitScale=doubleOrbit?clamp(exitDist*.42,2.2,5.0):clamp(exitDist*1.20,6.0,30.0);",
        'outgoing tangent handle',
    )

    # Taper lateral coordinates in the same centerline API consumed by both the
    # renderer and racing logic. Straight road stays full width.
    old = "const pos=add(center,mul(f.right,lane)),kind=kindBetween(a,b,u),bank=(a.bank||0)+((b.bank||0)-(a.bank||0))*u;"
    new = "const kind=kindBetween(a,b,u),laneScale=kind==='loop'?LOOP_LANE_SCALE:1,pos=add(center,mul(f.right,lane*laneScale)),bank=(a.bank||0)+((b.bank||0)-(a.bank||0))*u;"
    s = one(s, old, new, 'render lane taper')

    # Collision width matches the visibly tapered ribbon.
    old = "const allowance=RACE3D_TRACK.halfWidth+(forChassis?2.1:1.35);if(Math.abs(p.lane)>allowance||p.kind==='jump-gap')return null;\n const lane=clamp(p.lane,-RACE3D_TRACK.halfWidth,RACE3D_TRACK.halfWidth),point={x:p.x+p.right.x*lane,y:p.y+p.right.y*lane,z:p.z+p.right.z*lane};"
    new = "const surfaceHalf=p.kind==='loop'?RACE3D_TRACK.halfWidth*LOOP_LANE_SCALE:RACE3D_TRACK.halfWidth,allowance=surfaceHalf+(forChassis?2.1:1.35);if(Math.abs(p.lane)>allowance||p.kind==='jump-gap')return null;\n const lane=clamp(p.lane,-surfaceHalf,surfaceHalf),point={x:p.x+p.right.x*lane,y:p.y+p.right.y*lane,z:p.z+p.right.z*lane};"
    s = one(s, old, new, 'collision lane taper')

    s = one(
        s,
        "halfWidth:RACE3D_TRACK.halfWidth,loop:loopGroups[0],loops:loopGroups",
        "halfWidth:RACE3D_TRACK.halfWidth,loopHalfWidth:RACE3D_TRACK.halfWidth*LOOP_LANE_SCALE,loop:loopGroups[0],loops:loopGroups",
        'feature loop width',
    )
    racing3d.write_text(s)

    # Loop ribs must use the same tapered width or they recreate the barrel
    # silhouette even when the asphalt ribbon is narrow.
    view = target / 'track-view.js'
    s = view.read_text()
    s = one(
        s,
        "TRACK.halfWidth*2+.35",
        "(spec.loopHalfWidth||TRACK.halfWidth)*2+.35",
        'loop rib width',
    )
    view.write_text(s)


if __name__ == '__main__':
    apply_reference_loop_geometry_v8(Path('_site'))
