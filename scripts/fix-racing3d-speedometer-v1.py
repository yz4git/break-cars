"""Use true rigid-body speed for the Wrecking Racing 3D speedometer.

The legacy HUD measures only ``sqrt(vx^2 + vz^2)``. That is correct on a flat
road but reports near-zero speed when a car is moving mostly vertically through
RAMPAGE's Omega. The 3D physics body already carries vx/vy/vz, so racing mode
should display its full velocity magnitude. Colosseum behavior is unchanged.
"""
from pathlib import Path


def apply_racing3d_speedometer_v1(target: Path) -> None:
    path = target / 'game.js'
    s = path.read_text()
    old = "$('speed').querySelector('b').textContent=Math.round(Math.hypot(p.vx,p.vz)*3.6);"
    new = "const hudSpeed=world.mode==='racing'&&p.p3?.active?Math.hypot(p.p3.vx,p.p3.vy,p.p3.vz):Math.hypot(p.vx,p.vz);$('speed').querySelector('b').textContent=Math.round(hudSpeed*3.6);"
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f'Racing3D speedometer v1: expected 1 match, found {n}')
    path.write_text(s.replace(old, new, 1))


if __name__ == '__main__':
    apply_racing3d_speedometer_v1(Path('_site'))
