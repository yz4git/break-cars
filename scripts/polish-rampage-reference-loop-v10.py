"""Make RAMPAGE read as one continuous toy-track vertical loop.

The road itself forms the stunt.  There is no hidden flat chord and no separate
hoop.  Keep the revolution mainly in the forward/up plane, bow the whole loop
outward only after a straight gate lead, and separate the two lower branches by
opposite forward offsets with long C1-smooth envelopes.

The first/last few percent are deliberately untouched, so entry and exit inherit
the authored road direction before they begin to curve.  This avoids both the
old X-shaped lower crossing and the corkscrew look of the earlier helix fix.
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
        "entryX=clamp((u-.055)/.32,0,1),exitX=clamp(((1-u)-.055)/.32,0,1),entryOpen=Math.sin(Math.PI*entryX)**2,exitOpen=Math.sin(Math.PI*exitX)**2,openAlong=14*(exitOpen-entryOpen),outRamp=smooth01((u-.035)/.18)*smooth01(((1-u)-.035)/.18),outboard=28*outRamp,twist=7*Math.sin(TAU*u)*outRamp,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*1.05;",
        'smooth lower branch envelopes',
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
