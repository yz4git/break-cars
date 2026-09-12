"""MAYHEM TOUR v8.16: add compact act chapter stingers to TOUR RECAP.

The v8.15 recap is readable and visually distinct per event, but nine cards still
play as one continuous list. This presentation-only pass restores the four-act
Tour structure inside the recap with three brief chapter cards before events
4, 7 and 9. Total added runtime is under two seconds. No result data, physics,
AI, replay recording or progression is changed.
"""
from pathlib import Path


def apply_mayhem_recap_v816(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += r'''

/* MAYHEM TOUR v8.16 — compact act chapter stingers */
const MAYHEM_RECAP_V816_CHAPTER_MS=560;
const MAYHEM_RECAP_V816_CHAPTERS={
 3:{kicker:'ACT II',title:'VENDETTA',sub:'THE RIVALRY TIGHTENS'},
 6:{kicker:'ACT III',title:'REDLINE',sub:'NO ROOM LEFT'},
 8:{kicker:'FINAL ACT',title:'DOUBLE OR NOTHING',sub:'ONE LAST RUN'}
};
let mayhemRecapV816ChapterDone=-1;
function mayhemRecapV816ShowChapter(index,row){
 const meta=MAYHEM_RECAP_V816_CHAPTERS[index],el=mayhemRecapOverlay(),stage=el.querySelector('.mayhem-recap-stage');
 mayhemRecapIndex=index;mayhemRecapTrack(el,index);mayhemRecapV813Scene(el,'chapter',row.event.course);stage.dataset.kind='chapter';stage.dataset.chapter=String(index);stage.classList.remove('flash');void stage.offsetWidth;stage.classList.add('flash');stage.innerHTML=`<small>${meta.kicker}</small><b>${meta.title}</b><span>${meta.sub}</span><em>EVENT ${index+1}/9 · ${row.event.name}</em>`;mayhemRecapTelemetry('CHAPTER',index,{scene:'chapter',course:row.event.course,chapter:meta.kicker,title:meta.title,holdMs:MAYHEM_RECAP_V816_CHAPTER_MS});mayhemRecapV816ChapterDone=index;mayhemRecapTimer=setTimeout(()=>mayhemRecapEvent(index),MAYHEM_RECAP_V816_CHAPTER_MS);
}
mayhemRecapEvent=function(index){
 if(!mayhemRecapActive)return;const rows=mayhemRecapResults();if(index>=rows.length){mayhemRecapFinale();return;}const row=rows[index],chapter=MAYHEM_RECAP_V816_CHAPTERS[index];if(chapter&&mayhemRecapV816ChapterDone!==index){mayhemRecapV816ShowChapter(index,row);return;}const r=row.result,el=mayhemRecapOverlay(),stage=el.querySelector('.mayhem-recap-stage'),won=r.rivalResult!=='RIVAL',act=mayhemActMeta(row.index).short,series=r.series&&Number.isFinite(r.series.player)&&Number.isFinite(r.series.rival)?` · SERIES ${r.series.player}-${r.series.rival}`:'';mayhemRecapIndex=row.index;mayhemRecapTrack(el,row.index);mayhemRecapV813Scene(el,'event',row.event.course);stage.dataset.kind=won?'player':'rival';delete stage.dataset.chapter;stage.classList.remove('flash');void stage.offsetWidth;stage.classList.add('flash');stage.innerHTML=`<small>${act} · EVENT ${row.index+1}/9</small><b>${row.event.name}</b><span>${mayhemRecapEventOutcome(r)} · ${(Number(r.score)||0).toLocaleString()} PTS${series}</span><em>HULL ${Math.round(clamp(Number(r.hull)||0,0,1)*100)}% · ${String(r.director||'DIRECTOR').replace('RIVAL RUSH','RIVAL PRESSURE')}</em>`;mayhemRecapTelemetry('EVENT',row.index,{event:row.event.name,result:won?'PLAYER':'RIVAL',course:row.event.course,scene:'event',holdMs:MAYHEM_RECAP_V813_EVENT_MS});mayhemRecapTimer=setTimeout(()=>mayhemRecapEvent(index+1),MAYHEM_RECAP_V813_EVENT_MS);
};
window.__breakCarsMayhemV816=true;
'''
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.16: act chapter cards break the nine-event film into four memorable movements. */
.mayhem-recap-stage[data-kind="chapter"]{border-color:#efb55d42!important;background:linear-gradient(100deg,#0a0c10e8,#21170dd9 48%,#0a0c10e8)!important;box-shadow:0 0 34px #0008,inset 0 0 28px #efb55d0a!important}
.mayhem-recap-stage[data-kind="chapter"] small{color:#efb55d!important;letter-spacing:.34em!important}
.mayhem-recap-stage[data-kind="chapter"] b{font-size:clamp(31px,6.2vw,58px)!important;color:#fff!important;letter-spacing:.09em!important;text-shadow:0 0 24px #efb55d25!important}
.mayhem-recap-stage[data-kind="chapter"] span{color:#efc979!important;letter-spacing:.18em!important}
.mayhem-recap-stage[data-kind="chapter"] em{color:#9ba4b4!important;letter-spacing:.12em!important}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_recap_v816(Path('_site'))
