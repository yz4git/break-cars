"""MAYHEM TOUR v8.5: turn the persistent RIVAL into a nine-event series.

v8.4 finishes the cinematic replay framing. This pass keeps gameplay physics,
course rules and Director pressure unchanged, but gives the run a clear sporting
rivalry: every event awards one head-to-head win, PIT/final panels show the
series score, and the ninth event resolves into RIVAL DEFEATED / RIVAL WINS.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8.5 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_rivalry_v85(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    old_default = "function mayhemDefault(){return{active:true,event:0,car:selection,hull:1,power:0,armor:0,handling:0,total:0,results:[],rivalId:1+((selection*3+4)%(COUNT-1)),rivalHull:1,rivalHeat:1};}"
    new_default = "function mayhemDefault(){return{active:true,event:0,car:selection,hull:1,power:0,armor:0,handling:0,total:0,results:[],rivalId:1+((selection*3+4)%(COUNT-1)),rivalHull:1,rivalHeat:1,rivalryPlayer:0,rivalryRival:0};}"
    s = one(s, old_default, new_default, 'series state')

    rival_live = "function mayhemRivalLive(){const id=mayhemRivalId();return id>0?world?.cars?.[id]||null:null;}"
    rivalry_core = rival_live + r'''
function mayhemRivalryScore(){return{player:Math.max(0,Number(mayhemState?.rivalryPlayer)||0),rival:Math.max(0,Number(mayhemState?.rivalryRival)||0)};}
function mayhemRivalryOutcome(p=world?.cars?.[0],r=mayhemRivalLive()){
 if(!p||!r)return'PLAYER';
 if(world?.mode==='racing'){
  const pp=racingPoints(p).total,rp=racingPoints(r).total;if(pp!==rp)return pp>rp?'PLAYER':'RIVAL';
  const order=trackPosition(world),pi=order.indexOf(p),ri=order.indexOf(r);if(pi!==ri)return pi>=0&&(ri<0||pi<ri)?'PLAYER':'RIVAL';
 }
 if(!!p.dead!==!!r.dead)return p.dead?'RIVAL':'PLAYER';
 const ph=clamp(p.hp/Math.max(1,p.maxHP),0,1),rh=clamp(r.hp/Math.max(1,r.maxHP),0,1);if(Math.abs(ph-rh)>.015)return ph>rh?'PLAYER':'RIVAL';
 return (p.score||0)>=(r.score||0)?'PLAYER':'RIVAL';
}
function mayhemRivalryLabel(){const s=mayhemRivalryScore();return s.player===s.rival?'SERIES TIED':s.player>s.rival?'YOU LEAD':'RIVAL LEADS';}
'''
    s = one(s, rival_live, rivalry_core, 'rivalry helpers')

    old_after = "mayhemState.hull=hull;const tourRival=mayhemRivalLive();mayhemState.rivalHull=tourRival?(tourRival.dead?.22:clamp(tourRival.hp/tourRival.maxHP,.22,1)):(mayhemState.rivalHull||1);mayhemState.rivalHeat=Math.min(5,Math.max(1,(mayhemState.rivalHeat||1)+(tourRival&&!tourRival.dead?1:0)));mayhemState.total=(mayhemState.total||0)+score;"
    new_after = "mayhemState.hull=hull;const tourRival=mayhemRivalLive();mayhemState.rivalHull=tourRival?(tourRival.dead?.22:clamp(tourRival.hp/tourRival.maxHP,.22,1)):(mayhemState.rivalHull||1);mayhemState.rivalHeat=Math.min(5,Math.max(1,(mayhemState.rivalHeat||1)+(tourRival&&!tourRival.dead?1:0)));const rivalryWinner=mayhemRivalryOutcome(p,tourRival);if(rivalryWinner==='PLAYER')mayhemState.rivalryPlayer=(mayhemState.rivalryPlayer||0)+1;else mayhemState.rivalryRival=(mayhemState.rivalryRival||0)+1;mayhemState.total=(mayhemState.total||0)+score;"
    s = one(s, old_after, new_after, 'award event rivalry win')

    old_result = "mayhemState.results[event]={course:MAYHEM_EVENTS[event].course,score,hull,rivalHull:mayhemState.rivalHull,director:mayhemDirectorState};"
    new_result = "mayhemState.results[event]={course:MAYHEM_EVENTS[event].course,score,hull,rivalHull:mayhemState.rivalHull,director:mayhemDirectorState,rivalResult:rivalryWinner,series:mayhemRivalryScore()};"
    s = one(s, old_result, new_result, 'record rivalry result')

    old_card = "card.innerHTML=`<small>${final?'RIVALRY COMPLETE':`NEXT · ${next.short}`}</small><b>${mayhemRivalName()}</b><span>RIVAL HULL ${rival}% · HEAT ${heat}/5</span>`;"
    new_card = "const series=mayhemRivalryScore(),leader=series.player===series.rival?'tied':series.player>series.rival?'player':'rival',verdict=series.player>series.rival?'RIVAL DEFEATED':'RIVAL WINS';card.dataset.series=leader;card.innerHTML=`<small>${final?verdict:`${mayhemRivalryLabel()} · NEXT · ${next.short}`}</small><b>${mayhemRivalName()}</b><span>SERIES ${series.player}-${series.rival} · RIVAL HULL ${rival}% · HEAT ${heat}/5</span>`;"
    s = one(s, old_card, new_card, 'series PIT and final card')

    old_expose = "window.__breakCarsMayhemTour=()=>mayhemActive()?{...mayhemState,tourLength:MAYHEM_EVENTS.length,eventDef:MAYHEM_EVENTS[mayhemState.event],worldMode:world?.mode,hp:world?.cars?.[0]?.hp,maxHP:world?.cars?.[0]?.maxHP,rival:{id:mayhemRivalId(),name:mayhemRivalName(),hp:mayhemRivalLive()?.hp??0,maxHP:mayhemRivalLive()?.maxHP??0},director:window.__breakCarsMayhemDirector||{state:mayhemDirectorState,intensity:mayhemDirectorIntensity}}:null;"
    new_expose = "window.__breakCarsMayhemTour=()=>mayhemActive()?{...mayhemState,tourLength:MAYHEM_EVENTS.length,series:mayhemRivalryScore(),eventDef:MAYHEM_EVENTS[mayhemState.event],worldMode:world?.mode,hp:world?.cars?.[0]?.hp,maxHP:world?.cars?.[0]?.maxHP,rival:{id:mayhemRivalId(),name:mayhemRivalName(),hp:mayhemRivalLive()?.hp??0,maxHP:mayhemRivalLive()?.maxHP??0},director:window.__breakCarsMayhemDirector||{state:mayhemDirectorState,intensity:mayhemDirectorIntensity}}:null;"
    s = one(s, old_expose, new_expose, 'series telemetry')
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.5: nine-event rivalry series */
.tour-rival-status[data-series="player"]{border-color:#68e0b077;box-shadow:inset 0 0 18px #38d89b12}
.tour-rival-status[data-series="rival"]{border-color:#ff5f7f77;box-shadow:inset 0 0 18px #ff315a12}
.tour-rival-status[data-series="tied"]{border-color:#ffc76a77}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_rivalry_v85(Path('_site'))
