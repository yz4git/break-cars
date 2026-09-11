"""Run MAYHEM TOUR menu setup after every existing final UI/course override."""
from pathlib import Path


def apply_mayhem_tour_finalize_v1(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    old = 'selectMode(activeCourse.mode);setupMayhemMenu();'
    if s.count(old) != 1:
        raise RuntimeError(f'MAYHEM TOUR finalize: expected 1 early setup call, found {s.count(old)}')
    s = s.replace(old, 'selectMode(activeCourse.mode);', 1)
    if s.rstrip().endswith('setupMayhemMenu();'):
        raise RuntimeError('MAYHEM TOUR finalize: final setup call already present')
    s = s.rstrip() + '\nsetupMayhemMenu();\n'
    game.write_text(s)


if __name__ == '__main__':
    apply_mayhem_tour_finalize_v1(Path('_site'))
