"""MAYHEM TOUR v5: persistent RIVAL + LIVE MAYHEM DIRECTOR.

A single rival car now follows the player through the whole Tour and carries its
hull damage between events. The live director reads player hull, event progress
and rival proximity, then moves through BUILD / PRESSURE / RIVAL RUSH / RELIEF /
FINALE beats. It changes *behavior* rather than course geometry: the rival keeps
pressure on the player in arena modes and receives a bounded forward push in
racing modes, while low player hull deliberately backs the pressure off.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v5 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_rival_director_v5(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    default = "function mayhemDefault(){return{active:true,event:0,car:selection,hull:1,power:0,armor:0,handling:0,total:0,results:[]};}"
    default_new = "function mayhemDefault(){return{active:true,event:0,car:selection,hull:1,power:0,armor:0,handling:0,total:0,results:[],rivalId:1+((selection*3+4)%(COUNT-1)),rivalHull:1,rivalHeat:1};}"
    s = one(s, default, default_new, 'persistent rival state')

    state_anchor = "let mayhemState=mayhemLoad();"
    director = state_anchor + r'''
const MAYHEM_RIVAL_NAMES=['JACKAL','RAZOR','VEX','MAMMOTH','HEX','BOLT','GRIM','FANG','NOVA','BRUTE','VIPER'];
let mayhemDirectorClock=0,mayhemDirectorState='BUILD',mayhemDirectorIntensity=.34,mayhemDirectorLast='';
function mayhemRivalId(){if(!mayhemState)return-1;const fallback=1+(((mayhemState.car||0)*3+4)%(COUNT-1)),id=Number(mayhemState.rivalId);if(Number.isInteger(id)&&id>0&&id<COUNT)return id;mayhemState.rivalId=fallback;return fallback;}
function mayhemRivalName(){const id=mayhemRivalId();return id>0?`${MAYHEM_RIVAL_NAMES[(id-1)%MAYHEM_RIVAL_NAMES.length]} #${String(id+1).padStart(2,'0')}`:'RIVAL';}
function mayhemRivalLive(){const id=mayhemRivalId();return id>0?world?.cars?.[id]||null:null;}
function applyMayhemRival(){if(!mayhemActive()||!world?.cars?.length)return;const id=mayhemRivalId(),r=world.cars[id];if(!r)return;const h=clamp(Number(mayhemState.rivalHull??1),.22,1);r.tourRival=true;r.hp=Math.max(1,Math.round(r.maxHP*h));for(const k of Object.keys(r.parts||{}))r.parts[k]=Math.max(34,Math.round(45+h*55));world.mayhemRivalId=id;world.mayhemIntensity=.34;world.mayhemDirectorState='BUILD';}
function mayhemDirectorReset(){mayhemDirectorClock=0;mayhemDirectorState='BUILD';mayhemDirectorIntensity=.34;mayhemDirectorLast='';if(world){world.mayhemIntensity=.34;world.mayhemDirectorState='BUILD';world.mayhemRivalId=mayhemRivalId();}}
function mayhemDirectorProgress(){if(!world)return 0;const end=world.mode==='racing'?(world.endAt||DURATION):DURATION;return clamp(world.time/Math.max(1,end),0,1);}
function mayhemDirectorTick(dt){if(!mayhemActive()||mode!=='race'||!world?.cars?.[0])return;mayhemDirectorClock-=dt;const p=world.cars[0],r=mayhemRivalLive();if(mayhemDirectorClock<=0){mayhemDirectorClock=.28;const hull=clamp(p.hp/p.maxHP,0,1),progress=mayhemDirectorProgress(),distance=r&&!r.dead?Math.hypot(r.x-p.x,r.z-p.z):999;let next='BUILD',intensity=.34;if(hull<.32){next='RELIEF';intensity=.18;}else if(progress>.78){next='FINALE';intensity=.88;}else if(r&&!r.dead&&distance<22){next='RIVAL RUSH';intensity=.72;}else if(progress>.18&&hull>.56){next='PRESSURE';intensity=.56;}mayhemDirectorState=next;mayhemDirectorIntensity=intensity;world.mayhemIntensity=intensity;world.mayhemDirectorState=next;world.mayhemRivalId=mayhemRivalId();if(next!==mayhemDirectorLast){mayhemDirectorLast=next;mayhemState.rivalHeat=Math.max(1,Math.min(5,1+(mayhemState.event||0)+Math.round(intensity*2)));}}
 const state=mayhemDirectorState,intensity=mayhemDirectorIntensity;if(r&&!r.dead&&!r.finished){if(world.mode!=='racing'){if(state!=='RELIEF'){r.target=0;r.aiTimer=.65;}else if(r.target===0)r.aiTimer=0;}else{const push=(state==='FINALE'?3.2:state==='RIVAL RUSH'?2.35:state==='PRESSURE'?1.25:state==='BUILD'?.55:-.25)*dt;if(push>0){r.vx+=Math.sin(r.heading)*push;r.vz+=Math.cos(r.heading)*push;}else{r.vx*=Math.exp(-.12*dt);r.vz*=Math.exp(-.12*dt);}}}
 if(world.mode!=='racing'&&state!=='RELIEF'){let pressure=Math.floor(intensity*3.2);for(const c of world.cars){if(pressure<=0)break;if(c.id===0||c.id===mayhemRivalId()||c.dead)continue;c.target=0;c.aiTimer=Math.max(c.aiTimer,.24);pressure--;}}
 let hud=$('mayhem-director');if(!hud){hud=document.createElement('div');hud.id='mayhem-director';document.body.appendChild(hud);}const rh=r?Math.round(clamp(r.hp/r.maxHP,0,1)*100):0;hud.innerHTML=`<b>LIVE MAYHEM DIRECTOR · ${state}</b><span>${mayhemRivalName()} · ${rh}% · HEAT ${Math.round(intensity*100)}</span>`;window.__breakCarsMayhemDirector={state,intensity,progress:mayhemDirectorProgress(),rivalId:mayhemRivalId(),rivalHull:r?clamp(r.hp/r.maxHP,0,1):0,playerHull:clamp(p.hp/p.maxHP,0,1)};}
'''
    s = one(s, state_anchor, director, 'director core')

    reset = "for(const c of world.cars)carMeshes.push(buildCar(c));applyMayhemLoadout();resultShown=false;clearParticles();clearBlasts();skidCount=0;skidMesh.count=0;}"
    reset_new = "for(const c of world.cars)carMeshes.push(buildCar(c));applyMayhemLoadout();applyMayhemRival();mayhemDirectorReset();resultShown=false;clearParticles();clearBlasts();skidCount=0;skidMesh.count=0;}"
    s = one(s, reset, reset_new, 'rival load after world reset')

    after_hull = "mayhemState.hull=hull;mayhemState.total=(mayhemState.total||0)+score;"
    after_hull_new = "mayhemState.hull=hull;const tourRival=mayhemRivalLive();mayhemState.rivalHull=tourRival?(tourRival.dead?.22:clamp(tourRival.hp/tourRival.maxHP,.22,1)):(mayhemState.rivalHull||1);mayhemState.rivalHeat=Math.min(5,Math.max(1,(mayhemState.rivalHeat||1)+(tourRival&&!tourRival.dead?1:0)));mayhemState.total=(mayhemState.total||0)+score;"
    s = one(s, after_hull, after_hull_new, 'carry rival hull')

    result = "mayhemState.results[event]={course:MAYHEM_EVENTS[event].course,score,hull};"
    result_new = "mayhemState.results[event]={course:MAYHEM_EVENTS[event].course,score,hull,rivalHull:mayhemState.rivalHull,director:mayhemDirectorState};"
    s = one(s, result, result_new, 'record rival/director result')

    badge = "function mayhemBadgeText(){if(!mayhemActive())return'';return`TOUR ${mayhemState.event+1}/3 · P${mayhemState.power||0} A${mayhemState.armor||0} H${mayhemState.handling||0}`;}"
    badge_new = "function mayhemBadgeText(){if(!mayhemActive())return'';return`TOUR ${mayhemState.event+1}/3 · P${mayhemState.power||0} A${mayhemState.armor||0} H${mayhemState.handling||0} · R${mayhemRivalId()+1}`;}"
    s = one(s, badge, badge_new, 'rival tour badge')

    entry = "entry.innerHTML='<b>MAYHEM TOUR</b><small>3 EVENT RUN · DAMAGE CARRIES</small>';"
    entry_new = "entry.innerHTML='<b>MAYHEM TOUR</b><small>3 EVENT RUN · RIVAL · LIVE DIRECTOR</small>';"
    s = one(s, entry, entry_new, 'menu feature label')

    hint = "if(hint)hint.textContent=`HULL ${Math.round((mayhemState.hull||1)*100)}% · POWER ${mayhemState.power||0} · ARMOR ${mayhemState.armor||0} · HANDLING ${mayhemState.handling||0} · TOTAL ${(mayhemState.total||0).toLocaleString()} PTS`;"
    hint_new = "if(hint)hint.textContent=`HULL ${Math.round((mayhemState.hull||1)*100)}% · ${mayhemRivalName()} ${Math.round((mayhemState.rivalHull??1)*100)}% · POWER ${mayhemState.power||0} · ARMOR ${mayhemState.armor||0} · HANDLING ${mayhemState.handling||0} · TOTAL ${(mayhemState.total||0).toLocaleString()} PTS`;"
    s = one(s, hint, hint_new, 'menu rival status')

    expose = "window.__breakCarsMayhemTour=()=>mayhemActive()?{...mayhemState,eventDef:MAYHEM_EVENTS[mayhemState.event],worldMode:world?.mode,hp:world?.cars?.[0]?.hp,maxHP:world?.cars?.[0]?.maxHP}:null;"
    expose_new = "window.__breakCarsMayhemTour=()=>mayhemActive()?{...mayhemState,eventDef:MAYHEM_EVENTS[mayhemState.event],worldMode:world?.mode,hp:world?.cars?.[0]?.hp,maxHP:world?.cars?.[0]?.maxHP,rival:{id:mayhemRivalId(),name:mayhemRivalName(),hp:mayhemRivalLive()?.hp??0,maxHP:mayhemRivalLive()?.maxHP??0},director:window.__breakCarsMayhemDirector||{state:mayhemDirectorState,intensity:mayhemDirectorIntensity}}:null;"
    s = one(s, expose, expose_new, 'runtime telemetry')

    frame = "}if(mode!=='paused'){if(toastTime>0){"
    frame_new = "}if(mode==='race'&&mayhemActive())mayhemDirectorTick(dt);if(mode!=='paused'){if(toastTime>0){"
    s = one(s, frame, frame_new, 'director frame tick')
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
#mayhem-director{position:fixed;z-index:19;top:max(84px,calc(env(safe-area-inset-top) + 76px));left:50%;transform:translateX(-50%);min-width:250px;max-width:min(82vw,430px);padding:5px 9px;border:1px solid #ff416c66;border-radius:7px;background:#130f18e8;box-shadow:0 5px 22px #0008;color:#ffd6e0;text-align:center;pointer-events:none;font:800 9px/1.12 system-ui;letter-spacing:.07em;white-space:nowrap}
#mayhem-director b,#mayhem-director span{display:block}#mayhem-director b{color:#ff7797;font-size:9px}#mayhem-director span{margin-top:2px;color:#d8dce3;font-size:8px}
body.mayhem-tour-result #mayhem-director{display:none!important}
@media(orientation:landscape) and (max-height:430px){#mayhem-director{top:max(73px,calc(env(safe-area-inset-top) + 65px));padding:4px 8px;min-width:230px}#mayhem-director b{font-size:8px}#mayhem-director span{font-size:7px}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_rival_director_v5(Path('_site'))
