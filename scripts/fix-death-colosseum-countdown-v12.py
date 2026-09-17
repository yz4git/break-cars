"""Death Colosseum v1.2 visual start fix.

Full 3D bodies are intentionally created on the first simulation step. During
countdown, however, the legacy render fallback was still drawing cars at y=0,
under the authored elevated survival deck. Keep physics frozen during the
countdown but render fallback cars on the analytical course height.
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
    game_path.write_text(game)


if __name__ == '__main__':
    apply_death_colosseum_countdown_fix_v12(Path('_site'))
