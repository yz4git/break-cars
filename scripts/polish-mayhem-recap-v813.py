"""MAYHEM TOUR v8.13: make the results-driven TOUR RECAP read like a film.

The v8.12 visual review showed that the recap information is strong, but the
640 ms event cards cut too quickly on an iPhone and every chapter sits over the
same DOUBLE ORBIT background. We intentionally do not fake old 3D replays on
the wrong course. Instead this presentation-only pass gives each real result a
course-coded kinetic title backdrop and a readable editorial cadence.
"""
from pathlib import Path


def apply_mayhem_recap_v813(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += r'''

/* MAYHEM TOUR v8.13 — cinematic, readable results film */
const MAYHEM_RECAP_V813_OPENING_MS=2400;
const MAYHEM_RECAP_V813_EVENT_MS=980;
const MAYHEM_RECAP_V813_FINAL_MS=2600;
function mayhemRecapV813Scene(el,scene,course=''){
 if(!el)return;let backdrop=el.querySelector('.mayhem-recap-backdrop');
 if(!backdrop){backdrop=document.createElement('div');backdrop.className='mayhem-recap-backdrop';el.insertBefore(backdrop,el.firstChild);}
 const key=course||scene;el.dataset.scene=scene;el.dataset.course=key;backdrop.dataset.course=key;
 backdrop.classList.remove('cut');void backdrop.offsetWidth;backdrop.classList.add('cut');
}
mayhemRecapOpening=function(){
 if(!mayhemRecapActive)return;const el=mayhemRecapOverlay(),stats=mayhemRecapStats(),stage=el.querySelector('.mayhem-recap-stage');mayhemRecapIndex=-1;mayhemRecapTrack(el,-1);mayhemRecapV813Scene(el,'opening','opening');stage.dataset.kind='opening';stage.innerHTML=`<small>THE COMPLETE RUN</small><b>NINE EVENTS. ONE RIVAL.</b><span>YOU ${stats.playerWins} — ${stats.rivalWins} ${mayhemRivalName()}</span><em>${stats.total.toLocaleString()} TOUR POINTS</em>`;mayhemRecapTelemetry('OPENING',-1,{scene:'opening',holdMs:MAYHEM_RECAP_V813_OPENING_MS});mayhemRecapTimer=setTimeout(()=>mayhemRecapEvent(0),MAYHEM_RECAP_V813_OPENING_MS);
};
mayhemRecapEvent=function(index){
 if(!mayhemRecapActive)return;const rows=mayhemRecapResults();if(index>=rows.length){mayhemRecapFinale();return;}const row=rows[index],r=row.result,el=mayhemRecapOverlay(),stage=el.querySelector('.mayhem-recap-stage'),won=r.rivalResult!=='RIVAL',act=mayhemActMeta(row.index).short,series=r.series&&Number.isFinite(r.series.player)&&Number.isFinite(r.series.rival)?` · SERIES ${r.series.player}-${r.series.rival}`:'';mayhemRecapIndex=row.index;mayhemRecapTrack(el,row.index);mayhemRecapV813Scene(el,'event',row.event.course);stage.dataset.kind=won?'player':'rival';stage.classList.remove('flash');void stage.offsetWidth;stage.classList.add('flash');stage.innerHTML=`<small>${act} · EVENT ${row.index+1}/9</small><b>${row.event.name}</b><span>${mayhemRecapEventOutcome(r)} · ${(Number(r.score)||0).toLocaleString()} PTS${series}</span><em>HULL ${Math.round(clamp(Number(r.hull)||0,0,1)*100)}% · ${String(r.director||'DIRECTOR').replace('RIVAL RUSH','RIVAL PRESSURE')}</em>`;mayhemRecapTelemetry('EVENT',row.index,{event:row.event.name,result:won?'PLAYER':'RIVAL',course:row.event.course,scene:'event',holdMs:MAYHEM_RECAP_V813_EVENT_MS});mayhemRecapTimer=setTimeout(()=>mayhemRecapEvent(index+1),MAYHEM_RECAP_V813_EVENT_MS);
};
mayhemRecapFinale=function(){
 if(!mayhemRecapActive)return;const el=mayhemRecapOverlay(),stats=mayhemRecapStats(),stage=el.querySelector('.mayhem-recap-stage'),best=stats.best?.event?.name||'—',toughest=stats.toughest?.event?.name||'—';mayhemRecapIndex=MAYHEM_EVENTS.length;mayhemRecapTrack(el,MAYHEM_EVENTS.length);mayhemRecapV813Scene(el,'finale','finale');stage.dataset.kind=stats.champion?'champion':'rival-final';stage.classList.remove('flash');void stage.offsetWidth;stage.classList.add('flash');stage.innerHTML=`<small>FINAL RECORD · ${stats.playerWins}-${stats.rivalWins}</small><b>${stats.champion?'MAYHEM TOUR CHAMPION':'RIVAL WINS THE TOUR'}</b><span>${stats.total.toLocaleString()} PTS · FINAL HULL ${Math.round(stats.finalHull*100)}%</span><em>BEST · ${best} · TOUGHEST WIN · ${toughest}</em>`;mayhemRecapTelemetry('FINAL',MAYHEM_EVENTS.length,{scene:'finale',holdMs:MAYHEM_RECAP_V813_FINAL_MS});mayhemRecapTimer=setTimeout(()=>mayhemRecapStop(true),MAYHEM_RECAP_V813_FINAL_MS);
};
window.__breakCarsMayhemV813=true;
'''
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.13: course-coded kinetic title cards without faking old 3D footage. */
#mayhem-tour-recap>.mayhem-recap-head,#mayhem-tour-recap>.mayhem-recap-stage,#mayhem-tour-recap>.mayhem-recap-track{position:relative;z-index:1}
.mayhem-recap-backdrop{position:absolute;z-index:0;inset:14% 0;overflow:hidden;pointer-events:none;opacity:.36;--recap-a:236,171,81;--recap-b:255,101,116;background:radial-gradient(circle at 28% 45%,rgba(var(--recap-a),.34),transparent 28%),radial-gradient(circle at 72% 58%,rgba(var(--recap-b),.2),transparent 33%),linear-gradient(108deg,transparent 0 34%,rgba(var(--recap-a),.1) 34% 37%,transparent 37% 62%,rgba(var(--recap-b),.09) 62% 65%,transparent 65% 100%);transform:scale(1.02)}
.mayhem-recap-backdrop:after{content:"";position:absolute;inset:-24% -10%;background:repeating-linear-gradient(112deg,transparent 0 12%,rgba(255,255,255,.035) 12% 12.7%,transparent 12.7% 23%);transform:translateX(-5%);animation:mayhemRecapDrift 3.8s linear infinite}
.mayhem-recap-backdrop.cut{animation:mayhemRecapCut .52s cubic-bezier(.2,.75,.25,1) both}
#mayhem-tour-recap[data-course="classic"] .mayhem-recap-backdrop{--recap-a:255,151,71;--recap-b:248,215,122}
#mayhem-tour-recap[data-course="crater-crown"] .mayhem-recap-backdrop{--recap-a:255,126,160;--recap-b:210,126,255}
#mayhem-tour-recap[data-course="maelstrom-pit"] .mayhem-recap-backdrop{--recap-a:162,118,255;--recap-b:105,191,255}
#mayhem-tour-recap[data-course="hunt-classic"] .mayhem-recap-backdrop{--recap-a:255,92,82;--recap-b:255,178,79}
#mayhem-tour-recap[data-course="cross-fire"] .mayhem-recap-backdrop{--recap-a:104,224,188;--recap-b:92,175,255}
#mayhem-tour-recap[data-course="tidal-foundry"] .mayhem-recap-backdrop{--recap-a:84,204,255;--recap-b:91,244,218}
#mayhem-tour-recap[data-course="rampage-3d"] .mayhem-recap-backdrop{--recap-a:255,197,77;--recap-b:255,114,70}
#mayhem-tour-recap[data-course="sky-forge"] .mayhem-recap-backdrop{--recap-a:100,177,255;--recap-b:172,220,255}
#mayhem-tour-recap[data-course="double-orbit"] .mayhem-recap-backdrop{--recap-a:229,121,255;--recap-b:255,113,170}
#mayhem-tour-recap[data-course="opening"] .mayhem-recap-backdrop{--recap-a:239,181,93;--recap-b:255,255,255;opacity:.27}
#mayhem-tour-recap[data-course="finale"] .mayhem-recap-backdrop{--recap-a:255,112,143;--recap-b:239,181,93;opacity:.42}
@keyframes mayhemRecapCut{0%{opacity:.05;transform:scale(1.08) translateX(2.5%)}32%{opacity:.5}100%{opacity:.36;transform:scale(1.02) translateX(0)}}
@keyframes mayhemRecapDrift{from{transform:translateX(-6%)}to{transform:translateX(6%)}}
@media (prefers-reduced-motion:reduce){.mayhem-recap-backdrop,.mayhem-recap-backdrop:after{animation:none!important}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_recap_v813(Path('_site'))
