"""RAMPAGE v21: reduce recover-button visual weight without changing behavior.

The manual -200 recovery remains always available in racing exactly as before.
Only the RAMPAGE course gets a shorter label and compact, translucent styling;
the touch target stays at least 44px high and returns to full opacity on focus,
hover or press. No recovery eligibility, cooldown, score, physics or camera code
is changed.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE recover v21 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_recover_v21(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    marker = "selectMode(activeCourse.mode);$('mode-tag').textContent=activeCourse.name+' / '+activeCourse.mode.toUpperCase();"
    replacement = "selectMode(activeCourse.mode);const rampageCourseUI=activeCourse.id==='rampage-3d';document.body.classList.toggle('rampage-course-ui',rampageCourseUI);if(rampageCourseUI)$('recover').innerHTML='復帰 <small>−200</small>';$('mode-tag').textContent=activeCourse.name+' / '+activeCourse.mode.toUpperCase();"
    s = one(s, marker, replacement, 'course UI marker')
    game.write_text(s)

    racing = target / 'racing.css'
    css = racing.read_text()
    marker = '#race-results{'
    compact = "body.rampage-course-ui #recover{min-width:78px;min-height:44px;padding:7px 9px;font-size:10px;opacity:.58;backdrop-filter:blur(3px);transition:opacity .14s ease,transform .14s ease}body.rampage-course-ui #recover small{font-size:9px}body.rampage-course-ui #recover:hover,body.rampage-course-ui #recover:focus-visible,body.rampage-course-ui #recover:active{opacity:1;transform:scale(1.04)}"
    css = one(css, marker, compact + marker, 'compact recover CSS')
    racing.write_text(css)


if __name__ == '__main__':
    apply_rampage_recover_v21(Path('_site'))
