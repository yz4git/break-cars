"""MAYHEM TOUR v8.20: iPhone-landscape visual priority pass.

A fresh 852x393 touch audit showed a real readability failure when the Tour
badge, LIVE MAYHEM DIRECTOR, Director stinger, RIVAL battle-flow cue and
in-world RIVAL marker all occupied the center-top at once. The game was still
playable, but the actual rival cars were hidden by UI exactly when pressure was
highest.

This pass keeps every gameplay/AI value intact and gives those overlays one
shared priority lane: stinger > battle-flow cue > Director HUD > world marker.
The Tour badge remains persistent. On short landscape screens the cinematic
stinger becomes a compact one-line replacement instead of another stacked
panel. The central speed/condition cluster is also reduced slightly without
shrinking any touch target.
"""
from pathlib import Path


def apply_mayhem_visual_clarity_v820(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += r'''

/* MAYHEM TOUR v8.20 — iPhone visual-priority arbitration */
let mayhemV820StingerTimer=0,mayhemV820FlowTimer=0;
const mayhemDirectorStingerV820Base=mayhemDirectorStinger;
mayhemDirectorStinger=function(state,intensity){
 document.body.classList.add('mayhem-v820-stinger-active');clearTimeout(mayhemV820StingerTimer);
 mayhemDirectorStingerV820Base(state,intensity);
 mayhemV820StingerTimer=setTimeout(()=>document.body.classList.remove('mayhem-v820-stinger-active'),1480);
};
const mayhemRivalBattleCueV820Base=mayhemRivalBattleCueV818;
mayhemRivalBattleCueV818=function(kicker,title,sub=''){
 document.body.classList.add('mayhem-v820-flow-active');clearTimeout(mayhemV820FlowTimer);
 mayhemRivalBattleCueV820Base(kicker,title,sub);
 mayhemV820FlowTimer=setTimeout(()=>document.body.classList.remove('mayhem-v820-flow-active'),860);
};
window.__breakCarsMayhemV820={singlePriorityLane:true,touchTargetsPreserved:true};
'''
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.20: only one transient MAYHEM message owns the center-top lane. */
body.mayhem-v820-stinger-active #mayhem-director,
body.mayhem-v820-stinger-active #mayhem-rival-flow,
body.mayhem-v820-stinger-active #mayhem-rival-marker{opacity:0!important;visibility:hidden!important}
body.mayhem-v820-flow-active:not(.mayhem-v820-stinger-active) #mayhem-director,
body.mayhem-v820-flow-active:not(.mayhem-v820-stinger-active) #mayhem-rival-marker{opacity:0!important;visibility:hidden!important}
@media(orientation:landscape) and (max-height:430px){
 #mayhem-director-stinger{top:max(73px,calc(env(safe-area-inset-top) + 65px));min-width:150px;max-width:min(54vw,300px);padding:5px 12px;border:1px solid #ff5f8177;border-radius:999px;background:#120b12ee;filter:drop-shadow(0 5px 14px #000b)}
 #mayhem-director-stinger small,#mayhem-director-stinger span{display:none}
 #mayhem-director-stinger b{margin:0;font-size:12px;line-height:1;letter-spacing:.11em;white-space:nowrap}
 #mayhem-rival-flow{top:max(72px,calc(env(safe-area-inset-top) + 64px));min-width:142px;max-width:min(54vw,300px);padding:4px 9px}
 #mayhem-rival-flow small{font-size:7px}#mayhem-rival-flow b{font-size:9px}
}
'''
    css.write_text(c)

    style = target / 'style.css'
    base = style.read_text()
    base += r'''
/* MAYHEM v8.20 audit: free the forward view on iPhone landscape; controls stay full size. */
@media(orientation:landscape) and (max-height:430px){
 #speed{bottom:72px}
 #speed b{font-size:34px;line-height:.9;letter-spacing:-1px}
 #speed small{font-size:8px;letter-spacing:1.6px}
 #condition{bottom:max(22px,env(safe-area-inset-bottom));width:150px}
 .health-title{font-size:9px;letter-spacing:1.6px}
 .bar{margin:6px 0}
 .damage-sections{font-size:8px}
}
'''
    style.write_text(base)


if __name__ == '__main__':
    apply_mayhem_visual_clarity_v820(Path('_site'))
