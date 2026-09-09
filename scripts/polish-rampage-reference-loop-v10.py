"""Make RAMPAGE read as one continuous toy-track vertical loop.

The road itself forms the stunt. There is no hidden flat chord and no separate
hoop. Keep the revolution mainly in the forward/up plane. RAMPAGE keeps the
broad authored-road cut so the stunt has room to exist outside the figure-eight,
but the visible separation is concentrated in the *lower legs*: the incoming
and outgoing ramps peel to opposite sides only near the bottom, then merge into
an almost planar vertical crown.

This matches the open toy-track loop reference: road -> rising entry leg ->
vertical loop -> descending exit leg -> road. The two lower ribbons no longer
sit on top of each other or form an X, while both gates still return smoothly to
the authored road. The outgoing guide remains short and late so it cannot drag
the descending half across the incoming figure-eight branch.

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
        "entryX=clamp((u-.055)/.44,0,1),exitX=clamp(((1-u)-.055)/.44,0,1),entryOpen=Math.sin(Math.PI*entryX)**2,exitOpen=Math.sin(Math.PI*exitX)**2,openAlong=9*(exitOpen-entryOpen),outRamp=smooth01((u-.035)/.24)*smooth01(((1-u)-.035)/.30),entrySplay=14*smooth01((u-.045)/.12)*(1-smooth01((u-.22)/.16)),exitSplay=-14*smooth01(((1-u)-.045)/.12)*(1-smooth01(((1-u)-.22)/.16)),outboard=24*outRamp,twist=3*Math.sin(TAU*u)*outRamp,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*1.05;",
        'opposed lower-leg splay without crown corkscrew',
    )
    s = one(
        s,
        "const lateral=outwardSign*(outboard+twist),pos=add(add(add(add(frame.p,mul(loopForward,horizR*sn)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lateral)),mul(ringUp,gateRise));",
        "const lateral=outwardSign*(outboard+twist+entrySplay+exitSplay),basePos=add(add(add(add(frame.p,mul(loopForward,horizR*sn+openAlong)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lateral)),mul(ringUp,gateRise)),exitAlign=smooth01((u-.74)/.20),exitGuide=add(endFrame.p,mul(endH,-36*(1-u))),pos={x:basePos.x+(exitGuide.x-basePos.x)*exitAlign,y:basePos.y,z:basePos.z+(exitGuide.z-basePos.z)*exitAlign};",
        'late short outgoing-road guide',
    )
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v10(Path('_site'))
