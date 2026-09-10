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
import importlib.util


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE Omega entry v13 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def load_patch(filename: str, module_name: str):
    patch_path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, patch_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        "guideForward=curveGuide?norm(add(mul(road.forward,exitBlend?.42:entryTransition?.925:.60),mul(ahead.forward,exitBlend?.58:entryTransition?.075:.40))):road.forward",
        'entry tangent blend',
    )
    s = replace_once(
        s,
        "guide=crownBand?(b.groundedWheels===0?12.0:10.2):contactArc?(exitBlend?2.0:8.4):6.2",
        "guide=entryTransition?23.2:crownBand?(b.groundedWheels===0?12.0:10.2):contactArc?(exitBlend?2.0:8.4):6.2",
        'entry cross-velocity damping',
    )
    s = replace_once(
        s,
        "turnBase=exitBlend?26:12,turnScale=exitBlend?1.55:1.05,turnCap=exitBlend?110:70",
        "turnBase=exitBlend?26:entryTransition?29.2:12,turnScale=exitBlend?1.55:entryTransition?1.50:1.05,turnCap=exitBlend?110:entryTransition?114:70",
        'entry steering force',
    )
    path.write_text(s)

    # Final camera presentation uses the exact v12 geometry but an oblique view
    # so its physically separated lower legs stay visually separated as an Omega.
    camera = load_patch('polish-rampage-omega-camera-v15.py', 'break_cars_rampage_omega_camera_v15')
    camera.apply_rampage_omega_camera_v15(target)

    # Audit-only start comes last and does not affect ordinary gameplay URLs.
    audit = load_patch('add-rampage-live-audit-start-v14.py', 'break_cars_rampage_live_audit_v14')
    audit.apply_rampage_live_audit_start_v14(target)


if __name__ == '__main__':
    apply_rampage_omega_entry_v13(Path('_site'))
