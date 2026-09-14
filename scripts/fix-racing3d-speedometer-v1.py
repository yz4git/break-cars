"""Keep the driving speedometer synchronized with the rendered rigid body.

WRECKING RACING needs the full 3D velocity magnitude because vertical motion
through a loop is real forward speed. The previous v1 fix used that correct
formula, but it still lived inside the shared 10 Hz HUD refresh block. During
Omega entry/exit the rigid body can change speed quickly enough for the visible
number to lag the actual car by more than 15 km/h.

Update only the speed readout once per rendered frame. The heavier ranking,
score, damage and radar HUD remains on the existing 10 Hz cadence, so this does
not add meaningful UI work. Colosseum keeps its planar vx/vz speed formula.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Racing3D speedometer v2 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_racing3d_speedometer_v1(target: Path) -> None:
    path = target / 'game.js'
    s = path.read_text()

    legacy = "$('speed').querySelector('b').textContent=Math.round(Math.hypot(p.vx,p.vz)*3.6);"
    s = one(s, legacy, '', 'remove 10 Hz legacy speed write')

    hud_gate = "uiClock+=dt;if(uiClock>.1){"
    live_speed = "const liveHudSpeed=world.mode==='racing'&&player.p3?.active?Math.hypot(player.p3.vx,player.p3.vy,player.p3.vz):Math.hypot(player.vx,player.vz);$('speed').querySelector('b').textContent=Math.round(liveHudSpeed*3.6);"
    s = one(s, hud_gate, live_speed + hud_gate, 'insert per-frame speed write')

    path.write_text(s)


if __name__ == '__main__':
    apply_racing3d_speedometer_v1(Path('_site'))
