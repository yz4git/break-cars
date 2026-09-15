"""Final generated-output cleanup for Death Colosseum HUD copy.

The per-frame HUD refresh is emitted after the start-screen setup, so patch it
at the final boundary to keep the score label mode-aware during live play.
"""
from pathlib import Path


def apply_death_colosseum_hud_fix_v11(target: Path) -> None:
    game_path = target / 'game.js'
    game = game_path.read_text()
    old = "if($('score-label'))$('score-label').textContent=world.mode==='wreck-hunt'?'HUNT SCORE':'IMPACT SCORE';"
    new = "if($('score-label'))$('score-label').textContent=world.mode==='wreck-hunt'?'HUNT SCORE':world.mode==='death-colosseum'?'RING OUT SCORE':'IMPACT SCORE';"
    n = game.count(old)
    if n != 1:
        raise RuntimeError(f'Death Colosseum HUD v1.1: expected live score label once, found {n}')
    game_path.write_text(game.replace(old, new, 1))

    final = game_path.read_text()
    if final.count("?'RING OUT SCORE':'IMPACT SCORE'") < 2:
        raise RuntimeError('Death Colosseum HUD v1.1: start/live labels are not both mode-aware')


if __name__ == '__main__':
    apply_death_colosseum_hud_fix_v11(Path('_site'))
