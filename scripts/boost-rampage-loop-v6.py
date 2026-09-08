"""Make the RAMPAGE 3D open loop comfortably clearable.

The outboard loop is substantially longer than the original authored boost zone.
Loop assistance therefore follows the generated road kind as well as the old
boost marker.  This keeps the physical assist attached to the actual loop after
geometry edits instead of silently ending halfway through the new entry/exit.

The helper remains force-only: it never writes position, orientation or track
progress.  A modest off-tangent damper keeps the car aligned to the continuously
curved road without teleporting or auto-uprighting it.
"""
from pathlib import Path


def apply_rampage_loop_boost_v6(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    old = "if(w.mode==='racing'&&b.grounded&&rampageBoostZone(c)){const road=racePointAt(c.trackS??0),v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),target=road.kind==='loop'?24.5:22.5;if(v>0&&v<target){const force=(target-v)*b.mass*8.5;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else c.rampageBoost=false;}else c.rampageBoost=false;"
    new = "if(w.mode==='racing'){const road=racePointAt(c.trackS??0),zone=rampageBoostZone(c)||road.kind==='loop';if(zone){const vel={x:b.vx,y:b.vy,z:b.vz},v=dot(vel,road.forward),L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,inLoop=road.kind==='loop',span=Math.max(1,RAMPAGE_RACE_SPEC.loop.endS-RAMPAGE_RACE_SPEC.loop.startS),loopT=inLoop?Math.max(0,Math.min(1,(q-RAMPAGE_RACE_SPEC.loop.startS)/span)):0,target=inLoop?(loopT<.72?29.5:29.5-(loopT-.72)/.28*3.5):28.2,gain=inLoop?11.5:11.2,assistContact=b.grounded||inLoop;if(inLoop){const tangent=mul(road.forward,v),off=sub(vel,tangent),guide=4.8;addForce(acc,mul(off,-b.mass*guide));}if(assistContact&&v<target){const effective=Math.max(v,-4),force=(target-effective)*b.mass*gain;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else if(assistContact&&inLoop&&loopT>.72&&v>target+.8){const trim=(v-target)*b.mass*3.8;addForce(acc,mul(road.forward,-trim));c.rampageBoost=true;}else c.rampageBoost=false;c.rampageBoostTarget=target;}else{c.rampageBoost=false;c.rampageBoostTarget=0;}}else{c.rampageBoost=false;c.rampageBoostTarget=0;}"
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE boost v6: expected 1 boost block, found {count}')
    path.write_text(s.replace(old, new, 1))


if __name__ == '__main__':
    apply_rampage_loop_boost_v6(Path('_site'))
