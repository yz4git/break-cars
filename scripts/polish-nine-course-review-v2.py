"""Second visual-review pass for the three 3D racing courses.

Keep loops and collisions fully physical while improving pack flow after
stunts and keeping jump cameras clear of elevated track structures.
"""
from pathlib import Path
import re


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'nine-course v2 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def regex_one(text: str, pattern: str, new: str, label: str) -> str:
    out, n = re.subn(pattern, new, text, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError(f'nine-course v2 {label}: expected 1 match, found {n}')
    return out


def apply_nine_course_review_v2(target: Path) -> None:
    # Put the jump camera above the entire course envelope. This avoids the
    # camera sitting inside a loop rib / elevated crossover on SKY FORGE and
    # DOUBLE ORBIT while still looking ahead to the landing.
    game = target / 'game.js'
    s = game.read_text()
    old_jump = "else if(racingJump){const landingPose=trackPoint((p.trackS??0)+14,0),jumpCamY=Math.max(b.py+6.8,landingPose.y+5.2);camTarget.set(b.px-racePose.forward.x*9,b.py+5.8,b.pz-racePose.forward.z*7);lookTarget.set(landingPose.x+landingPose.up.x*1.15,landingPose.y+landingPose.up.y*1.15,landingPose.z+landingPose.up.z*1.15);camera.up.lerp(physicsWorldUp,1-Math.exp(-9*dt));camera.fov=64;}"
    if old_jump not in s:
        old_jump = "else if(racingJump){const landingPose=trackPoint((p.trackS??0)+14,0),jumpCamY=Math.max(b.py+6.8,landingPose.y+5.2);camTarget.set(b.px-racePose.forward.x*9,jumpCamY,b.pz-racePose.forward.z*9);lookTarget.set(landingPose.x+landingPose.up.x*1.15,landingPose.y+landingPose.up.y*1.15,landingPose.z+landingPose.up.z*1.15);camera.up.lerp(physicsWorldUp,1-Math.exp(-10*dt));camera.fov=66;}"
    new_jump = "else if(racingJump){const landingPose=trackPoint((p.trackS??0)+15,0),rearPose=trackPoint((p.trackS??0)-6,0),courseTop=fullPhysicsSpec.race?.maxY||0,jumpCamY=Math.max(b.py+11.5,landingPose.y+10.5,courseTop+4.5);camTarget.set(rearPose.x,jumpCamY,rearPose.z);lookTarget.set(landingPose.x+landingPose.up.x*1.2,landingPose.y+landingPose.up.y*1.2,landingPose.z+landingPose.up.z*1.2);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=68;}"
    s = one(s, old_jump, new_jump, 'high jump camera')
    game.write_text(s)

    # Keep AI flowing for longer after loop/jump exits. Physical collisions
    # remain enabled; only target selection and lane discipline are stabilized.
    racing = target / 'racing.js'
    s = racing.read_text()
    old_flow = "const stunt=p.kind==='jump-ramp'||p.kind==='jump-gap'||p.kind==='jump-landing',sinceJump=wrap(p.s-COURSE_SPEC.jump.endS),landingFlow=stunt||sinceJump<22;"
    new_flow = "const stunt=p.kind==='jump-ramp'||p.kind==='jump-gap'||p.kind==='jump-landing',sinceJump=wrap(p.s-COURSE_SPEC.jump.endS),loopExitFlow=(COURSE_SPEC.loops||[COURSE_SPEC.loop]).some(l=>wrap(p.s-l.endS)<32),landingFlow=stunt||sinceJump<34||loopExitFlow;"
    s = one(s, old_flow, new_flow, 'extended stunt flow')
    racing.write_text(s)

    physics = target / 'physics3d.js'
    s = physics.read_text()
    # Multi-course stunt safety is intentionally contact-only. BOOST is kept
    # through the loop and for 32m after the exit; this specifically covers the
    # SKY FORGE post-loop transition that was able to bleed to ~0m/s. There is
    # no orientation torque or quaternion correction, so loops remain free 6DoF.
    helpers = """const rampageStuntSafety=c=>{if(!c)return false;const L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,kind=racePointAt(q).kind,loops=RAMPAGE_RACE_SPEC.loops||[RAMPAGE_RACE_SPEC.loop],nearLoop=loops.some(l=>{const before=(l.startS-q+L)%L,after=(q-l.endS+L)%L;return(q>=l.startS&&q<=l.endS)||before<38||after<32;}),j=RAMPAGE_RACE_SPEC.jump,beforeJump=(j.startS-q+L)%L,afterJump=(q-j.endS+L)%L;return nearLoop||kind==='jump-ramp'||kind==='jump-gap'||kind==='jump-landing'||beforeJump<10||afterJump<34;};
const rampageBoostZone=c=>{if(!c)return false;const L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,kind=racePointAt(q).kind,loops=RAMPAGE_RACE_SPEC.loops||[RAMPAGE_RACE_SPEC.loop];return loops.some(l=>{const before=(l.startS-q+L)%L,after=(q-l.endS+L)%L;return(q>=l.startS&&q<=l.endS)||before<36||after<32;})||kind==='loop';};
"""
    s = regex_one(s, r"const rampageStuntSafety=c=>\{.*?\};\nconst rampageBoostZone=c=>\{.*?\};\n", helpers, 'multi-stunt safety helpers')
    physics.write_text(s)

    # Match the physical assist with visible pads; no invisible post-loop push.
    view = target / 'track-view.js'
    s = view.read_text()
    old_visual = "for(let s=loop.startS-34;s<=loop.endS;s+=3.3)"
    if old_visual in s:
        s = one(s, old_visual, "for(let s=loop.startS-34;s<=loop.endS+30;s+=3.3)", 'exit boost visuals')
    else:
        old_visual = "for(let s=spec.loop.startS-34;s<=spec.loop.endS;s+=3.3)"
        s = one(s, old_visual, "for(let s=spec.loop.startS-34;s<=spec.loop.endS+30;s+=3.3)", 'exit boost visuals')
    view.write_text(s)


if __name__ == '__main__':
    apply_nine_course_review_v2(Path('_site'))
