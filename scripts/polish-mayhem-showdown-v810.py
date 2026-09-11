"""MAYHEM TOUR v8.10: final presentation cleanup after iPhone visual review.

The v8.8 high-side replay fixed the severe DOUBLE ORBIT underside obstruction,
and v8.9 added the nine-event TOUR RECAP. The latest 852x393 review still showed
three presentation-only issues at the very end of the run:
- SHOWDOWN CHASE carried too much foreground loop geometry on the left;
- the ending verdict card sat directly on top of the final result panel;
- the FINAL SHOWDOWN REPLAY CTA wrapped into a cramped three-line label.

This pass only adjusts event-9 presentation. Physics, AI, Tour progression,
generic replay cameras and the v8.9 recap film are unchanged.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8.10 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_showdown_v810(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    chase = "nextShot='SHOWDOWN CHASE';const back=clamp(12.8+separation*.18,13,17);mayhemReplayDesired.copy(mayhemReplayP).addScaledVector(mayhemReplayForward,-back).addScaledVector(mayhemReplaySide,5.2);mayhemReplayDesired.y=Math.max(mayhemReplayDesired.y+8.2,mayhemReplayMid.y+8.6);mayhemReplayTarget.copy(mayhemReplayP).addScaledVector(mayhemReplayForward,4.8);mayhemReplayTarget.y+=1.0;fov=62;"
    chase_new = "nextShot='SHOWDOWN CHASE';const back=clamp(15.8+separation*.20,16.2,20.5);mayhemReplayDesired.copy(mayhemReplayP).addScaledVector(mayhemReplayForward,-back).addScaledVector(mayhemReplaySide,1.6);mayhemReplayDesired.y=Math.max(mayhemReplayDesired.y+12.8,mayhemReplayMid.y+13.6);mayhemReplayTarget.copy(mayhemReplayP).addScaledVector(mayhemReplayForward,5.2);mayhemReplayTarget.y+=1.05;fov=63;"
    s = one(s, chase, chase_new, 'clean high showdown chase')

    telemetry = "camera:'HIGH-SIDE',shot:mayhemReplayShot"
    telemetry_new = "camera:'CLEAN-HIGH',shot:mayhemReplayShot"
    s = one(s, telemetry, telemetry_new, 'clean high replay telemetry')

    ending_anim = "el.classList.remove('show');void el.offsetWidth;el.classList.add('show');setTimeout(()=>el?.classList.remove('show'),2300);window.__breakCarsMayhemShowdown="
    ending_anim_new = "document.body.classList.add('mayhem-showdown-ending-active');el.classList.remove('show');void el.offsetWidth;el.classList.add('show');setTimeout(()=>{el?.classList.remove('show');document.body.classList.remove('mayhem-showdown-ending-active');},2300);window.__breakCarsMayhemShowdown="
    s = one(s, ending_anim, ending_anim_new, 'isolated ending verdict')

    final_button = "button.innerHTML=mayhemFinalDuelActive()?'<b>FINAL SHOWDOWN REPLAY</b><small>FINISH CUT · SLOW MOTION</small>':'<b>HIGHLIGHT REPLAY</b><small>DIRECTOR CUT</small>';"
    final_button_new = "button.innerHTML=mayhemFinalDuelActive()?'<b>SHOWDOWN REPLAY</b><small>FINAL CUT · SLOW MOTION</small>':'<b>HIGHLIGHT REPLAY</b><small>DIRECTOR CUT</small>';"
    s = one(s, final_button, final_button_new, 'compact showdown replay CTA')

    s += "\nwindow.__breakCarsMayhemV810=true;\n"
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.10: final presentation cleanup from iPhone landscape review. */
body.mayhem-showdown-ending-active #modal{opacity:0!important;pointer-events:none!important}
body.mayhem-showdown-ending-active #mayhem-showdown-ending{z-index:70}
.tour-final .tour-replay-button{white-space:nowrap!important;min-width:0!important;padding-left:8px!important;padding-right:8px!important}
.tour-final .tour-replay-button b{white-space:nowrap!important;font-size:clamp(8px,1.15vw,11px)!important;letter-spacing:.045em!important;line-height:1!important}
.tour-final .tour-replay-button small{white-space:nowrap!important;font-size:6px!important;letter-spacing:.07em!important;line-height:1!important}
@media(orientation:landscape) and (max-height:430px){.tour-final .tour-replay-button{padding-left:6px!important;padding-right:6px!important}.tour-final .tour-replay-button b{font-size:8px!important}.tour-final .tour-replay-button small{font-size:5px!important}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_showdown_v810(Path('_site'))
