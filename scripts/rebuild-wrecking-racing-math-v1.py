"""WRECKING RACING Math Rebuild v1.

Replace the accumulated final racing geometry with one calculation-driven source
for RAMPAGE 3D, SKY FORGE and DOUBLE ORBIT. Existing physics/game APIs stay
compatible, while centerlines, banking, loops and jumps come from one model.
"""
from pathlib import Path
import importlib.util
import shutil


def apply_wrecking_racing_math_v1(target: Path) -> None:
    here = Path(__file__).parent
    shutil.copyfile(here / 'wrecking-racing-math-v1.js', target / 'racing3d.js')
    shutil.copyfile(here / 'wrecking-racing-track-view-v1.js', target / 'track-view.js')

    # The legacy full-physics layer already passes c.trackS into surface sampling.
    # Because this final rebuild replaces racing3d.js after that patch ran, keep
    # the same branch hint in the generated API or closed loops can make wheels
    # snap back to the previous loop branch after the gate.
    course = target / 'racing3d.js'
    r = course.read_text()
    old_surface = "export function sampleRaceSurface(x,y,z,up={x:0,y:1,z:0},forChassis=false){const p=projectRacePoint(x,y,z,null,true);"
    new_surface = "export function sampleRaceSurface(x,y,z,up={x:0,y:1,z:0},forChassis=false,hintS=null){const p=projectRacePoint(x,y,z,hintS,true);"
    count = r.count(old_surface)
    if count != 1:
        raise RuntimeError(f'WRECKING RACING math v1 surface hint: expected 1 match, found {count}')
    course.write_text(r.replace(old_surface, new_surface, 1))

    racing = target / 'racing.js'
    s = racing.read_text()
    if "activeCourse as mathCourseV1" not in s:
        s = "import {activeCourse as mathCourseV1} from './courses.js';\n" + s
    old = "w.raceCourse='rampage-3d';"
    if s.count(old) != 1:
        raise RuntimeError(f'WRECKING RACING math v1 raceCourse: expected 1 match, found {s.count(old)}')
    s = s.replace(old, "w.raceCourse=mathCourseV1.mode==='racing'?mathCourseV1.id:'rampage-3d';", 1)
    s = s.replace("name:'RAMPAGE 3D'", "name:mathCourseV1.mode==='racing'?mathCourseV1.name:'RAMPAGE 3D'", 1)
    racing.write_text(s)

    courses = target / 'courses.js'
    c = courses.read_text()
    hints = {
        "hint:'2連垂直ループ、約40度バンク、14m高架。空と地面が入れ替わる4周。'": "hint:'設計速度26m/s。曲率連動バンク、半径9.6/9.9mの2連ループ、弾道安全率を持つジャンプを計算生成。'",
        "hint:'非対称の立体8字。大ループ、連続うねり、天空交差橋を4周。'": "hint:'設計速度24.5m/s。立体8字の交差高低差を約9m確保し、曲率連動バンクと半径9.8mループを計算生成。'",
        "hint:'既存のBOOST LOOPコース'": "hint:'設計速度25.5m/s。曲率からバンク角を算出し、半径9.4mループと安全余裕付きジャンプを計算生成。'",
    }
    for old_hint, new_hint in hints.items():
        if old_hint in c:
            c = c.replace(old_hint, new_hint, 1)
    courses.write_text(c)

    contact_path = here / 'polish-wrecking-racing-contact-zones-v2.py'
    spec = importlib.util.spec_from_file_location('break_cars_wrecking_racing_contact_v2', contact_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_wrecking_racing_contact_v2(target)

    rival_path = here / 'polish-wrecking-racing-rival-duel-v4.py'
    spec = importlib.util.spec_from_file_location('break_cars_wrecking_racing_rival_duel_v4', rival_path)
    rival_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rival_module)
    rival_module.apply_wrecking_racing_rival_duel_v4(target)

    feud_path = here / 'polish-wrecking-racing-rival-feud-v5.py'
    spec = importlib.util.spec_from_file_location('break_cars_wrecking_racing_rival_feud_v5', feud_path)
    feud_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(feud_module)
    feud_module.apply_wrecking_racing_rival_feud_v5(target)

    # v5.0.1: guard a generator typo at the final emitted-JS boundary. Keep this
    # assertive so a later source rewrite cannot silently reintroduce bad output.
    generated = target / 'racing.js'
    js = generated.read_text()
    broken_guard = "if(targetId>0&&feudAliveV5=(w,targetId)){"
    fixed_guard = "if(targetId>0&&feudAliveV5(w,targetId)){"
    guard_count = js.count(broken_guard)
    if guard_count != 1:
        raise RuntimeError(f'WRECKING RACING rival feud v5 target guard: expected 1 match, found {guard_count}')
    generated.write_text(js.replace(broken_guard, fixed_guard, 1))

    nemesis_path = here / 'polish-wrecking-racing-rival-nemesis-v6.py'
    spec = importlib.util.spec_from_file_location('break_cars_wrecking_racing_rival_nemesis_v6', nemesis_path)
    nemesis_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nemesis_module)
    nemesis_module.apply_wrecking_racing_rival_nemesis_v6(target)

    showdown_path = here / 'polish-wrecking-racing-rival-showdown-v7.py'
    spec = importlib.util.spec_from_file_location('break_cars_wrecking_racing_rival_showdown_v7', showdown_path)
    showdown_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(showdown_module)
    showdown_module.apply_wrecking_racing_rival_showdown_v7(target)


if __name__ == '__main__':
    apply_wrecking_racing_math_v1(Path('_site'))
