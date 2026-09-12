"""MAYHEM TOUR v8.15: remove redundant finale recap copy.

The v8.14 iPhone review showed the stronger recap identities working, but the
final card can repeat the same event twice when the best-scoring event is also
the toughest win (for example: BEST RAMPAGE 3D / TOUGHEST WIN RAMPAGE 3D).
This presentation-only pass collapses that case into one PEAK EVENT line with
score and hull context. Split best/toughest events remain distinct.
"""
from pathlib import Path


def apply_mayhem_recap_v815(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += r'''

/* MAYHEM TOUR v8.15 — concise, non-redundant recap finale */
function mayhemRecapV815Summary(stats){
 const best=stats.best,toughest=stats.toughest;
 if(best&&toughest&&best.index===toughest.index){
  const score=Number(best.result?.score)||0,hull=Math.round(clamp(Number(best.result?.hull)||0,0,1)*100);
  return{kind:'peak',text:`PEAK EVENT · ${best.event.name} · ${score.toLocaleString()} PTS · ${hull}% HULL`,best:best.index,toughest:toughest.index};
 }
 const bestText=best?`${best.event.name} · ${(Number(best.result?.score)||0).toLocaleString()} PTS`:'—';
 const toughText=toughest?`${toughest.event.name} · ${Math.round(clamp(Number(toughest.result?.hull)||0,0,1)*100)}% HULL`:'—';
 return{kind:'split',text:`BEST · ${bestText} · TOUGHEST WIN · ${toughText}`,best:best?.index??-1,toughest:toughest?.index??-1};
}
mayhemRecapFinale=function(){
 if(!mayhemRecapActive)return;const el=mayhemRecapOverlay(),stats=mayhemRecapStats(),stage=el.querySelector('.mayhem-recap-stage'),summary=mayhemRecapV815Summary(stats);mayhemRecapIndex=MAYHEM_EVENTS.length;mayhemRecapTrack(el,MAYHEM_EVENTS.length);mayhemRecapV813Scene(el,'finale','finale');stage.dataset.kind=stats.champion?'champion':'rival-final';stage.dataset.summary=summary.kind;stage.classList.remove('flash');void stage.offsetWidth;stage.classList.add('flash');stage.innerHTML=`<small>FINAL RECORD · ${stats.playerWins}-${stats.rivalWins}</small><b>${stats.champion?'MAYHEM TOUR CHAMPION':'RIVAL WINS THE TOUR'}</b><span>${stats.total.toLocaleString()} PTS · FINAL HULL ${Math.round(stats.finalHull*100)}%</span><em>${summary.text}</em>`;mayhemRecapTelemetry('FINAL',MAYHEM_EVENTS.length,{scene:'finale',holdMs:MAYHEM_RECAP_V813_FINAL_MS,summary:summary.kind,best:summary.best,toughest:summary.toughest});mayhemRecapTimer=setTimeout(()=>mayhemRecapStop(true),MAYHEM_RECAP_V813_FINAL_MS);
};
window.__breakCarsMayhemV815=true;
'''
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.15: one strong finale fact instead of repeating the same event twice. */
.mayhem-recap-stage[data-summary="peak"] em{color:#f0c977!important;letter-spacing:.13em!important;text-shadow:0 0 18px #e4b75b24}
.mayhem-recap-stage[data-summary="split"] em{letter-spacing:.09em!important}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_recap_v815(Path('_site'))
