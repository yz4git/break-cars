"""MAYHEM TOUR v8.2: peak-centered replay editing and final-act punch.

The focused iPhone-sized visual review of v8.1 showed that the replay logic was
functionally correct but not yet editorially convincing: CHASE could begin before
the camera settled, TWO-SHOT could crop one car, and IMPACT CLOSE could be wider
than the action. This pass keeps gameplay/physics untouched and:
- retains pre-roll + post-roll around the hottest recorded RIVAL moment,
- cuts the three replay cameras relative to that actual peak rather than thirds,
- frames both cars from their live separation and snaps cleanly on shot changes,
- makes FINAL ACT enter FINALE pressure immediately,
- removes a clipped low-priority course hint from short landscape Tour menus.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8.2 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_product_v82(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    # FINAL ACT should feel different from frame one rather than briefly reading
    # as another ordinary RIVAL RUSH before progress crosses 12%.
    old_final = "if(hull<.29&&progress<.82){next='RELIEF';intensity=Math.max(.18,base-.30);}else if(eventIndex===MAYHEM_EVENTS.length-1&&progress>.12){next='FINALE';intensity=.97;}else if(progress>.78){next='FINALE';intensity=Math.min(.96,base+.18);}"
    new_final = "if(eventIndex===MAYHEM_EVENTS.length-1){next='FINALE';intensity=.97;}else if(hull<.29&&progress<.82){next='RELIEF';intensity=Math.max(.18,base-.30);}else if(progress>.78){next='FINALE';intensity=Math.min(.96,base+.18);}"
    s = one(s, old_final, new_final, 'immediate FINAL ACT pressure')

    # Append late function declarations so the mature v7/v8 pipeline stays intact
    # while these product-review overrides become the effective implementations.
    s += r'''

/* MAYHEM TOUR v8.2 — visual-review editorial overrides */
let mayhemReplayV82BestPeak=0,mayhemReplayV82PostFrames=0,mayhemReplayV82FrozenPeak=0,mayhemReplayV82LastShot='';
function mayhemReplayV82Clone(f){return{p:[...f.p],r:[...f.r],c:[...f.c],heat:f.heat,state:f.state};}
function mayhemReplayReset(){
 mayhemReplayClock=0;mayhemReplayFrames=[];mayhemReplayBest=[];mayhemReplayBestHeat=-1;mayhemReplayFrozen=[];mayhemReplayPlaying=false;mayhemReplayTime=0;mayhemReplayLastHp=world?.cars?.[0]?.hp||0;
 mayhemReplayV82BestPeak=0;mayhemReplayV82PostFrames=0;mayhemReplayV82FrozenPeak=0;mayhemReplayV82LastShot='';
 const o=$('mayhem-replay-overlay');if(o)o.remove();
}
function mayhemReplayCapture(dt){
 if(!mayhemActive()||mode!=='race'||mayhemReplayPlaying)return;
 mayhemReplayClock-=dt;if(mayhemReplayClock>0)return;mayhemReplayClock=MAYHEM_REPLAY_STEP;
 const p=world?.cars?.[0],rid=mayhemRivalId(),pm=carMeshes[0]?.g,rm=carMeshes[rid]?.g;if(!p||!pm||!rm)return;
 const rival=world.cars[rid],distance=rival?Math.hypot(rival.x-p.x,rival.z-p.z):99,damage=mayhemReplayLastHp>0?Math.max(0,mayhemReplayLastHp-p.hp)/Math.max(1,p.maxHP):0;mayhemReplayLastHp=p.hp;
 const heat=mayhemDirectorIntensity+(1-clamp(distance/30,0,1))*.34+damage*3+(mayhemDirectorState==='FINALE'?.18:mayhemDirectorState==='RIVAL RUSH'?.12:0),frame={p:mayhemReplayPose(pm),r:mayhemReplayPose(rm),c:mayhemReplayPose(camera),heat,state:mayhemDirectorState};
 mayhemReplayFrames.push(frame);if(mayhemReplayFrames.length>MAYHEM_REPLAY_FRAMES)mayhemReplayFrames.shift();
 if(mayhemReplayFrames.length>=18&&heat>mayhemReplayBestHeat+.012){
  mayhemReplayBestHeat=heat;const start=Math.max(0,mayhemReplayFrames.length-18);mayhemReplayBest=mayhemReplayFrames.slice(start).map(mayhemReplayV82Clone);mayhemReplayV82BestPeak=mayhemReplayBest.length-1;mayhemReplayV82PostFrames=18;
 }else if(mayhemReplayV82PostFrames>0&&mayhemReplayBest.length){
  mayhemReplayBest.push(mayhemReplayV82Clone(frame));mayhemReplayV82PostFrames--;
 }
 window.__breakCarsHighlightReplay={recording:true,frames:mayhemReplayFrames.length,bestFrames:mayhemReplayBest.length,bestHeat:mayhemReplayBestHeat,peakIndex:mayhemReplayV82BestPeak,playing:false,v82:true};
}
function mayhemReplayFreeze(){
 const usingBest=mayhemReplayBest.length>=12,src=usingBest?mayhemReplayBest:mayhemReplayFrames;if(!src.length){mayhemReplayFrozen=[];return;}
 let peak=usingBest?Math.max(0,Math.min(src.length-1,mayhemReplayV82BestPeak)):0;
 if(!usingBest){let heat=-Infinity;for(let i=0;i<src.length;i++)if((src[i].heat??-Infinity)>heat){heat=src[i].heat;peak=i;}}
 const start=Math.max(0,peak-14),end=Math.min(src.length,peak+17);mayhemReplayFrozen=src.slice(start,end).map(mayhemReplayV82Clone);mayhemReplayV82FrozenPeak=Math.max(0,peak-start);mayhemReplayV82LastShot='';
 window.__breakCarsHighlightReplay={recording:false,frames:mayhemReplayFrozen.length,bestFrames:mayhemReplayBest.length,bestHeat:mayhemReplayBestHeat,peakIndex:mayhemReplayV82FrozenPeak,peakProgress:mayhemReplayFrozen.length>1?mayhemReplayV82FrozenPeak/(mayhemReplayFrozen.length-1):0,playing:false,v82:true};
}
function mayhemReplayCinematicCamera(a,b,t,progress){
 mayhemReplayLerp3(a.p,b.p,t,mayhemReplayP);mayhemReplayLerp3(a.r,b.r,t,mayhemReplayR);mayhemReplayMid.copy(mayhemReplayP).lerp(mayhemReplayR,.5);
 mayhemReplayQuat.set(a.p[3],a.p[4],a.p[5],a.p[6]).slerp(new THREE.Quaternion(b.p[3],b.p[4],b.p[5],b.p[6]),t);mayhemReplayForward.set(0,0,1).applyQuaternion(mayhemReplayQuat);mayhemReplayForward.y=0;if(mayhemReplayForward.lengthSq()<.01)mayhemReplayForward.set(0,0,1);else mayhemReplayForward.normalize();
 mayhemReplaySide.copy(mayhemReplayR).sub(mayhemReplayP);mayhemReplaySide.y=0;const separation=Math.max(.1,mayhemReplaySide.length());if(separation<.4)mayhemReplaySide.set(-mayhemReplayForward.z,0,mayhemReplayForward.x);else{mayhemReplaySide.normalize();mayhemReplaySide.set(-mayhemReplaySide.z,0,mayhemReplaySide.x);}
 const count=Math.max(2,mayhemReplayFrozen.length),peak=clamp(mayhemReplayV82FrozenPeak/(count-1),.28,.74),twoStart=Math.max(.16,peak-.16),impactStart=Math.min(.82,peak+.07);let fov=58,nextShot='CHASE';
 if(progress<twoStart){
  nextShot='CHASE';const back=10.8+Math.min(3,separation*.12);mayhemReplayDesired.copy(mayhemReplayP).addScaledVector(mayhemReplayForward,-back).addScaledVector(mayhemReplaySide,1.0);mayhemReplayDesired.y+=3.0;mayhemReplayTarget.copy(mayhemReplayP).addScaledVector(mayhemReplayForward,3.6);mayhemReplayTarget.y+=.75;fov=62;
 }else if(progress<impactStart){
  nextShot='RIVAL TWO-SHOT';const d=clamp(9.5+separation*.78,10.5,18);mayhemReplayDesired.copy(mayhemReplayMid).addScaledVector(mayhemReplaySide,d).addScaledVector(mayhemReplayForward,-1.0);mayhemReplayDesired.y+=3.6;mayhemReplayTarget.copy(mayhemReplayMid);mayhemReplayTarget.y+=.8;fov=clamp(54+separation*.28,54,60);
 }else{
  nextShot='IMPACT CLOSE';const d=clamp(5.2+separation*.30,5.8,8.8);mayhemReplayDesired.copy(mayhemReplayMid).addScaledVector(mayhemReplaySide,-d).addScaledVector(mayhemReplayForward,-.8);mayhemReplayDesired.y+=2.05;mayhemReplayTarget.copy(mayhemReplayMid);mayhemReplayTarget.y+=.65;fov=44;
 }
 const changed=mayhemReplayV82LastShot!==nextShot;mayhemReplayV82LastShot=nextShot;mayhemReplayShot=nextShot;if(changed)camera.position.copy(mayhemReplayDesired);else camera.position.lerp(mayhemReplayDesired,.38);camera.lookAt(mayhemReplayTarget);if(camera.fov!==undefined){camera.fov+=(fov-camera.fov)*(changed?.55:.24);camera.updateProjectionMatrix?.();}
}
window.__breakCarsMayhemV82=true;
'''
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''

/* v8.2: short landscape menus already communicate the objective above the fold. */
@media(orientation:landscape) and (max-height:430px){body.mayhem-tour:not(.playing) .course-hint{display:none!important}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_product_v82(Path('_site'))
