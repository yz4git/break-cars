"""MAYHEM TOUR v8.7: FINAL SHOWDOWN cinematics for DOUBLE ORBIT.

This pass is presentation-only. It leaves v8.6 duel AI, course geometry and
physics untouched while giving the ninth event a complete cinematic arc:
- a short pre-race player/RIVAL confrontation two-shot during the countdown,
- a LAST ORBIT visual escalation near the end of the race,
- a finish-focused replay cut rather than the generic hottest-moment cut,
- automatic slow motion through the decisive final replay frames,
- a win/loss-specific ending card after the replay.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8.7 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_showdown_v87(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    duel_anchor = "let mayhemFinalDuelPhase=0;"
    showdown_core = duel_anchor + r'''
let mayhemShowdownIntro=0,mayhemShowdownEndingReplay=false,mayhemShowdownAutoQueued=false,mayhemShowdownLastOrbitShown=false;
const mayhemShowdownP=new THREE.Vector3(),mayhemShowdownR=new THREE.Vector3(),mayhemShowdownMid=new THREE.Vector3(),mayhemShowdownSide=new THREE.Vector3(),mayhemShowdownCam=new THREE.Vector3(),mayhemShowdownTarget=new THREE.Vector3();
function mayhemShowdownOverlay(){let el=$('mayhem-showdown-intro');if(!el){el=document.createElement('div');el.id='mayhem-showdown-intro';document.body.appendChild(el);}return el;}
function mayhemShowdownOnStart(){
 mayhemShowdownIntro=0;mayhemShowdownEndingReplay=false;mayhemShowdownAutoQueued=false;mayhemShowdownLastOrbitShown=false;document.body.classList.remove('mayhem-showdown-intro','mayhem-showdown-last-stand');const old=$('mayhem-showdown-intro');if(old)old.remove();const orbit=$('mayhem-showdown-last-orbit');if(orbit)orbit.remove();
 if(!mayhemFinalDuelActive())return;mayhemShowdownIntro=1.9;document.body.classList.add('mayhem-showdown-intro');const score=mayhemRivalryScore(),el=mayhemShowdownOverlay();el.innerHTML=`<small>FINAL ACT · DOUBLE ORBIT</small><b>FINAL SHOWDOWN</b><span>YOU ${score.player} — ${score.rival} ${mayhemRivalName()}</span>`;window.__breakCarsMayhemShowdown={stage:'FACE OFF',intro:true,slowMotion:false,ending:false};
}
function mayhemShowdownIntroTick(dt){
 if(mayhemShowdownIntro<=0)return;mayhemShowdownIntro=Math.max(0,mayhemShowdownIntro-dt);const pm=carMeshes[0]?.g,rm=carMeshes[mayhemRivalId()]?.g;if(pm&&rm&&mode==='countdown'){pm.getWorldPosition(mayhemShowdownP);rm.getWorldPosition(mayhemShowdownR);mayhemShowdownMid.copy(mayhemShowdownP).lerp(mayhemShowdownR,.5);mayhemShowdownSide.copy(mayhemShowdownR).sub(mayhemShowdownP);mayhemShowdownSide.y=0;if(mayhemShowdownSide.lengthSq()<.3)mayhemShowdownSide.set(1,0,0);else mayhemShowdownSide.normalize();const dolly=9.6+mayhemShowdownIntro*1.1;mayhemShowdownCam.copy(mayhemShowdownMid).addScaledVector(mayhemShowdownSide,dolly);mayhemShowdownCam.y+=4.1;mayhemShowdownTarget.copy(mayhemShowdownMid);mayhemShowdownTarget.y+=.75;camera.position.copy(mayhemShowdownCam);camera.lookAt(mayhemShowdownTarget);if(camera.fov!==undefined){camera.fov+=(50-camera.fov)*.3;camera.updateProjectionMatrix?.();}}
 if(mayhemShowdownIntro<=0){document.body.classList.remove('mayhem-showdown-intro');const el=$('mayhem-showdown-intro');if(el)el.remove();}
}
function mayhemShowdownRaceTick(){
 if(!mayhemFinalDuelActive()||mode!=='race'){document.body.classList.remove('mayhem-showdown-last-stand');return;}const progress=mayhemDirectorProgress();document.body.classList.toggle('mayhem-showdown-last-stand',progress>=.73);if(progress>=.86&&!mayhemShowdownLastOrbitShown){mayhemShowdownLastOrbitShown=true;let el=$('mayhem-showdown-last-orbit');if(!el){el=document.createElement('div');el.id='mayhem-showdown-last-orbit';document.body.appendChild(el);}el.innerHTML=`<small>DOUBLE ORBIT</small><b>LAST ORBIT</b><span>${mayhemRivalName()} · SETTLE IT NOW</span>`;el.classList.add('show');setTimeout(()=>{el?.classList.remove('show');setTimeout(()=>el?.remove(),320);},1450);}}
function mayhemShowdownFrameTick(dt){mayhemShowdownIntroTick(dt);mayhemShowdownRaceTick();}
function mayhemShowdownFreezeFinish(){
 if(!mayhemFinalDuelActive()||!mayhemReplayFrames.length)return;const src=mayhemReplayFrames,start=Math.max(0,src.length-34);mayhemReplayFrozen=src.slice(start).map(mayhemReplayV82Clone);while(mayhemReplayFrozen.length<28&&mayhemReplayFrozen.length)mayhemReplayFrozen.unshift(mayhemReplayV82Clone(mayhemReplayFrozen[0]));mayhemReplayV82FrozenPeak=Math.max(0,mayhemReplayFrozen.length-7);mayhemReplayV82LastShot='';window.__breakCarsHighlightReplay={recording:false,frames:mayhemReplayFrozen.length,bestFrames:mayhemReplayBest.length,bestHeat:mayhemReplayBestHeat,peakIndex:mayhemReplayV82FrozenPeak,peakProgress:mayhemReplayFrozen.length>1?mayhemReplayV82FrozenPeak/(mayhemReplayFrozen.length-1):0,playing:false,finishCut:true,v87:true};
}
function mayhemShowdownReplayRate(){if(!mayhemShowdownEndingReplay||!mayhemFinalDuelActive())return 1;const total=Math.max(.001,(mayhemReplayFrozen.length-1)*MAYHEM_REPLAY_STEP),p=clamp(mayhemReplayTime/total,0,1);return p>=.72?.42:p>=.5?.68:1;}
function mayhemShowdownEndingCard(){
 const score=mayhemRivalryScore(),last=mayhemState.results?.[MAYHEM_EVENTS.length-1]?.rivalResult||'',won=score.player>score.rival;let el=$('mayhem-showdown-ending');if(!el){el=document.createElement('div');el.id='mayhem-showdown-ending';document.body.appendChild(el);}el.dataset.result=won?'win':'loss';el.innerHTML=won?`<small>FINAL SHOWDOWN · ${last==='PLAYER'?'DUEL WON':'SERIES WON'}</small><b>MAYHEM TOUR CHAMPION</b><span>RIVALRY SETTLED · ${mayhemRivalName()} DEFEATED · ${score.player}-${score.rival}</span>`:`<small>FINAL SHOWDOWN · ${last==='RIVAL'?'DUEL LOST':'SERIES LOST'}</small><b>RIVAL OWNS THE NIGHT</b><span>${mayhemRivalName()} TAKES THE TOUR · ${score.player}-${score.rival} · RUN IT BACK</span>`;el.classList.remove('show');void el.offsetWidth;el.classList.add('show');setTimeout(()=>el?.classList.remove('show'),2300);window.__breakCarsMayhemShowdown={stage:'ENDING',intro:false,slowMotion:false,ending:true,won,series:score};
}
function mayhemShowdownScheduleEndingReplay(){
 if(!mayhemFinalDuelActive()||mayhemShowdownAutoQueued||mayhemReplayFrozen.length<2)return;mayhemShowdownAutoQueued=true;if(mayhemParams.get('tourAudit')==='1')return;setTimeout(()=>{if(!mayhemActive()||mayhemReplayPlaying)return;mayhemShowdownEndingReplay=true;mayhemReplayStart();},620);
}
'''
    s = one(s, duel_anchor, showdown_core, 'showdown cinematic core')

    start_hook = "if(mayhemActive()){mayhemReplayReset();document.body.classList.remove('mayhem-tour-result');"
    start_hook_new = "if(mayhemActive()){mayhemReplayReset();mayhemShowdownOnStart();document.body.classList.remove('mayhem-tour-result');"
    s = one(s, start_hook, start_hook_new, 'final face-off start')

    render_hook = "if(mayhemReplayPlaying)mayhemReplayApply(dt);else if(mode==='race'&&mayhemActive())mayhemReplayCapture(dt);renderer.render(scene,camera);"
    render_hook_new = "if(mayhemReplayPlaying)mayhemReplayApply(dt);else if(mode==='race'&&mayhemActive())mayhemReplayCapture(dt);mayhemShowdownFrameTick(dt);renderer.render(scene,camera);"
    s = one(s, render_hook, render_hook_new, 'showdown frame cinematics')

    freeze_hook = "mayhemReplayFreeze();document.body.classList.add('mayhem-tour-result');"
    freeze_hook_new = "mayhemReplayFreeze();mayhemShowdownFreezeFinish();document.body.classList.add('mayhem-tour-result');"
    s = one(s, freeze_hook, freeze_hook_new, 'finish-focused replay freeze')

    time_hook = "mayhemReplayTime+=dt;const duration=(mayhemReplayFrozen.length-1)*MAYHEM_REPLAY_STEP;"
    time_hook_new = "mayhemReplayTime+=dt*mayhemShowdownReplayRate();const duration=(mayhemReplayFrozen.length-1)*MAYHEM_REPLAY_STEP;"
    s = one(s, time_hook, time_hook_new, 'decisive replay slow motion')

    replay_overlay = "o.innerHTML=`<small>MAYHEM TOUR</small><b>HIGHLIGHT REPLAY</b><span>DIRECTOR CUT · ${mayhemRivalName()}</span>`;"
    replay_overlay_new = "const showdown=mayhemShowdownEndingReplay&&mayhemFinalDuelActive();o.dataset.showdown=showdown?'1':'0';o.innerHTML=showdown?`<small>FINAL ACT · DOUBLE ORBIT</small><b>FINAL SHOWDOWN REPLAY</b><span>FINISH CUT · ${mayhemRivalName()} · SLOW MOTION</span>`:`<small>MAYHEM TOUR</small><b>HIGHLIGHT REPLAY</b><span>DIRECTOR CUT · ${mayhemRivalName()}</span>`;if(showdown)window.__breakCarsMayhemShowdown={stage:'FINISH REPLAY',intro:false,slowMotion:true,ending:false};"
    s = one(s, replay_overlay, replay_overlay_new, 'showdown replay title')

    stop_head = "function mayhemReplayStop(){mayhemReplayPlaying=false;mayhemReplayStageStop();"
    stop_head_new = "function mayhemReplayStop(){const showdownEnding=mayhemShowdownEndingReplay&&mayhemFinalDuelActive();mayhemReplayPlaying=false;mayhemReplayStageStop();"
    s = one(s, stop_head, stop_head_new, 'remember ending replay')

    stop_modal = "$('modal').classList.remove('hidden');window.__breakCarsHighlightReplay="
    stop_modal_new = "$('modal').classList.remove('hidden');if(showdownEnding)mayhemShowdownEndingCard();mayhemShowdownEndingReplay=false;window.__breakCarsHighlightReplay="
    s = one(s, stop_modal, stop_modal_new, 'ending card after replay')

    button_hook = "button.innerHTML='<b>HIGHLIGHT REPLAY</b><small>DIRECTOR CUT</small>';button.onclick=mayhemReplayStart;"
    button_hook_new = "button.innerHTML=mayhemFinalDuelActive()?'<b>FINAL SHOWDOWN REPLAY</b><small>FINISH CUT · SLOW MOTION</small>':'<b>HIGHLIGHT REPLAY</b><small>DIRECTOR CUT</small>';button.onclick=()=>{mayhemShowdownEndingReplay=mayhemFinalDuelActive();mayhemReplayStart();};"
    s = one(s, button_hook, button_hook_new, 'final replay button')

    final_hook = "mayhemIntermissionPolish(box,event,true);$('result-kicker').textContent='MAYHEM TOUR / COMPLETE';return;"
    final_hook_new = "mayhemIntermissionPolish(box,event,true);mayhemShowdownScheduleEndingReplay();$('result-kicker').textContent='MAYHEM TOUR / COMPLETE';return;"
    s = one(s, final_hook, final_hook_new, 'automatic showdown ending replay')

    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.7: FINAL SHOWDOWN CINEMATICS */
#mayhem-showdown-intro{position:fixed;z-index:48;left:50%;bottom:max(22px,calc(env(safe-area-inset-bottom) + 16px));transform:translateX(-50%);min-width:min(72vw,420px);padding:9px 22px 8px;border-top:1px solid #ffd16b99;border-bottom:1px solid #ff6b4a77;background:linear-gradient(90deg,transparent,#100b0eea 14%,#21120fee 50%,#100b0eea 86%,transparent);color:#fff;text-align:center;pointer-events:none;text-shadow:0 2px 10px #000;font-family:system-ui}#mayhem-showdown-intro small,#mayhem-showdown-intro b,#mayhem-showdown-intro span{display:block}#mayhem-showdown-intro small{font:900 7px/1.1 system-ui;letter-spacing:.25em;color:#ffbf65}#mayhem-showdown-intro b{margin-top:3px;font:950 italic 18px/.95 system-ui;letter-spacing:.12em;color:#fff1ce}#mayhem-showdown-intro span{margin-top:5px;font:850 8px/1 system-ui;letter-spacing:.1em;color:#ffd9ca}
body.mayhem-showdown-intro #driving,body.mayhem-showdown-intro #mayhem-director,body.mayhem-showdown-intro #mayhem-rival-marker,body.mayhem-showdown-intro #tour-run-badge{opacity:0!important;pointer-events:none!important}
body.mayhem-showdown-last-stand:after{content:"";position:fixed;z-index:17;inset:0;pointer-events:none;box-shadow:inset 0 0 68px #ff402433,inset 0 0 18px #ffb12a1b;animation:showdownPulse .85s ease-in-out infinite alternate}
#mayhem-showdown-last-orbit{position:fixed;z-index:35;left:50%;top:50%;transform:translate(-50%,-50%) scale(.82);min-width:min(68vw,380px);padding:12px 20px;border:1px solid #ffc45f99;background:#140c0bea;box-shadow:0 12px 44px #000c,0 0 32px #ff5a2538;color:#fff;text-align:center;opacity:0;pointer-events:none;font-family:system-ui;transition:.22s ease}#mayhem-showdown-last-orbit.show{opacity:1;transform:translate(-50%,-50%) scale(1)}#mayhem-showdown-last-orbit small,#mayhem-showdown-last-orbit b,#mayhem-showdown-last-orbit span{display:block}#mayhem-showdown-last-orbit small{font:900 7px/1 system-ui;letter-spacing:.25em;color:#ffb85d}#mayhem-showdown-last-orbit b{margin-top:4px;font:950 italic 22px/.95 system-ui;letter-spacing:.14em;color:#fff0ca}#mayhem-showdown-last-orbit span{margin-top:6px;font:850 8px/1 system-ui;letter-spacing:.09em;color:#ffd2c4}
#mayhem-replay-overlay[data-showdown="1"]{border-color:#ffd064aa;background:linear-gradient(90deg,#100b10ed,#35130eed,#100b10ed);box-shadow:0 8px 42px #000d,0 0 30px #ff7a283c}#mayhem-replay-overlay[data-showdown="1"] small{color:#ffbd63}#mayhem-replay-overlay[data-showdown="1"] b{color:#fff0c8}
#mayhem-showdown-ending{position:fixed;z-index:55;left:50%;top:50%;transform:translate(-50%,-50%) scale(.88);min-width:min(76vw,470px);padding:16px 24px 14px;border:1px solid #ffffff55;background:linear-gradient(145deg,#11131cf5,#22110ff5);box-shadow:0 16px 58px #000e;color:#fff;text-align:center;opacity:0;pointer-events:none;font-family:system-ui;transition:.26s ease}#mayhem-showdown-ending.show{opacity:1;transform:translate(-50%,-50%) scale(1)}#mayhem-showdown-ending[data-result="win"]{border-color:#ffd56f99;box-shadow:0 16px 58px #000e,0 0 42px #ffb13a32}#mayhem-showdown-ending[data-result="loss"]{border-color:#ff607c88;box-shadow:0 16px 58px #000e,0 0 36px #ff31552b}#mayhem-showdown-ending small,#mayhem-showdown-ending b,#mayhem-showdown-ending span{display:block}#mayhem-showdown-ending small{font:900 7px/1 system-ui;letter-spacing:.21em;color:#ffbd68}#mayhem-showdown-ending b{margin-top:5px;font:950 italic 21px/.98 system-ui;letter-spacing:.08em}#mayhem-showdown-ending span{margin-top:7px;font:850 8px/1.15 system-ui;letter-spacing:.08em;color:#e6d9d4}
@keyframes showdownPulse{from{opacity:.48}to{opacity:1}}
@media(orientation:landscape) and (max-height:430px){#mayhem-showdown-intro{bottom:max(8px,env(safe-area-inset-bottom));padding:6px 18px 5px}#mayhem-showdown-intro b{font-size:14px}#mayhem-showdown-last-orbit{padding:8px 16px}#mayhem-showdown-last-orbit b{font-size:17px}#mayhem-showdown-ending{padding:10px 18px}#mayhem-showdown-ending b{font-size:16px}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_showdown_v87(Path('_site'))
