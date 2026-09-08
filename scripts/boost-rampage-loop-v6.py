"""Make the RAMPAGE 3D BOOST LOOP comfortably clearable.

This remains a physical forward force, not a teleport or kinematic snap.  The
approach target is raised to about 99 km/h and the lower/middle loop target to
about 106 km/h.  The final quarter of the loop gently tapers toward about
94 km/h so the car clears the stunt with margin without launching off the
following course.  Cars slowed to zero or nudged slightly backward are also
recovered by the strip.  While physically inside the loop, the strip keeps
applying its forward force through brief suspension-unloaded moments at the
inverted crown so a taller/open loop cannot lose the assist for a few frames.
"""
from pathlib import Path


def apply_rampage_loop_boost_v6(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    old = "if(w.mode==='racing'&&b.grounded&&rampageBoostZone(c)){const road=racePointAt(c.trackS??0),v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),target=road.kind==='loop'?24.5:22.5;if(v>0&&v<target){const force=(target-v)*b.mass*8.5;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else c.rampageBoost=false;}else c.rampageBoost=false;"
    new = "if(w.mode==='racing'&&rampageBoostZone(c)){const road=racePointAt(c.trackS??0),v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,inLoop=road.kind==='loop',span=Math.max(1,RAMPAGE_RACE_SPEC.loop.endS-RAMPAGE_RACE_SPEC.loop.startS),loopT=inLoop?Math.max(0,Math.min(1,(q-RAMPAGE_RACE_SPEC.loop.startS)/span)):0,target=inLoop?(loopT<.72?29.5:29.5-(loopT-.72)/.28*3.5):27.5,gain=inLoop?11.5:10.5,assistContact=b.grounded||inLoop;if(assistContact&&v<target){const effective=Math.max(v,-4),force=(target-effective)*b.mass*gain;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else if(assistContact&&inLoop&&loopT>.72&&v>target+.8){const trim=(v-target)*b.mass*3.8;addForce(acc,mul(road.forward,-trim));c.rampageBoost=true;}else c.rampageBoost=false;c.rampageBoostTarget=target;}else{c.rampageBoost=false;c.rampageBoostTarget=0;}"
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE boost v6: expected 1 boost block, found {count}')
    path.write_text(s.replace(old, new, 1))


if __name__ == '__main__':
    apply_rampage_loop_boost_v6(Path('_site'))
