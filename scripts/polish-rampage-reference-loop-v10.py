"""Make the RAMPAGE loop read like one continuous toy-track vertical loop.

v9 proved the lower branches can be separated, but its very large lateral twist
made the road read as a corkscrew and made the vehicle velocity fight the local
road tangent.  Keep the same continuous road/gate construction while moving the
clearance into the forward/up loop ellipse: a larger forward radius separates
the lower halves naturally and only a mild depth twist remains.

SKY FORGE and DOUBLE ORBIT are deliberately untouched.
"""
from pathlib import Path


def apply_rampage_reference_loop_v10(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()
    old = "outboard=14*env,twist=32*Math.sin(TAU*u)*env,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*.64;"
    new = "outboard=15*env,twist=12*Math.sin(TAU*u)*env,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*1.05;"
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE reference loop v10: expected 1 geometry match, found {count}')
    s = s.replace(old, new, 1)
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v10(Path('_site'))
