"""Keep the driving speedometer synchronized with the rendered rigid body.

WRECKING RACING needs the full 3D velocity magnitude because vertical motion
through a loop is real forward speed. The original v1 fix used that correct
formula but only inside the shared 10 Hz HUD refresh block, which let the
visible number lag rapid Omega speed changes by more than 15 km/h.

Keep the existing corrected 10 Hz assignment byte-for-byte because the later
RAMPAGE HUD pass intentionally anchors to it, and add a lightweight per-render
speed write before the shared HUD gate. The occasional 10 Hz rewrite therefore
uses the same value model and cannot introduce stale planar speed. Rankings,
score, damage and radar stay on their existing cadence.
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
    corrected = "const hudSpeed=world.mode==='racing'&&p.p3?.active?Math.hypot(p.p3.vx,p.p3.vy,p.p3.vz):Math.hypot(p.vx,p.vz);$('speed').querySelector('b').textContent=Math.round(hudSpeed*3.6);"
    s = one(s, legacy, corrected, 'preserve corrected 10 Hz speed write')

    hud_gate = "uiClock+=dt;if(uiClock>.1){"
    live_speed = "const liveHudSpeed=world.mode==='racing'&&player.p3?.active?Math.hypot(player.p3.vx,player.p3.vy,player.p3.vz):Math.hypot(player.vx,player.vz);$('speed').querySelector('b').textContent=Math.round(liveHudSpeed*3.6);"
    s = one(s, hud_gate, live_speed + hud_gate, 'insert per-frame speed write')

    path.write_text(s)


if __name__ == '__main__':
    apply_racing3d_speedometer_v1(Path('_site'))
