"""Final RAMPAGE reference-loop shape and visibility pass.

The target is an open, realistic twisted loop rather than a closed hoop: normal
road -> distinct rising entry leg -> clean circular upper revolution -> distinct
descending exit leg -> normal road. The upper revolution keeps a clean circular
side silhouette. Depth separation is introduced smoothly through the loop plane,
then fades back out before the lower exit. The two lower legs also splay apart
only near the throat, leaving a clearly open Omega shape without deforming the
upper circle.

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

    gate_line = "const LOOP_HALF_T=(doubleOrbit||skyForge)?.18:.19,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=(!doubleOrbit&&!skyForge)?.58:1;"
    if s.count(gate_line) != 1:
        raise RuntimeError(f'RAMPAGE reference loop v11 gate interval: expected 1 match, found {s.count(gate_line)}')

    start = s.index("const open=.70,entryEnd=.12,exitStart=.88")
    end = s.index("const hermiteOpen=", start)
    omega_ring = """const open=.62,entryEnd=.14,exitStart=.86,arc=TAU-open*2,entryLead=2.2,exitLead=2.2,joinLift=1.05,outboardShift=16.5,forwardSplay=5.8,lowerWindow=.26,exitDriftStart=.68;\n   const entryAnchor=add(add(startFrame.p,mul(startFrame.forward,entryLead)),mul(ringUp,joinLift)),desiredExit=add(add(endFrame.p,mul(endFrame.forward,-exitLead)),mul(ringUp,joinLift));\n   const sinOpen=Math.sin(open),cosOpen=Math.cos(open),baseCircleExit=mul(loopForward,-2*LOOP_R*sinOpen),baseDrift=sub(sub(desiredExit,entryAnchor),baseCircleExit),depthEnvelope=q=>smooth01(q/.20)*smooth01((1-q)/.22),lowerBump=x=>x>0&&x<lowerWindow?Math.sin(Math.PI*x/lowerWindow)**2:0,exitEase=q=>smooth01((q-exitDriftStart)/(1-exitDriftStart));\n   const ringPoint=q=>{\n    const th=open+arc*clamp(q,0,1),c=Math.cos(th),sn=Math.sin(th),splay=lowerBump(q)-lowerBump(1-q),circle=add(mul(loopForward,LOOP_R*(sn-sinOpen)-forwardSplay*splay),mul(ringUp,LOOP_R*(cosOpen-c))),depth=outwardSign*outboardShift*depthEnvelope(q),pos=add(add(add(entryAnchor,circle),mul(flatRight,depth)),mul(baseDrift,exitEase(q))),radial=norm(add(mul(ringUp,c),mul(loopForward,-sn)));return{pos,up:radial};\n   };\n   const ringEntry=ringPoint(0),ringExit=ringPoint(1),dq=.001,entryT=norm(sub(ringPoint(dq).pos,ringEntry.pos)),exitT=norm(sub(ringExit.pos,ringPoint(1-dq).pos)),entryLaunchT=norm(add(startFrame.forward,mul(ringUp,.34)));\n   """
    s = s[:start] + omega_ring + s[end:]

    s = one(
        s,
        "const entryScale=clamp(len(sub(ringEntry.pos,startFrame.p))*.9,1.8,3.6),exitScale=clamp(len(sub(endFrame.p,ringExit.pos))*.95,1.9,3.8);",
        "const entryScale=clamp(len(sub(ringEntry.pos,startFrame.p))*.92,2.8,6.5),exitScale=clamp(len(sub(endFrame.p,ringExit.pos))*.95,2.8,6.5);",
        'short separate lower legs',
    )
    s = one(
        s,
        "if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),seed=mixV(startFrame.up,ringEntry.up,smooth01(q)),pos=hermiteOpen(startFrame.p,startFrame.forward,ringEntry.pos,entryT,entryScale,entryScale,q);return{pos,frame:{up:seed},upSeed:seed};}",
        "if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),seed=mixV(startFrame.up,ringEntry.up,smooth01(q)),pos=hermiteOpen(startFrame.p,entryLaunchT,ringEntry.pos,entryT,entryScale,entryScale,q);return{pos,frame:{up:seed},upSeed:seed};}",
        'naturally rising entry leg',
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
