"""Make the RAMPAGE loop read like one continuous toy-track vertical loop.

The road itself forms the loop; there is no hidden flat road or independent hoop.
v9 proved that lower-branch separation is essential, while the first v10 pass
proved that a larger forward/up ellipse gives much better physical tangency than
a tight corkscrew.  This pass keeps that long ellipse, moves the whole elevated
loop farther outside the figure-eight, and restores only enough depth opening to
keep the full-width lower ribbons apart.

SKY FORGE and DOUBLE ORBIT are deliberately untouched.
"""
from pathlib import Path


def apply_rampage_reference_loop_v10(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()
    old = "outboard=14*env,twist=32*Math.sin(TAU*u)*env,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*.64;"
    new = "outboard=28*env,twist=26*Math.sin(TAU*u)*env,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*1.05;"
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE reference loop v10: expected 1 geometry match, found {count}')
    s = s.replace(old, new, 1)
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v10(Path('_site'))
