"""Make the separated single-loop exit leg face the outgoing authored road early.

The lateral ring relocation increases ringExit->road distance.  The old Hermite
handle was capped at 5 m, so the last two metres still crossed the outgoing road
nearly sideways.  Keep DOUBLE ORBIT's proven handle; give RAMPAGE/SKY a longer
outgoing tangent handle so the visible exit is a proper merge, not a crossing.
"""
from pathlib import Path


def apply_open_loop_exit_alignment_v9(target: Path) -> None:
    path = target / 'racing3d.js'
    text = path.read_text()
    old = "entryScale=clamp(entryDist*.46,2.1,4.2),exitScale=clamp(exitDist*.42,2.2,5.0);"
    new = "entryScale=clamp(entryDist*.46,2.1,4.2),exitScale=doubleOrbit?clamp(exitDist*.42,2.2,5.0):clamp(exitDist*1.20,6.0,30.0);"
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'open loop exit v9: expected 1 scale match, found {count}')
    path.write_text(text.replace(old, new, 1))


if __name__ == '__main__':
    apply_open_loop_exit_alignment_v9(Path('_site'))
