"""MAYHEM TOUR v4: make PIT/final result screens visually clean.

During a Tour result modal the ordinary driving HUD remains mounted. Hide that
entire layer and the WRECK HUNT target navigator only while the Tour result/PIT
is open, then restore them when the next event starts. This removes speedometer,
controls, radar, recover UI and target callouts from behind the result panel
without affecting normal single-event result screens.

The v5 persistent RIVAL + LIVE MAYHEM DIRECTOR, v6 nine-course expansion,
v7 transform-based HIGHLIGHT REPLAY, v8 product presentation polish, v8.1
visual-review composition fixes, v8.2 peak-centered replay polish, v8.3 minimum
cinematic replay window, v8.4 impact framing, v8.5 nine-event rivalry series,
v8.6 DOUBLE ORBIT FINAL DUEL, v8.7 FINAL SHOWDOWN cinematics, v8.7.1 replay
caption polish, v8.8 showdown replay camera safety, v8.9 nine-event TOUR RECAP,
v8.10 final presentation cleanup, v8.11 result consolidation, v8.12 ending HUD
cleanup, v8.13 recap cinematics, v8.14 recap visual identity and v8.15 finale
editorial cleanup are chained here so Pages build order stays stable.
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
    load_and_apply(
        'polish-mayhem-product-v8.py',
        'break_cars_mayhem_product_v8',
        'apply_mayhem_product_v8',
        target,
    )
    load_and_apply(
        'polish-mayhem-product-v81.py',
        'break_cars_mayhem_product_v81',
        'apply_mayhem_product_v81',
        target,
    )
    load_and_apply(
        'polish-mayhem-product-v82.py',
        'break_cars_mayhem_product_v82',
        'apply_mayhem_product_v82',
        target,
    )
    load_and_apply(
        'polish-mayhem-product-v83.py',
        'break_cars_mayhem_product_v83',
        'apply_mayhem_product_v83',
        target,
    )
    load_and_apply(
        'polish-mayhem-product-v84.py',
        'break_cars_mayhem_product_v84',
        'apply_mayhem_product_v84',
        target,
    )
    load_and_apply(
        'polish-mayhem-rivalry-v85.py',
        'break_cars_mayhem_rivalry_v85',
        'apply_mayhem_rivalry_v85',
        target,
    )
    load_and_apply(
        'polish-mayhem-final-duel-v86.py',
        'break_cars_mayhem_final_duel_v86',
        'apply_mayhem_final_duel_v86',
        target,
    )
    load_and_apply(
        'polish-mayhem-showdown-v87.py',
        'break_cars_mayhem_showdown_v87',
        'apply_mayhem_showdown_v87',
        target,
    )
    load_and_apply(
        'polish-mayhem-showdown-v871.py',
        'break_cars_mayhem_showdown_v871',
        'apply_mayhem_showdown_v871',
        target,
    )
    load_and_apply(
        'polish-mayhem-showdown-v88.py',
        'break_cars_mayhem_showdown_v88',
        'apply_mayhem_showdown_v88',
        target,
    )
    load_and_apply(
        'polish-mayhem-recap-v89.py',
        'break_cars_mayhem_recap_v89',
        'apply_mayhem_recap_v89',
        target,
    )
    load_and_apply(
        'polish-mayhem-showdown-v810.py',
        'break_cars_mayhem_showdown_v810',
        'apply_mayhem_showdown_v810',
        target,
    )
    load_and_apply(
        'polish-mayhem-result-v811.py',
        'break_cars_mayhem_result_v811',
        'apply_mayhem_result_v811',
        target,
    )
    load_and_apply(
        'polish-mayhem-showdown-v812.py',
        'break_cars_mayhem_showdown_v812',
        'apply_mayhem_showdown_v812',
        target,
    )
    load_and_apply(
        'polish-mayhem-recap-v813.py',
        'break_cars_mayhem_recap_v813',
        'apply_mayhem_recap_v813',
        target,
    )
    load_and_apply(
        'polish-mayhem-recap-v814.py',
        'break_cars_mayhem_recap_v814',
        'apply_mayhem_recap_v814',
        target,
    )
    load_and_apply(
        'polish-mayhem-recap-v815.py',
        'break_cars_mayhem_recap_v815',
        'apply_mayhem_recap_v815',
        target,
    )


if __name__ == '__main__':
    apply_mayhem_tour_v4(Path('_site'))