"""RAMPAGE v12: road-width-driven planar Omega loop.

Dimensionless reference proportions:

    W = loop road width
    D = 2.0 W       -> one full W of empty space between parallel road edges
    R = 2.5 W       -> outside loop diameter = 5 W
    opening         -> 2 R - W = 4 W

A full circle cannot connect two laterally separated parallel roads while also
matching both road tangents: that is geometrically impossible in one plane.
The correct construction is therefore an open Omega.  Its large main arc lives
in one exact vertical plane; only two short lower transition legs move from the
parallel roads into that plane.

The bottom cut angle is not guessed.  We choose

    alpha = asin(D / (2 R))

so the two endpoints of the planar main arc are separated by exactly D along
the forward axis.  For D=2W and R=2.5W, alpha=23.578 degrees.  Each lower leg is
a quintic Bezier whose position, tangent and curvature match the straight road
at one end and the circle at the other (C2 geometric join).  This keeps the
upper ~87% of the revolution perfectly planar instead of twisting the whole
road ribbon into a wall.

SKY FORGE and DOUBLE ORBIT are unchanged.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE parallel loop v12 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_parallel_loop_v12(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()

    # W = 8.5 * .44 * 2 = 7.48 m; R = 2.5W = 18.70 m.
    s = one(
        s,
        "loopRadius:doubleOrbit?8.6:skyForge?7.5:11.5",
        "loopRadius:doubleOrbit?8.6:skyForge?7.5:18.7",
        'road-width-derived RAMPAGE radius',
    )

    # Build two long parallel straights.  D=2W means their inner edges retain
    # exactly one complete road width of open space.
    anchor = "const raw=[];\nconst ts=[];for(let i=0;i<=BASE_STEPS;i++)ts.push(i/BASE_STEPS*TAU);for(const c of loopCenters)ts.push(c-LOOP_HALF_T,c+LOOP_HALF_T);ts.sort((a,b)=>a-b);\nconst insertedLoops=new Set();\n"
    corridor = """const RAMPAGE_ENTRY_T=RAMPAGE_LOOP_T-LOOP_HALF_T,RAMPAGE_EXIT_T=RAMPAGE_LOOP_T+LOOP_HALF_T;
const rampageWorldUp={x:0,y:1,z:0},rampageBaseMid=baseAt(RAMPAGE_LOOP_T),rampageFD=.0025,rampageFA=baseAt(RAMPAGE_LOOP_T-rampageFD),rampageFB=baseAt(RAMPAGE_LOOP_T+rampageFD);
const rampageForward=norm({x:rampageFB.x-rampageFA.x,y:0,z:rampageFB.z-rampageFA.z});
let rampageRight=norm(cross(rampageWorldUp,rampageForward));if(len(rampageRight)<.2)rampageRight={x:1,y:0,z:0};
const rampageLoopRoadWidth=RACE3D_TRACK.halfWidth*LOOP_LANE_SCALE*2,rampageGateSeparation=rampageLoopRoadWidth*2.0,rampageLoopRadius=rampageLoopRoadWidth*2.5,rampageOutward=(rampageBaseMid.x*rampageRight.x+rampageBaseMid.z*rampageRight.z)>=0?1:-1;
const rampageGateY=(baseAt(RAMPAGE_ENTRY_T).y+baseAt(RAMPAGE_EXIT_T).y)*.5,rampageGateCenter={x:rampageBaseMid.x+rampageRight.x*rampageOutward*9.5,y:rampageGateY,z:rampageBaseMid.z+rampageRight.z*rampageOutward*9.5};
const rampageGateA=add(rampageGateCenter,mul(rampageRight,-rampageGateSeparation*.5)),rampageGateB=add(rampageGateCenter,mul(rampageRight,rampageGateSeparation*.5)),rampageOldEntry=baseAt(RAMPAGE_ENTRY_T),rampageOldExit=baseAt(RAMPAGE_EXIT_T);
const rampageScoreAB=len(sub(rampageOldEntry,rampageGateA))+len(sub(rampageOldExit,rampageGateB)),rampageEntryGate=rampageScoreAB<=len(sub(rampageOldEntry,rampageGateB))+len(sub(rampageOldExit,rampageGateA))?rampageGateA:rampageGateB,rampageExitGate=rampageEntryGate===rampageGateA?rampageGateB:rampageGateA;
const rampageBlendIn=RAMPAGE_ENTRY_T-.18,rampageStraightIn=RAMPAGE_ENTRY_T-.075,rampageStraightOut=RAMPAGE_EXIT_T+.075,rampageBlendOut=RAMPAGE_EXIT_T+.18,rampageLead=Math.max(20.0,rampageLoopRoadWidth*3.0);
const rampageLineIn=add(rampageEntryGate,mul(rampageForward,-rampageLead)),rampageLineOut=add(rampageExitGate,mul(rampageForward,rampageLead));
const rampageSmooth5=q=>{q=clamp(q,0,1);return q*q*q*(10+q*(-15+6*q));};
const rampageHermite=(p0,t0,p1,t1,s0,s1,q)=>{const q2=q*q,q3=q2*q,h00=2*q3-3*q2+1,h10=q3-2*q2+q,h01=-2*q3+3*q2,h11=q3-q2;return{x:p0.x*h00+t0.x*s0*h10+p1.x*h01+t1.x*s1*h11,y:p0.y*h00+t0.y*s0*h10+p1.y*h01+t1.y*s1*h11,z:p0.z*h00+t0.z*s0*h10+p1.z*h01+t1.z*s1*h11};};
const rampageBaseForward=t=>{const d=.002,a=baseAt(t-d),b=baseAt(t+d);return norm(sub(b,a));};
const rampageCourseRoadAt=t=>{
 if(doubleOrbit||skyForge||t<rampageBlendIn||t>rampageBlendOut)return baseAt(t);
 if(t<RAMPAGE_ENTRY_T){
  if(t>=rampageStraightIn){const q=(t-rampageStraightIn)/(RAMPAGE_ENTRY_T-rampageStraightIn),p=add(rampageLineIn,mul(rampageForward,rampageLead*q));return{...p,t,kind:'track',bank:0};}
  const q=(t-rampageBlendIn)/(rampageStraightIn-rampageBlendIn),p0=baseAt(rampageBlendIn),d=len(sub(rampageLineIn,p0)),p=rampageHermite(p0,rampageBaseForward(rampageBlendIn),rampageLineIn,rampageForward,d*.72,d*.72,q);return{...p,t,kind:'track',bank:0};
 }
 if(t>RAMPAGE_EXIT_T){
  if(t<=rampageStraightOut){const q=(t-RAMPAGE_EXIT_T)/(rampageStraightOut-RAMPAGE_EXIT_T),p=add(rampageExitGate,mul(rampageForward,rampageLead*q));return{...p,t,kind:'track',bank:0};}
  const q=(t-rampageStraightOut)/(rampageBlendOut-rampageStraightOut),p1=baseAt(rampageBlendOut),d=len(sub(p1,rampageLineOut)),p=rampageHermite(rampageLineOut,rampageForward,p1,rampageBaseForward(rampageBlendOut),d*.72,d*.72,q);return{...p,t,kind:'track',bank:0};
 }
 return t<=(RAMPAGE_ENTRY_T+RAMPAGE_EXIT_T)*.5?{...rampageEntryGate,t,kind:'track',bank:0}:{...rampageExitGate,t,kind:'track',bank:0};
};
const raw=[];
const ts=[];for(let i=0;i<=BASE_STEPS;i++)ts.push(i/BASE_STEPS*TAU);for(const c of loopCenters)ts.push(c-LOOP_HALF_T,c+LOOP_HALF_T);if(!doubleOrbit&&!skyForge){for(let i=0;i<=16;i++){ts.push(rampageBlendIn+(RAMPAGE_ENTRY_T-rampageBlendIn)*i/16);ts.push(RAMPAGE_EXIT_T+(rampageBlendOut-RAMPAGE_EXIT_T)*i/16);}}ts.sort((a,b)=>a-b);
const insertedLoops=new Set();
"""
    s = one(s, anchor, corridor, 'dimensioned parallel-road corridor')

    old_frame = """const roadFrameAt=t=>{
 const dt=.0015,p=baseAt(t),a=baseAt(t-dt),b=baseAt(t+dt),forward=norm(sub(b,a)),worldUp={x:0,y:1,z:0};
 let right=norm(cross(worldUp,forward));if(len(right)<.2)right={x:1,y:0,z:0};
 let up=norm(cross(forward,right));up=norm(rotateAround(up,forward,p.bank||0));right=norm(cross(up,forward));
 return{p,forward,up,right};
};"""
    new_frame = """const roadFrameAt=t=>{
 const worldUp={x:0,y:1,z:0};
 if(!doubleOrbit&&!skyForge&&(Math.abs(t-RAMPAGE_ENTRY_T)<1e-5||Math.abs(t-RAMPAGE_EXIT_T)<1e-5)){const p=rampageCourseRoadAt(t),forward=rampageForward,right=rampageRight,up=norm(cross(forward,right));return{p,forward,up,right};}
 const dt=.0015,p=rampageCourseRoadAt(t),a=rampageCourseRoadAt(t-dt),b=rampageCourseRoadAt(t+dt),forward=norm(sub(b,a));
 let right=norm(cross(worldUp,forward));if(len(right)<.2)right={x:1,y:0,z:0};
 let up=norm(cross(forward,right));up=norm(rotateAround(up,forward,p.bank||0));right=norm(cross(up,forward));
 return{p,forward,up,right};
};"""
    s = one(s, old_frame, new_frame, 'straight gate frames')
    s = one(s, "const p=baseAt(t);raw.push({...p,explicitUp:null});", "const p=rampageCourseRoadAt(t);raw.push({...p,explicitUp:null});", 'reshape surrounding road')

    # Exact planar Omega: only the two lower C2 legs leave the ring plane.
    ring_start = s.index("const open=.50,entryEnd=.18,exitStart=.82")
    ring_end = s.index("for(let j=0;j<=LOOP_STEPS;j++){", ring_start)
    ring = """const gateDelta=sub(endFrame.p,startFrame.p),gateAcross=dot(gateDelta,rampageRight),parallelOffset=Math.abs(gateAcross),loopRadius=rampageLoopRadius,ringBase=mul(add(startFrame.p,endFrame.p),.5),openAngle=Math.asin(clamp(parallelOffset/(2*loopRadius),.08,.72)),ringArc=TAU-openAngle*2;
   const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),pos=add(add(ringBase,mul(loopForward,loopRadius*sn)),mul(ringUp,loopRadius*(1-c))),tangent=norm(add(mul(loopForward,c),mul(ringUp,sn))),up=norm(add(mul(ringUp,c),mul(loopForward,-sn)));return{pos,tangent,up};};
   const ringEntry=circleAt(openAngle),ringExit=circleAt(TAU-openAngle),zero={x:0,y:0,z:0};
   const bezier5=(c,q)=>{const v=1-q,q2=q*q,q3=q2*q,q4=q3*q,q5=q4*q,v2=v*v,v3=v2*v,v4=v3*v,v5=v4*v;return{x:c[0].x*v5+5*c[1].x*q*v4+10*c[2].x*q2*v3+10*c[3].x*q3*v2+5*c[4].x*q4*v+c[5].x*q5,y:c[0].y*v5+5*c[1].y*q*v4+10*c[2].y*q2*v3+10*c[3].y*q3*v2+5*c[4].y*q4*v+c[5].y*q5,z:c[0].z*v5+5*c[1].z*q*v4+10*c[2].z*q2*v3+10*c[3].z*q3*v2+5*c[4].z*q4*v+c[5].z*q5};};
   const makeC2Leg=(p0,t0,a0,p1,t1,a1)=>{const speed=len(sub(p1,p0)),v0=mul(t0,speed),v1=mul(t1,speed),c0=p0,c1=add(c0,mul(v0,.2)),c2=add(sub(mul(c1,2),c0),mul(a0,.05)),c5=p1,c4=sub(c5,mul(v1,.2)),c3=add(sub(mul(c4,2),c5),mul(a1,.05));return{ctrl:[c0,c1,c2,c3,c4,c5],metric:speed};};
   const entrySpeed=len(sub(ringEntry.pos,startFrame.p)),exitSpeed=len(sub(endFrame.p,ringExit.pos)),entryAccel=mul(ringEntry.up,entrySpeed*entrySpeed/loopRadius),exitAccel=mul(ringExit.up,exitSpeed*exitSpeed/loopRadius),entryLeg=makeC2Leg(startFrame.p,startFrame.forward,zero,ringEntry.pos,ringEntry.tangent,entryAccel),exitLeg=makeC2Leg(ringExit.pos,ringExit.tangent,exitAccel,endFrame.p,endFrame.forward,zero),ringMetric=loopRadius*ringArc,totalMetric=entryLeg.metric+ringMetric+exitLeg.metric,entryEnd=entryLeg.metric/totalMetric,exitStart=1-exitLeg.metric/totalMetric;
   const sample=u=>{
    if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),pos=bezier5(entryLeg.ctrl,q),seed=mixV(startFrame.up,ringEntry.up,rampageSmooth5(q));return{pos,frame:{up:seed},upSeed:seed};}
    if(u>=exitStart){const q=clamp((u-exitStart)/(1-exitStart),0,1),pos=bezier5(exitLeg.ctrl,q),seed=mixV(ringExit.up,endFrame.up,rampageSmooth5(q));return{pos,frame:{up:seed},upSeed:seed};}
    const q=clamp((u-entryEnd)/(exitStart-entryEnd),0,1),p=circleAt(openAngle+ringArc*q);return{pos:p.pos,frame:{up:p.up},upSeed:p.up};
   };
   """
    s = s[:ring_start] + ring + s[ring_end:]
    ramp_for = s.index("for(let j=0;j<=LOOP_STEPS;j++){", ring_start)
    suffix = s[ramp_for:]
    suffix = suffix.replace("for(let j=0;j<=LOOP_STEPS;j++){", "const rampageSampleSteps=128;\n   for(let j=0;j<=rampageSampleSteps;j++){", 1)
    suffix = suffix.replace("const u=j/LOOP_STEPS,du=.25/LOOP_STEPS", "const u=j/rampageSampleSteps,du=.25/rampageSampleSteps", 1)
    s = s[:ramp_for] + suffix
    path.write_text(s)

    # Camera is scaled from the true R and stays on the clear side of the outer
    # lobe.  The larger loop is framed as a whole rather than chased from below.
    game = target / 'game.js'
    s = game.read_text()
    b0 = s.find("if(racingLoop){const s0=raceLoopSpec.startS")
    b1 = s.find("}else if(racingJump){", b0)
    if b0 < 0 or b1 < 0:
        raise RuntimeError('RAMPAGE parallel loop v12 camera branch not found')
    cam = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,dx=z.x-a.x,dz=z.z-a.z,dl=Math.hypot(dx,dz)||1,nx=dx/dl,nz=dz/dl,fx=a.forward.x,fz=a.forward.z,outward=(mx*nx+mz*nz)>=0?1:-1,side=-(view===1?3.35:3.15)*raceLoopSpec.radius*outward,back=(view===1?.72:.62)*raceLoopSpec.radius,stageLift=view===1?4.0:3.0;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(b.px,b.py+.45,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?58:60;"""
    s = s[:b0] + cam + s[b1:]
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_parallel_loop_v12(Path('_site'))
