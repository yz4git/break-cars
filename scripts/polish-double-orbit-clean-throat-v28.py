"""DOUBLE ORBIT v28: clear the twin-loop sightline at the start gate.

The twin rings begin immediately after the start line, so the generic full-width
course gantry sits inside the reference sightline and its tall posts read as
support poles through the loop openings. The supplied toy-track reference keeps
those loop throats visually open. Suppress only that decorative start gantry on
courses exposing two loops; start position, timing, physics and all other course
geometry remain untouched.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT clean throat v28 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_clean_throat_v28(target: Path) -> None:
    path = target / 'track-view.js'
    s = path.read_text()

    # apply-course-pack has already converted the original RAMPAGE 3D banner
    # into the active racing-course name by the time this late visual pass runs.
    old = "const start=trackPoint(0,0);for(const side of [-1,1]){const p=trackPoint(0,side*(TRACK.halfWidth+1.3));box(group,p.x,3.4,p.z,.42,6.8,.42,0x89938e,true);}const beam=box(group,start.x,6.6,start.z,TRACK.halfWidth*2+5,.48,.52,0xff7040,true);beam.rotation.y=start.heading;const banner=sign(activeCourse.mode==='racing'?activeCourse.name:'RAMPAGE 3D',22,2.2);banner.position.set(start.x,start.y+5.5,start.z);banner.rotation.y=start.heading+Math.PI/2;group.add(banner);"
    new = "const start=trackPoint(0,0);if((spec.loops||[]).length<2){for(const side of [-1,1]){const p=trackPoint(0,side*(TRACK.halfWidth+1.3));box(group,p.x,3.4,p.z,.42,6.8,.42,0x89938e,true);}const beam=box(group,start.x,6.6,start.z,TRACK.halfWidth*2+5,.48,.52,0xff7040,true);beam.rotation.y=start.heading;const banner=sign(activeCourse.mode==='racing'?activeCourse.name:'RAMPAGE 3D',22,2.2);banner.position.set(start.x,start.y+5.5,start.z);banner.rotation.y=start.heading+Math.PI/2;group.add(banner);}"
    s = one(s, old, new, 'start gantry visibility')
    path.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_clean_throat_v28(Path('_site'))
