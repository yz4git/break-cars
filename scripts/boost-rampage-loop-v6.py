"""Make the RAMPAGE 3D open loop comfortably clearable.

The outboard loop is substantially longer than the original authored boost zone.
Loop assistance therefore follows the generated road kind as well as the old
boost marker. This keeps the physical assist attached to the actual loop after
geometry edits instead of silently ending halfway through the new entry/exit.

The helper remains force/torque-only: it never writes position, orientation,
velocity or track progress. The speed controller still becomes firmer only on
the steep ASCENDING leg and gravity compensation remains ascent-only, so the
exit does not inherit artificial energy. Around the upper half of the loop we
instead strengthen tyre-like velocity alignment, road adhesion and chassis
attitude torque. That keeps a fast car following the authored ribbon through the
crown without turning the loop into a kinematic rail.

The helper is explicitly scoped to RAMPAGE (plus the legacy classic test harness)
so SKY FORGE and DOUBLE ORBIT physics are unchanged.
"""
from pathlib import Path


def apply_rampage_loop_boost_v6(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    old = "if(w.mode==='racing'&&b.grounded&&rampageBoostZone(c)){const road=racePointAt(c.trackS??0),v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),target=road.kind==='loop'?24.5:22.5;if(v>0&&v<target){const force=(target-v)*b.mass*8.5;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else c.rampageBoost=false;}else c.rampageBoost=false;"
    new = "if(w.mode==='racing'&&(boostCourse.id==='rampage-3d'||boostCourse.id==='classic')){const road=racePointAt(c.trackS??0),zone=rampageBoostZone(c)||road.kind==='loop';if(zone){const vel={x:b.vx,y:b.vy,z:b.vz},v=dot(vel,road.forward),L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,inLoop=road.kind==='loop',span=Math.max(1,RAMPAGE_RACE_SPEC.loop.endS-RAMPAGE_RACE_SPEC.loop.startS),loopT=inLoop?Math.max(0,Math.min(1,(q-RAMPAGE_RACE_SPEC.loop.startS)/span)):0,target=inLoop?(loopT<.12?31.0:loopT<.72?30.2:30.2-(loopT-.72)/.28*4.2):31.5,steepClimb=inLoop&&loopT<.58&&road.forward.y>.35,upperLoop=inLoop&&loopT>.20&&loopT<.78,crownBand=inLoop&&loopT>.30&&loopT<.70,gain=inLoop?(loopT<.12?15.0:steepClimb?18.5:12.5):15.5,assistContact=b.grounded||inLoop;if(inLoop){const tangent=mul(road.forward,v),off=sub(vel,tangent),guide=crownBand?(b.groundedWheels===0?12.0:10.2):upperLoop?8.4:6.2;addForce(acc,mul(off,-b.mass*guide));const centerErr={x:b.px-road.x,y:b.py-road.y,z:b.pz-road.z},sideErr=dot(centerErr,road.right),sideVel=dot(vel,road.right),normalErr=dot(centerErr,road.up)-COM_VISUAL_Y,normalVel=dot(vel,road.up),sideAccel=Math.max(-44,Math.min(44,-sideErr*(upperLoop?7.2:6.2)-sideVel*(upperLoop?5.8:5.2))),normalAccel=Math.max(-48,Math.min(34,-normalErr*(upperLoop?8.8:7.0)-normalVel*(upperLoop?3.8:3.0)-(upperLoop?11.5:9.0)));addForce(acc,mul(road.right,sideAccel*b.mass));addForce(acc,mul(road.up,normalAccel*b.mass));if(upperLoop){const bu=bodyUp(b),omega={x:b.wx,y:b.wy,z:b.wz},align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),tiltK=crownBand?(align<.20?15.0:12.5):9.0,tiltD=3.5,maxTilt=(crownBand?14.0:10.5)*b.mass;acc.tx+=Math.max(-maxTilt,Math.min(maxTilt,(tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass));acc.ty+=Math.max(-maxTilt,Math.min(maxTilt,(tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass));acc.tz+=Math.max(-maxTilt,Math.min(maxTilt,(tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass));}if(steepClimb)addForce(acc,mul(road.forward,road.forward.y*9.81*b.mass));}if(assistContact&&v<target){const effective=Math.max(v,-4),force=(target-effective)*b.mass*gain;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else if(assistContact&&inLoop&&loopT>.72&&v>target+.8){const trim=(v-target)*b.mass*3.8;addForce(acc,mul(road.forward,-trim));c.rampageBoost=true;}else c.rampageBoost=false;c.rampageBoostTarget=target;}else{c.rampageBoost=false;c.rampageBoostTarget=0;}}else{c.rampageBoost=false;c.rampageBoostTarget=0;}"
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
