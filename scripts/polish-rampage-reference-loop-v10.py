"""Make the RAMPAGE loop read like one continuous toy-track vertical loop.

The road itself forms the loop; there is no hidden flat road or independent hoop.
Keep the loop almost entirely in the forward/up plane.  The wide figure-eight
clearance remains an outward bow, while the lower rising and falling branches
get opposite *forward* offsets.  That turns the closed-looking lower crossing
into a true open loop without turning the whole stunt into a corkscrew.

The branch-opening envelopes stay exactly zero in a short zone at both road
gates, preserving the original gate tangents as well as the exact gate points.
SKY FORGE and DOUBLE ORBIT are deliberately untouched.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE reference loop v10 {label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)


def apply_rampage_reference_loop_v10(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()

    s = one(
        s,
        "outboard=14*env,twist=32*Math.sin(TAU*u)*env,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*.64;",
        "entryOpen=smooth01((u-.035)/.09)*(1-smooth01((u-.24)/.12)),exitOpen=smooth01(((1-u)-.035)/.09)*(1-smooth01(((1-u)-.24)/.12)),openAlong=10.5*(exitOpen-entryOpen),outboard=28*env,twist=10*Math.sin(TAU*u)*env,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*1.05;",
        'lower branch envelopes',
    )
    s = one(
        s,
        "const lateral=outwardSign*(outboard+twist),pos=add(add(add(add(frame.p,mul(loopForward,horizR*sn)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lateral)),mul(ringUp,gateRise));",
        "const lateral=outwardSign*(outboard+twist),pos=add(add(add(add(frame.p,mul(loopForward,horizR*sn+openAlong)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lateral)),mul(ringUp,gateRise));",
        'forward-plane open loop position',
    )
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v10(Path('_site'))
