"""DOUBLE ORBIT v24: true side-by-side planar rings plus force-only loop guidance.

v23 proved the two insertions can live next to each other, but the legacy
forward-progress helix still rotated each ring with the underlying figure-eight
road. The result looked twisted in the live WebGL capture and the player could
fall back inside loop one.

This final DOUBLE ORBIT-only pass makes both rings share one horizontal travel
axis, gives each a near-complete circular vertical arc with separate smooth
entry/exit legs, and adds a force/torque-only guide while a car is physically
inside either ring. No position, quaternion, velocity, track progress or race
distance is assigned by the guide.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT planar v24 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_planar_v24(target: Path) -> None:
    racing3d = target / 'racing3d.js'
    s = racing3d.read_text()

    branch_start = """  if(doubleOrbit||skyForge){
   const lowerLegLift=x=>(doubleOrbit?.48:.48)*smooth01(x/.055)*(1-smooth01((x-.11)/.09));
   const sample=u=>{
    const spineT=startT+(endT-startT)*u,frame=roadFrameAt(spineT),phase=u-Math.sin(TAU*u)/TAU,th=phase*TAU,c=Math.cos(th),sn=Math.sin(th),sideR=LOOP_R*(doubleOrbit?1.00:1.55),vertR=LOOP_R,sideAxis=norm({x:frame.right.x,y:0,z:frame.right.z}),gateLift=lowerLegLift(u)+lowerLegLift(1-u);
    const center=add(frame.p,mul(frame.up,vertR)),pos=add(add(add(frame.p,mul(sideAxis,sideR*sn)),mul(frame.up,vertR*(1-c))),mul(frame.up,gateLift));
    const loopUp=norm(add(mul(frame.up,c),mul(sideAxis,-sn)));
    return{pos,center,frame,loopUp};
   };
   for(let j=0;j<=LOOP_STEPS;j++){
    const u=j/LOOP_STEPS,du=.25/LOOP_STEPS,here=sample(u),prev=sample(Math.max(0,u-du)),next=sample(Math.min(1,u+du)),tangent=norm(sub(next.pos,prev.pos));
    const radialUp=here.loopUp,roll=.10*Math.sin(Math.PI*u)*Math.sin(TAU*u),up=norm(rotateAround(radialUp,tangent,roll));
    raw.push({x:here.pos.x,y:here.pos.y,z:here.pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent});
   }
"""
    if s.count(branch_start) != 1:
        raise RuntimeError(f'DOUBLE ORBIT planar v24 geometry branch: expected 1 match, found {s.count(branch_start)}')

    replacement = """  if(doubleOrbit){
   const startFrame=roadFrameAt(startT),endFrame=roadFrameAt(endT),worldUp={x:0,y:1,z:0};
   const pairA=baseAt(loopCenters[0]),pairB=baseAt(loopCenters[1]),pairAxis=horizontal(sub(pairB,pairA)),startH=horizontal(startFrame.forward)||norm(startFrame.forward),ringForward=pairAxis||startH;
   let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=startFrame.right;const ringUp=norm(cross(ringForward,ringRight));
   const open=.30,ringBottom=baseAt(startCenter),circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),pos=add(add(ringBottom,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),tangent=norm(add(mul(ringForward,c),mul(ringUp,sn))),up=norm(add(mul(ringUp,c),mul(ringForward,-sn)));return{pos,tangent,up};};
   const ringEntry=circleAt(open),ringExit=circleAt(TAU-open);
   const hermiteDO=(p0,t0,p1,t1,s0,s1,u)=>{const u2=u*u,u3=u2*u,h00=2*u3-3*u2+1,h10=u3-2*u2+u,h01=-2*u3+3*u2,h11=u3-u2;return{x:p0.x*h00+t0.x*s0*h10+p1.x*h01+t1.x*s1*h11,y:p0.y*h00+t0.y*s0*h10+p1.y*h01+t1.y*s1*h11,z:p0.z*h00+t0.z*s0*h10+p1.z*h01+t1.z*s1*h11};};
   const entryDist=len(sub(ringEntry.pos,startFrame.p)),exitDist=len(sub(endFrame.p,ringExit.pos)),entryScale=clamp(entryDist*.72,4.5,9.5),exitScale=clamp(exitDist*.72,4.5,9.5),LEG_STEPS=Math.max(16,Math.round(LOOP_STEPS*.20)),RING_STEPS=Math.max(64,LOOP_STEPS);
   const pushLeg=(p0,t0,u0,p1,t1,u1,s0,s1,steps,skipFirst=false)=>{for(let j=skipFirst?1:0;j<=steps;j++){const q=j/steps,dq=.18/steps,pos=hermiteDO(p0,t0,p1,t1,s0,s1,q),prev=hermiteDO(p0,t0,p1,t1,s0,s1,Math.max(0,q-dq)),next=hermiteDO(p0,t0,p1,t1,s0,s1,Math.min(1,q+dq)),tangent=norm(sub(next,prev)),seed=mixV(u0,u1,smooth01(q)),up=orthoUp(seed,tangent,ringUp);raw.push({x:pos.x,y:pos.y,z:pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent});}};
   // The Actions geometry probe measured only +4.56 cm of rise at 2 m with
   // a .08 toe. Scaling the Hermite start tangent from the measured response
   // gives ~12 cm at the same probe distance while keeping the gate smooth.
   const entryToe=norm(add(startFrame.forward,mul(startFrame.up,.22)));
   pushLeg(startFrame.p,entryToe,startFrame.up,ringEntry.pos,ringEntry.tangent,ringEntry.up,entryScale,entryScale,LEG_STEPS,false);
   for(let j=1;j<=RING_STEPS;j++){const q=j/RING_STEPS,th=open+(TAU-open*2)*q,p=circleAt(th);raw.push({x:p.pos.x,y:p.pos.y,z:p.pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:p.up,explicitForward:p.tangent});}
   pushLeg(ringExit.pos,ringExit.tangent,ringExit.up,endFrame.p,endFrame.forward,endFrame.up,exitScale,exitScale,LEG_STEPS,true);
  }else if(skyForge){
   const lowerLegLift=x=>.48*smooth01(x/.055)*(1-smooth01((x-.11)/.09));
   const sample=u=>{
    const spineT=startT+(endT-startT)*u,frame=roadFrameAt(spineT),phase=u-Math.sin(TAU*u)/TAU,th=phase*TAU,c=Math.cos(th),sn=Math.sin(th),sideR=LOOP_R*1.55,vertR=LOOP_R,sideAxis=norm({x:frame.right.x,y:0,z:frame.right.z}),gateLift=lowerLegLift(u)+lowerLegLift(1-u);
    const center=add(frame.p,mul(frame.up,vertR)),pos=add(add(add(frame.p,mul(sideAxis,sideR*sn)),mul(frame.up,vertR*(1-c))),mul(frame.up,gateLift));
    const loopUp=norm(add(mul(frame.up,c),mul(sideAxis,-sn)));
    return{pos,center,frame,loopUp};
   };
   for(let j=0;j<=LOOP_STEPS;j++){
    const u=j/LOOP_STEPS,du=.25/LOOP_STEPS,here=sample(u),prev=sample(Math.max(0,u-du)),next=sample(Math.min(1,u+du)),tangent=norm(sub(next.pos,prev.pos));
    const radialUp=here.loopUp,roll=.10*Math.sin(Math.PI*u)*Math.sin(TAU*u),up=norm(rotateAround(radialUp,tangent,roll));
    raw.push({x:here.pos.x,y:here.pos.y,z:here.pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent});
   }
"""
    s = s.replace(branch_start, replacement, 1)
    racing3d.write_text(s)

    physics = target / 'physics3d.js'
    s = physics.read_text()
    hook_old = "doubleOrbitFinalJumpAttitude(w,c,ctx,acc);doubleOrbitExitRunoff(w,c,acc,ctx);"
    hook_new = "doubleOrbitLoopGuide(w,c,acc,ctx);doubleOrbitFinalJumpAttitude(w,c,ctx,acc);doubleOrbitExitRunoff(w,c,acc,ctx);"
    s = one(s, hook_old, hook_new, 'physics hook')

    anchor = "function doubleOrbitExitRunoff(w,c,acc,ctx){"
    if s.count(anchor) != 1:
        raise RuntimeError(f'DOUBLE ORBIT planar v24 guide anchor: expected 1 match, found {s.count(anchor)}')
    guide = r"""function doubleOrbitLoopGuide(w,c,acc,ctx){
  if(w.mode!=='racing'||activeCourse.id!=='double-orbit'||!c?.p3)return;
  const b=c.p3,q=c.trackS??0,road=racePointAt(q);if(road.kind!=='loop')return;
  const loop=raceLoopAt(q),vel={x:b.vx,y:b.vy,z:b.vz},omega={x:b.wx,y:b.wy,z:b.wz},rel={x:b.px-road.x,y:b.py-road.y,z:b.pz-road.z},height=dot(rel,road.up),forwardSpeed=dot(vel,road.forward),normalSpeed=dot(vel,road.up),lateral=dot(rel,road.right),sideSpeed=dot(vel,road.right);
  if(height<-.45||height>4.8)return;
  const target=c.id===0?23.5:21.5,driveAccel=forwardSpeed<target?ctx.clamp((target-forwardSpeed)*(c.id===0?6.8:5.4),0,c.id===0?42:34):0;
  if(driveAccel>0)addForce(acc,mul(road.forward,driveAccel*b.mass));
  const laneGoal=c.id===0?0:ctx.clamp((c.loopLane??0)*.48,-2.25,2.25),sideAccel=ctx.clamp((laneGoal-lateral)*5.0-sideSpeed*5.8,-38,38);addForce(acc,mul(road.right,sideAccel*b.mass));
  const speed=Math.max(8,Math.max(0,forwardSpeed)),ride=.92,centripetal=speed*speed/Math.max(4,loop.radius),normalAccel=ctx.clamp(centripetal*.56+(ride-height)*11.5-normalSpeed*4.8,0,38);addForce(acc,mul(road.up,normalAccel*b.mass));
  const ds=.48,rb=racePointAt(q-ds),ra=racePointAt(q+ds),curve=cross(rb.forward,ra.forward),curvature=dot(curve,road.right)/(2*ds),desiredPitch=ctx.clamp(curvature*speed,-5.2,5.2),pitchRate=dot(omega,road.right),pitchTorque=ctx.clamp((desiredPitch-pitchRate)*b.mass*9.2,-46*b.mass,46*b.mass),pt=mul(road.right,pitchTorque);acc.tx+=pt.x;acc.ty+=pt.y;acc.tz+=pt.z;
}

"""
    s = s.replace(anchor, guide + anchor, 1)
    physics.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_planar_v24(Path('_site'))
