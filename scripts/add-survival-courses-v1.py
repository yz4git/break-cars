"""Stable loader for survival course pack v1.

The final generated runtime is intentionally assembled from many gameplay
layers. Keep the survival core strict, but adapt its two insertion points that
are known to have stable semantic locations while their exact emitted text can
change: the courses.js import and the end of the full-physics substep block.
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


if __name__ == '__main__':
    apply_survival_courses_v1(Path('_site'))
