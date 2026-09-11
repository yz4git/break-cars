"""MAYHEM TOUR v8.1: visual-review composition fixes.

The first v8 browser screenshots exposed two presentation-only problems:
- a distant screen-space RIVAL marker could climb into the compact Director HUD;
- ACT names were repeated in both the upper-left mode tag and lower-right caption.

Keep the upper-left ACT tag as the primary chapter read, move the act stakes to
the lower-right caption, restore the short course goal to a single line, and
reserve a clean top band below the Director HUD for the RIVAL marker.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8.1 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_product_v81(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    s = one(
        s,
        "$('mode-lead').textContent=`${def.goal} · ${act.stakes}`;",
        "$('mode-lead').textContent=def.goal;",
        'single-line event goal',
    )
    s = one(
        s,
        "$('arena-caption').innerHTML=`${act.short}<span>${def.name} · EVENT ${event+1}/${MAYHEM_EVENTS.length}</span>`;",
        "$('arena-caption').innerHTML=`${act.stakes}<span>${def.name} · EVENT ${event+1}/${MAYHEM_EVENTS.length}</span>`;",
        'lower-right stakes caption',
    )
    s = one(
        s,
        "y=clamp((-mayhemRivalScreen.y*.5+.5)*innerHeight,92,innerHeight-86),rh=",
        "y=clamp((-mayhemRivalScreen.y*.5+.5)*innerHeight,132,innerHeight-86),rh=",
        'RIVAL marker top safe band',
    )
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += "\n/* v8.1: keep world-space RIVAL marker below the Director readout */\n#mayhem-rival-marker{max-width:min(38vw,190px)}\n"
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_product_v81(Path('_site'))
