"""Make the RAMPAGE 3D open loop comfortably clearable.

Loop assistance follows the generated road kind as well as the old authored
boost marker, and remains force/torque-only. The validated Omega-loop tuning
keeps the proven 0.042*speed look-ahead around most of the loop, but extends
look-ahead to 0.10*speed only through the steep mid-descent. This anticipates
the rapidly rotating road tangent after the crown, preserving contact-speed
margin without changing position, orientation, track progress, or the authored
Omega geometry. SKY FORGE and DOUBLE ORBIT are deliberately untouched.
"""
from pathlib import Path


def apply_rampage_loop_boost_v6(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    old = "if(w.mode==='racing'&&b.grounded&&rampageBoostZone(c)){const road=racePointAt(c.trackS??0),v=dot({x:b.vx,y:b.vy,z:b.vz},road.forward),target=road.kind==='loop'?24.5:22.5;if(v>0&&v<target){const force=(target-v)*b.mass*8.5;addForce(acc,mul(road.forward,force));c.rampageBoost=true;}else c.rampageBoost=false;}else c.rampageBoost=false;"
    new = "if(w.mode==='racing'&&(boostCourse.id==='rampage-3d'||boostCourse.id==='classic')){const road=racePointAt(c.trackS??0),zone=rampageBoostZone(c)||road.kind==='loop';if(zone){const vel={x:b.vx,y:b.vy,z:b.vz},v=dot(vel,road.forward),speed=Math.hypot(vel.x,vel.y,vel.z),L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,inLoop=road.kind==='loop',span=Math.max(1,RAMPAGE_RACE_SPEC.loop.endS-RAMPAGE_RACE_SPEC.loop.startS),loopT=inLoop?Math.max(0,Math.min(1,(q-RAMPAGE_RACE_SPEC.loop.startS)/span)):0,target=inLoop?(loopT<.12?31.0:loopT<.72?30.2:30.2-(loopT-.72)/.28*4.2):31.5,steepClimb=inLoop&&loopT<.58&&road.forward.y>.35,curveGuide=inLoop&&loopT>.18,contactArc=inLoop&&loopT>.20,crownBand=inLoop&&loopT>.30&&loopT<.70,midDescent=inLoop&&loopT>.43&&loopT<.66&&road.forward.y<-.20,exitBlend=inLoop&&loopT>.72,lookAhead=curveGuide?(exitBlend?Math.min(4.0,Math.max(1.25,speed*.16)):midDescent?Math.min(3.2,Math.max(1.0,speed*.100)):Math.min(2.4,Math.max(.75,speed*.042))):0,ahead=curveGuide?racePointAt(Math.min(RAMPAGE_RACE_SPEC.loop.endS,q+lookAhead)):road,guideForward=curveGuide?norm(add(mul(road.forward,exitBlend?.42:.60),mul(ahead.forward,exitBlend?.58:.40))):road.forward,gain=inLoop?(loopT<.12?15.0:steepClimb?18.5:exitBlend&&v<18?20.0:12.5):15.5,assistContact=b.grounded||inLoop;if(inLoop){const tangent=mul(road.forward,v),off=sub(vel,tangent),guide=crownBand?(b.groundedWheels===0?12.0:10.2):contactArc?(exitBlend?2.0:8.4):6.2;if(curveGuide&&speed>5){const velDir=mul(vel,1/speed),along=dot(velDir,guideForward),steerVec=sub(guideForward,mul(velDir,along)),steerLen=Math.hypot(steerVec.x,steerVec.y,steerVec.z);if(steerLen>.01){const radius=Math.max(4,RAMPAGE_RACE_SPEC.loop.radius),turnBase=exitBlend?26:12,turnScale=exitBlend?1.55:1.05,turnCap=exitBlend?110:70,turnAccel=Math.min(turnCap,turnBase+speed*speed/radius*turnScale)*steerLen;addForce(acc,mul(steerVec,turnAccel*b.mass/steerLen));}}addForce(acc,mul(off,-b.mass*guide));const centerErr={x:b.px-road.x,y:b.py-road.y,z:b.pz-road.z},sideErr=dot(centerErr,road.right),sideVel=dot(vel,road.right),normalErr=dot(centerErr,road.up)-COM_VISUAL_Y,normalVel=dot(vel,road.up),sideAccel=Math.max(-44,Math.min(44,-sideErr*(contactArc?7.2:6.2)-sideVel*(contactArc?5.8:5.2))),normalAccel=Math.max(-56,Math.min(36,-normalErr*(contactArc?9.6:7.0)-normalVel*(contactArc?4.1:3.0)-(contactArc?12.5:9.0)));addForce(acc,mul(road.right,sideAccel*b.mass));addForce(acc,mul(road.up,normalAccel*b.mass));if(contactArc){const bu=bodyUp(b),omega={x:b.wx,y:b.wy,z:b.wz},align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},tiltErr=cross(bu,road.up),tiltK=crownBand?(align<.20?15.0:12.5):exitBlend?10.5:9.0,tiltD=3.5,maxTilt=(crownBand?14.0:exitBlend?11.5:10.5)*b.mass;acc.tx+=Math.max(-maxTilt,Math.min(maxTilt,(tiltErr.x*tiltK-tiltRate.x*tiltD)*b.mass));acc.ty+=Math.max(-maxTilt,Math.min(maxTilt,(tiltErr.y*tiltK-tiltRate.y*tiltD)*b.mass));acc.tz+=Math.max(-maxTilt,Math.min(maxTilt,(tiltErr.z*tiltK-tiltRate.z*tiltD)*b.mass));}if(steepClimb)addForce(acc,mul(road.forward,road.forward.y*9.81*b.mass));}if(assistContact&&v<target){const effective=Math.max(v,-4),force=(target-effective)*b.mass*gain;addForce(acc,mul(curveGuide?guideForward:road.forward,force));c.rampageBoost=true;}else if(assistContact&&inLoop&&loopT>.72&&v>target+.8){const trim=(v-target)*b.mass*3.8;addForce(acc,mul(road.forward,-trim));c.rampageBoost=true;}else c.rampageBoost=false;c.rampageBoostTarget=target;}else{c.rampageBoost=false;c.rampageBoostTarget=0;}}else{c.rampageBoost=false;c.rampageBoostTarget=0;}"
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE boost v6: expected 1 boost block, found {count}')
    s = s.replace(old, new, 1)
    s = "import {activeCourse as boostCourse} from './courses.js';\n" + s
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_loop_boost_v6(Path('_site'))
