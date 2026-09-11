"""DOUBLE ORBIT v24: open twin loops, parallel road joins, and per-loop camera.

The supplied toy-track reference is not a closed pair of rings. Each vertical
loop has a visibly open lower throat, and the ordinary road before and after
the stunt remains almost parallel. Keep the two rings side-by-side on one
horizontal travel axis, but shorten the replaced base-road interval so the
outgoing road no longer turns away from the approach, and expose a much wider
lower opening with separate smooth entry/exit legs.

The traversal helper stays force/torque-only: it never assigns position,
quaternion, velocity, track progress or race distance. A DOUBLE ORBIT-only
camera branch stages whichever of the two loops the player is actually in,
keeps world-up through inversion, and preserves the existing RAMPAGE Omega
camera byte-for-byte for every non-DOUBLE-ORBIT loop.
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

    # The reference keeps the ordinary road before and after each loop nearly
    # parallel. At the old +/- .16 base span loop two turned about 31 degrees.
    # +/- .05 keeps both joins on the local straight (about 4 and 10 degrees).
    s = one(
        s,
        "const LOOP_HALF_T=doubleOrbit?.16:skyForge?.18:.19,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=doubleOrbit?.50:skyForge?1:.44;",
        "const LOOP_HALF_T=doubleOrbit?.05:skyForge?.18:.19,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=doubleOrbit?.50:skyForge?1:.44;",
        'parallel base-road gate span',
    )

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
   // The toy loop is deliberately open at the bottom. .58 rad removes roughly
   // 66 degrees of the lower circle; the two Hermite legs stay physically
   // separate instead of drawing a closing road segment across the throat.
   const open=.58,ringBottom=baseAt(startCenter),circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),pos=add(add(ringBottom,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),tangent=norm(add(mul(ringForward,c),mul(ringUp,sn))),up=norm(add(mul(ringUp,c),mul(ringForward,-sn)));return{pos,tangent,up};};
   const ringEntry=circleAt(open),ringExit=circleAt(TAU-open);
   const hermiteDO=(p0,t0,p1,t1,s0,s1,u)=>{const u2=u*u,u3=u2*u,h00=2*u3-3*u2+1,h10=u3-2*u2+u,h01=-2*u3+3*u2,h11=u3-u2;return{x:p0.x*h00+t0.x*s0*h10+p1.x*h01+t1.x*s1*h11,y:p0.y*h00+t0.y*s0*h10+p1.y*h01+t1.y*s1*h11,z:p0.z*h00+t0.z*s0*h10+p1.z*h01+t1.z*s1*h11};};
   const entryDist=len(sub(ringEntry.pos,startFrame.p)),exitDist=len(sub(endFrame.p,ringExit.pos)),entryScale=clamp(entryDist*.72,4.5,10.5),exitScale=clamp(exitDist*.72,4.5,10.5),LEG_STEPS=Math.max(18,Math.round(LOOP_STEPS*.23)),RING_STEPS=Math.max(68,LOOP_STEPS);
   const pushLeg=(p0,t0,u0,p1,t1,u1,s0,s1,steps,skipFirst=false)=>{for(let j=skipFirst?1:0;j<=steps;j++){const q=j/steps,dq=.18/steps,pos=hermiteDO(p0,t0,p1,t1,s0,s1,q),prev=hermiteDO(p0,t0,p1,t1,s0,s1,Math.max(0,q-dq)),next=hermiteDO(p0,t0,p1,t1,s0,s1,Math.min(1,q+dq)),tangent=norm(sub(next,prev)),seed=mixV(u0,u1,smooth01(q)),up=orthoUp(seed,tangent,ringUp);raw.push({x:pos.x,y:pos.y,z:pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent});}};
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

    # The generic racing loop camera only knows the first loop. DOUBLE ORBIT
    # must select the ring around the player's current trackS, while RAMPAGE
    # keeps its proven v18 Omega camera exactly as-is.
    game = target / 'game.js'
    s = game.read_text()
    old_select = "raceLoopSpec=fullPhysicsSpec.race?.loop,racePose=gameMode==='racing'?trackPoint(p.trackS??0,0):null,racingLoop=!!raceLoopSpec&&!!racePose&&p.trackS>=raceLoopSpec.startS-7&&p.trackS<=raceLoopSpec.endS+7"
    new_select = "raceLoops=fullPhysicsSpec.race?.loops||[fullPhysicsSpec.race?.loop].filter(Boolean),doubleOrbitLoop=activeCourse?.id==='double-orbit'?raceLoops.find(q=>(p.trackS??0)>=q.startS-6&&(p.trackS??0)<=q.endS+6):null,raceLoopSpec=doubleOrbitLoop||fullPhysicsSpec.race?.loop,racePose=gameMode==='racing'?trackPoint(p.trackS??0,0):null,racingLoop=!!raceLoopSpec&&!!racePose&&p.trackS>=raceLoopSpec.startS-7&&p.trackS<=raceLoopSpec.endS+7"
    s = one(s, old_select, new_select, 'per-loop camera selection')

    rampage_camera = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,dx=z.x-a.x,dz=z.z-a.z,dl=Math.hypot(dx,dz)||1,nx=dx/dl,nz=dz/dl,fx=a.forward.x,fz=a.forward.z,outward=(mx*nx+mz*nz)>=0?1:-1,side=-(view===1?2.64:2.45)*raceLoopSpec.radius*outward,back=(view===1?2.17:2.00)*raceLoopSpec.radius,stageLift=view===1?3.5:2.7,loopFocusY=my+raceLoopSpec.radius-2.6,playerFocus=.24;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(mx+(b.px-mx)*playerFocus,loopFocusY+(b.py+.45-loopFocusY)*playerFocus,mz+(b.pz-mz)*playerFocus);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?54:55;}"""
    double_camera = """if(racingLoop&&activeCourse?.id==='double-orbit'){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,rd=Math.hypot(a.right.x,a.right.z)||1,rx=a.right.x/rd,rz=a.right.z/rd,fd=Math.hypot(a.forward.x,a.forward.z)||1,fx=a.forward.x/fd,fz=a.forward.z/fd,outward=(mx*rx+mz*rz)>=0?1:-1,side=(view===1?2.85:2.55)*raceLoopSpec.radius*outward,back=(view===1?1.55:1.28)*raceLoopSpec.radius,stageLift=view===1?2.8:2.1,loopFocusY=my+raceLoopSpec.radius-1.35,playerFocus=.30;camTarget.set(mx+rx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+rz*side-fz*back);lookTarget.set(mx+(b.px-mx)*playerFocus,loopFocusY+(b.py+.45-loopFocusY)*playerFocus,mz+(b.pz-mz)*playerFocus);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?56:57;}else """ + rampage_camera
    s = one(s, rampage_camera, double_camera, 'DOUBLE ORBIT stage camera')
    game.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_planar_v24(Path('_site'))
