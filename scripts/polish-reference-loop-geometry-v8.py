"""Make RAMPAGE use a genuinely open, outboard loop without destabilizing other races.

RAMPAGE's ordinary road is removed for a broad interval and becomes one
continuous entry leg, loop, exit leg and road again. The whole RAMPAGE ring is
kept outside the figure-eight envelope; only the long entrance/exit legs return
to the authored road. This avoids the old failure mode where the late half of
the ring was pulled back across another course branch just to hit a nearby exit
gate.

Large RAMPAGE lateral offsets are always horizontal (flatRight), never along the
banked road-right vector. SKY FORGE and DOUBLE ORBIT keep their already-proven
compact loop geometry/width so the RAMPAGE clearance fix cannot regress their
raceability.
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

    s = one(s, "loopRadius:doubleOrbit?8.6:skyForge?7.5:7.2", "loopRadius:doubleOrbit?8.6:skyForge?7.5:11.5", 'loop radii')
    # Only RAMPAGE needs the broad cut. SKY and DOUBLE retain their proven gate
    # spacing and full-width ribbon.
    s = one(s, "const LOOP_HALF_T=.10,LOOP_OPEN_ANGLE=.42;", "const LOOP_HALF_T=(doubleOrbit||skyForge)?.10:.36,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=(doubleOrbit||skyForge)?1:.58;", 'RAMPAGE-only open gate spacing and loop lane scale')

    s = one(
        s,
        "const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),ringForward=startH;\n  let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=startFrame.right;const ringUp=norm(cross(ringForward,ringRight));",
        "const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),flatRight=norm(cross(worldUp,startH)),outwardSign=(startFrame.p.x*flatRight.x+startFrame.p.z*flatRight.z)>=0?1:-1,yawSign=outwardSign,ringYaw=doubleOrbit?.52:skyForge?0:.16,ringForward=norm(rotateAround(startH,worldUp,yawSign*ringYaw));\n  let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=flatRight;const ringUp=norm(cross(ringForward,ringRight));",
        'RAMPAGE-only outboard ring orientation',
    )

    s = one(
        s,
        "const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=clamp(gateChord*.22,1.8,3.6),legRise=.85;\n  const desiredEntry=add(add(startFrame.p,mul(startH,legLead)),mul(ringUp,legRise));",
        "const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=doubleOrbit?clamp(gateChord*.30,3.2,4.8):skyForge?clamp(gateChord*.22,1.8,3.6):clamp(gateChord*.34,7.0,11.5),legRise=doubleOrbit?.95:skyForge?.85:1.45,ringSideShift=(doubleOrbit||skyForge)?0:17.0;\n  const desiredEntry=add(add(add(startFrame.p,mul(startH,legLead)),mul(ringUp,legRise)),mul(flatRight,outwardSign*ringSideShift));",
        'RAMPAGE-only outboard entry leg and ring',
    )

    # Do NOT drag the RAMPAGE descending half back toward the authored exit.
    # SKY remains the compact original circle; DOUBLE keeps its tuned separation.
    s = one(
        s,
        "const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),pos=add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),tangent=norm(add(mul(ringForward,c),mul(ringUp,sn))),up=norm(add(mul(ringUp,c),mul(ringForward,-sn)));return{pos,tangent,up};};",
        "const sepSign=outwardSign,ringSep=doubleOrbit?2.2:skyForge?0:7.5,crownPush=(doubleOrbit||skyForge)?0:9.5;\n  const circlePos=th=>{const c=Math.cos(th),sn=Math.sin(th),q=clamp((th-open)/(TAU-open*2),0,1),engage=(doubleOrbit||skyForge)?0:smooth01((q-.12)/.30),lat=sepSign*ringSep*engage,crown=Math.sin(Math.PI*q),advance=crownPush*crown*crown;return add(add(add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lat)),mul(ringForward,advance));};\n  const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),h=.0025,a=circlePos(Math.max(open,th-h)),b=circlePos(Math.min(TAU-open,th+h)),pos=circlePos(th),tangent=norm(sub(b,a)),seed=norm(add(mul(ringUp,c),mul(ringForward,-sn))),up=orthoUp(seed,tangent,ringUp);return{pos,tangent,up};};",
        'RAMPAGE-only unfolded outboard loop ring',
    )

    s = one(
        s,
        "entryScale=clamp(entryDist*.46,2.1,4.2),exitScale=clamp(exitDist*.42,2.2,5.0);",
        "entryScale=(doubleOrbit||skyForge)?clamp(entryDist*.46,2.1,4.2):clamp(entryDist*.88,13.0,24.0),exitScale=(doubleOrbit||skyForge)?clamp(exitDist*.42,2.2,5.0):clamp(exitDist*.88,14.0,26.0);",
        'RAMPAGE-only long clear entry and exit tangent handles',
    )

    s = one(
        s,
        "pushLeg(startFrame.p,startFrame.forward,startFrame.up,ringEntry.pos,ringEntry.tangent,ringEntry.up,entryScale,LEG_STEPS,false);",
        "const entryForward=(doubleOrbit||skyForge)?startFrame.forward:norm(add(startFrame.forward,mul(startFrame.up,.20)));\n  pushLeg(startFrame.p,entryForward,startFrame.up,ringEntry.pos,ringEntry.tangent,ringEntry.up,entryScale,LEG_STEPS,false);",
        'RAMPAGE-only rising outboard entry tangent',
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
