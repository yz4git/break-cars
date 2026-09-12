"""MAYHEM TOUR v8.19: carry RIVAL battle-flow history into PIT/results.

v8.18 makes each on-track rivalry leg readable. This pass records those CLASH
beats into the existing event result, then annotates the existing RIVAL card in
the PIT/final result. It adds no new permanent HUD and changes no AI/physics.
"""
from pathlib import Path


def apply_mayhem_rival_history_v819(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += r'''

/* MAYHEM TOUR v8.19 — RIVAL clash history in PIT/results */
const mayhemIntermissionPolishV819Base=mayhemIntermissionPolish;
function mayhemRivalHistoryLabelV819(clashes){return clashes>=4?'WARZONE':clashes>=2?'GRUDGE MATCH':clashes===1?'FIRST BLOOD':'CLEAN RUN';}
function mayhemRivalTourClashesV819(){return (mayhemState?.results||[]).reduce((sum,r)=>sum+Math.max(0,Number(r?.battleClashes)||0),0);}
mayhemIntermissionPolish=function(box,event,final=false){
 mayhemIntermissionPolishV819Base(box,event,final);const host=box?.querySelector(final?'.tour-final':'.tour-pit'),card=host?.querySelector('.tour-rival-status');if(!card)return;
 let stat=card.querySelector('.rival-flow-stat');if(!stat){stat=document.createElement('i');stat.className='rival-flow-stat';card.appendChild(stat);}
 const result=mayhemState?.results?.[event]||{},clashes=Math.max(0,Number(result.battleClashes)||0),total=mayhemRivalTourClashesV819();
 stat.dataset.level=clashes>=4?'high':clashes>=2?'mid':clashes===1?'low':'clean';
 stat.textContent=final?`TOUR CLASHES ${total} · ${total>=12?'ALL-OUT RIVALRY':total>=6?'HEATED RIVALRY':total>=2?'ACTIVE RIVALRY':'CLEAN SERIES'}`:`EVENT CLASHES ${clashes} · ${mayhemRivalHistoryLabelV819(clashes)}`;
};
const mayhemAfterEventV819Base=mayhemAfterEvent;
mayhemAfterEvent=function(){
 if(!mayhemActive()){mayhemAfterEventV819Base();return;}
 const event=Math.max(0,Math.min(MAYHEM_EVENTS.length-1,Number(mayhemState?.event)||0)),clashes=Math.max(0,Number(mayhemRivalBattleEventClashes)||0),encounters=Math.max(0,Number(mayhemRivalBattleEncounter)||0);
 mayhemAfterEventV819Base();mayhemState.results=Array.isArray(mayhemState.results)?mayhemState.results:[];const result=mayhemState.results[event]||(mayhemState.results[event]={course:MAYHEM_EVENTS[event]?.course||''});result.battleClashes=clashes;result.battleEncounters=encounters;result.rivalBattleLabel=mayhemRivalHistoryLabelV819(clashes);mayhemSave();
 const box=$('tour-intermission');if(box)mayhemIntermissionPolish(box,event,event>=MAYHEM_EVENTS.length-1);
};
window.__breakCarsMayhemRivalHistory=()=>mayhemActive()?{tourClashes:mayhemRivalTourClashesV819(),eventClashes:Math.max(0,Number(mayhemRivalBattleEventClashes)||0),results:(mayhemState.results||[]).map(r=>({course:r?.course||'',battleClashes:Number(r?.battleClashes)||0,rivalBattleLabel:r?.rivalBattleLabel||''}))}:null;
window.__breakCarsMayhemV819=true;
'''
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.19: compact event rivalry history inside the existing RIVAL card. */
.tour-rival-status .rival-flow-stat{display:block;margin-top:4px;padding-top:4px;border-top:1px solid #ffffff12;color:#9da8b7;font:900 7px/1 system-ui;font-style:normal;letter-spacing:.12em}
.tour-rival-status .rival-flow-stat[data-level="low"]{color:#e8c68b}.tour-rival-status .rival-flow-stat[data-level="mid"]{color:#ff9a78}.tour-rival-status .rival-flow-stat[data-level="high"]{color:#ff6683;text-shadow:0 0 12px #ff315a33}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_rival_history_v819(Path('_site'))
