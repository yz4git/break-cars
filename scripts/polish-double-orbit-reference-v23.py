"""DOUBLE ORBIT v23: place two near-circular vertical loops side-by-side.

The reference toy track shows two matching vertical rings next to each other,
not one loop on each side of the circuit.  Keep the existing race topology,
physics model and loop radius, but move both loop insertions onto the same
right-hand lobe where the base road headings are already similar.  Narrow the
loop ribbon and remove the old horizontal stretch so each ring reads as a
circle instead of a wide helix.

Only DOUBLE ORBIT generated geometry is changed. RAMPAGE and SKY FORGE stay
bit-for-bit on their existing geometry branches.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT reference v23 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_reference_v23(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()

    # Keep both insertions on the same visually coherent right-hand lobe.
    # At t=.58 and 1.08 the authored base centres are about 23 m apart while
    # sharing a similar z/depth, producing the side-by-side silhouette in the
    # supplied reference instead of the previous ~100 m separation.
    s = one(
        s,
        "const RAMPAGE_LOOP_T=.44,loopCenters=doubleOrbit?[LOOP_T,3.85]:skyForge?[LOOP_T]:[RAMPAGE_LOOP_T];",
        "const RAMPAGE_LOOP_T=.44,loopCenters=doubleOrbit?[.58,1.08]:skyForge?[LOOP_T]:[RAMPAGE_LOOP_T];",
        'twin loop centres',
    )

    # Shorter gate intervals make the loop body dominate over the connecting
    # spine, and the narrowed ribbon restores the toy-track ring proportions.
    s = one(
        s,
        "const LOOP_HALF_T=(doubleOrbit||skyForge)?.18:.19,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=(!doubleOrbit&&!skyForge)?.44:1;",
        "const LOOP_HALF_T=doubleOrbit?.10:skyForge?.18:.19,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=doubleOrbit?.50:skyForge?1:.44;",
        'gate span and loop width',
    )

    # DOUBLE ORBIT used an intentionally wide 1.35R horizontal ellipse for
    # pack robustness. With the two loops now close together, a 1.00R side
    # radius gives the near-circular front silhouette of the reference image.
    s = one(
        s,
        "sideR=LOOP_R*(doubleOrbit?1.35:1.55),vertR=LOOP_R",
        "sideR=LOOP_R*(doubleOrbit?1.00:1.55),vertR=LOOP_R",
        'circular loop aspect',
    )

    # Reduce the small lower-leg hump so the ordinary road appears to flow
    # naturally into the bottom of each ring instead of climbing a visible step.
    s = one(
        s,
        "const lowerLegLift=x=>(doubleOrbit?.82:.48)*smooth01(x/.055)*(1-smooth01((x-.11)/.09));",
        "const lowerLegLift=x=>(doubleOrbit?.48:.48)*smooth01(x/.055)*(1-smooth01((x-.11)/.09));",
        'lower leg rise',
    )

    path.write_text(s)

    courses = target / 'courses.js'
    c = courses.read_text()
    c = one(
        c,
        "{id:'double-orbit',mode:'racing',name:'DOUBLE ORBIT',hint:'2連垂直ループ、約40度バンク、14m高架。空と地面が入れ替わる4周。'},",
        "{id:'double-orbit',mode:'racing',name:'DOUBLE ORBIT',hint:'横並びの2連垂直ループを連続走破。玩具コースのような真円リングを4周。'},",
        'course hint',
    )
    courses.write_text(c)


if __name__ == '__main__':
    apply_double_orbit_reference_v23(Path('_site'))
