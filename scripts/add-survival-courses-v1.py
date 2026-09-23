"""Stable loader for survival course pack v1.

The final generated runtime is intentionally assembled from many gameplay
layers. Keep the survival core strict, but adapt its two insertion points that
are known to have stable semantic locations while their exact emitted text can
change: the courses.js import and the end of the full-physics substep block.
After the core patch, normalize elevated non-racing starts so WRECK HUNT's
ordinary opening choreography cannot place a rival over a real survival hole.
Death Colosseum then layers its authored fall-only arenas on that stable final
runtime so both the earlier survival courses and the new mode keep safe spawns.
"""
from pathlib import Path
import importlib.util
import re


def apply_survival_courses_v1(target: Path) -> None:
    core_path = Path(__file__).with_name('add-survival-courses-core-v1.py')
    spec = importlib.util.spec_from_file_location('break_cars_survival_courses_core_v1', core_path)
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    strict_one = core.one

    def tolerant_one(text: str, old: str, new: str, label: str) -> str:
        if label == 'physics active course import' and old not in text:
            has_active = re.search(r"import\s*\{[^}]*\bactiveCourse\b[^}]*\}\s*from\s*['\"]\./courses\.js", text)
            if not has_active:
                text = "import {activeCourse} from './courses.js';\n" + text
            return text
        if label == 'fall check after physics' and old not in text:
            # add-player-auto-upright runs before this final pass and inserts its
            # call between the substep loop and the mode dispatch. Fatal falls
            # belong at exactly that boundary: physics has settled, but no
            # recovery or finish logic has run yet.
            anchor = "  updatePlayerAutoUpright(w,dt);\n  if (w.mode==='racing')"
            replacement = "  for (const c of w.cars) survivalFall(w,c,ctx);\n  updatePlayerAutoUpright(w,dt);\n  if (w.mode==='racing')"
            n = text.count(anchor)
            if n != 1:
                raise RuntimeError(f'Survival courses fall check after physics: expected semantic anchor once, found {n}')
            return text.replace(anchor, replacement, 1)
        return strict_one(text, old, new, label)

    core.one = tolerant_one
    core.apply_survival_courses_v1(target)

    fix_path = Path(__file__).with_name('fix-survival-spawns-v11.py')
    fix_spec = importlib.util.spec_from_file_location('break_cars_survival_spawn_fix_v11', fix_path)
    fix = importlib.util.module_from_spec(fix_spec)
    fix_spec.loader.exec_module(fix)
    fix.apply_survival_spawn_fix_v11(target)

    death_path = Path(__file__).with_name('add-death-colosseum-v1.py')
    death_spec = importlib.util.spec_from_file_location('break_cars_death_colosseum_v1', death_path)
    death = importlib.util.module_from_spec(death_spec)
    death_spec.loader.exec_module(death)
    death.apply_death_colosseum_v1(target)

    opening_path = Path(__file__).with_name('improve-death-colosseum-openings-v13.py')
    opening_spec = importlib.util.spec_from_file_location('break_cars_death_colosseum_openings_v13', opening_path)
    opening = importlib.util.module_from_spec(opening_spec)
    opening_spec.loader.exec_module(opening)
    opening.apply_death_colosseum_openings_v13(target)

    playability_path = Path(__file__).with_name('improve-death-colosseum-playability-v14.py')
    playability_spec = importlib.util.spec_from_file_location('break_cars_death_colosseum_playability_v14', playability_path)
    playability = importlib.util.module_from_spec(playability_spec)
    playability_spec.loader.exec_module(playability)
    playability.apply_death_colosseum_playability_v14(target)

    combat_path = Path(__file__).with_name('improve-death-colosseum-combat-v15.py')
    combat_spec = importlib.util.spec_from_file_location('break_cars_death_colosseum_combat_v15', combat_path)
    combat = importlib.util.module_from_spec(combat_spec)
    combat_spec.loader.exec_module(combat)
    combat.apply_death_colosseum_combat_v15(target)

    visual_path = Path(__file__).with_name('improve-death-colosseum-visual-v16.py')
    visual_spec = importlib.util.spec_from_file_location('break_cars_death_colosseum_visual_v16', visual_path)
    visual = importlib.util.module_from_spec(visual_spec)
    visual_spec.loader.exec_module(visual)
    visual.apply_death_colosseum_visual_v16(target)

    sky_tiles_path = Path(__file__).with_name('improve-death-colosseum-sky-tiles-v17.py')
    sky_tiles_spec = importlib.util.spec_from_file_location('break_cars_death_colosseum_sky_tiles_v17', sky_tiles_path)
    sky_tiles = importlib.util.module_from_spec(sky_tiles_spec)
    sky_tiles_spec.loader.exec_module(sky_tiles)
    sky_tiles.apply_death_colosseum_sky_tiles_v17(target)

    razor_path = Path(__file__).with_name('improve-death-colosseum-razor-v18.py')
    razor_spec = importlib.util.spec_from_file_location('break_cars_death_colosseum_razor_v18', razor_path)
    razor = importlib.util.module_from_spec(razor_spec)
    razor_spec.loader.exec_module(razor)
    razor.apply_death_colosseum_razor_v18(target)

    fall_camera_path = Path(__file__).with_name('improve-death-colosseum-fall-camera-v19.py')
    fall_camera_spec = importlib.util.spec_from_file_location('break_cars_death_colosseum_fall_camera_v19', fall_camera_path)
    fall_camera = importlib.util.module_from_spec(fall_camera_spec)
    fall_camera_spec.loader.exec_module(fall_camera)
    fall_camera.apply_death_colosseum_fall_camera_v19(target)

    countdown_path = Path(__file__).with_name('fix-death-colosseum-countdown-v12.py')
    countdown_spec = importlib.util.spec_from_file_location('break_cars_death_colosseum_countdown_v12', countdown_path)
    countdown = importlib.util.module_from_spec(countdown_spec)
    countdown_spec.loader.exec_module(countdown)
    countdown.apply_death_colosseum_countdown_fix_v12(target)

    hud_path = Path(__file__).with_name('fix-death-colosseum-hud-v11.py')
    hud_spec = importlib.util.spec_from_file_location('break_cars_death_colosseum_hud_v11', hud_path)
    hud = importlib.util.module_from_spec(hud_spec)
    hud_spec.loader.exec_module(hud)
    hud.apply_death_colosseum_hud_fix_v11(target)


if __name__ == '__main__':
    apply_survival_courses_v1(Path('_site'))
