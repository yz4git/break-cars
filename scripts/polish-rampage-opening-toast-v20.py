"""RAMPAGE v20: shorten only the RAMPAGE race-start instruction.

Keep every existing non-RAMPAGE opening cue byte-for-byte, especially Wreck
Hunt's HUNT START callout. Physics, camera, controls and HUD stay unchanged.
The real WebGL review showed 1.15s still overlapped the first Omega reveal, so
RAMPAGE alone uses a 0.75s cue.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE opening toast v20 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_opening_toast_v20(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    # By this point the Wreck Hunt and racing-UI passes have both run. Preserve
    # their current branches verbatim and add one RAMPAGE-course special case.
    old = "if(count<=0){mode='race';toast(world.mode==='racing'?'RAMPAGE 3D！ 飛べ、ぶつけろ、ループを抜けろ。':world.mode==='wreck-hunt'?'HUNT START — WRECK TARGETS':'側面を狙え。生き残れ。',2);}"
    new = "if(count<=0){mode='race';if(world.mode==='racing'&&activeCourse.id==='rampage-3d')toast('RAMPAGE 3D — OMEGAへ',.75);else toast(world.mode==='racing'?'RAMPAGE 3D！ 飛べ、ぶつけろ、ループを抜けろ。':world.mode==='wreck-hunt'?'HUNT START — WRECK TARGETS':'側面を狙え。生き残れ。',2);}"
    s = one(s, old, new, 'RAMPAGE-only start cue')
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_opening_toast_v20(Path('_site'))
