"""DOUBLE ORBIT v28: clear the twin-loop sightline after the v29-v32 road passes.

DOUBLE ORBIT puts its twin rings near the circuit's central over/under crossing.
Generic start-gate posts, bridge support columns and distant floodlight towers can
therefore read as poles driven through the ring openings. The toy-track reference
keeps those throats visually open. First apply the v29 broad U-shaped outer return,
v30 lowers the visible roll through its first U turn, v31 compacts the tall bridge
footprint, and v32 moves that compact bridge crest away from the twin-ring camera
before this pass removes decorative/support obstructions only for DOUBLE ORBIT.
Other course geometry, controls and progress remain untouched.
"""
from pathlib import Path
import importlib.util


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT clean throat v28 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_u_return(target: Path) -> None:
    module_path = Path(__file__).with_name('polish-double-orbit-u-return-v29.py')
    spec = importlib.util.spec_from_file_location('break_cars_double_orbit_u_return_v29', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_double_orbit_u_return_v29(target)


def apply_low_return_bank(target: Path) -> None:
    module_path = Path(__file__).with_name('polish-double-orbit-low-return-bank-v30.py')
    spec = importlib.util.spec_from_file_location('break_cars_double_orbit_low_return_bank_v30', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_double_orbit_low_return_bank_v30(target)


def apply_compact_bridge(target: Path) -> None:
    module_path = Path(__file__).with_name('polish-double-orbit-compact-bridge-v31.py')
    spec = importlib.util.spec_from_file_location('break_cars_double_orbit_compact_bridge_v31', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_double_orbit_compact_bridge_v31(target)


def apply_shift_bridge(target: Path) -> None:
    module_path = Path(__file__).with_name('polish-double-orbit-shift-bridge-v32.py')
    spec = importlib.util.spec_from_file_location('break_cars_double_orbit_shift_bridge_v32', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_double_orbit_shift_bridge_v32(target)


def apply_double_orbit_clean_throat_v28(target: Path) -> None:
    # v25 invokes this pass after v27, so this is the final safe point to replace
    # only the road after loop two while preserving the proven twin-loop geometry.
    apply_u_return(target)
    apply_low_return_bank(target)
    apply_compact_bridge(target)
    apply_shift_bridge(target)

    path = target / 'track-view.js'
    s = path.read_text()

    # apply-course-pack has already converted the original RAMPAGE 3D banner
    # into the active racing-course name by the time this late visual pass runs.
    old = "const start=trackPoint(0,0);for(const side of [-1,1]){const p=trackPoint(0,side*(TRACK.halfWidth+1.3));box(group,p.x,3.4,p.z,.42,6.8,.42,0x89938e,true);}const beam=box(group,start.x,6.6,start.z,TRACK.halfWidth*2+5,.48,.52,0xff7040,true);beam.rotation.y=start.heading;const banner=sign(activeCourse.mode==='racing'?activeCourse.name:'RAMPAGE 3D',22,2.2);banner.position.set(start.x,start.y+5.5,start.z);banner.rotation.y=start.heading+Math.PI/2;group.add(banner);"
    new = "const start=trackPoint(0,0);if(activeCourse.id!=='double-orbit'){for(const side of [-1,1]){const p=trackPoint(0,side*(TRACK.halfWidth+1.3));box(group,p.x,3.4,p.z,.42,6.8,.42,0x89938e,true);}const beam=box(group,start.x,6.6,start.z,TRACK.halfWidth*2+5,.48,.52,0xff7040,true);beam.rotation.y=start.heading;const banner=sign(activeCourse.mode==='racing'?activeCourse.name:'RAMPAGE 3D',22,2.2);banner.position.set(start.x,start.y+5.5,start.z);banner.rotation.y=start.heading+Math.PI/2;group.add(banner);}"
    s = one(s, old, new, 'start gantry visibility')

    # The elevated return road itself stays intact, but its generic vertical
    # support pair sits almost exactly on the camera-to-loop sightline.
    bridge_old = "const bridge=trackPoint(spec.bridge.s,0);for(const lane of [-7.3,7.3]){const p=trackPoint(spec.bridge.s,lane);box(group,p.x,(p.y-2.25)/2,p.z,.52,Math.max(2,p.y+1.5),.52,0x46545d,true);box(group,p.x,p.y-.65,p.z,2.1,.42,2.1,0x5a666a,true);}if((spec.loopHalfWidth||TRACK.halfWidth)>TRACK.halfWidth*.7){const crossSign=sign('OVER / UNDER SMASH',20,2.2);crossSign.position.set(bridge.x,bridge.y+4.3,bridge.z);crossSign.rotation.y=bridge.heading+Math.PI/2;group.add(crossSign);}"
    bridge_new = "const bridge=trackPoint(spec.bridge.s,0);if(activeCourse.id!=='double-orbit')for(const lane of [-7.3,7.3]){const p=trackPoint(spec.bridge.s,lane);box(group,p.x,(p.y-2.25)/2,p.z,.52,Math.max(2,p.y+1.5),.52,0x46545d,true);box(group,p.x,p.y-.65,p.z,2.1,.42,2.1,0x5a666a,true);}if((spec.loopHalfWidth||TRACK.halfWidth)>TRACK.halfWidth*.7){const crossSign=sign('OVER / UNDER SMASH',20,2.2);crossSign.position.set(bridge.x,bridge.y+4.3,bridge.z);crossSign.rotation.y=bridge.heading+Math.PI/2;group.add(crossSign);}"
    s = one(s, bridge_old, bridge_new, 'bridge support visibility')

    # Stadium floodlight masts are useful on the other courses, but one aligns
    # inside the first ring from the authored DOUBLE ORBIT chase camera.
    lights_old = "for(const x of [-82,82])for(const z of [-45,45]){box(group,x,10,z,.4,20,.4,0x344451);box(group,x,20,z,5,1.4,.8,0xeff1e4);}"
    lights_new = "if(activeCourse.id!=='double-orbit')for(const x of [-82,82])for(const z of [-45,45]){box(group,x,10,z,.4,20,.4,0x344451);box(group,x,20,z,5,1.4,.8,0xeff1e4);}"
    s = one(s, lights_old, lights_new, 'floodlight visibility')

    path.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_clean_throat_v28(Path('_site'))
