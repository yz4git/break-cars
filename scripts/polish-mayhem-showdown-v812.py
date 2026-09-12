"""MAYHEM TOUR v8.12: keep the FINAL SHOWDOWN verdict fully cinematic.

The v8.11 iPhone landscape review confirmed that the Tour result, CLEAN-HIGH
replay and isolated ending card are correct, but the ordinary race HUD becomes
visible again behind the 3.6 second ending verdict. This presentation-only pass
hides the mounted driving HUD while the existing v8.10 ending-active class is
present. The UI restores automatically when that class is removed.
"""
from pathlib import Path


def apply_mayhem_showdown_v812(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += "\nwindow.__breakCarsMayhemV812=true;\n"
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.12: FINAL SHOWDOWN verdict owns the entire frame. */
body.mayhem-showdown-ending-active #hud,
body.mayhem-showdown-ending-active #driving,
body.mayhem-showdown-ending-active #hunt-nav,
body.mayhem-showdown-ending-active #mayhem-director,
body.mayhem-showdown-ending-active #mayhem-rival-marker,
body.mayhem-showdown-ending-active #tour-run-badge{
  opacity:0!important;
  visibility:hidden!important;
  pointer-events:none!important;
}
body.mayhem-showdown-ending-active #mayhem-showdown-ending{
  opacity:1!important;
  visibility:visible!important;
}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_showdown_v812(Path('_site'))
