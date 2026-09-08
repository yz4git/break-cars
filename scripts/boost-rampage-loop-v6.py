"""Make the RAMPAGE 3D BOOST LOOP comfortably clearable.

This remains physical force/torque only, not a teleport or kinematic snap.
The boost preserves entry/crown speed, while the contact-patch attitude moment
is strengthened for RAMPAGE's larger, laterally displaced open ring so the
chassis follows the rotating road normal instead of staying too world-upright at
the inverted crown. DOUBLE ORBIT keeps the older generic authority; SKY keeps
its dedicated stronger controller.
"""
from pathlib import Path


def apply_rampage_loop_boost_v6(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()

    old = "if(w.mode==='racing'&&b.grounded&&rampageBoostZone(c)){const road=racePointAt(c.trackS??0),v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),target=road.kind==='loop'?24.5:22.5;if(v>0&&v<target){const force=(target-v)*b.mass*8.5;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else c.rampageBoost=false;}else c.rampageBoost=false;"
    new = "if(w.mode==='racing'&&rampageBoostZone(c)){const road=racePointAt(c.trackS??0),v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,inLoop=road.kind==='loop',span=Math.max(1,RAMPAGE_RACE_SPEC.loop.endS-RAMPAGE_RACE_SPEC.loop.startS),loopT=inLoop?Math.max(0,Math.min(1,(q-RAMPAGE_RACE_SPEC.loop.startS)/span)):0,target=inLoop?(loopT<.72?29.5:29.5-(loopT-.72)/.28*3.5):28.2,gain=inLoop?11.5:11.2,assistContact=b.grounded||inLoop;if(assistContact&&v<target){const effective=Math.max(v,-4),force=(target-effective)*b.mass*gain;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else if(assistContact&&inLoop&&loopT>.72&&v>target+.8){const trim=(v-target)*b.mass*3.8;addForce(acc,mul(road.forward,-trim));c.rampageBoost=true;}else c.rampageBoost=false;c.rampageBoostTarget=target;}else{c.rampageBoost=false;c.rampageBoostTarget=0;}"
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE boost v6: expected 1 boost block, found {count}')
    s = s.replace(old, new, 1)

    # RAMPAGE's new open ring rotates the road frame farther sideways before
    # the crown. The former generic torque let chassis-up lag at about -0.54
    # world-up even though the road itself was fully inverted. Raise only the
    # RAMPAGE branch to the authority proven by the 6DoF solo-lap diagnostic.
    old = "const tiltK=sky?(align<.20?19.0:align<.68?16.5:13.8):(align<.25?13.5:align<.72?10.5:7.2),tiltD=sky?4.7:3.25,maxTilt=(sky?19.0:12.5)*b.mass;"
    new = "const tiltK=sky?(align<.20?19.0:align<.68?16.5:13.8):rampage?(align<.20?22.0:align<.68?18.5:15.0):(align<.25?13.5:align<.72?10.5:7.2),tiltD=sky?4.7:rampage?4.8:3.25,maxTilt=(sky?19.0:rampage?22.0:12.5)*b.mass;"
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE boost v6: expected 1 loop attitude block, found {count}')
    path.write_text(s.replace(old, new, 1))


if __name__ == '__main__':
    apply_rampage_loop_boost_v6(Path('_site'))
