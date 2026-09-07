"""Make the RAMPAGE 3D BOOST LOOP comfortably clearable.

This remains a physical forward force, not a teleport or kinematic snap.  The
approach target is about 103 km/h and the loop target about 112 km/h.  The
strip also recovers cars that were slowed to zero or nudged slightly backward
inside the stunt zone.
"""
from pathlib import Path


def apply_rampage_loop_boost_v6(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    old = "if(w.mode==='racing'&&b.grounded&&rampageBoostZone(c)){const road=racePointAt(c.trackS??0),v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),target=road.kind==='loop'?24.5:22.5;if(v>0&&v<target){const force=(target-v)*b.mass*8.5;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else c.rampageBoost=false;}else c.rampageBoost=false;"
    new = "if(w.mode==='racing'&&b.grounded&&rampageBoostZone(c)){const road=racePointAt(c.trackS??0),v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),inLoop=road.kind==='loop',target=inLoop?31:28.5,gain=inLoop?14:12;if(v<target){const effective=Math.max(v,-4),force=(target-effective)*b.mass*gain;addForce(acc,mul(road.forward,force));c.rampageBoost=true;c.rampageBoostTarget=target;}else{c.rampageBoost=false;c.rampageBoostTarget=target;}}else{c.rampageBoost=false;c.rampageBoostTarget=0;}"
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE boost v6: expected 1 boost block, found {count}')
    path.write_text(s.replace(old, new, 1))


if __name__ == '__main__':
    apply_rampage_loop_boost_v6(Path('_site'))
