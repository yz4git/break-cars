"""MAYHEM TOUR v8.4: keep both duel cars inside IMPACT CLOSE.

The final real-browser review of v8.3 showed the three-shot grammar working, but
an unusually wide player/rival separation can push the player to the lower edge
of IMPACT CLOSE. Keep the tight crash framing for close impacts while adapting
camera distance and FOV to live separation when the duel has opened up.
Gameplay, replay selection/timing, and physics are unchanged.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v8.4 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_product_v84(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    old = "else{nextShot='IMPACT CLOSE';const d=clamp(5.2+separation*.30,5.8,8.8);mayhemReplayDesired.copy(mayhemReplayMid).addScaledVector(mayhemReplaySide,-d).addScaledVector(mayhemReplayForward,-.8);mayhemReplayDesired.y+=2.05;mayhemReplayTarget.copy(mayhemReplayMid);mayhemReplayTarget.y+=.65;fov=44;}"
    new = "else{nextShot='IMPACT CLOSE';const d=clamp(6.1+separation*.58,6.8,14.6);mayhemReplayDesired.copy(mayhemReplayMid).addScaledVector(mayhemReplaySide,-d).addScaledVector(mayhemReplayForward,-.35);mayhemReplayDesired.y+=2.35+Math.min(1.2,separation*.045);mayhemReplayTarget.copy(mayhemReplayMid);mayhemReplayTarget.y+=.72;fov=clamp(46+separation*.38,46,56);}"
    s = one(s, old, new, 'adaptive impact framing')
    game.write_text(s)


if __name__ == '__main__':
    apply_mayhem_product_v84(Path('_site'))
