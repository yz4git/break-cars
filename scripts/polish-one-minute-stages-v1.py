"""BREAK CARS one-minute stage pacing v1.

Make every standalone event resolve in roughly one minute without flattening the
mode identities:
- COLOSSEUM: hard score/survival deadline at 60 seconds.
- WRECK HUNT: hard score-attack deadline at 60 seconds.
- WRECKING RACING: 2 laps, 65 second safety cap, 8 second post-leader grace.

This runs at the final generated-output boundary so MAYHEM TOUR inherits the
same event pacing after all of its gameplay/presentation layers are applied.
Legacy DURATION/w.limit values are retained for compatibility with older tuning
code; stageLimit is the authoritative non-racing deadline exposed to both the
legacy facade and the authoritative full-3D runtime.
"""
from pathlib import Path
import re

STAGE_SECONDS = 60
RACE_LAPS = 2
RACE_LIMIT = 65
RACE_GRACE = 8


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'One-minute stages {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def regex_one(text: str, pattern: str, repl: str, label: str) -> str:
    text, n = re.subn(pattern, repl, text, count=1)
    if n != 1:
        raise RuntimeError(f'One-minute stages {label}: expected 1 match, found {n}')
    return text


def apply_one_minute_stages_v1(target: Path) -> None:
    physics_path = target / 'physics.js'
    physics = physics_path.read_text()
    physics = one(
        physics,
        'const w={cars,time:0,events:[],pairs:new Map(),rand,done:false,mode:gameMode,limit:DURATION};',
        f'const w={{cars,time:0,events:[],pairs:new Map(),rand,done:false,mode:gameMode,limit:DURATION,stageLimit:{STAGE_SECONDS}}};',
        'world stage deadline',
    )
    physics = one(
        physics,
        'w.time>=w.limit',
        'w.time>=(w.stageLimit||w.limit)',
        'legacy WRECK HUNT deadline',
    )
    physics = one(
        physics,
        'w.time>=DURATION',
        'w.time>=(w.stageLimit||DURATION)',
        'legacy COLOSSEUM deadline',
    )
    physics_path.write_text(physics)

    # physics.js is now a compatibility facade: actual gameplay steps through
    # stepFullPhysics in physics3d.js. Patch both paths so tests and production
    # cannot disagree about when a one-minute stage ends.
    physics3d_path = target / 'physics3d.js'
    physics3d = physics3d_path.read_text()
    physics3d = one(
        physics3d,
        'p.lastContact=w.time; if (p.dead||w.time>=w.limit) w.done=true;',
        'p.lastContact=w.time; if (p.dead||w.time>=(w.stageLimit||w.limit)) w.done=true;',
        'full 3D WRECK HUNT deadline',
    )
    physics3d = one(
        physics3d,
        'w.time>=ctx.DURATION',
        'w.time>=(w.stageLimit||ctx.DURATION)',
        'full 3D COLOSSEUM deadline',
    )
    physics3d_path.write_text(physics3d)

    racing_path = target / 'racing.js'
    racing = racing_path.read_text()
    racing = regex_one(
        racing,
        r"export const TRACK=\{straight:0,radius:0,halfWidth:RACE3D_TRACK\.halfWidth,laps:\d+,limit:\d+,grace:\d+,name:",
        f"export const TRACK={{straight:0,radius:0,halfWidth:RACE3D_TRACK.halfWidth,laps:{RACE_LAPS},limit:{RACE_LIMIT},grace:{RACE_GRACE},name:",
        'WRECKING RACING laps/deadline',
    )
    racing_path.write_text(racing)

    game_path = target / 'game.js'
    game = game_path.read_text()
    timer_old = "const remain=Math.max(0,Math.ceil((world.mode==='racing'?world.endAt:(world.limit||DURATION))-world.time));"
    timer_new = "const remain=Math.max(0,Math.ceil((world.mode==='racing'?world.endAt:(world.stageLimit||world.limit||DURATION))-world.time));"
    game = one(game, timer_old, timer_new, 'HUD timer deadline')
    game = game.replace('world.time>=DURATION', 'world.time>=(world.stageLimit||DURATION)')

    # Presentation copy is intentionally patched after all MAYHEM/WRECK HUNT
    # layers so menus, pause help, opening toast and Tour event copy agree.
    copy_replacements = (
        ('150 SECONDS', '60 SECONDS'),
        ('150秒', '60秒'),
        ('4 LAPS', '2 LAPS'),
        ('4周', '2周'),
    )
    for old, new in copy_replacements:
        game = game.replace(old, new)
    game_path.write_text(game)

    courses_path = target / 'courses.js'
    courses = courses_path.read_text()
    for old, new in copy_replacements:
        courses = courses.replace(old, new)
    courses_path.write_text(courses)

    # Final-output invariants. These make generator drift fail loudly instead of
    # silently publishing the old multi-minute pacing.
    final_physics = physics_path.read_text()
    final_physics3d = physics3d_path.read_text()
    final_racing = racing_path.read_text()
    final_game = game_path.read_text()
    if f'stageLimit:{STAGE_SECONDS}' not in final_physics:
        raise RuntimeError('One-minute stages: stageLimit missing from generated physics')
    if 'w.time>=(w.stageLimit||w.limit)' not in final_physics:
        raise RuntimeError('One-minute stages: legacy WRECK HUNT deadline not generated')
    if 'w.time>=(w.stageLimit||DURATION)' not in final_physics:
        raise RuntimeError('One-minute stages: legacy COLOSSEUM deadline not generated')
    if 'w.time>=(w.stageLimit||w.limit)' not in final_physics3d:
        raise RuntimeError('One-minute stages: full 3D WRECK HUNT deadline not generated')
    if 'w.time>=(w.stageLimit||ctx.DURATION)' not in final_physics3d:
        raise RuntimeError('One-minute stages: full 3D COLOSSEUM deadline not generated')
    expected_track = f'laps:{RACE_LAPS},limit:{RACE_LIMIT},grace:{RACE_GRACE}'
    if expected_track not in final_racing:
        raise RuntimeError('One-minute stages: WRECKING RACING timing not generated')
    if '150秒' in final_game or '150 SECONDS' in final_game or '4 LAPS' in final_game or '4周' in final_game:
        raise RuntimeError('One-minute stages: stale long-format timing copy remains in game.js')


if __name__ == '__main__':
    apply_one_minute_stages_v1(Path('_site'))
