"""MAYHEM TOUR v8: product-level dramaturgy, RIVAL readability and cinematic replay.

This pass is based on the iPhone-sized Playwright visual audit of the complete
nine-event run. It keeps all physics/course rules intact while improving four
presentation layers:
- a real 4-act escalation curve for LIVE MAYHEM DIRECTOR,
- an in-world screen-space RIVAL marker with carried hull status,
- readable ACT progression across the nine-event menus and PIT screens,
- a HUD-free, letterboxed multi-shot HIGHLIGHT REPLAY camera.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_product_v8(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    replay_anchor = "const MAYHEM_REPLAY_STEP=.08,MAYHEM_REPLAY_FRAMES=100;"
    product_core = replay_anchor + r'''
const MAYHEM_PRESSURE_CURVE=[.28,.34,.41,.48,.55,.62,.70,.78,.87];
const MAYHEM_ACTS=[
 {id:1,from:0,to:2,short:'ACT I · IGNITION',kicker:'ACT I · IGNITION',stakes:'THE RIVAL AWAKENS'},
 {id:2,from:3,to:5,short:'ACT II · VENDETTA',kicker:'ACT II · VENDETTA',stakes:'NO SAFE LINES'},
 {id:3,from:6,to:7,short:'ACT III · REDLINE',kicker:'ACT III · REDLINE',stakes:'FULL-CONTACT REDLINE'},
 {id:4,from:8,to:8,short:'FINAL ACT',kicker:'FINAL ACT · DOUBLE ORBIT',stakes:'SETTLE THE RIVALRY'}
];
let mayhemDirectorStingerStamp=0,mayhemReplayBaseFov=60,mayhemReplayShot='CHASE';
const mayhemRivalScreen=new THREE.Vector3(),mayhemRivalView=new THREE.Vector3();
const mayhemReplayP=new THREE.Vector3(),mayhemReplayR=new THREE.Vector3(),mayhemReplayMid=new THREE.Vector3(),mayhemReplayForward=new THREE.Vector3(),mayhemReplaySide=new THREE.Vector3(),mayhemReplayDesired=new THREE.Vector3(),mayhemReplayTarget=new THREE.Vector3();
const mayhemReplayQuat=new THREE.Quaternion();
function mayhemActMeta(index=mayhemState?.event||0){return MAYHEM_ACTS.find(a=>index>=a.from&&index<=a.to)||MAYHEM_ACTS[MAYHEM_ACTS.length-1];}
function mayhemTourPressure(){const i=Math.max(0,Math.min(MAYHEM_PRESSURE_CURVE.length-1,mayhemState?.event||0));return MAYHEM_PRESSURE_CURVE[i];}
function mayhemDirectorStateLabel(state){return state==='PRESSURE'?'PRESSURE UP':state==='RIVAL RUSH'?'RIVAL RUSH':state==='RELIEF'?'BREATHING ROOM':state==='FINALE'?'FINAL PUSH':'BUILD';}
function mayhemDirectorStinger(state,intensity){if(state==='BUILD'||mayhemReplayPlaying)return;const now=performance.now();if(state!=='FINALE'&&now-mayhemDirectorStingerStamp<2200)return;mayhemDirectorStingerStamp=now;let el=$('mayhem-director-stinger');if(!el){el=document.createElement('div');el.id='mayhem-director-stinger';document.body.appendChild(el);}const act=mayhemActMeta(),copy=state==='RIVAL RUSH'?`${mayhemRivalName()} IS HUNTING YOU`:state==='RELIEF'?'DIRECTOR BACKS THE FIELD OFF':state==='FINALE'?'NO MORE RELIEF':`FIELD PRESSURE ${Math.round(intensity*100)}`;el.dataset.state=state;el.innerHTML=`<small>${act.short} · LIVE DIRECTOR</small><b>${mayhemDirectorStateLabel(state)}</b><span>${copy}</span>`;el.classList.remove('show');void el.offsetWidth;el.classList.add('show');setTimeout(()=>el?.classList.remove('show'),1450);}
function mayhemMenuPolish(def){if(!mayhemActive())return;const act=mayhemActMeta(),event=mayhemState.event||0;document.body.dataset.mayhemAct=String(act.id);$('mode-tag').textContent=`${act.kicker} · ${event+1}/${MAYHEM_EVENTS.length}`;$('mode-lead').textContent=`${def.goal} · ${act.stakes}`;$('arena-caption').innerHTML=`${act.short}<span>${def.name} · EVENT ${event+1}/${MAYHEM_EVENTS.length}</span>`;$('start').innerHTML=`${event===MAYHEM_EVENTS.length-1?'FINAL EVENT':`EVENT ${event+1}`} START <span>↗</span>`;}
function mayhemIntermissionPolish(box,event,final=false){const host=box?.querySelector(final?'.tour-final':'.tour-pit');if(!host)return;let card=host.querySelector('.tour-rival-status');if(!card){card=document.createElement('div');card.className='tour-rival-status';host.insertBefore(card,host.lastElementChild);}const rival=Math.round((mayhemState.rivalHull??1)*100),next=mayhemActMeta(Math.min(event+1,MAYHEM_EVENTS.length-1)),heat=Math.min(5,Math.max(1,mayhemState.rivalHeat||1));card.innerHTML=`<small>${final?'RIVALRY COMPLETE':`NEXT · ${next.short}`}</small><b>${mayhemRivalName()}</b><span>RIVAL HULL ${rival}% · HEAT ${heat}/5</span>`;}
function mayhemRivalMarkerHide(){const m=$('mayhem-rival-marker');if(m)m.classList.remove('visible');}
function mayhemRivalMarkerUpdate(){if(!mayhemActive()||mayhemReplayPlaying||mode!=='race'){mayhemRivalMarkerHide();return;}const r=mayhemRivalLive(),g=carMeshes[mayhemRivalId()]?.g;if(!r||!g||r.dead||r.finished){mayhemRivalMarkerHide();return;}let m=$('mayhem-rival-marker');if(!m){m=document.createElement('div');m.id='mayhem-rival-marker';m.innerHTML='<b>RIVAL</b><span></span><i><em></em></i>';document.body.appendChild(m);}g.getWorldPosition(mayhemRivalScreen);mayhemRivalScreen.y+=2.8;mayhemRivalView.copy(mayhemRivalScreen).applyMatrix4(camera.matrixWorldInverse);if(mayhemRivalView.z>=-.15){m.classList.remove('visible');return;}mayhemRivalScreen.project(camera);const edge=Math.abs(mayhemRivalScreen.x)>1||Math.abs(mayhemRivalScreen.y)>1,x=clamp((mayhemRivalScreen.x*.5+.5)*innerWidth,54,innerWidth-54),y=clamp((-mayhemRivalScreen.y*.5+.5)*innerHeight,92,innerHeight-86),rh=Math.round(clamp(r.hp/r.maxHP,0,1)*100);m.style.left=`${x}px`;m.style.top=`${y}px`;m.dataset.edge=edge?'1':'0';m.querySelector('span').textContent=`${mayhemRivalName()} · ${rh}%`;m.querySelector('em').style.width=`${rh}%`;m.classList.add('visible');}
function mayhemReplayStageStart(){document.body.classList.add('mayhem-replay-active');mayhemReplayBaseFov=Number(camera.fov)||60;let lb=$('mayhem-letterbox');if(!lb){lb=document.createElement('div');lb.id='mayhem-letterbox';lb.innerHTML='<i></i><i></i>';document.body.appendChild(lb);}mayhemRivalMarkerHide();}
function mayhemReplayStageStop(){document.body.classList.remove('mayhem-replay-active');const lb=$('mayhem-letterbox');if(lb)lb.remove();if(Number.isFinite(mayhemReplayBaseFov)&&camera.fov!==undefined){camera.fov=mayhemReplayBaseFov;camera.updateProjectionMatrix?.();}}
function mayhemReplayLerp3(a,b,t,out){return out.set(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t);}
function mayhemReplayCinematicCamera(a,b,t,progress){mayhemReplayLerp3(a.p,b.p,t,mayhemReplayP);mayhemReplayLerp3(a.r,b.r,t,mayhemReplayR);mayhemReplayMid.copy(mayhemReplayP).lerp(mayhemReplayR,.5);mayhemReplayQuat.set(a.p[3],a.p[4],a.p[5],a.p[6]).slerp(new THREE.Quaternion(b.p[3],b.p[4],b.p[5],b.p[6]),t);mayhemReplayForward.set(0,0,1).applyQuaternion(mayhemReplayQuat);mayhemReplayForward.y=0;if(mayhemReplayForward.lengthSq()<.01)mayhemReplayForward.set(0,0,1);else mayhemReplayForward.normalize();mayhemReplaySide.copy(mayhemReplayR).sub(mayhemReplayP);mayhemReplaySide.y=0;if(mayhemReplaySide.lengthSq()<.4)mayhemReplaySide.set(-mayhemReplayForward.z,0,mayhemReplayForward.x);else{mayhemReplaySide.normalize();mayhemReplaySide.set(-mayhemReplaySide.z,0,mayhemReplaySide.x);}let fov=56;if(progress<.34){mayhemReplayShot='CHASE';mayhemReplayDesired.copy(mayhemReplayP).addScaledVector(mayhemReplayForward,-8.6).addScaledVector(mayhemReplaySide,1.8);mayhemReplayDesired.y+=4.0;mayhemReplayTarget.copy(mayhemReplayP).addScaledVector(mayhemReplayForward,4.2);mayhemReplayTarget.y+=1.0;fov=58;}else if(progress<.68){mayhemReplayShot='RIVAL TWO-SHOT';mayhemReplayDesired.copy(mayhemReplayMid).addScaledVector(mayhemReplaySide,10.2);mayhemReplayDesired.y+=5.2;mayhemReplayTarget.copy(mayhemReplayMid);mayhemReplayTarget.y+=1.0;fov=52;}else{mayhemReplayShot='IMPACT CLOSE';mayhemReplayDesired.copy(mayhemReplayMid).addScaledVector(mayhemReplaySide,-7.1).addScaledVector(mayhemReplayForward,-2.6);mayhemReplayDesired.y+=3.4;mayhemReplayTarget.copy(mayhemReplayMid);mayhemReplayTarget.y+=.9;fov=48;}camera.position.lerp(mayhemReplayDesired,.24);camera.lookAt(mayhemReplayTarget);if(camera.fov!==undefined){camera.fov+=(fov-camera.fov)*.16;camera.updateProjectionMatrix?.();}}
'''
    s = one(s, replay_anchor, product_core, 'product core')

    director_curve = "let next='BUILD',intensity=.34;if(hull<.32){next='RELIEF';intensity=.18;}else if(progress>.78){next='FINALE';intensity=.88;}else if(r&&!r.dead&&distance<22){next='RIVAL RUSH';intensity=.72;}else if(progress>.18&&hull>.56){next='PRESSURE';intensity=.56;}"
    director_curve_new = "const eventIndex=Math.max(0,Math.min(MAYHEM_EVENTS.length-1,mayhemState.event||0)),base=mayhemTourPressure();let next='BUILD',intensity=base;if(hull<.29&&progress<.82){next='RELIEF';intensity=Math.max(.18,base-.30);}else if(eventIndex===MAYHEM_EVENTS.length-1&&progress>.12){next='FINALE';intensity=.97;}else if(progress>.78){next='FINALE';intensity=Math.min(.96,base+.18);}else if(r&&!r.dead&&distance<Math.max(17,27-eventIndex*.7)){next='RIVAL RUSH';intensity=Math.min(.92,base+.19);}else if(progress>.12||eventIndex>=3){next='PRESSURE';intensity=Math.min(.86,base+.08);}"
    s = one(s, director_curve, director_curve_new, 'nine-event Director curve')

    transition = "if(next!==mayhemDirectorLast){mayhemDirectorLast=next;mayhemState.rivalHeat=Math.max(1,Math.min(5,1+(mayhemState.event||0)+Math.round(intensity*2)));}"
    transition_new = "if(next!==mayhemDirectorLast){mayhemDirectorLast=next;mayhemState.rivalHeat=Math.max(1,Math.min(5,1+Math.floor((mayhemState.event||0)/2)+Math.round(intensity*2)));mayhemDirectorStinger(next,intensity);}"
    s = one(s, transition, transition_new, 'Director transition stinger')

    racing_push = "const push=(state==='FINALE'?3.2:state==='RIVAL RUSH'?2.35:state==='PRESSURE'?1.25:state==='BUILD'?.55:-.25)*dt;"
    racing_push_new = "const push=(state==='FINALE'?3.2:state==='RIVAL RUSH'?2.35:state==='PRESSURE'?1.25:state==='BUILD'?.55:-.25)*(.78+intensity*.48)*dt;"
    s = one(s, racing_push, racing_push_new, 'Director intensity affects racing pressure')

    director_hud = "hud.innerHTML=`<b>LIVE MAYHEM DIRECTOR · ${state}</b><span>${mayhemRivalName()} · ${rh}% · HEAT ${Math.round(intensity*100)}</span>`;"
    director_hud_new = "hud.dataset.state=state;hud.innerHTML=`<b>${mayhemDirectorStateLabel(state)}</b><span>${mayhemRivalName()} <em>${rh}%</em></span><i style=\"--heat:${Math.round(intensity*100)}%\"></i>`;"
    s = one(s, director_hud, director_hud_new, 'compact Director HUD')

    director_telemetry = "window.__breakCarsMayhemDirector={state,intensity,progress:mayhemDirectorProgress(),rivalId:mayhemRivalId(),rivalHull:r?clamp(r.hp/r.maxHP,0,1):0,playerHull:clamp(p.hp/p.maxHP,0,1)};"
    director_telemetry_new = "window.__breakCarsMayhemDirector={state,intensity,progress:mayhemDirectorProgress(),rivalId:mayhemRivalId(),rivalHull:r?clamp(r.hp/r.maxHP,0,1):0,playerHull:clamp(p.hp/p.maxHP,0,1),act:mayhemActMeta().short,eventPressure:mayhemTourPressure()};"
    s = one(s, director_telemetry, director_telemetry_new, 'Director act telemetry')

    badge = "function mayhemBadgeText(){if(!mayhemActive())return'';return`TOUR ${mayhemState.event+1}/${MAYHEM_EVENTS.length} · P${mayhemState.power||0} A${mayhemState.armor||0} H${mayhemState.handling||0} · R${mayhemRivalId()+1}`;}"
    badge_new = "function mayhemBadgeText(){if(!mayhemActive())return'';const a=mayhemActMeta();return`${a.short} · ${mayhemState.event+1}/${MAYHEM_EVENTS.length} · HULL ${Math.round((mayhemState.hull||1)*100)}% · RIVAL ${Math.round((mayhemState.rivalHull??1)*100)}%`; }"
    s = one(s, badge, badge_new, 'readable Tour badge')

    menu_tail = "resetWorld();}\nwindow.__breakCarsMayhemTour"
    menu_tail_new = "resetWorld();mayhemMenuPolish(def);}\nwindow.__breakCarsMayhemTour"
    s = one(s, menu_tail, menu_tail_new, 'menu act dramaturgy')

    final_hook = "box.querySelector('[data-tour-final=\"garage\"]').onclick=mayhemEndRun;mayhemReplayAttachButton(box);$('result-kicker').textContent='MAYHEM TOUR / COMPLETE';return;"
    final_hook_new = "box.querySelector('[data-tour-final=\"garage\"]').onclick=mayhemEndRun;mayhemReplayAttachButton(box);mayhemIntermissionPolish(box,event,true);$('result-kicker').textContent='MAYHEM TOUR / COMPLETE';return;"
    s = one(s, final_hook, final_hook_new, 'final rivalry status')

    pit_hook = "box.querySelectorAll('[data-tour-up]').forEach(b=>b.onclick=()=>mayhemChoose(b.dataset.tourUp));mayhemReplayAttachButton(box);$('result-kicker').textContent=`MAYHEM TOUR / EVENT ${event+1} CLEAR`;"
    pit_hook_new = "box.querySelectorAll('[data-tour-up]').forEach(b=>b.onclick=()=>mayhemChoose(b.dataset.tourUp));mayhemReplayAttachButton(box);mayhemIntermissionPolish(box,event,false);$('result-kicker').textContent=`MAYHEM TOUR / EVENT ${event+1} CLEAR`;"
    s = one(s, pit_hook, pit_hook_new, 'PIT rivalry status')

    replay_start = "function mayhemReplayStart(){if(mayhemReplayFrozen.length<2||mayhemReplayPlaying)return;mayhemReplayPlaying=true;mayhemReplayTime=0;$('modal').classList.add('hidden');"
    replay_start_new = "function mayhemReplayStart(){if(mayhemReplayFrozen.length<2||mayhemReplayPlaying)return;mayhemReplayPlaying=true;mayhemReplayTime=0;mayhemReplayStageStart();$('modal').classList.add('hidden');"
    s = one(s, replay_start, replay_start_new, 'replay cinema start')

    replay_stop = "function mayhemReplayStop(){mayhemReplayPlaying=false;const o=$('mayhem-replay-overlay');if(o)o.remove();$('modal').classList.remove('hidden');"
    replay_stop_new = "function mayhemReplayStop(){mayhemReplayPlaying=false;mayhemReplayStageStop();const o=$('mayhem-replay-overlay');if(o)o.remove();$('modal').classList.remove('hidden');"
    s = one(s, replay_stop, replay_stop_new, 'replay cinema stop')

    replay_camera = "mayhemReplaySetPose(camera,a.c,b.c,t);const o=$('mayhem-replay-overlay');"
    replay_camera_new = "mayhemReplayCinematicCamera(a,b,t,mayhemReplayTime/duration);const o=$('mayhem-replay-overlay');"
    s = one(s, replay_camera, replay_camera_new, 'cinematic replay camera')

    replay_caption = "o.querySelector('span').textContent=`DIRECTOR CUT · ${mayhemRivalName()} · ${state}`;"
    replay_caption_new = "o.querySelector('span').textContent=`${MAYHEM_EVENTS[mayhemState.event]?.name||'MAYHEM'} · ${mayhemRivalName()} · ${state} · ${mayhemReplayShot}`;"
    s = one(s, replay_caption, replay_caption_new, 'replay shot caption')

    replay_telemetry = "window.__breakCarsHighlightReplay={recording:false,frames:mayhemReplayFrozen.length,bestHeat:mayhemReplayBestHeat,playing:true,index:i};"
    replay_telemetry_new = "window.__breakCarsHighlightReplay={recording:false,frames:mayhemReplayFrozen.length,bestHeat:mayhemReplayBestHeat,playing:true,index:i,shot:mayhemReplayShot};"
    s = one(s, replay_telemetry, replay_telemetry_new, 'replay shot telemetry')

    render = "if(mayhemReplayPlaying)mayhemReplayApply(dt);else if(mode==='race'&&mayhemActive())mayhemReplayCapture(dt);renderer.render(scene,camera);"
    render_new = "if(mayhemReplayPlaying)mayhemReplayApply(dt);else if(mode==='race'&&mayhemActive())mayhemReplayCapture(dt);if(mode==='race'&&mayhemActive()&&!mayhemReplayPlaying)mayhemRivalMarkerUpdate();else mayhemRivalMarkerHide();renderer.render(scene,camera);"
    s = one(s, render, render_new, 'RIVAL marker render hook')

    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8 product polish: readable Director, persistent RIVAL marker, four-act arc, cinematic replay */
#tour-run-badge{top:max(57px,calc(env(safe-area-inset-top) + 49px));padding:4px 9px;font-size:9px;letter-spacing:.055em;background:#10141bea;border-color:#ff9b6c77;box-shadow:0 5px 18px #0008,0 0 18px #ff704022}
#mayhem-director{top:max(82px,calc(env(safe-area-inset-top) + 74px));left:50%;right:auto;transform:translateX(-50%);min-width:0;max-width:none;width:min(55vw,310px);padding:4px 8px 5px;border-radius:999px;background:#100e16e8;display:grid;grid-template-columns:auto 1fr;gap:1px 8px;align-items:center;text-align:left;white-space:nowrap;overflow:hidden}
#mayhem-director b,#mayhem-director span{display:block;margin:0;overflow:hidden;text-overflow:ellipsis}#mayhem-director b{font-size:8px;color:#ff8da8;letter-spacing:.09em}#mayhem-director span{font-size:7px;color:#dbe0e7;text-align:right}#mayhem-director span em{font-style:normal;color:#ffb4c6}#mayhem-director>i{grid-column:1/-1;display:block;height:2px;border-radius:2px;background:linear-gradient(90deg,#ff426d var(--heat),#ffffff16 var(--heat));box-shadow:0 0 8px #ff426d55}
#mayhem-director[data-state="RELIEF"]{border-color:#5dc9ff77}#mayhem-director[data-state="FINALE"]{border-color:#ffb14fbb;box-shadow:0 0 24px #ff683c33,0 6px 20px #0009}
#mayhem-director-stinger{position:fixed;z-index:39;left:50%;top:29%;transform:translate(-50%,-50%) scale(.94);min-width:min(65vw,360px);padding:10px 18px 9px;border-top:1px solid #ff5f8177;border-bottom:1px solid #ff5f8177;background:linear-gradient(90deg,transparent,#120b12e8 17%,#120b12e8 83%,transparent);opacity:0;text-align:center;pointer-events:none;color:#fff;filter:drop-shadow(0 8px 18px #000a)}#mayhem-director-stinger.show{animation:mayhemStinger 1.45s cubic-bezier(.2,.85,.2,1)}#mayhem-director-stinger small,#mayhem-director-stinger b,#mayhem-director-stinger span{display:block}#mayhem-director-stinger small{font:800 7px/1.1 system-ui;letter-spacing:.24em;color:#ff8ca8}#mayhem-director-stinger b{margin-top:3px;font:950 italic 22px/.95 system-ui;letter-spacing:.08em}#mayhem-director-stinger span{margin-top:4px;font:800 7px/1.1 system-ui;letter-spacing:.14em;color:#dce0e6}#mayhem-director-stinger[data-state="RELIEF"]{border-color:#67d6ff88}#mayhem-director-stinger[data-state="RELIEF"] small{color:#8de2ff}#mayhem-director-stinger[data-state="FINALE"]{border-color:#ffb14faa;background:linear-gradient(90deg,transparent,#251109ed 17%,#251109ed 83%,transparent)}#mayhem-director-stinger[data-state="FINALE"] small{color:#ffc06c}
#mayhem-rival-marker{position:fixed;z-index:24;transform:translate(-50%,-115%);min-width:90px;padding:3px 7px 4px;border:1px solid #ff4f72aa;border-radius:5px;background:#170b11e8;box-shadow:0 4px 15px #0009,0 0 16px #ff315544;color:#fff;text-align:center;pointer-events:none;opacity:0;transition:opacity .12s;font-family:system-ui}#mayhem-rival-marker.visible{opacity:1}#mayhem-rival-marker:after{content:"";position:absolute;left:50%;bottom:-8px;transform:translateX(-50%);border:4px solid transparent;border-top-color:#ff4f72aa}#mayhem-rival-marker b,#mayhem-rival-marker span{display:block}#mayhem-rival-marker b{font:950 7px/1 system-ui;letter-spacing:.2em;color:#ff6c8e}#mayhem-rival-marker span{margin-top:2px;font:800 7px/1 system-ui;white-space:nowrap}#mayhem-rival-marker i{display:block;height:2px;margin-top:4px;border-radius:2px;background:#ffffff1c;overflow:hidden}#mayhem-rival-marker i em{display:block;height:100%;background:linear-gradient(90deg,#ff3158,#ff9a72)}#mayhem-rival-marker[data-edge="1"]{border-color:#ffb14fbb;box-shadow:0 0 20px #ff8b3844}
.tour-rival-status{margin:8px 0;padding:7px 9px;border-left:2px solid #ff4f72;background:linear-gradient(90deg,#ff315516,transparent);text-align:left}.tour-rival-status small,.tour-rival-status b,.tour-rival-status span{display:block}.tour-rival-status small{font-size:7px;letter-spacing:.13em;color:#ff8ba7}.tour-rival-status b{margin-top:2px;font-size:11px;letter-spacing:.08em}.tour-rival-status span{margin-top:2px;font-size:7px;color:#d9dde4}
body[data-mayhem-act="2"] #tour-run-badge{border-color:#ff6d72aa}body[data-mayhem-act="3"] #tour-run-badge{border-color:#ffb14faa;box-shadow:0 0 20px #ff6d3630}body[data-mayhem-act="4"] #tour-run-badge{border-color:#ffd074cc;background:#21130cea;box-shadow:0 0 26px #ff7a3448}
body.mayhem-replay-active #hud,body.mayhem-replay-active #driving,body.mayhem-replay-active #tour-run-badge,body.mayhem-replay-active #mayhem-director,body.mayhem-replay-active #mayhem-rival-marker,body.mayhem-replay-active #toast,body.mayhem-replay-active #countdown{opacity:0!important;visibility:hidden!important}body.mayhem-replay-active #scene{filter:saturate(1.16) contrast(1.07) brightness(.94)}
#mayhem-letterbox{position:fixed;z-index:35;inset:0;pointer-events:none}#mayhem-letterbox i{position:absolute;left:0;width:100%;height:8.5vh;background:#050607;box-shadow:0 0 22px #000}#mayhem-letterbox i:first-child{top:0}#mayhem-letterbox i:last-child{bottom:0}
#mayhem-replay-overlay{z-index:41;top:max(8px,env(safe-area-inset-top));min-width:min(64vw,390px);padding:6px 16px 5px;border-width:0;background:linear-gradient(90deg,transparent,#09080bcc 14%,#09080bcc 86%,transparent);box-shadow:none}#mayhem-replay-overlay small{font-size:6px;color:#ff9aaf}#mayhem-replay-overlay b{font-size:13px}#mayhem-replay-overlay span{font-size:6px;letter-spacing:.09em}
@keyframes mayhemStinger{0%{opacity:0;transform:translate(-50%,-50%) scale(.92)}14%{opacity:1;transform:translate(-50%,-50%) scale(1.02)}68%{opacity:1;transform:translate(-50%,-50%) scale(1)}100%{opacity:0;transform:translate(-50%,-50%) scale(1.015)}}
@media(orientation:landscape) and (max-height:430px){#tour-run-badge{top:max(50px,calc(env(safe-area-inset-top) + 42px));font-size:8px}#mayhem-director{top:max(72px,calc(env(safe-area-inset-top) + 64px));width:min(53vw,290px);padding:3px 7px 4px}#mayhem-director b{font-size:7px}#mayhem-director span{font-size:6px}#mayhem-director-stinger{top:27%;padding:8px 15px 7px}#mayhem-director-stinger b{font-size:18px}#mayhem-rival-marker{min-width:82px;padding:3px 6px}#mayhem-letterbox i{height:9vh}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_product_v8(Path('_site'))
