"""RAMPAGE v20: make the race-start instruction brief enough to reveal Omega.

The v19 full-sequence WebGL contact sheet shows the stunt itself is readable,
but the generic two-second racing toast was replaced with a long RAMPAGE phrase
that spans the upper third of the phone screen during the approach. Keep all
physics, camera, controls and HUD behavior unchanged. Use a short RAMPAGE cue
for 1.15 seconds; other racing courses get their own concise course-name cue.
"""
from pathlib import Path
import re


def regex_one(text: str, pattern: str, new: str, label: str) -> str:
    out, n = re.subn(pattern, new, text, count=1)
    if n != 1:
        raise RuntimeError(f'RAMPAGE opening toast v20 {label}: expected 1 match, found {n}')
    return out


def apply_rampage_opening_toast_v20(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    # Earlier UI/course patches are allowed to change the racing copy. Match the
    # unique countdown->race toast structure instead of coupling to that wording.
    pattern = r"if\(count<=0\)\{mode='race';toast\(world\.mode==='racing'\?.*?:'側面を狙え。生き残れ。',2\);\}"
    new = "if(count<=0){mode='race';const opening=world.mode==='racing'?(activeCourse.id==='rampage-3d'?'RAMPAGE 3D — OMEGAへ':`${activeCourse.name} — GO`):'側面を狙え。生き残れ。';toast(opening,world.mode==='racing'?1.15:2);}"
    s = regex_one(s, pattern, new, 'short course-aware start cue')
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_opening_toast_v20(Path('_site'))
