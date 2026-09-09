"""Make RAMPAGE read as one continuous toy-track vertical loop.

The road itself forms the stunt. There is no hidden flat chord and no separate
hoop. Keep the revolution mainly in the forward/up plane. The whole loop bows
away from the unrelated figure-eight road only after a straight gate lead, and
the two lower branches get opposite forward offsets so their ribbons never form
an X.

The final descending leg is not allowed to wander and then snap back at the
last gate. Its X/Z centerline is C1-blended onto a guide ray traced backward
from the outgoing authored road. The last portion therefore already points in
the exact outgoing-road direction before reaching the gate, matching the toy-
track reference where the loop simply becomes the road again.

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
        "entryX=clamp((u-.055)/.44,0,1),exitX=clamp(((1-u)-.055)/.44,0,1),entryOpen=Math.sin(Math.PI*entryX)**2,exitOpen=Math.sin(Math.PI*exitX)**2,openAlong=13*(exitOpen-entryOpen),outRamp=smooth01((u-.035)/.24)*smooth01(((1-u)-.035)/.30),outboard=24*outRamp,twist=5*Math.sin(TAU*u)*outRamp,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*1.05;",
        'long natural branch tapers',
    )
    s = one(
        s,
        "const lateral=outwardSign*(outboard+twist),pos=add(add(add(add(frame.p,mul(loopForward,horizR*sn)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lateral)),mul(ringUp,gateRise));",
        "const lateral=outwardSign*(outboard+twist),basePos=add(add(add(add(frame.p,mul(loopForward,horizR*sn+openAlong)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lateral)),mul(ringUp,gateRise)),exitAlign=smooth01((u-.72)/.23),exitGuide=add(endFrame.p,mul(endH,-55*(1-u))),pos={x:basePos.x+(exitGuide.x-basePos.x)*exitAlign,y:basePos.y,z:basePos.z+(exitGuide.z-basePos.z)*exitAlign};",
        'outgoing-road aligned loop position',
    )
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v10(Path('_site'))
