"""Stable loader for survival course pack v1.

The generated full-physics file may carry a cache/versioned courses.js import
by the time the final gameplay layers run.  Keep the core patch strict for all
other generator invariants, but provide activeCourse as a separate binding when
that one import has already changed shape.
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
        return strict_one(text, old, new, label)

    core.one = tolerant_one
    core.apply_survival_courses_v1(target)


if __name__ == '__main__':
    apply_survival_courses_v1(Path('_site'))
