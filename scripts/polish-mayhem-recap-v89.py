"""MAYHEM TOUR v8.9: post-tour highlight recap and career-style results.

The ninth event already ends with a real FINAL SHOWDOWN replay. Replaying old
3D clips against DOUBLE ORBIT would fake their original course backgrounds, so
this pass keeps that authentic final replay and adds a separate results-driven
TOUR RECAP film: all nine actual event results, series score, best event,
toughest win, total points and final hull are cut into a compact cinematic
sequence. Physics, AI, course geometry and replay recording are untouched.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8.9 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_recap_v89(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    final_hook = "mayhemIntermissionPolish(box,event,true);mayhemShowdownScheduleEndingReplay();$('result-kicker').textContent='MAYHEM TOUR / COMPLETE';return;"
    final_hook_new = "mayhemIntermissionPolish(box,event,true);mayhemRecapAttach(box);mayhemShowdownScheduleEndingReplay();$('result-kicker').textContent='MAYHEM TOUR / COMPLETE';return;"
    s = one(s, final_hook, final_hook_new, 'attach recap to final results')

    s += r'''

/* MAYHEM TOUR v8.9 — nine-event TOUR RECAP */
let mayhemRecapTimer=0,mayhemRecapIndex=-1,mayhemRecapActive=false,mayhemRecapCompleted=false;
function mayhemRecapResults(){
 const src=Array.isArray(mayhemState?.results)?mayhemState.results:[];
 return MAYHEM_EVENTS.map((event,index)=>({event,index,result:src[index]||null})).filter(x=>x.result);
}
function mayhemRecapStats(){
 const rows=mayhemRecapResults(),series=mayhemRivalryScore();let best=null,toughest=null;
 for(const row of rows){
  const r=row.result,score=Number(r.score)||0,hull=clamp(Number(r.hull)||0,0,1);
  if(!best||score>(Number(best.result.score)||0))best=row;
  if(r.rivalResult==='PLAYER'&&(!toughest||hull<clamp(Number(toughest.result.hull)||0,0,1)))toughest=row;
 }
 return{events:rows.length,playerWins:series.player,rivalWins:series.rival,champion:series.player>series.rival,total:Number(mayhemState?.total)||0,finalHull:clamp(Number(mayhemState?.hull)||0,0,1),best,toughest};
}
function mayhemRecapEventOutcome(result){return result?.rivalResult==='RIVAL'?'RIVAL WIN':'PLAYER WIN';}
function mayhemRecapTelemetry(stage,index=-1,extra={}){
 const stats=mayhemRecapStats();window.__breakCarsMayhemRecap={active:mayhemRecapActive,stage,index,completed:mayhemRecapCompleted,stats:{events:stats.events,playerWins:stats.playerWins,rivalWins:stats.rivalWins,champion:stats.champion,total:stats.total,finalHull:stats.finalHull,best:stats.best?.index??-1,toughest:stats.toughest?.index??-1},...extra};
}
function mayhemRecapAttach(box){
 const host=box?.querySelector('.tour-final');if(!host||host.querySelector('.tour-recap-panel'))return;const stats=mayhemRecapStats(),rows=mayhemRecapResults(),panel=document.createElement('section');panel.className='tour-recap-panel';panel.dataset.champion=stats.champion?'1':'0';
 const timeline=MAYHEM_EVENTS.map((event,index)=>{const r=mayhemState?.results?.[index],won=r?.rivalResult!=='RIVAL';return`<i data-result="${r?(won?'player':'rival'):'none'}" title="${event.name}"><b>${index+1}</b><small>${r?(won?'P':'R'):'·'}</small></i>`;}).join('');
 const best=stats.best?`${stats.best.event.name} · ${(Number(stats.best.result.score)||0).toLocaleString()} PTS`:'—',toughest=stats.toughest?`${stats.toughest.event.name} · ${Math.round(clamp(Number(stats.toughest.result.hull)||0,0,1)*100)}% HULL`:'—';
 panel.innerHTML=`<div class="tour-recap-title"><small>9 EVENT RECORD</small><b>TOUR RECAP</b><span>${stats.champion?'CHAMPION RUN':'RIVAL SERIES'} · ${stats.playerWins}-${stats.rivalWins}</span></div><div class="tour-recap-metrics"><span><small>TOTAL</small><b>${stats.total.toLocaleString()}</b></span><span><small>FINAL HULL</small><b>${Math.round(stats.finalHull*100)}%</b></span><span><small>BEST EVENT</small><b>${best}</b></span><span><small>TOUGHEST WIN</small><b>${toughest}</b></span></div><div class="tour-recap-timeline">${timeline}</div><button type="button" data-tour-recap-film><b>PLAY TOUR RECAP</b><small>9 EVENT HIGHLIGHT FILM</small></button>`;
 const controls=host.lastElementChild;host.insertBefore(panel,controls);panel.querySelector('[data-tour-recap-film]').onclick=mayhemRecapPlay;mayhemRecapTelemetry('READY',-1,{rows:rows.length});
}
function mayhemRecapOverlay(){
 let el=$('mayhem-tour-recap');if(el)return el;el=document.createElement('div');el.id='mayhem-tour-recap';el.innerHTML='<button type="button" data-mayhem-recap-close>SKIP</button><div class="mayhem-recap-head"><small>MAYHEM TOUR</small><b>TOUR RECAP</b><span>9 EVENTS · ONE RIVAL</span></div><div class="mayhem-recap-stage"></div><div class="mayhem-recap-track"></div>';document.body.appendChild(el);el.querySelector('[data-mayhem-recap-close]').onclick=()=>mayhemRecapStop(false);return el;
}
function mayhemRecapTrack(el,active){
 const results=mayhemState?.results||[];el.querySelector('.mayhem-recap-track').innerHTML=MAYHEM_EVENTS.map((event,index)=>{const r=results[index],kind=r?.rivalResult==='RIVAL'?'rival':'player',state=index===active?'active':index<active?'past':'future';return`<i data-result="${r?kind:'none'}" data-state="${state}"><b>${index+1}</b><small>${r?(kind==='player'?'P':'R'):'·'}</small></i>`;}).join('');
}
function mayhemRecapOpening(){
 if(!mayhemRecapActive)return;const el=mayhemRecapOverlay(),stats=mayhemRecapStats(),stage=el.querySelector('.mayhem-recap-stage');mayhemRecapIndex=-1;mayhemRecapTrack(el,-1);stage.dataset.kind='opening';stage.innerHTML=`<small>THE COMPLETE RUN</small><b>NINE EVENTS. ONE RIVAL.</b><span>YOU ${stats.playerWins} — ${stats.rivalWins} ${mayhemRivalName()}</span><em>${stats.total.toLocaleString()} TOUR POINTS</em>`;mayhemRecapTelemetry('OPENING',-1);mayhemRecapTimer=setTimeout(()=>mayhemRecapEvent(0),780);
}
function mayhemRecapEvent(index){
 if(!mayhemRecapActive)return;const rows=mayhemRecapResults();if(index>=rows.length){mayhemRecapFinale();return;}const row=rows[index],r=row.result,el=mayhemRecapOverlay(),stage=el.querySelector('.mayhem-recap-stage'),won=r.rivalResult!=='RIVAL',act=mayhemActMeta(row.index).short;mayhemRecapIndex=row.index;mayhemRecapTrack(el,row.index);stage.dataset.kind=won?'player':'rival';stage.classList.remove('flash');void stage.offsetWidth;stage.classList.add('flash');stage.innerHTML=`<small>${act} · EVENT ${row.index+1}/9</small><b>${row.event.name}</b><span>${mayhemRecapEventOutcome(r)} · ${(Number(r.score)||0).toLocaleString()} PTS</span><em>HULL ${Math.round(clamp(Number(r.hull)||0,0,1)*100)}% · ${String(r.director||'DIRECTOR').replace('RIVAL RUSH','RIVAL PRESSURE')}</em>`;mayhemRecapTelemetry('EVENT',row.index,{event:row.event.name,result:won?'PLAYER':'RIVAL'});mayhemRecapTimer=setTimeout(()=>mayhemRecapEvent(index+1),640);
}
function mayhemRecapFinale(){
 if(!mayhemRecapActive)return;const el=mayhemRecapOverlay(),stats=mayhemRecapStats(),stage=el.querySelector('.mayhem-recap-stage'),best=stats.best?.event?.name||'—',toughest=stats.toughest?.event?.name||'—';mayhemRecapIndex=MAYHEM_EVENTS.length;mayhemRecapTrack(el,MAYHEM_EVENTS.length);stage.dataset.kind=stats.champion?'champion':'rival-final';stage.classList.remove('flash');void stage.offsetWidth;stage.classList.add('flash');stage.innerHTML=`<small>FINAL RECORD · ${stats.playerWins}-${stats.rivalWins}</small><b>${stats.champion?'MAYHEM TOUR CHAMPION':'RIVAL WINS THE TOUR'}</b><span>${stats.total.toLocaleString()} PTS · FINAL HULL ${Math.round(stats.finalHull*100)}%</span><em>BEST · ${best} · TOUGHEST WIN · ${toughest}</em>`;mayhemRecapTelemetry('FINAL',MAYHEM_EVENTS.length);mayhemRecapTimer=setTimeout(()=>mayhemRecapStop(true),1900);
}
function mayhemRecapPlay(){
 if(mayhemRecapActive||mayhemReplayPlaying||mayhemRecapResults().length<1)return;mayhemRecapActive=true;mayhemRecapCompleted=false;clearTimeout(mayhemRecapTimer);const ending=$('mayhem-showdown-ending');if(ending)ending.remove();$('modal')?.classList.add('hidden');document.body.classList.add('mayhem-recap-active');const old=$('mayhem-tour-recap');if(old)old.remove();mayhemRecapOverlay();mayhemRecapOpening();
}
function mayhemRecapStop(completed=false){
 clearTimeout(mayhemRecapTimer);mayhemRecapTimer=0;mayhemRecapActive=false;mayhemRecapCompleted=!!completed;document.body.classList.remove('mayhem-recap-active');const el=$('mayhem-tour-recap');if(el)el.remove();$('modal')?.classList.remove('hidden');mayhemRecapTelemetry(completed?'COMPLETE':'IDLE',mayhemRecapIndex);
}
window.__breakCarsMayhemV89=true;mayhemRecapTelemetry('IDLE');
'''
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.9: complete nine-event results + TOUR RECAP film */
.tour-recap-panel{margin:8px 0 2px;padding:8px;border:1px solid #ffffff20;background:linear-gradient(135deg,#11151dd9,#171018d9);box-shadow:inset 0 0 22px #0005}.tour-recap-title{display:grid;grid-template-columns:1fr auto;align-items:end;gap:2px 8px;text-align:left}.tour-recap-title small{font:850 6px/1 system-ui;letter-spacing:.18em;color:#aab4c7}.tour-recap-title b{grid-row:2;font:950 italic 13px/1 system-ui;letter-spacing:.1em}.tour-recap-title span{grid-column:2;grid-row:1/3;align-self:center;font:900 8px/1 system-ui;letter-spacing:.08em;color:#ffd27b}.tour-recap-metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4px;margin-top:7px}.tour-recap-metrics>span{min-width:0;padding:5px 6px;background:#070a0e99;border-left:2px solid #ffffff1f;text-align:left}.tour-recap-metrics small,.tour-recap-metrics b{display:block}.tour-recap-metrics small{font:800 5px/1 system-ui;letter-spacing:.14em;color:#8e9aad}.tour-recap-metrics b{margin-top:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font:900 7px/1 system-ui;color:#f2f4f8}.tour-recap-timeline,.mayhem-recap-track{display:grid;grid-template-columns:repeat(9,1fr);gap:3px;margin-top:7px}.tour-recap-timeline i,.mayhem-recap-track i{display:block;padding:3px 0 2px;border:1px solid #ffffff18;background:#090c11;text-align:center;font-style:normal}.tour-recap-timeline b,.tour-recap-timeline small,.mayhem-recap-track b,.mayhem-recap-track small{display:block}.tour-recap-timeline b,.mayhem-recap-track b{font:900 6px/1 system-ui;color:#aab3c1}.tour-recap-timeline small,.mayhem-recap-track small{margin-top:2px;font:950 7px/1 system-ui}.tour-recap-timeline i[data-result="player"],.mayhem-recap-track i[data-result="player"]{border-color:#68ddb75a}.tour-recap-timeline i[data-result="player"] small,.mayhem-recap-track i[data-result="player"] small{color:#72e0bc}.tour-recap-timeline i[data-result="rival"],.mayhem-recap-track i[data-result="rival"]{border-color:#ff64745c}.tour-recap-timeline i[data-result="rival"] small,.mayhem-recap-track i[data-result="rival"] small{color:#ff7d8a}.tour-recap-panel [data-tour-recap-film]{width:100%;margin-top:7px;padding:7px 9px;border:1px solid #ffd36a66;background:linear-gradient(90deg,#24160d,#17111a,#24160d);box-shadow:0 7px 18px #0006}.tour-recap-panel [data-tour-recap-film] b,.tour-recap-panel [data-tour-recap-film] small{display:block}.tour-recap-panel [data-tour-recap-film] b{font:950 italic 9px/1 system-ui;letter-spacing:.1em}.tour-recap-panel [data-tour-recap-film] small{margin-top:3px;font:800 5px/1 system-ui;letter-spacing:.15em;color:#e5b862}
#mayhem-tour-recap{position:fixed;z-index:64;inset:0;padding:max(24px,env(safe-area-inset-top)) max(26px,calc(env(safe-area-inset-right) + 18px)) max(22px,env(safe-area-inset-bottom)) max(26px,calc(env(safe-area-inset-left) + 18px));display:flex;flex-direction:column;justify-content:center;background:radial-gradient(circle at 50% 44%,#321d1ed9 0,#10131bea 52%,#06080bf5 100%);color:#fff;font-family:system-ui;text-align:center;overflow:hidden}#mayhem-tour-recap:before,#mayhem-tour-recap:after{content:"";position:absolute;left:0;right:0;height:14%;background:#030405;z-index:-1}#mayhem-tour-recap:before{top:0}#mayhem-tour-recap:after{bottom:0}#mayhem-tour-recap>[data-mayhem-recap-close]{position:absolute;z-index:2;top:max(10px,env(safe-area-inset-top));right:max(12px,env(safe-area-inset-right));padding:5px 9px;border:1px solid #ffffff2e;background:#0b0e13d9;color:#c9d0db;font:850 6px/1 system-ui;letter-spacing:.14em}.mayhem-recap-head small,.mayhem-recap-head b,.mayhem-recap-head span,.mayhem-recap-stage small,.mayhem-recap-stage b,.mayhem-recap-stage span,.mayhem-recap-stage em{display:block}.mayhem-recap-head small{font:900 6px/1 system-ui;letter-spacing:.3em;color:#efb55d}.mayhem-recap-head b{margin-top:4px;font:950 italic 14px/1 system-ui;letter-spacing:.14em}.mayhem-recap-head span{margin-top:4px;font:800 6px/1 system-ui;letter-spacing:.12em;color:#aeb7c5}.mayhem-recap-stage{width:min(86vw,620px);min-height:112px;margin:16px auto 0;padding:14px 18px 12px;display:flex;flex-direction:column;justify-content:center;border-top:1px solid #ffffff34;border-bottom:1px solid #ffffff24;background:linear-gradient(90deg,transparent,#080b10d9 10%,#12151bdf 50%,#080b10d9 90%,transparent);text-shadow:0 2px 10px #000}.mayhem-recap-stage.flash{animation:mayhemRecapCut .24s ease-out}.mayhem-recap-stage small{font:900 6px/1 system-ui;letter-spacing:.22em;color:#e2b568}.mayhem-recap-stage b{margin-top:6px;font:950 italic clamp(20px,5vw,34px)/.94 system-ui;letter-spacing:.06em}.mayhem-recap-stage span{margin-top:8px;font:900 9px/1 system-ui;letter-spacing:.11em;color:#f0f2f6}.mayhem-recap-stage em{margin-top:7px;font:800 6px/1 system-ui;letter-spacing:.1em;color:#9da7b7;font-style:normal}.mayhem-recap-stage[data-kind="player"] b,.mayhem-recap-stage[data-kind="champion"] b{color:#b9ffe8}.mayhem-recap-stage[data-kind="rival"] b,.mayhem-recap-stage[data-kind="rival-final"] b{color:#ffbec7}.mayhem-recap-track{width:min(82vw,560px);margin:14px auto 0}.mayhem-recap-track i{padding:5px 0 4px;opacity:.38;transform:scale(.93);transition:.18s ease}.mayhem-recap-track i[data-state="past"]{opacity:.68}.mayhem-recap-track i[data-state="active"]{opacity:1;transform:scale(1.08);box-shadow:0 0 18px #ffffff16}body.mayhem-recap-active #hud,body.mayhem-recap-active #driving,body.mayhem-recap-active #mayhem-director,body.mayhem-recap-active #mayhem-rival-marker,body.mayhem-recap-active #tour-run-badge,body.mayhem-recap-active #mayhem-showdown-ending,body.mayhem-recap-active #mayhem-showdown-last-orbit{display:none!important}@keyframes mayhemRecapCut{0%{opacity:.1;transform:scale(.96)}100%{opacity:1;transform:scale(1)}}
@media(orientation:landscape) and (max-height:430px){.tour-recap-panel{padding:6px;margin-top:5px}.tour-recap-metrics{gap:3px;margin-top:5px}.tour-recap-metrics>span{padding:4px 5px}.tour-recap-timeline{margin-top:5px}.tour-recap-panel [data-tour-recap-film]{margin-top:5px;padding:5px 8px}#mayhem-tour-recap{padding-top:max(12px,env(safe-area-inset-top));padding-bottom:max(10px,env(safe-area-inset-bottom))}.mayhem-recap-head b{font-size:12px}.mayhem-recap-stage{min-height:86px;margin-top:9px;padding:9px 14px}.mayhem-recap-stage b{font-size:23px}.mayhem-recap-stage span{margin-top:5px;font-size:8px}.mayhem-recap-stage em{margin-top:5px}.mayhem-recap-track{margin-top:8px}.mayhem-recap-track i{padding:3px 0 2px}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_recap_v89(Path('_site'))
