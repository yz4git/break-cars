"""MAYHEM TOUR v8.7.1: preserve FINAL SHOWDOWN slow-motion replay caption.

v8.7 correctly labels the showdown replay at start, but the existing v8 per-frame
shot caption then replaces the third line. Keep the live shot grammar while
retaining the FINISH CUT / SLOW MOTION read throughout the final replay.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8.7.1 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_showdown_v871(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    old = "o.querySelector('span').textContent=`${MAYHEM_EVENTS[mayhemState.event]?.name||'MAYHEM'} · ${mayhemRivalName()} · ${state} · ${mayhemReplayShot}`;"
    new = "o.querySelector('span').textContent=mayhemShowdownEndingReplay&&mayhemFinalDuelActive()?`FINISH CUT · ${mayhemRivalName()} · SLOW MOTION · ${mayhemReplayShot}`:`${MAYHEM_EVENTS[mayhemState.event]?.name||'MAYHEM'} · ${mayhemRivalName()} · ${state} · ${mayhemReplayShot}`;"
    s = one(s, old, new, 'live showdown replay caption')
    game.write_text(s)


if __name__ == '__main__':
    apply_mayhem_showdown_v871(Path('_site'))
