"""Final RAMPAGE reference-loop shape and visibility pass.

RAMPAGE is one continuous road: ordinary approach -> gentle lower entry leg ->
clean vertical circular revolution -> gentle lower exit leg -> ordinary road.
The visible upper loop is strictly planar. The only 3D twist is hidden in the
open lower throat, where entry and exit are separated along the loop-plane
normal so the wide race ribbons cannot intersect physically. From the dedicated
side camera that depth separation collapses visually into the compact crossover
seen on a real toy-track Omega loop instead of a warped barrel.

The ring is centered between the authored gates rather than dragged from one gate
toward the other. This removes the long diagonal ramp/chord that previously cut
through the loop silhouette. SKY FORGE and DOUBLE ORBIT are untouched.
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

    gate_line = "const LOOP_HALF_T=(doubleOrbit||skyForge)?.18:.19,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=(!doubleOrbit&&!skyForge)?.58:1;"
    if s.count(gate_line) != 1:
        raise RuntimeError(f'RAMPAGE reference loop v11 gate interval: expected 1 match, found {s.count(gate_line)}')

    start = s.index("const open=.70,entryEnd=.12,exitStart=.88")
    end = s.index("const hermiteOpen=", start)
    omega_ring = """const open=.30,entryEnd=.18,exitStart=.82,arc=TAU-open*2,joinLift=.55,throatDepth=9.0,depthWindow=.30;\n   const gateMid=mul(add(startFrame.p,endFrame.p),.5),gapAlong=LOOP_R*Math.sin(open),ringEntryBase=add(add(gateMid,mul(loopForward,gapAlong)),mul(ringUp,joinLift));\n   const depthAt=q=>{const a=1-smooth01(q/depthWindow),b=1-smooth01((1-q)/depthWindow);return outwardSign*throatDepth*(a-b);};\n   const ringPoint=q=>{\n    const th=open+arc*clamp(q,0,1),c=Math.cos(th),sn=Math.sin(th),circle=add(mul(loopForward,LOOP_R*(sn-Math.sin(open))),mul(ringUp,LOOP_R*(Math.cos(open)-c))),pos=add(add(ringEntryBase,circle),mul(flatRight,depthAt(q))),radial=norm(add(mul(ringUp,c),mul(loopForward,-sn)));return{pos,up:radial};\n   };\n   const ringEntry=ringPoint(0),ringExit=ringPoint(1),dq=.001,entryT=norm(sub(ringPoint(dq).pos,ringEntry.pos)),exitT=norm(sub(ringExit.pos,ringPoint(1-dq).pos)),entryLaunchT=norm(add(startFrame.forward,mul(ringUp,.12)));\n   """
    s = s[:start] + omega_ring + s[end:]

    s = one(
        s,
        "const entryScale=clamp(len(sub(ringEntry.pos,startFrame.p))*.9,1.8,3.6),exitScale=clamp(len(sub(endFrame.p,ringExit.pos))*.95,1.9,3.8);",
        "const entryScale=clamp(len(sub(ringEntry.pos,startFrame.p))*.70,6.0,13.0),exitScale=clamp(len(sub(endFrame.p,ringExit.pos))*.70,6.0,13.0);",
        'gentle lower connection legs',
    )
    s = one(
        s,
        "if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),seed=mixV(startFrame.up,ringEntry.up,smooth01(q)),pos=hermiteOpen(startFrame.p,startFrame.forward,ringEntry.pos,entryT,entryScale,entryScale,q);return{pos,frame:{up:seed},upSeed:seed};}",
        "if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),seed=mixV(startFrame.up,ringEntry.up,smooth01(q)),pos=hermiteOpen(startFrame.p,entryLaunchT,ringEntry.pos,entryT,entryScale,entryScale,q);return{pos,frame:{up:seed},upSeed:seed};}",
        'gentle rising entry',
    )
    racing3d.write_text(s)

    game = target / 'game.js'
    s = game.read_text()
    branch_start = s.find("if(racingLoop){const base=trackPoint(raceLoopSpec.startS,0)")
    if branch_start < 0:
        raise RuntimeError('RAMPAGE reference loop v11 camera: racingLoop branch start not found')
    branch_end = s.find("}else if(racingJump){", branch_start)
    if branch_end < 0:
        raise RuntimeError('RAMPAGE reference loop v11 camera: racingJump branch boundary not found')
    new_branch = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,span=Math.max(1,s1-s0),mid=trackPoint(s0+span*.50,0),center={x:mid.x+mid.up.x*raceLoopSpec.radius,y:mid.y+mid.up.y*raceLoopSpec.radius,z:mid.z+mid.up.z*raceLoopSpec.radius},rl=Math.hypot(mid.right.x,mid.right.z)||1,rx=mid.right.x/rl,rz=mid.right.z/rl,outward=(center.x*rx+center.z*rz)>=0?1:-1,side=(view===1?44:40)*outward,stageLift=view===1?3.2:2.4;camTarget.set(center.x+rx*side,center.y+stageLift,center.z+rz*side);lookTarget.set(b.px,b.py+.45,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?58:60;"""
    s = s[:branch_start] + new_branch + s[branch_end:]
    s = one(
        s,
        "racingLoop=!!raceLoopSpec&&!!racePose&&p.trackS>=raceLoopSpec.startS-7&&p.trackS<=raceLoopSpec.endS+7",
        "racingLoop=!!raceLoopSpec&&!!racePose&&p.trackS>=raceLoopSpec.startS-18&&p.trackS<=raceLoopSpec.endS+16",
        'early/late exterior camera takeover',
    )
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v11(Path('_site'))
