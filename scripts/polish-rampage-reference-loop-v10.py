"""Make RAMPAGE read as one continuous toy-track vertical loop.

The road itself forms the stunt. There is no hidden flat chord and no separate
hoop. Keep the revolution mainly in the forward/up plane. The RAMPAGE gates now
use the same compact 0.18-radian half span as the proven stunt loops so incoming
and outgoing road tangents remain broadly aligned instead of forcing the lower
loop to fold across a figure-eight turn.

The whole loop bows away from the unrelated figure-eight road only after a
straight gate lead, and the two lower branches get opposite forward offsets so
their ribbons do not form an X. The descending half begins merging toward the
outgoing road before the bottom; its X/Z centerline is C1-blended onto a ray
traced backward from the outgoing authored road, then remains on that ray near
the gate. The car therefore has a physical run in which its velocity can align
with the outgoing road instead of encountering a last-second heading change.

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

    # The old 0.36 RAMPAGE cut spanned a large figure-eight bend: the start/end
    # road headings differed by roughly 78 degrees, so even a clean vertical
    # ring had to drag its descending lower leg back across the incoming road.
    # A 0.18 half-span still removes the authored road under the whole stunt but
    # keeps both gates on the same natural road run.
    s = one(
        s,
        "const LOOP_HALF_T=(doubleOrbit||skyForge)?.18:.36,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=(!doubleOrbit&&!skyForge)?.58:1;",
        "const LOOP_HALF_T=.18,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=(!doubleOrbit&&!skyForge)?.58:1;",
        'compact natural gate span',
    )
    s = one(
        s,
        "outboard=14*env,twist=32*Math.sin(TAU*u)*env,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*.64;",
        "entryX=clamp((u-.055)/.44,0,1),exitX=clamp(((1-u)-.055)/.44,0,1),entryOpen=Math.sin(Math.PI*entryX)**2,exitOpen=Math.sin(Math.PI*exitX)**2,openAlong=13*(exitOpen-entryOpen),outRamp=smooth01((u-.035)/.24)*smooth01(((1-u)-.035)/.30),outboard=24*outRamp,twist=5*Math.sin(TAU*u)*outRamp,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*1.05;",
        'long natural branch tapers',
    )
    s = one(
        s,
        "const lateral=outwardSign*(outboard+twist),pos=add(add(add(add(frame.p,mul(loopForward,horizR*sn)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lateral)),mul(ringUp,gateRise));",
        "const lateral=outwardSign*(outboard+twist),basePos=add(add(add(add(frame.p,mul(loopForward,horizR*sn+openAlong)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lateral)),mul(ringUp,gateRise)),exitAlign=smooth01((u-.55)/.22),exitGuide=add(endFrame.p,mul(endH,-68*(1-u))),pos={x:basePos.x+(exitGuide.x-basePos.x)*exitAlign,y:basePos.y,z:basePos.z+(exitGuide.z-basePos.z)*exitAlign};",
        'long outgoing-road aligned loop position',
    )
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v10(Path('_site'))
