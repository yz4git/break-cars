"""MAYHEM TOUR v4: make PIT/final result screens visually clean.

During a Tour result modal the ordinary driving HUD remains mounted. Hide that
entire layer and the WRECK HUNT target navigator only while the Tour result/PIT
is open, then restore them when the next event starts. This removes speedometer,
controls, radar, recover UI and target callouts from behind the result panel
without affecting normal single-event result screens.

The v5 persistent RIVAL + LIVE MAYHEM DIRECTOR, v6 nine-course expansion and
v7 transform-based HIGHLIGHT REPLAY are chained here so the existing Pages build
order remains stable.
"""
from pathlib import Path
import importlib.util


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v4 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def load_and_apply(filename: str, module_name: str, function_name: str, target: Path) -> None:
    module_path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    getattr(module, function_name)(target)


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

    load_and_apply(
        'apply-mayhem-rival-director-v5.py',
        'break_cars_mayhem_rival_director_v5',
        'apply_mayhem_rival_director_v5',
        target,
    )
    load_and_apply(
        'expand-mayhem-nine-course-v6.py',
        'break_cars_mayhem_nine_course_v6',
        'apply_mayhem_nine_course_v6',
        target,
    )
    load_and_apply(
        'add-mayhem-highlight-replay-v7.py',
        'break_cars_mayhem_highlight_replay_v7',
        'apply_mayhem_highlight_replay_v7',
        target,
    )


if __name__ == '__main__':
    apply_mayhem_tour_v4(Path('_site'))
