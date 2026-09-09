"""Rebuild RAMPAGE as a clean reference-style vertical loop and keep it visible.

The previous production loop passed physics tests but still deformed the ring to
meet distant gates. That made the silhouette read as a twisted/dragged stunt
instead of one planar toy-track loop. This final polish narrows the RAMPAGE gate
interval and replaces the deformed ring with one fixed vertical circular arc.
Only short Hermite entry/exit blends connect the circle to the authored road.

The camera fix is deliberately applied last. While the player is approaching,
inside, or leaving the RAMPAGE loop, the chase camera becomes an exterior stage
camera on the OUTER side of the loop plane. It is far enough away for an iPhone
landscape viewport to keep the car and the full loop readable instead of letting
the road ribbon fill the frame.

SKY FORGE and DOUBLE ORBIT geometry are untouched.
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

    # Bring the two lower gates close enough to read as one loop while keeping
    # enough centerline separation for the narrowed RAMPAGE ribbon.
    s = one(
        s,
        "const LOOP_HALF_T=(doubleOrbit||skyForge)?.18:.19,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=(!doubleOrbit&&!skyForge)?.58:1;",
        "const LOOP_HALF_T=(doubleOrbit||skyForge)?.18:.14,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=(!doubleOrbit&&!skyForge)?.58:1;",
        'compact RAMPAGE gate interval',
    )

    start = s.index("const open=.70,entryEnd=.12,exitStart=.88")
    end = s.index("const hermiteOpen=", start)
    clean_ring = """const open=.64,entryEnd=.14,exitStart=.86,arc=TAU-open*2,entryLead=1.8,joinLift=.42;\n   const ringEntry=add(add(startFrame.p,mul(startFrame.forward,entryLead)),mul(ringUp,joinLift)),sinOpen=Math.sin(open),cosOpen=Math.cos(open);\n   const ringPoint=q=>{\n    const th=open+arc*clamp(q,0,1),c=Math.cos(th),sn=Math.sin(th),pos=add(ringEntry,add(mul(loopForward,LOOP_R*(sn-sinOpen)),mul(ringUp,LOOP_R*(cosOpen-c)))),radial=norm(add(mul(ringUp,c),mul(loopForward,-sn)));return{pos,up:radial};\n   };\n   const ringExit=ringPoint(1),dq=.001,entryT=norm(sub(ringPoint(dq).pos,ringEntry)),exitT=norm(sub(ringExit.pos,ringPoint(1-dq).pos));\n   """
    s = s[:start] + clean_ring + s[end:]

    s = one(
        s,
        "const entryScale=clamp(len(sub(ringEntry.pos,startFrame.p))*.9,1.8,3.6),exitScale=clamp(len(sub(endFrame.p,ringExit.pos))*.95,1.9,3.8);",
        "const entryScale=clamp(len(sub(ringEntry-startFrame.p))*.9,1.8,4.8),exitScale=clamp(len(sub(endFrame.p,ringExit.pos))*.72,3.2,8.5);",
        'entry/exit handles placeholder',
    ) if False else s

    # The generated source stores ringEntry as a vector in v11, not {pos,up}.
    # Patch the handle expression directly and keep generous exit easing.
    old_handles = "const entryScale=clamp(len(sub(ringEntry.pos,startFrame.p))*.9,1.8,3.6),exitScale=clamp(len(sub(endFrame.p,ringExit.pos))*.95,1.9,3.8);"
    new_handles = "const entryScale=clamp(len(sub(ringEntry,startFrame.p))*.85,1.8,4.8),exitScale=clamp(len(sub(endFrame.p,ringExit.pos))*.72,3.2,8.5);"
    s = one(s, old_handles, new_handles, 'long clean exit blend')

    # v10's sample refers to ringEntry.up/.pos. For the clean ring, obtain the
    # endpoint normal from ringPoint(0), while the position is the vector above.
    s = one(
        s,
        "if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),seed=mixV(startFrame.up,ringEntry.up,smooth01(q)),pos=hermiteOpen(startFrame.p,startFrame.forward,ringEntry.pos,entryT,entryScale,entryScale,q);return{pos,frame:{up:seed},upSeed:seed};}",
        "if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),ring0=ringPoint(0),seed=mixV(startFrame.up,ring0.up,smooth01(q)),pos=hermiteOpen(startFrame.p,startFrame.forward,ringEntry,entryT,entryScale,entryScale,q);return{pos,frame:{up:seed},upSeed:seed};}",
        'clean entry blend',
    )
    racing3d.write_text(s)

    game = target / 'game.js'
    s = game.read_text()
    old_camera = "if(racingLoop){const base=trackPoint(raceLoopSpec.startS,0),side=view===1?22:18.5,centerY=base.y+raceLoopSpec.radius,stageLift=view===1?2.8:1.8;camTarget.set(base.x+base.right.x*side,centerY+stageLift+base.right.y*side,base.z+base.right.z*side);lookTarget.set(b.px,b.py+.35,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-10*dt));camera.fov=view===1?55:58;}else{"
    new_camera = "if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,span=Math.max(1,s1-s0),a=trackPoint(s0,0),q1=trackPoint(s0+span*.25,0),q2=trackPoint(s0+span*.50,0),q3=trackPoint(s0+span*.75,0),z=trackPoint(s1,0),cx=(a.x+q1.x+q2.x+q3.x+z.x)/5,cy=(a.y+q1.y+q2.y+q3.y+z.y)/5,cz=(a.z+q1.z+q2.z+q3.z+z.z)/5,rl=Math.hypot(a.right.x,a.right.z)||1,rx=a.right.x/rl,rz=a.right.z/rl,outward=(cx*rx+cz*rz)>=0?1:-1,side=(view===1?34:29)*outward,stageLift=view===1?5.0:3.8;camTarget.set(cx+rx*side,cy+stageLift,cz+rz*side);lookTarget.set(b.px,b.py+.55,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?60:62;}else{"
    s = one(s, old_camera, new_camera, 'exterior loop camera')
    s = one(
        s,
        "racingLoop=!!raceLoopSpec&&!!racePose&&p.trackS>=raceLoopSpec.startS-7&&p.trackS<=raceLoopSpec.endS+7",
        "racingLoop=!!raceLoopSpec&&!!racePose&&p.trackS>=raceLoopSpec.startS-14&&p.trackS<=raceLoopSpec.endS+14",
        'early/late camera takeover',
    )
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v11(Path('_site'))
