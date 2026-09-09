"""Final RAMPAGE reference-loop shape and visibility pass.

The target is an open, realistic twisted loop rather than a closed hoop: normal
road -> distinct rising entry leg -> clean circular upper revolution -> distinct
descending exit leg -> normal road. The circular part itself is never stretched
or pulled toward the road gates. Instead the whole ring lives outboard of the
figure-eight and the lower entry/exit legs do the 3D twisting needed to rejoin
the authored road. This keeps the reference-like Omega silhouette and prevents
a flat road chord from passing underneath the ring.

The camera takes over before the entry leg and stays outside the loop plane until
after the exit. It uses world-up and enough distance/FOV for an iPhone landscape
viewport to keep both the car and the loop readable while the chassis is vertical
or inverted.

SKY FORGE and DOUBLE ORBIT are untouched.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE reference loop v11 {label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)


def apply_rampage_reference_loop_v11(target: Path) -> None:
    racing3d = target / 'racing3d.js'
    s = racing3d.read_text()

    # Keep v9's proven gate interval. The visible revolution is moved outboard
    # as one rigid circle; only its two lower connection legs twist in 3D.
    gate_line = "const LOOP_HALF_T=(doubleOrbit||skyForge)?.18:.19,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=(!doubleOrbit&&!skyForge)?.58:1;"
    if s.count(gate_line) != 1:
        raise RuntimeError(f'RAMPAGE reference loop v11 gate interval: expected 1 match, found {s.count(gate_line)}')

    start = s.index("const open=.70,entryEnd=.12,exitStart=.88")
    end = s.index("const hermiteOpen=", start)
    clean_ring = """const open=.60,entryEnd=.20,exitStart=.80,arc=TAU-open*2,joinLift=.52,outboardShift=17.0,entryLead=2.0,exitLead=1.8;\n   const outboard=mul(flatRight,outwardSign*outboardShift),desiredExit=add(add(add(endFrame.p,mul(endFrame.forward,-exitLead)),mul(ringUp,joinLift)),outboard),sinOpen=Math.sin(open),cosOpen=Math.cos(open),circleExitDelta=add(mul(loopForward,-2*LOOP_R*sinOpen),mul(ringUp,0));\n   const ringEntry=sub(desiredExit,circleExitDelta);\n   const ringPoint=q=>{\n    const th=open+arc*clamp(q,0,1),c=Math.cos(th),sn=Math.sin(th),pos=add(ringEntry,add(mul(loopForward,LOOP_R*(sn-sinOpen)),mul(ringUp,LOOP_R*(cosOpen-c)))),radial=norm(add(mul(ringUp,c),mul(loopForward,-sn)));return{pos,up:radial};\n   };\n   const ring0=ringPoint(0),ringExit=ringPoint(1),dq=.001,entryT=norm(sub(ringPoint(dq).pos,ring0.pos)),exitT=norm(sub(ringExit.pos,ringPoint(1-dq).pos)),entryLaunchT=norm(add(startFrame.forward,mul(ringUp,.34)));\n   """
    s = s[:start] + clean_ring + s[end:]

    old_handles = "const entryScale=clamp(len(sub(ringEntry.pos,startFrame.p))*.9,1.8,3.6),exitScale=clamp(len(sub(endFrame.p,ringExit.pos))*.95,1.9,3.8);"
    new_handles = "const entryDist=len(sub(ring0.pos,startFrame.p)),exitDist=len(sub(endFrame.p,ringExit.pos)),entryScale=clamp(entryDist*.72,10.0,24.0),exitScale=clamp(exitDist*.68,8.0,20.0);"
    s = one(s, old_handles, new_handles, 'long twisted lower legs')

    s = one(
        s,
        "if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),seed=mixV(startFrame.up,ringEntry.up,smooth01(q)),pos=hermiteOpen(startFrame.p,startFrame.forward,ringEntry.pos,entryT,entryScale,entryScale,q);return{pos,frame:{up:seed},upSeed:seed};}",
        "if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),seed=mixV(startFrame.up,ring0.up,smooth01(q)),pos=hermiteOpen(startFrame.p,entryLaunchT,ring0.pos,entryT,entryScale,entryScale,q);return{pos,frame:{up:seed},upSeed:seed};}",
        'outboard rising entry leg',
    )
    # v10's exit branch already connects ringExit to endFrame with Hermite. With
    # the rigid outboard ring above, this becomes the separate twisted lower exit.
    racing3d.write_text(s)

    game = target / 'game.js'
    s = game.read_text()
    branch_start = s.find("if(racingLoop){const base=trackPoint(raceLoopSpec.startS,0)")
    if branch_start < 0:
        raise RuntimeError('RAMPAGE reference loop v11 camera: racingLoop branch start not found')
    branch_end = s.find("}else if(racingJump){", branch_start)
    if branch_end < 0:
        raise RuntimeError('RAMPAGE reference loop v11 camera: racingJump branch boundary not found')
    new_branch = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,span=Math.max(1,s1-s0),mid=trackPoint(s0+span*.50,0),center={x:mid.x+mid.up.x*raceLoopSpec.radius,y:mid.y+mid.up.y*raceLoopSpec.radius,z:mid.z+mid.up.z*raceLoopSpec.radius},rl=Math.hypot(mid.right.x,mid.right.z)||1,rx=mid.right.x/rl,rz=mid.right.z/rl,outward=(center.x*rx+center.z*rz)>=0?1:-1,side=(view===1?42:38)*outward,stageLift=view===1?4.8:3.6;camTarget.set(center.x+rx*side,center.y+stageLift,center.z+rz*side);lookTarget.set(b.px,b.py+.55,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?60:62;"""
    s = s[:branch_start] + new_branch + s[branch_end:]
    s = one(
        s,
        "racingLoop=!!raceLoopSpec&&!!racePose&&p.trackS>=raceLoopSpec.startS-7&&p.trackS<=raceLoopSpec.endS+7",
        "racingLoop=!!raceLoopSpec&&!!racePose&&p.trackS>=raceLoopSpec.startS-16&&p.trackS<=raceLoopSpec.endS+14",
        'early/late exterior camera takeover',
    )
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v11(Path('_site'))
