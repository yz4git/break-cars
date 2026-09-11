"""MAYHEM TOUR v8.11: remove duplicated single-event result chrome.

The final iPhone-sized v8.10 review showed the native race-result title/detail/
stats above the dedicated MAYHEM TOUR result card. The Tour already owns its
PIT/final result presentation, rivalry status, recap, and replay actions, so the
base single-event summary is redundant and makes the final screen look stacked.

This pass only hides that base summary while a MAYHEM Tour result is open.
Single-event results, gameplay, physics, AI, Tour state and recap data are
unchanged.
"""
from pathlib import Path


def apply_mayhem_result_v811(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += "\nwindow.__breakCarsMayhemV811=true;\n"
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.11: the Tour owns its result screen; suppress the duplicated base result. */
body.mayhem-tour-result #result-title,
body.mayhem-tour-result #result-detail,
body.mayhem-tour-result #result-stats,
body.mayhem-tour-result #race-results{display:none!important}
body.mayhem-tour-result #tour-intermission{margin-top:0!important}
body.mayhem-tour-result #result-kicker{margin-bottom:8px}
@media(orientation:landscape) and (max-height:430px){body.mayhem-tour-result #result-kicker{margin-bottom:5px}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_result_v811(Path('_site'))
