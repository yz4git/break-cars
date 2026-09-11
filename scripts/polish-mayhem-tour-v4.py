"""MAYHEM TOUR v4: make PIT/final result screens visually clean.

During a Tour result modal the ordinary driving HUD remains mounted. Hide that
entire layer and the WRECK HUNT target navigator only while the Tour result/PIT
is open, then restore them when the next event starts. This removes speedometer,
controls, radar, recover UI and target callouts from behind the result panel
without affecting normal single-event result screens.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v4 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_tour_v4(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    after = "function mayhemAfterEvent(){if(!mayhemActive())return;const runBadge=$('tour-run-badge');if(runBadge)runBadge.remove();const p=world.cars[0]"
    after_new = "function mayhemAfterEvent(){if(!mayhemActive())return;document.body.classList.add('mayhem-tour-result');const runBadge=$('tour-run-badge');if(runBadge)runBadge.remove();const p=world.cars[0]"
    s = one(s, after, after_new, 'result class on')

    start = "if(mayhemActive()){const oldBadge=$('tour-run-badge');if(oldBadge)oldBadge.remove();const badge=document.createElement('div');badge.id='tour-run-badge';badge.textContent=mayhemBadgeText();document.body.appendChild(badge);}"
    start_new = "if(mayhemActive()){document.body.classList.remove('mayhem-tour-result');const oldBadge=$('tour-run-badge');if(oldBadge)oldBadge.remove();const badge=document.createElement('div');badge.id='tour-run-badge';badge.textContent=mayhemBadgeText();document.body.appendChild(badge);}"
    s = one(s, start, start_new, 'result class off on event start')
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += "\nbody.mayhem-tour-result #driving,body.mayhem-tour-result #hunt-nav{display:none!important}\n"
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_tour_v4(Path('_site'))
