"""RAMPAGE v19: clear the Omega throat by compacting the centre HUD in-loop.

v18 gives the Omega stable, readable framing at iPhone landscape size. The
remaining visual obstruction is the tall speed/HULL stack at bottom centre,
which sits over the two open lower legs. Keep physics, camera, controls and all
non-RAMPAGE presentation unchanged. While the player is physically on the
RAMPAGE loop, collapse the damage-zone labels, shrink the HULL strip and move a
slightly smaller speed readout lower into the otherwise unused centre gap.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE Omega HUD v19 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_omega_hud_v19(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    old = "const hudSpeed=world.mode==='racing'&&p.p3?.active?Math.hypot(p.p3.vx,p.p3.vy,p.p3.vz):Math.hypot(p.vx,p.vz);$('speed').querySelector('b').textContent=Math.round(hudSpeed*3.6);"
    new = old + "const omegaHudFocus=activeCourse.id==='rampage-3d'&&world.mode==='racing'&&mode==='race'&&p.p3?.active&&trackPoint(p.trackS??0,0)?.kind==='loop';document.body.classList.toggle('rampage-omega-focus',omegaHudFocus);"
    s = one(s, old, new, 'loop focus class')
    game.write_text(s)

    style = target / 'style.css'
    css = style.read_text()
    marker = '@media(hover:none)'
    compact = """#condition,#speed{transition:bottom .18s ease,width .18s ease,opacity .18s ease}#speed b{transition:font-size .18s ease}body.rampage-omega-focus #speed{bottom:max(46px,calc(env(safe-area-inset-bottom) + 26px));opacity:.9}body.rampage-omega-focus #speed b{font-size:36px;letter-spacing:-1px}body.rampage-omega-focus #speed small{font-size:8px;letter-spacing:1.6px}body.rampage-omega-focus #condition{bottom:max(8px,env(safe-area-inset-bottom));width:132px;opacity:.82}body.rampage-omega-focus .health-title{font-size:9px;letter-spacing:1.4px}body.rampage-omega-focus .bar{height:3px;margin:4px 0 0}body.rampage-omega-focus .damage-sections{display:none}"""
    css = one(css, marker, compact + marker, 'compact HUD CSS')
    style.write_text(css)


if __name__ == '__main__':
    apply_rampage_omega_hud_v19(Path('_site'))
