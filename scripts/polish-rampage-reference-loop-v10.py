"""Make the RAMPAGE loop read like one continuous toy-track vertical loop.

The road itself forms the loop; there is no hidden flat road or independent hoop.
Keep the long forward/up ellipse that gives clean vehicle tangency, move the
raised loop outside the figure-eight, and open only the lower rising/falling
halves in depth.  The branch-opening envelope is sin(pi*u), so the offset and
its first derivative are both zero at the road gates while separation develops
quickly enough near the bottom to keep the full road ribbons apart.

SKY FORGE and DOUBLE ORBIT are deliberately untouched.
"""
from pathlib import Path


def apply_rampage_reference_loop_v10(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()
    old = "outboard=14*env,twist=32*Math.sin(TAU*u)*env,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*.64;"
    new = "outboard=28*env,twist=26*Math.sin(TAU*u)*en,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*1.05;"
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE reference loop v10: expected 1 geometry match, found {count}')
    s = s.replace(old, new, 1)
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v10(Path('_site'))
