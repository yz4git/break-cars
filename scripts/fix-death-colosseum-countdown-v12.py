"""Death Colosseum v1.2 start robustness fixes.

Full 3D bodies are intentionally created on the first simulation step. During
countdown, however, the legacy render fallback was still drawing cars at y=0,
under the authored elevated survival deck. Keep physics frozen during the
countdown but render fallback cars on the analytical course height.

The shared frame loop also capped render dt at 50 ms before using it for the
countdown. That is correct for stable simulation/render effects, but it makes a
3.5 second countdown stretch dramatically on a slow GPU. Preserve the capped
dt everywhere else while making only the countdown follow real elapsed time.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Death Colosseum v1.2 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_death_colosseum_countdown_fix_v12(target: Path) -> None:
    game_path = target / 'game.js'
    game = game_path.read_text()

    old = "m.g.position.set(c.x,rxn.lift+groundClear+.025,c.z);"
    new = "const fallbackGround=activeCourse?.survival?(courseHeight(c.x,c.z)??0):0;m.g.position.set(c.x,fallbackGround+rxn.lift+groundClear+.025,c.z);"
    game = one(game, old, new, 'elevated countdown render')

    old = "function frame(now){requestAnimationFrame(frame);const dt=Math.min((now-last)/1000,.05);last=now;if(mode==='countdown'){const old=Math.ceil(count);count-=dt;"
    new = "function frame(now){requestAnimationFrame(frame);const rawDt=Math.max(0,(now-last)/1000),dt=Math.min(rawDt,.05);last=now;if(mode==='countdown'){const old=Math.ceil(count);count-=rawDt;"
    game = one(game, old, new, 'wall clock countdown')

    game_path.write_text(game)


if __name__ == '__main__':
    apply_death_colosseum_countdown_fix_v12(Path('_site'))
