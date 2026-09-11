"""DOUBLE ORBIT v30: keep the outer U return visually low.

The toy-track reference has a broad, low return after the two vertical rings.
The authored DOUBLE ORBIT bank profile intentionally reaches about 41 degrees,
but carrying that full roll through the first U turn makes the outside edge read
like a tall wall from the loop-stage camera.  Keep that stunt-bank contract on
the later return, while reducing only the first U turn and easing the roll back
in after the road has become the lower straight.

Geometry, elevation, loop physics, progress and all other courses are unchanged.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT low-return bank v30 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_low_return_bank_v30(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()
    old = " const p=doubleOrbitReturnAt(t);return{...base,x:p.x,y:p.y+base.y,z:p.z,bank:(base.bank||0)};"
    new = " const p=doubleOrbitReturnAt(t),turnFade=t<doubleOrbitReturnT1?.18:t<doubleOrbitReturnT1+.58?.18+.82*doubleOrbitSmooth((t-doubleOrbitReturnT1)/.58):1;return{...base,x:p.x,y:p.y+base.y,z:p.z,bank:(base.bank||0)*turnFade};"
    s = one(s, old, new, 'first U-turn roll attenuation')
    path.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_low_return_bank_v30(Path('_site'))
