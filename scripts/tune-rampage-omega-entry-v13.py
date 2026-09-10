"""Physically align RAMPAGE velocity through the C2 Omega entry leg.

The planar-Omega geometry is intentionally left untouched.  The lower C2 leg
rotates the road tangent quickly enough that a fast car can carry cross-tangent
velocity through the first part of the loop.  This pass only changes force
guidance in that first 20% of RAMPAGE.

No position, orientation, velocity, track progress, recovery state, or geometry
is written directly. The rigid body is steered with force toward the current
road tangent plus a small look-ahead component.
"""
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE Omega entry v13 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_omega_entry_v13(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()

    s = replace_once(
        s,
        "steepClimb=inLoop&&loopT<.58&&road.forward.y>.35,curveGuide=inLoop&&loopT>.18,contactArc=inLoop&&loopT>.20",
        "steepClimb=inLoop&&loopT<.58&&road.forward.y>.35,entryTransition=inLoop&&loopT<.20,curveGuide=inLoop,contactArc=inLoop&&loopT>.20",
        'entry transition scope',
    )
    s = replace_once(
        s,
        "lookAhead=curveGuide?(exitBlend?Math.min(4.0,Math.max(1.25,speed*.16)):midDescent?Math.min(3.2,Math.max(1.0,speed*.100)):Math.min(2.4,Math.max(.75,speed*.042))):0",
        "lookAhead=curveGuide?(exitBlend?Math.min(4.0,Math.max(1.25,speed*.16)):midDescent?Math.min(3.2,Math.max(1.0,speed*.100)):entryTransition?Math.min(2.6,Math.max(.9,speed*.055)):Math.min(2.4,Math.max(.75,speed*.042))):0",
        'entry lookahead',
    )
    s = replace_once(
        s,
        "guideForward=curveGuide?norm(add(mul(road.forward,exitBlend?.42:.60),mul(ahead.forward,exitBlend?.58:.40))):road.forward",
        "guideForward=curveGuide?norm(add(mul(road.forward,exitBlend?.42:entryTransition?.84:.60),mul(ahead.forward,exitBlend?.58:entryTransition?.16:.40))):road.forward",
        'entry tangent blend',
    )
    s = replace_once(
        s,
        "guide=crownBand?(b.groundedWheels===0?12.0:10.2):contactArc?(exitBlend?2.0:8.4):6.2",
        "guide=entryTransition?20.0:crownBand?(b.groundedWheels===0?12.0:10.2):contactArc?(exitBlend?2.0:8.4):6.2",
        'entry cross-velocity damping',
    )
    s = replace_once(
        s,
        "turnBase=exitBlend?26:12,turnScale=exitBlend?1.55:1.05,turnCap=exitBlend?110:70",
        "turnBase=exitBlend?26:entryTransition?25:12,turnScale=exitBlend?1.55:entryTransition?1.35:1.05,turnCap=exitBlend?110:entryTransition?96:70",
        'entry steering force',
    )

    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_omega_entry_v13(Path('_site'))
