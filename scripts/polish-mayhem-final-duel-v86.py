"""MAYHEM TOUR v8.6: make DOUBLE ORBIT a real FINAL DUEL.

The first eight events keep their existing physics, Director curve and RIVAL
behavior. Event nine gets a three-phase duel presentation plus bounded,
course-safe RIVAL pressure. The extra acceleration only happens when the rival
is already close to the player or needs a small forward catch-up, so this pass
does not rewrite DOUBLE ORBIT geometry or general racing physics.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8.6 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_final_duel_v86(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    rivalry_anchor = "function mayhemRivalryLabel(){const s=mayhemRivalryScore();return s.player===s.rival?'SERIES TIED':s.player>s.rival?'YOU LEAD':'RIVAL LEADS';}"
    final_core = rivalry_anchor + r'''
let mayhemFinalDuelPhase=0;
function mayhemFinalDuelActive(){return mayhemActive()&&(mayhemState?.event||0)===MAYHEM_EVENTS.length-1;}
function mayhemFinalDuelMeta(progress=mayhemDirectorProgress()){
 const phase=progress>=.73?3:progress>=.38?2:1,score=mayhemRivalryScore();
 return{phase,label:phase===3?'PHASE III · LAST STAND':phase===2?'PHASE II · RAM PRESSURE':'PHASE I · LOCK ON',score};
}
function mayhemFinalDuelStinger(meta){
 let el=$('mayhem-director-stinger');if(!el){el=document.createElement('div');el.id='mayhem-director-stinger';document.body.appendChild(el);}
 const copy=meta.phase===3?'ONE LAST PUSH · NO RELIEF':meta.phase===2?`${mayhemRivalName()} COMMITS TO CONTACT`:'SETTLE THE RIVALRY';
 el.dataset.state='FINALE';el.innerHTML=`<small>FINAL ACT · DOUBLE ORBIT</small><b>${meta.label}</b><span>${copy}</span>`;el.classList.remove('show');void el.offsetWidth;el.classList.add('show');setTimeout(()=>el?.classList.remove('show'),1600);
}
function mayhemFinalDuelTick(dt,p,r){
 if(!mayhemFinalDuelActive()||mode!=='race'){mayhemFinalDuelPhase=0;window.__breakCarsMayhemFinalDuel=null;return;}
 const progress=mayhemDirectorProgress(),meta=mayhemFinalDuelMeta(progress);
 if(meta.phase!==mayhemFinalDuelPhase){mayhemFinalDuelPhase=meta.phase;mayhemFinalDuelStinger(meta);}
 if(r&&!r.dead&&!r.finished&&p){
  const dx=p.x-r.x,dz=p.z-r.z,dist=Math.hypot(dx,dz)||1,fx=Math.sin(r.heading),fz=Math.cos(r.heading),along=dx*fx+dz*fz,side=dx*fz-dz*fx;
  const desperation=meta.score.rival<meta.score.player?1.12:1;
  if(dist<16&&Math.abs(side)<7&&along>-5&&along<12){const ram=(meta.phase===3?.72:meta.phase===2?.46:.25)*desperation*dt;r.vx+=dx/dist*ram;r.vz+=dz/dist*ram;}
  if(world.mode==='racing'&&dist>10&&dist<42){const catchup=(meta.phase===3?.82:meta.phase===2?.52:.24)*desperation*dt;r.vx+=fx*catchup;r.vz+=fz*catchup;}
 }
 window.__breakCarsMayhemFinalDuel={active:true,phase:meta.phase,label:meta.label,progress,series:meta.score,rivalId:mayhemRivalId(),rivalHull:r?clamp(r.hp/r.maxHP,0,1):0,playerHull:p?clamp(p.hp/p.maxHP,0,1):0};
}
'''
    s = one(s, rivalry_anchor, final_core, 'final duel core')

    director_hook = "const state=mayhemDirectorState,intensity=mayhemDirectorIntensity;if(r&&!r.dead&&!r.finished){"
    director_hook_new = "const state=mayhemDirectorState,intensity=mayhemDirectorIntensity;mayhemFinalDuelTick(dt,p,r);if(r&&!r.dead&&!r.finished){"
    s = one(s, director_hook, director_hook_new, 'final duel AI tick')

    hud_old = "hud.dataset.state=state;hud.innerHTML=`<b>${mayhemDirectorStateLabel(state)}</b><span>${mayhemRivalName()} <em>${rh}%</em></span><i style=\"--heat:${Math.round(intensity*100)}%\"></i>`;"
    hud_new = "const duel=mayhemFinalDuelActive()?mayhemFinalDuelMeta():null;hud.dataset.state=duel?'FINAL DUEL':state;hud.dataset.finalDuel=duel?'1':'0';hud.innerHTML=duel?`<b>FINAL DUEL · ${duel.label}</b><span>${mayhemRivalName()} <em>${rh}%</em> · SERIES ${duel.score.player}-${duel.score.rival}</span><i style=\"--heat:${Math.round(intensity*100)}%\"></i>`:`<b>${mayhemDirectorStateLabel(state)}</b><span>${mayhemRivalName()} <em>${rh}%</em></span><i style=\"--heat:${Math.round(intensity*100)}%\"></i>`;"
    s = one(s, hud_old, hud_new, 'final duel HUD')

    card_old = "const series=mayhemRivalryScore(),leader=series.player===series.rival?'tied':series.player>series.rival?'player':'rival',verdict=series.player>series.rival?'RIVAL DEFEATED':'RIVAL WINS';card.dataset.series=leader;card.innerHTML=`<small>${final?verdict:`${mayhemRivalryLabel()} · NEXT · ${next.short}`}</small><b>${mayhemRivalName()}</b><span>SERIES ${series.player}-${series.rival} · RIVAL HULL ${rival}% · HEAT ${heat}/5</span>`;"
    card_new = "const series=mayhemRivalryScore(),leader=series.player===series.rival?'tied':series.player>series.rival?'player':'rival',verdict=series.player>series.rival?'RIVAL DEFEATED':'RIVAL WINS',last=mayhemState.results?.[event]?.rivalResult||'';card.dataset.series=leader;card.dataset.finalDuel=final?'1':'0';card.innerHTML=`<small>${final?`${verdict} · FINAL DUEL ${last==='PLAYER'?'WON':'LOST'}`:`${mayhemRivalryLabel()} · NEXT · ${next.short}`}</small><b>${mayhemRivalName()}</b><span>${final?`SERIES ${series.player}-${series.rival} · ${series.player>series.rival?'TOUR CHAMPION':'RIVAL TAKES THE TOUR'}`:`SERIES ${series.player}-${series.rival} · RIVAL HULL ${rival}% · HEAT ${heat}/5`}</span>`;"
    s = one(s, card_old, card_new, 'final duel result card')

    expose_old = "window.__breakCarsMayhemTour=()=>mayhemActive()?{...mayhemState,tourLength:MAYHEM_EVENTS.length,series:mayhemRivalryScore(),eventDef:MAYHEM_EVENTS[mayhemState.event],worldMode:world?.mode,hp:world?.cars?.[0]?.hp,maxHP:world?.cars?.[0]?.maxHP,rival:{id:mayhemRivalId(),name:mayhemRivalName(),hp:mayhemRivalLive()?.hp??0,maxHP:mayhemRivalLive()?.maxHP??0},director:window.__breakCarsMayhemDirector||{state:mayhemDirectorState,intensity:mayhemDirectorIntensity}}:null;"
    expose_new = "window.__breakCarsMayhemTour=()=>mayhemActive()?{...mayhemState,tourLength:MAYHEM_EVENTS.length,series:mayhemRivalryScore(),finalDuel:window.__breakCarsMayhemFinalDuel||null,eventDef:MAYHEM_EVENTS[mayhemState.event],worldMode:world?.mode,hp:world?.cars?.[0]?.hp,maxHP:world?.cars?.[0]?.maxHP,rival:{id:mayhemRivalId(),name:mayhemRivalName(),hp:mayhemRivalLive()?.hp??0,maxHP:mayhemRivalLive()?.maxHP??0},director:window.__breakCarsMayhemDirector||{state:mayhemDirectorState,intensity:mayhemDirectorIntensity}}:null;"
    s = one(s, expose_old, expose_new, 'final duel telemetry')

    start_old = "$('start').innerHTML=`${event===MAYHEM_EVENTS.length-1?'FINAL EVENT':`EVENT ${event+1}`} START <span>↗</span>`;"
    start_new = "$('start').innerHTML=event===MAYHEM_EVENTS.length-1?'SETTLE THE RIVALRY <span>↗</span>':`EVENT ${event+1} START <span>↗</span>`;"
    s = one(s, start_old, start_new, 'final event CTA')

    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.6: DOUBLE ORBIT FINAL DUEL */
#mayhem-director[data-final-duel="1"]{border-color:#ffcf6a99;background:linear-gradient(180deg,#23130ff2,#130f18f2);box-shadow:0 5px 26px #000a,0 0 22px #ff9c3822}
#mayhem-director[data-final-duel="1"] b{color:#ffd37a;letter-spacing:.11em}
#mayhem-director[data-final-duel="1"] span{color:#fff0d0}
.tour-rival-status[data-final-duel="1"]{border-color:#ffc75f99;box-shadow:inset 0 0 26px #ff9b2818,0 0 20px #0007}
.tour-rival-status[data-final-duel="1"] small{color:#ffd37a;font-weight:900;letter-spacing:.09em}
body[data-mayhem-act="4"] #tour-run-badge{border-color:#ffc75f77;box-shadow:0 4px 18px #0008,0 0 18px #ff9b2820}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_final_duel_v86(Path('_site'))
