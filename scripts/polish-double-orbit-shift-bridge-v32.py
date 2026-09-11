"""DOUBLE ORBIT v32: move the bridge crest out of the twin-ring sightline.

v31 narrows the tall bridge envelope but its peak still sits behind loop two from
the authored DOUBLE ORBIT camera. Keep the >14 m bridge stunt, jump timing, bank,
loops and U-return geometry intact; only move the DOUBLE ORBIT Gaussian bridge
crest later along the lower return so both ring openings read cleanly like the
supplied toy-track reference. Other racing courses are unchanged.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT shift bridge v32 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_shift_bridge_v32(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()
    s = one(
        s,
        "gauss(t,Math.PI,doubleOrbit?.32:skyForge?.36:.28)",
        "gauss(t,doubleOrbit?4.28:Math.PI,doubleOrbit?.26:skyForge?.36:.28)",
        'bridge crest position',
    )
    path.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_shift_bridge_v32(Path('_site'))
