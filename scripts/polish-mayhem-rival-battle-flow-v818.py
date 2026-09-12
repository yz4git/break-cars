"""MAYHEM TOUR v8.18: turn RIVAL pressure into readable fight beats.

v8.17 keeps the persistent rival close enough to matter. This pass gives that
pressure a rhythm: INBOUND -> LOCKED -> CLASH -> BREAKAWAY -> REMATCH. A clash
is counted only when proximity enters CONTACT, avoiding repeated counting from
old event-log entries. Racing briefly clears the rival's battle target during
BREAKAWAY, then deliberately reacquires the player for REMATCH. Arena modes keep
their authored combat AI and only receive presentation/state timing.

RELIEF and event-nine FINAL DUEL remain authoritative. No teleporting, damage
multipliers, geometry edits, player slowdown, or extra final-duel force is added.
"""
from pathlib import Path


def apply_mayhem_rival_battle_flow_v818(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += r'''

/* MAYHEM TOUR v8.18 — RIVAL BATTLE FLOW */
const mayhemDirectorTickV818Base=mayhemDirectorTick;
let mayhemRivalBattlePhase='SEARCH',mayhemRivalBattlePrevEngagement='SEARCH',mayhemRivalBattleUntil=0,mayhemRivalBattleLastClash=-99,mayhemRivalBattleEvent=-1,mayhemRivalBattleEventClashes=0,mayhemRivalBattleSeriesClashes=0,mayhemRivalBattleEncounter=0,mayhemRivalBattleCueTimer=0;
function mayhemRivalBattleCueV818(kicker,title,sub=''){
 let el=$('mayhem-rival-flow');if(!el){el=document.createElement('div');el.id='mayhem-rival-flow';document.body.appendChild(el);}
 el.innerHTML=`<small>${kicker}</small><b>${title}</b>${sub?`<span>${sub}</span>`:''}`;el.dataset.phase=mayhemRivalBattlePhase;el.classList.remove('show');void el.offsetWidth;el.classList.add('show');clearTimeout(mayhemRivalBattleCueTimer);mayhemRivalBattleCueTimer=setTimeout(()=>el?.classList.remove('show'),820);
}
function mayhemRivalBattleSetV818(next,now,cue=true){
 if(next===mayhemRivalBattlePhase)return false;mayhemRivalBattlePhase=next;document.body.dataset.mayhemRivalFlow=next.toLowerCase().replaceAll(' ','-');
 if(!cue)return true;
 if(next==='INBOUND')mayhemRivalBattleCueV818('RIVAL','INBOUND',mayhemRivalName());
 else if(next==='LOCKED')mayhemRivalBattleCueV818('RIVAL','LOCKED','CONTACT WINDOW');
 else if(next==='CLASH')mayhemRivalBattleCueV818(`CLASH ${mayhemRivalBattleEncounter}`,'RIVAL CONTACT','BREAK · RESET · RE-ENGAGE');
 else if(next==='BREAKAWAY')mayhemRivalBattleCueV818('RIVAL','BREAKAWAY','SPACE OPENS');
 else if(next==='REMATCH')mayhemRivalBattleCueV818('RIVAL','REMATCH','TARGET REACQUIRED');
 return true;
}
function mayhemRivalBattleTelemetryV818(p,r,extra={}){
 // v8.17 originally sampled the shared event array. Synchronize its public
 // contact counter to edge-triggered CLASH entries so stale events cannot grow it.
 mayhemRivalEngagementContacts=mayhemRivalBattleSeriesClashes;
 const payload={phase:mayhemRivalBattlePhase,encounter:mayhemRivalBattleEncounter,eventClashes:mayhemRivalBattleEventClashes,seriesClashes:mayhemRivalBattleSeriesClashes,event:mayhemState?.event??-1,distance:mayhemRivalEngagementDistance,engagement:mayhemRivalEngagementState,rivalId:mayhemRivalId(),...extra};
 window.__breakCarsMayhemRivalBattleFlow=payload;
 if(window.__breakCarsMayhemRivalEngagement)window.__breakCarsMayhemRivalEngagement.contacts=mayhemRivalBattleSeriesClashes;
 return payload;
}
function mayhemRivalBattleResetV818(eventIndex){
 mayhemRivalBattleEvent=eventIndex;mayhemRivalBattlePhase='SEARCH';mayhemRivalBattlePrevEngagement='SEARCH';mayhemRivalBattleUntil=0;mayhemRivalBattleLastClash=-99;mayhemRivalBattleEventClashes=0;mayhemRivalBattleEncounter=0;document.body.dataset.mayhemRivalFlow='search';const el=$('mayhem-rival-flow');if(el)el.classList.remove('show');
}
function mayhemRivalBattleTickV818(dt){
 if(!mayhemActive()||mode!=='race'||!world?.cars?.[0])return;
 const p=world.cars[0],r=mayhemRivalLive(),eventIndex=mayhemState?.event??-1,now=Number(world.time)||0;if(eventIndex!==mayhemRivalBattleEvent)mayhemRivalBattleResetV818(eventIndex);
 if(!r||r.dead||r.finished){mayhemRivalBattleSetV818('OUT',now,false);mayhemRivalBattleTelemetryV818(p,r);mayhemRivalBattlePrevEngagement=mayhemRivalEngagementState;return;}
 if(mayhemFinalDuelActive()){mayhemRivalBattleSetV818('FINAL DUEL',now,false);mayhemRivalBattleTelemetryV818(p,r,{finalDuel:true});mayhemRivalBattlePrevEngagement=mayhemRivalEngagementState;return;}
 if(mayhemDirectorState==='RELIEF'||mayhemRivalEngagementState==='RELIEF'){mayhemRivalBattleSetV818('RELIEF',now,false);mayhemRivalBattleTelemetryV818(p,r,{relief:true});mayhemRivalBattlePrevEngagement=mayhemRivalEngagementState;return;}
 const engagement=mayhemRivalEngagementState,enteredContact=engagement==='CONTACT'&&mayhemRivalBattlePrevEngagement!=='CONTACT'&&now-mayhemRivalBattleLastClash>.72;
 if(enteredContact){mayhemRivalBattleLastClash=now;mayhemRivalBattleEventClashes++;mayhemRivalBattleSeriesClashes++;mayhemRivalBattleEncounter++;mayhemRivalBattleUntil=now+.48;mayhemRivalBattleSetV818('CLASH',now,true);}
 else if(mayhemRivalBattlePhase==='CLASH'&&now>=mayhemRivalBattleUntil){mayhemRivalBattleUntil=now+.78;mayhemRivalBattleSetV818('BREAKAWAY',now,true);}
 else if(mayhemRivalBattlePhase==='BREAKAWAY'&&(now>=mayhemRivalBattleUntil||mayhemRivalEngagementDistance>14)){mayhemRivalBattleUntil=now+1.35;mayhemRivalBattleSetV818('REMATCH',now,true);}
 else if(mayhemRivalBattlePhase==='REMATCH'&&now>=mayhemRivalBattleUntil){mayhemRivalBattleSetV818(engagement==='LOCK'?'LOCKED':engagement==='HUNT'||engagement==='REJOIN'?'INBOUND':'SEARCH',now,false);}
 else if(!['CLASH','BREAKAWAY','REMATCH'].includes(mayhemRivalBattlePhase)){
  const next=engagement==='LOCK'?'LOCKED':engagement==='HUNT'||engagement==='REJOIN'?'INBOUND':engagement==='CONTACT'?'LOCKED':'SEARCH';
  if(next!==mayhemRivalBattlePhase){const announce=(next==='LOCKED'&&mayhemRivalBattlePhase==='INBOUND')||(next==='INBOUND'&&mayhemRivalBattlePhase==='SEARCH');mayhemRivalBattleSetV818(next,now,announce);}
 }
 // Racing gets a real separation beat instead of endless bumper-lock. The base
 // v8.17 catch-up stays intact; only battle-target ownership pauses briefly.
 if(world.mode==='racing'){
  if(mayhemRivalBattlePhase==='BREAKAWAY'){r.battleTarget=-1;r.battleTimer=Math.max(Number(r.battleTimer)||0,.42);}
  else if(mayhemRivalBattlePhase==='REMATCH'){const gap=(p.raceDistance||0)-(r.raceDistance||0);if(gap>-8&&gap<28){r.battleTarget=0;r.battleTimer=Math.min(Number(r.battleTimer)||.12,.06);}}
 }
 mayhemRivalBattleTelemetryV818(p,r,{until:Math.max(0,mayhemRivalBattleUntil-now)});mayhemRivalBattlePrevEngagement=engagement;
}
mayhemDirectorTick=function(dt){mayhemDirectorTickV818Base(dt);mayhemRivalBattleTickV818(dt);};
window.__breakCarsMayhemV818=true;
'''
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.18: one compact transient battle-flow cue; no permanent HUD expansion. */
#mayhem-rival-flow{position:fixed;z-index:24;top:max(111px,calc(env(safe-area-inset-top) + 103px));left:50%;transform:translate(-50%,-8px) scale(.96);min-width:150px;max-width:min(72vw,320px);padding:5px 11px;border:1px solid #ff6a7866;border-radius:999px;background:#120e14e8;box-shadow:0 6px 22px #0009,0 0 18px #ff315a16;color:#fff;text-align:center;pointer-events:none;opacity:0;transition:opacity .13s ease,transform .16s ease;font:800 8px/1.05 system-ui;letter-spacing:.08em;white-space:nowrap}
#mayhem-rival-flow.show{opacity:1;transform:translate(-50%,0) scale(1)}#mayhem-rival-flow small,#mayhem-rival-flow b,#mayhem-rival-flow span{display:inline-block}#mayhem-rival-flow small{margin-right:6px;color:#ff8193;font-size:7px}#mayhem-rival-flow b{font-size:9px;letter-spacing:.12em}#mayhem-rival-flow span{margin-left:7px;color:#bfc7d3;font-size:7px}
#mayhem-rival-flow[data-phase="CLASH"]{border-color:#ffd16f99;background:#21130fe8;box-shadow:0 6px 22px #0009,0 0 24px #ffb03725}#mayhem-rival-flow[data-phase="CLASH"] b{color:#ffe2a1}
body[data-mayhem-rival-flow="clash"] #mayhem-rival-marker{filter:drop-shadow(0 0 12px #ffd16faa)}body[data-mayhem-rival-flow="breakaway"] #mayhem-rival-marker{opacity:.62}body[data-mayhem-rival-flow="rematch"] #mayhem-rival-marker{filter:drop-shadow(0 0 10px #ff496baa)}
body.mayhem-tour-result #mayhem-rival-flow,body.mayhem-replay-active #mayhem-rival-flow,body.mayhem-recap-active #mayhem-rival-flow,body.mayhem-showdown-ending-active #mayhem-rival-flow{display:none!important}
@media(orientation:landscape) and (max-height:430px){#mayhem-rival-flow{top:max(94px,calc(env(safe-area-inset-top) + 86px));padding:4px 9px}#mayhem-rival-flow span{display:none}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_rival_battle_flow_v818(Path('_site'))
