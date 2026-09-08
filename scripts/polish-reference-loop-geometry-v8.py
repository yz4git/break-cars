"""Make stunt loops read like the supplied toy-track reference in real WebGL.

The previous open-loop topology was mathematically continuous, but its 17 m
road ribbon wrapped a ~14 m diameter planar circle.  In a chase camera that
looked like a black barrel: the descending half returned directly over the
approach road, so the player visibly drove underneath the loop before entering.

This pass is intentionally visual-geometry-first:
- increase loop diameter relative to road width;
- taper the road width only while it is on the loop;
- yaw the loop plane away from the incoming road like a toy-track transition;
- keep the incoming leg tangent to the authored road;
- move only the descending half laterally toward the outgoing side;
- return through a separate exit leg with zero offset at both gates.

Rendering and collision use the same tapered lane width.  No hidden road is
added under the loop and no position/orientation teleport is introduced.
"""
from pathlib import Path
import re


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'reference loop v8 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_reference_loop_geometry_v8(target: Path) -> None:
    racing3d = target / 'racing3d.js'
    s = racing3d.read_text()

    # A loop narrower than its diameter reads as a loop rather than a drum.
    # The three courses retain progressively larger stunt scale.
    s = one(
        s,
        "loopRadius:doubleOrbit?8.6:skyForge?7.5:7.2",
        "loopRadius:doubleOrbit?13.5:skyForge?12.5:11.5",
        'loop radii',
    )
    s = one(
        s,
        "const LOOP_HALF_T=.10,LOOP_OPEN_ANGLE=.42;",
        "const LOOP_HALF_T=.10,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=.60;",
        'loop lane scale constant',
    )

    # The photo does not aim the ring straight down the approach lane.  The
    # lower entry road curves into an oblique ring, placing the far/descending
    # side beside the incoming road instead of directly above it.
    s = one(
        s,
        "const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),ringForward=startH;\n  let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=startFrame.right;const ringUp=norm(cross(ringForward,ringRight));",
        "const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),exitSide=dot(gateVec,startFrame.right),yawSign=exitSide>=0?-1:1,ringYaw=doubleOrbit?.84:skyForge?.80:.82,ringForward=norm(rotateAround(startH,worldUp,yawSign*ringYaw));\n  let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=startFrame.right;const ringUp=norm(cross(ringForward,ringRight));",
        'oblique ring orientation',
    )

    # Give the road enough visible transition length to turn and rise before
    # touching the circular section.  This is the lower leg visible in the
    # reference photograph.
    s = one(
        s,
        "const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=clamp(gateChord*.22,1.8,3.6),legRise=.85;",
        "const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=clamp(gateChord*.42,4.8,7.6),legRise=1.15;",
        'entry leg length',
    )

    # Keep the ascending side close to a clean vertical ring.  Starting near
    # the crown, smoothly displace the descending half toward the outgoing side
    # and return that displacement to zero before the exit gate.  This is a
    # twist, not a helix: entry and exit remain exact authored-road points.
    s = one(
        s,
        "const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),pos=add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),tangent=norm(add(mul(ringForward,c),mul(ringUp,sn))),up=norm(add(mul(ringUp,c),mul(ringForward,-sn)));return{pos,tangent,up};};",
        "const sepSign=exitSide>=0?1:-1,ringSep=doubleOrbit?6.4:skyForge?5.9:5.5;\n  const circlePos=th=>{const c=Math.cos(th),sn=Math.sin(th),q=clamp((th-open)/(TAU-open*2),0,1),engage=smooth01((q-.40)/.20),release=1-smooth01((q-.84)/.16),lat=sepSign*ringSep*engage*release;return add(add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),mul(startFrame.right,lat));};\n  const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),h=.0025,a=circlePos(Math.max(open,th-h)),b=circlePos(Math.min(TAU-open,th+h)),pos=circlePos(th),tangent=norm(sub(b,a)),seed=norm(add(mul(ringUp,c),mul(ringForward,-sn))),up=orthoUp(seed,tangent,ringUp);return{pos,tangent,up};};",
        'descending-side separation',
    )

    # Taper lateral coordinates in the same centerline API consumed by both the
    # renderer and racing logic.  Straight road stays full width.
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
