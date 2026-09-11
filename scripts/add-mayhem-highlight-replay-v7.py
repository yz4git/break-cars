"""MAYHEM TOUR v7: real transform-based HIGHLIGHT REPLAY.

Record a small rolling window of the rendered player, persistent rival and camera
poses during Tour events. The hottest Director window is retained as a highlight.
At PIT/final results a HIGHLIGHT REPLAY button plays that recorded window back as
a short DIRECTOR CUT without resimulating physics or mutating Tour progression.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v7 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_highlight_replay_v7(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    director_anchor = "let mayhemDirectorClock=0,mayhemDirectorState='BUILD',mayhemDirectorIntensity=.34,mayhemDirectorLast='';"
    replay_core = director_anchor + r'''
let mayhemReplayClock=0,mayhemReplayFrames=[],mayhemReplayBest=[],mayhemReplayBestHeat=-1,mayhemReplayFrozen=[],mayhemReplayPlaying=false,mayhemReplayTime=0,mayhemReplayLastHp=0;
const MAYHEM_REPLAY_STEP=.08,MAYHEM_REPLAY_FRAMES=100;
function mayhemReplayReset(){mayhemReplayClock=0;mayhemReplayFrames=[];mayhemReplayBest=[];mayhemReplayBestHeat=-1;mayhemReplayFrozen=[];mayhemReplayPlaying=false;mayhemReplayTime=0;mayhemReplayLastHp=world?.cars?.[0]?.hp||0;const o=$('mayhem-replay-overlay');if(o)o.remove();}
function mayhemReplayPose(g){return[g.position.x,g.position.y,g.position.z,g.quaternion.x,g.quaternion.y,g.quaternion.z,g.quaternion.w];}
function mayhemReplayCapture(dt){if(!mayhemActive()||mode!=='race'||mayhemReplayPlaying)return;mayhemReplayClock-=dt;if(mayhemReplayClock>0)return;mayhemReplayClock=MAYHEM_REPLAY_STEP;const p=world?.cars?.[0],rid=mayhemRivalId(),pm=carMeshes[0]?.g,rm=carMeshes[rid]?.g;if(!p||!pm||!rm)return;const rival=world.cars[rid],distance=rival?Math.hypot(rival.x-p.x,rival.z-p.z):99,damage=mayhemReplayLastHp>0?Math.max(0,mayhemReplayLastHp-p.hp)/Math.max(1,p.maxHP):0;mayhemReplayLastHp=p.hp;const heat=mayhemDirectorIntensity+(1-clamp(distance/30,0,1))*.34+damage*3+(mayhemDirectorState==='FINALE'?.18:mayhemDirectorState==='RIVAL RUSH'?.12:0),frame={p:mayhemReplayPose(pm),r:mayhemReplayPose(rm),c:mayhemReplayPose(camera),heat,state:mayhemDirectorState};mayhemReplayFrames.push(frame);if(mayhemReplayFrames.length>MAYHEM_REPLAY_FRAMES)mayhemReplayFrames.shift();if(mayhemReplayFrames.length>=24&&heat>=mayhemReplayBestHeat){mayhemReplayBestHeat=heat;mayhemReplayBest=mayhemReplayFrames.map(f=>({p:[...f.p],r:[...f.r],c:[...f.c],heat:f.heat,state:f.state}));}window.__breakCarsHighlightReplay={recording:true,frames:mayhemReplayFrames.length,bestFrames:mayhemReplayBest.length,bestHeat:mayhemReplayBestHeat,playing:false};}
function mayhemReplayFreeze(){const src=mayhemReplayBest.length>=12?mayhemReplayBest:mayhemReplayFrames;mayhemReplayFrozen=src.map(f=>({p:[...f.p],r:[...f.r],c:[...f.c],heat:f.heat,state:f.state}));window.__breakCarsHighlightReplay={recording:false,frames:mayhemReplayFrozen.length,bestFrames:mayhemReplayBest.length,bestHeat:mayhemReplayBestHeat,playing:false};}
function mayhemReplaySetPose(g,a,b,t){if(!g||!a||!b)return;g.position.set(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t);const qa=new THREE.Quaternion(a[3],a[4],a[5],a[6]),qb=new THREE.Quaternion(b[3],b[4],b[5],b[6]);g.quaternion.copy(qa).slerp(qb,t);}
function mayhemReplayStart(){if(mayhemReplayFrozen.length<2||mayhemReplayPlaying)return;mayhemReplayPlaying=true;mayhemReplayTime=0;$('modal').classList.add('hidden');let o=$('mayhem-replay-overlay');if(!o){o=document.createElement('div');o.id='mayhem-replay-overlay';document.body.appendChild(o);}o.innerHTML=`<small>MAYHEM TOUR</small><b>HIGHLIGHT REPLAY</b><span>DIRECTOR CUT · ${mayhemRivalName()}</span>`;window.__breakCarsHighlightReplay={recording:false,frames:mayhemReplayFrozen.length,bestHeat:mayhemReplayBestHeat,playing:true};}
function mayhemReplayStop(){mayhemReplayPlaying=false;const o=$('mayhem-replay-overlay');if(o)o.remove();$('modal').classList.remove('hidden');window.__breakCarsHighlightReplay={recording:false,frames:mayhemReplayFrozen.length,bestHeat:mayhemReplayBestHeat,playing:false};}
function mayhemReplayApply(dt){if(!mayhemReplayPlaying||mayhemReplayFrozen.length<2)return;mayhemReplayTime+=dt;const duration=(mayhemReplayFrozen.length-1)*MAYHEM_REPLAY_STEP;if(mayhemReplayTime>=duration){mayhemReplayStop();return;}const f=mayhemReplayTime/MAYHEM_REPLAY_STEP,i=Math.min(mayhemReplayFrozen.length-2,Math.floor(f)),t=f-i,a=mayhemReplayFrozen[i],b=mayhemReplayFrozen[i+1],rid=mayhemRivalId();mayhemReplaySetPose(carMeshes[0]?.g,a.p,b.p,t);mayhemReplaySetPose(carMeshes[rid]?.g,a.r,b.r,t);mayhemReplaySetPose(camera,a.c,b.c,t);const o=$('mayhem-replay-overlay');if(o){const state=t<.5?a.state:b.state;o.dataset.state=state;o.querySelector('span').textContent=`DIRECTOR CUT · ${mayhemRivalName()} · ${state}`;}window.__breakCarsHighlightReplay={recording:false,frames:mayhemReplayFrozen.length,bestHeat:mayhemReplayBestHeat,playing:true,index:i};}
function mayhemReplayAttachButton(box){if(!box||mayhemReplayFrozen.length<2||box.querySelector('[data-tour-replay]'))return;const row=box.querySelector('.tour-final>div:last-child,.tour-pit>div:last-child')||box,button=document.createElement('button');button.type='button';button.dataset.tourReplay='1';button.className='tour-replay-button';button.innerHTML='<b>HIGHLIGHT REPLAY</b><small>DIRECTOR CUT</small>';button.onclick=mayhemReplayStart;row.appendChild(button);}
'''
    s = one(s, director_anchor, replay_core, 'replay core')

    after = "function mayhemAfterEvent(){if(!mayhemActive())return;document.body.classList.add('mayhem-tour-result');"
    after_new = "function mayhemAfterEvent(){if(!mayhemActive())return;mayhemReplayFreeze();document.body.classList.add('mayhem-tour-result');"
    s = one(s, after, after_new, 'freeze result highlight')

    final_hook = "box.querySelector('[data-tour-final=\"garage\"]').onclick=mayhemEndRun;$('result-kicker').textContent='MAYHEM TOUR / COMPLETE';return;"
    final_hook_new = "box.querySelector('[data-tour-final=\"garage\"]').onclick=mayhemEndRun;mayhemReplayAttachButton(box);$('result-kicker').textContent='MAYHEM TOUR / COMPLETE';return;"
    s = one(s, final_hook, final_hook_new, 'final replay button')

    pit_hook = "box.querySelectorAll('[data-tour-up]').forEach(b=>b.onclick=()=>mayhemChoose(b.dataset.tourUp));$('result-kicker').textContent=`MAYHEM TOUR / EVENT ${event+1} CLEAR`;"
    pit_hook_new = "box.querySelectorAll('[data-tour-up]').forEach(b=>b.onclick=()=>mayhemChoose(b.dataset.tourUp));mayhemReplayAttachButton(box);$('result-kicker').textContent=`MAYHEM TOUR / EVENT ${event+1} CLEAR`;"
    s = one(s, pit_hook, pit_hook_new, 'pit replay button')

    start = "if(mayhemActive()){document.body.classList.remove('mayhem-tour-result');const oldBadge=$('tour-run-badge');"
    start_new = "if(mayhemActive()){mayhemReplayReset();document.body.classList.remove('mayhem-tour-result');const oldBadge=$('tour-run-badge');"
    s = one(s, start, start_new, 'reset recorder on event start')

    render = "if(mode==='race'&&mayhemActive())mayhemDirectorTick(dt);if(mode!=='paused'){if(toastTime>0){toastTime-=dt;if(toastTime<=0)$('toast').textContent='';}visuals(dt);}else if(engineGain)engineGain.gain.setTargetAtTime(0,audioCtx.currentTime,.05);renderer.render(scene,camera);"
    render_new = "if(mode==='race'&&mayhemActive())mayhemDirectorTick(dt);if(mode!=='paused'){if(toastTime>0){toastTime-=dt;if(toastTime<=0)$('toast').textContent='';}visuals(dt);}else if(engineGain)engineGain.gain.setTargetAtTime(0,audioCtx.currentTime,.05);if(mayhemReplayPlaying)mayhemReplayApply(dt);else if(mode==='race'&&mayhemActive())mayhemReplayCapture(dt);renderer.render(scene,camera);"
    s = one(s, render, render_new, 'capture/play before render')

    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
.tour-replay-button{border-color:#ff3f7288!important;background:linear-gradient(135deg,#35131f,#171b27)!important;box-shadow:0 0 0 1px #ff6d9430 inset,0 8px 24px #0008!important}.tour-replay-button b,.tour-replay-button small{display:block}.tour-replay-button small{margin-top:2px;font-size:7px;letter-spacing:.12em;color:#ff9bb7}
#mayhem-replay-overlay{position:fixed;z-index:40;top:max(14px,env(safe-area-inset-top));left:50%;transform:translateX(-50%);min-width:min(74vw,360px);padding:8px 18px 7px;border:1px solid #ff4f7e99;border-radius:4px;background:linear-gradient(90deg,#100b13e8,#28101ae8,#100b13e8);box-shadow:0 8px 36px #000b,0 0 24px #ff315533;color:#fff;text-align:center;pointer-events:none;font-family:system-ui}#mayhem-replay-overlay small,#mayhem-replay-overlay b,#mayhem-replay-overlay span{display:block}#mayhem-replay-overlay small{font:800 7px/1.1 system-ui;letter-spacing:.28em;color:#ff8cab}#mayhem-replay-overlay b{margin-top:2px;font:950 italic 15px/1 system-ui;letter-spacing:.08em}#mayhem-replay-overlay span{margin-top:4px;font:800 7px/1.1 system-ui;letter-spacing:.12em;color:#d8dce5}
body:has(#mayhem-replay-overlay) #mayhem-director{display:none!important}
@media(orientation:landscape) and (max-height:430px){#mayhem-replay-overlay{top:max(7px,env(safe-area-inset-top));padding:5px 14px 4px}#mayhem-replay-overlay b{font-size:12px}#mayhem-replay-overlay span,#mayhem-replay-overlay small{font-size:6px}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_highlight_replay_v7(Path('_site'))
