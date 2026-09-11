"""MAYHEM TOUR v8.3: guarantee a complete three-shot replay window.

v8.2 correctly centers the edit on the hottest RIVAL moment, but an event can
finish exactly when the first 18-frame best window becomes available. In that
case the peak is the final source frame and the centered trim can collapse to
15 frames, too short to reliably expose CHASE -> RIVAL TWO-SHOT -> IMPACT CLOSE.

Keep the real recorded peak and all available real frames. Expand the trim back
toward the source edges first, then add only a brief frozen post-impact hold when
a very short event has no recorded post-roll. Gameplay/physics and replay timing
step remain untouched.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8.3 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_product_v83(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    old = "function mayhemReplayFreeze(){const usingBest=mayhemReplayBest.length>=12,src=usingBest?mayhemReplayBest:mayhemReplayFrames;if(!src.length){mayhemReplayFrozen=[];return;}let peak=usingBest?Math.max(0,Math.min(src.length-1,mayhemReplayV82BestPeak)):0;if(!usingBest){let heat=-Infinity;for(let i=0;i<src.length;i++)if((src[i].heat??-Infinity)>heat){heat=src[i].heat;peak=i;}}const start=Math.max(0,peak-14),end=Math.min(src.length,peak+17);mayhemReplayFrozen=src.slice(start,end).map(mayhemReplayV82Clone);mayhemReplayV82FrozenPeak=Math.max(0,peak-start);mayhemReplayV82LastShot='';window.__breakCarsHighlightReplay={recording:false,frames:mayhemReplayFrozen.length,bestFrames:mayhemReplayBest.length,bestHeat:mayhemReplayBestHeat,peakIndex:mayhemReplayV82FrozenPeak,peakProgress:mayhemReplayFrozen.length>1?mayhemReplayV82FrozenPeak/(mayhemReplayFrozen.length-1):0,playing:false,v82:true};}"
    new = "function mayhemReplayFreeze(){const usingBest=mayhemReplayBest.length>=12,src=usingBest?mayhemReplayBest:mayhemReplayFrames;if(!src.length){mayhemReplayFrozen=[];return;}let peak=usingBest?Math.max(0,Math.min(src.length-1,mayhemReplayV82BestPeak)):0;if(!usingBest){let heat=-Infinity;for(let i=0;i<src.length;i++)if((src[i].heat??-Infinity)>heat){heat=src[i].heat;peak=i;}}let start=Math.max(0,peak-14),end=Math.min(src.length,peak+17),clip=src.slice(start,end).map(mayhemReplayV82Clone),frozenPeak=Math.max(0,peak-start);const minFrames=24;while(clip.length<minFrames&&start>0){start--;clip.unshift(mayhemReplayV82Clone(src[start]));frozenPeak++;}while(clip.length<minFrames&&end<src.length){clip.push(mayhemReplayV82Clone(src[end++]));}while(clip.length<minFrames&&clip.length){clip.push(mayhemReplayV82Clone(clip[clip.length-1]));}mayhemReplayFrozen=clip;mayhemReplayV82FrozenPeak=Math.min(mayhemReplayFrozen.length-1,frozenPeak);mayhemReplayV82LastShot='';window.__breakCarsHighlightReplay={recording:false,frames:mayhemReplayFrozen.length,bestFrames:mayhemReplayBest.length,bestHeat:mayhemReplayBestHeat,peakIndex:mayhemReplayV82FrozenPeak,peakProgress:mayhemReplayFrozen.length>1?mayhemReplayV82FrozenPeak/(mayhemReplayFrozen.length-1):0,playing:false,v82:true,v83:true};}"
    s = one(s, old, new, 'minimum editorial replay window')
    game.write_text(s)


if __name__ == '__main__':
    apply_mayhem_product_v83(Path('_site'))
