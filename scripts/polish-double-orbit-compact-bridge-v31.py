"""DOUBLE ORBIT v31: compact the tall bridge behind the twin-loop sightline.

The bridge peak is an intentional stunt feature and remains above 14 m, but the
wide Gaussian crest sits almost directly behind loop two from the authored camera.
Narrow only DOUBLE ORBIT's bridge envelope so the peak and over/under gameplay are
preserved while substantially less elevated road fills the open ring sightline.
Other courses, loop geometry, jump timing, banking, controls and progress are
unchanged.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT compact bridge v31 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_compact_bridge_v31(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()
    s = one(
        s,
        "gauss(t,Math.PI,doubleOrbit?.43:skyForge?.36:.28)",
        "gauss(t,Math.PI,doubleOrbit?.32:skyForge?.36:.28)",
        'bridge envelope',
    )
    path.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_compact_bridge_v31(Path('_site'))
