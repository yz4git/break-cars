"""MAYHEM TOUR v2: keep the run badge out of PIT/result screens.

Also expose a tourAudit-only countdown skip so browser screenshots can review
real driving instead of a slow headless countdown. Normal gameplay is unchanged.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v2 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_tour_v2(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    after = "function mayhemAfterEvent(){if(!mayhemActive())return;const p=world.cars[0]"
    after_new = "function mayhemAfterEvent(){if(!mayhemActive())return;const runBadge=$('tour-run-badge');if(runBadge)runBadge.remove();const p=world.cars[0]"
    s = one(s, after, after_new, 'remove run badge on result')

    badge = "if(mayhemActive()){const badge=document.createElement('div');badge.id='tour-run-badge';badge.textContent=mayhemBadgeText();document.body.appendChild(badge);}"
    badge_new = "if(mayhemActive()){const oldBadge=$('tour-run-badge');if(oldBadge)oldBadge.remove();const badge=document.createElement('div');badge.id='tour-run-badge';badge.textContent=mayhemBadgeText();document.body.appendChild(badge);}"
    s = one(s, badge, badge_new, 'dedupe run badge')

    audit = "setupMayhemMenu();\n"
    audit_new = audit + "if(new URLSearchParams(location.search).get('tourAudit')==='1')window.__breakCarsMayhemAuditStart=()=>{if(mode==='countdown'){mode='race';count=0;$('countdown').textContent='';}};\n"
    s = one(s, audit, audit_new, 'audit driving helper')
    game.write_text(s)


if __name__ == '__main__':
    apply_mayhem_tour_v2(Path('_site'))
