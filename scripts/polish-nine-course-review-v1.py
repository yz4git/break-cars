"""Post visual-review polish shared by all nine courses."""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'nine-course polish {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_nine_course_review_polish(target: Path) -> None:
    # Player-only auto recovery must distinguish a roof-down car on a real road
    # from a legitimately inverted car whose wheels are loaded on a loop crown.
    physics = target / 'physics3d.js'
    s = physics.read_text()
    s = one(
        s,
        "const fullyFlipped=up.y<-.62&&b.groundedWheels===0&&nearSurface;",
        "const surfaceAlign=nearSurface?dot(up,surface.normal):1,fullyFlipped=nearSurface&&surfaceAlign<-.62;",
        'surface-frame auto upright',
    )
    physics.write_text(s)

    # Arena camera: follow XYZ motion, but never inherit chassis roll/pitch.
    # Keeping world-up also prevents the chase camera from going under custom
    # terrain when a car tumbles on Cross Fire / Tidal Foundry.
    game = target / 'game.js'
    s = game.read_text()
    old = "if(view===2){camTarget.set(b.px,42,b.pz-8);lookTarget.set(b.px,b.py,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-6*dt));camera.fov=65;}else{const loopDx="
    new = "if(view===2){camTarget.set(b.px,42,b.pz-8);lookTarget.set(b.px,b.py,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-6*dt));camera.fov=65;}else if(gameMode!=='racing'){camHeading+=angle(p.heading-camHeading)*(1-Math.exp(-4.5*dt));const distance=view===1?16:10.2,lift=view===1?9.5:5.2+speed*.014;camTarget.set(b.px-Math.sin(camHeading)*distance,b.py+lift,b.pz-Math.cos(camHeading)*distance);const terrainH=courseHeight(camTarget.x,camTarget.z);if(terrainH!==null)camTarget.y=Math.max(camTarget.y,terrainH+2.6);lookTarget.set(b.px+Math.sin(camHeading)*4,b.py+.35,b.pz+Math.cos(camHeading)*4);camera.up.lerp(physicsWorldUp,1-Math.exp(-9*dt));camera.fov=58+speed*.16;}else{const loopDx="
    s = one(s, old, new, 'world-up arena camera')

    old_jump = "else if(racingJump){const landingPose=trackPoint((p.trackS??0)+14,0);camTarget.set(b.px-racePose.forward.x*7,b.py+5.8,b.pz-racePose.forward.z*7);lookTarget.set(landingPose.x+landingPose.up.x*1.15,landingPose.y+landingPose.up.y*1.15,landingPose.z+landingPose.up.z*1.15);camera.up.lerp(physicsWorldUp,1-Math.exp(-9*dt));camera.fov=64;}"
    new_jump = "else if(racingJump){const landingPose=trackPoint((p.trackS??0)+14,0),jumpCamY=Math.max(b.py+6.8,landingPose.y+5.2);camTarget.set(b.px-racePose.forward.x*9,jumpCamY,b.pz-racePose.forward.z*9);lookTarget.set(landingPose.x+landingPose.up.x*1.15,landingPose.y+landingPose.up.y*1.15,landingPose.z+landingPose.up.z*1.15);camera.up.lerp(physicsWorldUp,1-Math.exp(-10*dt));camera.fov=66;}"
    s = one(s, old_jump, new_jump, 'jump visibility camera')
    game.write_text(s)

    # Racing flow: spread the pack before the jump and keep the first 22m of
    # the landing as a stunt-flow lane rather than an attack zone. Cars still
    # collide physically; only AI target selection is suspended briefly.
    racing = target / 'racing.js'
    s = racing.read_text()
    s = one(
        s,
        "c.stallTime=speed<2?c.stallTime+dt:Math.max(0,c.stallTime-dt);if(c.stallTime>1.6&&p.kind!=='loop'){c.aiReverse=1.0;c.stallTime=0;}",
        "c.stallTime=speed<2?c.stallTime+dt:Math.max(0,c.stallTime-dt);if(c.stallTime>1.2&&p.kind!=='loop'){c.aiReverse=1.25;c.stallTime=0;}",
        'CPU stall recovery',
    )
    old_stunt = "const stunt=p.kind==='jump-ramp'||p.kind==='jump-gap'||p.kind==='jump-landing';\n c.brawlTimer="
    new_stunt = "const stunt=p.kind==='jump-ramp'||p.kind==='jump-gap'||p.kind==='jump-landing',sinceJump=wrap(p.s-COURSE_SPEC.jump.endS),landingFlow=stunt||sinceJump<22;\n if(landingFlow){c.battleTarget=-1;c.aiReverse=0;const flowLane=c.id===0?0:clamp(((c.id%5)-2)*2.55,-5.6,5.6),target=trackPoint(p.s+clamp(11+speed*.30,12,19),flowLane),delta=angle(Math.atan2(target.x-c.x,target.z-c.z)-c.heading),laneFix=clamp((flowLane-p.lane)*.11,-.30,.30);return{gas:1,brake:0,steer:clamp(delta*1.4+laneFix,-.68,.68),hand:0};}\n c.brawlTimer="
    s = one(s, old_stunt, new_stunt, 'jump and landing flow lanes')
    racing.write_text(s)


if __name__ == '__main__':
    apply_nine_course_review_polish(Path('_site'))
