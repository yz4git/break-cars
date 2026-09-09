"""Make the RAMPAGE 3D open loop comfortably clearable.

The outboard loop is substantially longer than the original authored boost zone.
Loop assistance therefore follows the generated road kind as well as the old
boost marker. This keeps the physical assist attached to the actual loop after
geometry edits instead of silently ending halfway through the new entry/exit.

The helper remains force-only: it never writes position, orientation or track
progress. The loop guide damps velocity that points across the ribbon and uses a
suspension-like normal spring plus a modest constant road-adhesion load. That
load is important at the crown of the now more natural vertical loop: a car that
enters at the lower regression-test speed stays physically pressed toward the
road long enough for its chassis to follow the inverted surface rather than
coasting partially detached through the top.  The middle-loop drive target is
only slightly above the previous value so the slowest loaded sample retains a
small contact-speed reserve without turning the loop into a runaway boost.

The helper is explicitly scoped to RAMPAGE (plus the legacy classic test harness)
so SKY FORGE and DOUBLE ORBIT physics are unchanged.
"""
from pathlib import Path


def apply_rampage_loop_boost_v6(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    old = "if(w.mode==='racing'&&b.grounded&&rampageBoostZone(c)){const road=racePointAt(c.trackS??0),v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),target=road.kind==='loop'?24.5:22.5;if(v>0&&v<target){const force=(target-v)*b.mass*8.5;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else c.rampageBoost=false;}else c.rampageBoost=false;"
    new = "if(w.mode==='racing'&&(boostCourse.id==='rampage-3d'||boostCourse.id==='classic')){const road=racePointAt(c.trackS??0),zone=rampageBoostZone(c)||road.kind==='loop';if(zone){const vel={x:b.vx,y:b.vy,z:b.vz},v=dot(vel,road.forward),L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,inLoop=road.kind==='loop',span=Math.max(1,RAMPAGE_RACE_SPEC.loop.endS-RAMPAGE_RACE_SPEC.loop.startS),loopT=inLoop?Math.max(0,Math.min(1,(q-RAMPAGE_RACE_SPEC.loop.startS)/span)):0,target=inLoop?(loopT<.12?31.0:loopT<.72?30.2:30.2-(loopT-.72)/.28*4.2):31.5,gain=inLoop?(loopT<.12?15.0:12.5):15.5,assistContact=b.grounded||inLoop;if(inLoop){const tangent=mul(road.forward,v),off=sub(vel,tangent),guide=6.2;addForce(acc,mul(off,-b.mass*guide));const centerErr={x:b.px-road.x,y:b.py-road.y,z:b.pz-road.z},sideErr=dot(centerErr,road.right),sideVel=dot(vel,road.right),normalErr=dot(centerErr,road.up)-COM_VISUAL_Y,normalVel=dot(vel,road.up),sideAccel=Math.max(-42,Math.min(42,-sideErr*6.2-sideVel*5.2)),normalAccel=Math.max(-42,Math.min(32,-normalErr*7.0-normalVel*3.0-9.0));addForce(acc,mul(road.right,sideAccel*b.mass));addForce(acc,mul(road.up,normalAccel*b.mass));}if(assistContact&&v<target){const effective=Math.max(v,-4),force=(target-effective)*b.mass*gain;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else if(assistContact&&inLoop&&loopT>.72&&v>target+.8){const trim=(v-target)*b.mass*3.8;addForce(acc,mul(road.forward,-trim));c.rampageBoost=true;}else c.rampageBoost=false;c.rampageBoostTarget=target;}else{c.rampageBoost=false;c.rampageBoostTarget=0;}}else{c.rampageBoost=false;c.rampageBoostTarget=0;}"
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE boost v6: expected 1 boost block, found {count}')
    s = s.replace(old, new, 1)
    # Course-pack later prepends its own courseSurface import; duplicate imports
    # from the same module are valid and keeping a dedicated alias makes the
    # RAMPAGE-only ownership of this assist explicit.
    s = "import {activeCourse as boostCourse} from './courses.js';\n" + s
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_loop_boost_v6(Path('_site'))
