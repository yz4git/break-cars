"""MAYHEM TOUR v8.8: keep FINAL SHOWDOWN replay camera unobstructed.

The iPhone-sized v8.7 browser audit proved the showdown pipeline works through
FACE OFF -> FINAL DUEL -> finish-cut replay, but the generic low replay camera
could sit under DOUBLE ORBIT geometry and fill most of the frame with the
underside of the loop.

v8.7.1 already preserves the FINISH CUT / SLOW MOTION replay caption. This pass
therefore changes only event-9 replay camera placement and face-off HUD cleanup.
Generic Tour replay cameras, physics, AI and course geometry are untouched.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8.8 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_showdown_v88(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    camera_head = "function mayhemReplayCinematicCamera(a,b,t,progress){"
    camera_head_new = "function mayhemReplayCinematicCamera(a,b,t,progress){if(mayhemShowdownEndingReplay&&mayhemFinalDuelActive()){mayhemShowdownReplayCameraV88(a,b,t,progress);return;}"
    s = one(s, camera_head, camera_head_new, 'final replay camera override')

    frame_tick = "function mayhemShowdownFrameTick(dt){mayhemShowdownIntroTick(dt);mayhemShowdownRaceTick();}"
    frame_tick_new = "function mayhemShowdownFrameTick(dt){mayhemShowdownIntroTick(dt);mayhemShowdownRaceTick();const ending=$('mayhem-showdown-ending');if(ending?.classList.contains('show')&&!mayhemReplayPlaying)window.__breakCarsMayhemShowdown={...(window.__breakCarsMayhemShowdown||{}),stage:'ENDING',intro:false,slowMotion:false,ending:true};}"
    s = one(s, frame_tick, frame_tick_new, 'stable ending telemetry')

    s += r'''

/* MAYHEM TOUR v8.8 — FINAL SHOWDOWN replay camera safety */
function mayhemShowdownReplayCameraV88(a,b,t,progress){
 mayhemReplayLerp3(a.p,b.p,t,mayhemReplayP);mayhemReplayLerp3(a.r,b.r,t,mayhemReplayR);mayhemReplayMid.copy(mayhemReplayP).lerp(mayhemReplayR,.5);
 mayhemReplayQuat.set(a.p[3],a.p[4],a.p[5],a.p[6]).slerp(new THREE.Quaternion(b.p[3],b.p[4],b.p[5],b.p[6]),t);mayhemReplayForward.set(0,0,1).applyQuaternion(mayhemReplayQuat);mayhemReplayForward.y=0;if(mayhemReplayForward.lengthSq()<.01)mayhemReplayForward.set(0,0,1);else mayhemReplayForward.normalize();
 mayhemReplaySide.copy(mayhemReplayR).sub(mayhemReplayP);mayhemReplaySide.y=0;const separation=Math.max(.1,mayhemReplaySide.length());if(separation<.45)mayhemReplaySide.set(-mayhemReplayForward.z,0,mayhemReplayForward.x);else{mayhemReplaySide.normalize();mayhemReplaySide.set(-mayhemReplaySide.z,0,mayhemReplaySide.x);}
 let fov=58,nextShot='SHOWDOWN CHASE';
 if(progress<.46){
  nextShot='SHOWDOWN CHASE';const back=clamp(12.8+separation*.18,13,17);mayhemReplayDesired.copy(mayhemReplayP).addScaledVector(mayhemReplayForward,-back).addScaledVector(mayhemReplaySide,5.2);mayhemReplayDesired.y=Math.max(mayhemReplayDesired.y+8.2,mayhemReplayMid.y+8.6);mayhemReplayTarget.copy(mayhemReplayP).addScaledVector(mayhemReplayForward,4.8);mayhemReplayTarget.y+=1.0;fov=62;
 }else if(progress<.76){
  nextShot='SHOWDOWN TWO-SHOT';const d=clamp(15+separation*.72,16,23);mayhemReplayDesired.copy(mayhemReplayMid).addScaledVector(mayhemReplaySide,d).addScaledVector(mayhemReplayForward,-2.2);mayhemReplayDesired.y=Math.max(mayhemReplayDesired.y+11.5,mayhemReplayMid.y+12);mayhemReplayTarget.copy(mayhemReplayMid);mayhemReplayTarget.y+=.8;fov=clamp(58+separation*.22,58,64);
 }else{
  nextShot='FINISH IMPACT';const d=clamp(11.8+separation*.48,12.5,19);mayhemReplayDesired.copy(mayhemReplayMid).addScaledVector(mayhemReplaySide,-d).addScaledVector(mayhemReplayForward,-4.6);mayhemReplayDesired.y=Math.max(mayhemReplayDesired.y+9.2,mayhemReplayMid.y+9.8);mayhemReplayTarget.copy(mayhemReplayMid);mayhemReplayTarget.y+=.72;fov=clamp(54+separation*.30,54,62);
 }
 const changed=mayhemReplayShot!==nextShot;mayhemReplayShot=nextShot;if(changed)camera.position.copy(mayhemReplayDesired);else camera.position.lerp(mayhemReplayDesired,.34);camera.lookAt(mayhemReplayTarget);if(camera.fov!==undefined){camera.fov+=(fov-camera.fov)*(changed?.62:.28);camera.updateProjectionMatrix?.();}
 if(mayhemReplayPlaying&&mayhemShowdownEndingReplay)window.__breakCarsMayhemShowdown={...(window.__breakCarsMayhemShowdown||{}),stage:'FINISH REPLAY',intro:false,slowMotion:true,ending:false,camera:'HIGH-SIDE',shot:mayhemReplayShot};
}
window.__breakCarsMayhemV88=true;
'''
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.8: the face-off is a clean cinematic beat, not a gameplay HUD state. */
body.mayhem-showdown-intro #hud{opacity:0!important;pointer-events:none!important}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_showdown_v88(Path('_site'))
