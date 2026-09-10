"""RAMPAGE v12: reference geometry from two parallel straight road gates.

This pass intentionally runs after v11 and replaces only the final RAMPAGE
centreline construction.  The geometry rule is simple and measurable:

* the road immediately before and after the stunt is straight and parallel;
* those two road centrelines are separated by exactly one loop-road width;
* the loop starts and ends directly on those straight centrelines;
* position, tangent and road-up are continuous at both joins;
* the vertical revolution is a clean circle in side projection.  The required
  one-road-width side shift is distributed smoothly through the revolution with
  a quintic zero-slope/zero-acceleration blend, so there is no kink or lower
  throat detour to hide.

A short Hermite transition farther away from the loop reconnects the two local
straight roads to the original figure-eight.  SKY FORGE and DOUBLE ORBIT are
unchanged.
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

    # Build a local corridor around the loop before roadFrameAt is evaluated.
    # The two straight gates are one complete *loop road* width apart, not an
    # arbitrary clearance value.  Their common forward axis comes from the
    # original outer-lobe tangent, so both joins are genuinely straight.
    anchor = "const raw=[];\nconst ts=[];for(let i=0;i<=BASE_STEPS;i++)ts.push(i/BASE_STEPS*TAU);for(const c of loopCenters)ts.push(c-LOOP_HALF_T,c+LOOP_HALF_T);ts.sort((a,b)=>a-b);\nconst insertedLoops=new Set();\n"
    corridor = """const RAMPAGE_ENTRY_T=RAMPAGE_LOOP_T-LOOP_HALF_T,RAMPAGE_EXIT_T=RAMPAGE_LOOP_T+LOOP_HALF_T;
const rampageWorldUp={x:0,y:1,z:0},rampageBaseMid=baseAt(RAMPAGE_LOOP_T),rampageFD=.0025,rampageFA=baseAt(RAMPAGE_LOOP_T-rampageFD),rampageFB=baseAt(RAMPAGE_LOOP_T+rampageFD);
const rampageForward=norm({x:rampageFB.x-rampageFA.x,y:0,z:rampageFB.z-rampageFA.z});
let rampageRight=norm(cross(rampageWorldUp,rampageForward));if(len(rampageRight)<.2)rampageRight={x:1,y:0,z:0};
const rampageLoopRoadWidth=RACE3D_TRACK.halfWidth*LOOP_LANE_SCALE*2,rampageOutward=(rampageBaseMid.x*rampageRight.x+rampageBaseMid.z*rampageRight.z)>=0?1:-1;
const rampageGateY=(baseAt(RAMPAGE_ENTRY_T).y+baseAt(RAMPAGE_EXIT_T).y)*.5,rampageGateCenter={x:rampageBaseMid.x+rampageRight.x*rampageOutward*6.5,y:rampageGateY,z:rampageBaseMid.z+rampageRight.z*rampageOutward*6.5};
const rampageGateA=add(rampageGateCenter,mul(rampageRight,-rampageLoopRoadWidth*.5)),rampageGateB=add(rampageGateCenter,mul(rampageRight,rampageLoopRoadWidth*.5)),rampageOldEntry=baseAt(RAMPAGE_ENTRY_T),rampageOldExit=baseAt(RAMPAGE_EXIT_T);
const rampageScoreAB=len(sub(rampageOldEntry,rampageGateA))+len(sub(rampageOldExit,rampageGateB)),rampageEntryGate=rampageScoreAB<=len(sub(rampageOldEntry,rampageGateB))+len(sub(rampageOldExit,rampageGateA))?rampageGateA:rampageGateB,rampageExitGate=rampageEntryGate===rampageGateA?rampageGateB:rampageGateA;
const rampageBlendIn=RAMPAGE_ENTRY_T-.15,rampageStraightIn=RAMPAGE_ENTRY_T-.065,rampageStraightOut=RAMPAGE_EXIT_T+.065,rampageBlendOut=RAMPAGE_EXIT_T+.15,rampageLead=15.0;
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
const ts=[];for(let i=0;i<=BASE_STEPS;i++)ts.push(i/BASE_STEPS*TAU);for(const c of loopCenters)ts.push(c-LOOP_HALF_T,c+LOOP_HALF_T);if(!doubleOrbit&&!skyForge){for(let i=0;i<=12;i++){ts.push(rampageBlendIn+(RAMPAGE_ENTRY_T-rampageBlendIn)*i/12);ts.push(RAMPAGE_EXIT_T+(rampageBlendOut-RAMPAGE_EXIT_T)*i/12);}}ts.sort((a,b)=>a-b);
const insertedLoops=new Set();
"""
    s = one(s, anchor, corridor, 'parallel-road corridor')

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

    # Replace the former open/throat construction with a single clean vertical
    # revolution.  Entry and exit are already the exact parallel-road gates.
    ring_start = s.index("const open=.50,entryEnd=.18,exitStart=.82")
    ring_end = s.index("for(let j=0;j<=LOOP_STEPS;j++){", ring_start)
    ring = """const gateDelta=sub(endFrame.p,startFrame.p),gateAcross=dot(gateDelta,rampageRight),parallelOffset=Math.abs(gateAcross),loopRadius=LOOP_R;
   const ringPoint=q=>{
    q=clamp(q,0,1);const th=TAU*q,c=Math.cos(th),sn=Math.sin(th),side=rampageSmooth5(q),pos=add(add(add(startFrame.p,mul(rampageForward,loopRadius*sn)),mul(ringUp,loopRadius*(1-c))),mul(gateDelta,side)),h=.0015,qa=Math.max(0,q-h),qb=Math.min(1,q+h),tha=TAU*qa,thb=TAU*qb,pa=add(add(add(startFrame.p,mul(rampageForward,loopRadius*Math.sin(tha))),mul(ringUp,loopRadius*(1-Math.cos(tha)))),mul(gateDelta,rampageSmooth5(qa))),pb=add(add(add(startFrame.p,mul(rampageForward,loopRadius*Math.sin(thb))),mul(ringUp,loopRadius*(1-Math.cos(thb)))),mul(gateDelta,rampageSmooth5(qb))),tangent=norm(sub(pb,pa)),radial=norm(add(mul(ringUp,c),mul(rampageForward,-sn))),up=orthoUp(radial,tangent,ringUp);return{pos,up,tangent};
   };
   const sample=u=>{const ring=ringPoint(u);return{pos:ring.pos,frame:{up:ring.up},upSeed:ring.up};};
   """
    s = s[:ring_start] + ring + s[ring_end:]
    path.write_text(s)

    # Side/three-quarter stage camera: derive the viewing normal from the two
    # parallel gate centrelines.  A small backward component keeps their one-road
    # width separation visible instead of collapsing both straights into one.
    game = target / 'game.js'
    s = game.read_text()
    b0 = s.find("if(racingLoop){const s0=raceLoopSpec.startS")
    b1 = s.find("}else if(racingJump){", b0)
    if b0 < 0 or b1 < 0:
        raise RuntimeError('RAMPAGE parallel loop v12 camera branch not found')
    cam = """if(racingLoop){const s0=raceLoopSpec.startS,s1=raceLoopSpec.endS,a=trackPoint(s0,0),z=trackPoint(s1,0),mx=(a.x+z.x)*.5,my=(a.y+z.y)*.5,mz=(a.z+z.z)*.5,dx=z.x-a.x,dz=z.z-a.z,dl=Math.hypot(dx,dz)||1,nx=dx/dl,nz=dz/dl,fx=a.forward.x,fz=a.forward.z,side=-(view===1?45:41),back=view===1?10:8,stageLift=view===1?3.2:2.4;camTarget.set(mx+nx*side-fx*back,my+raceLoopSpec.radius+stageLift,mz+nz*side-fz*back);lookTarget.set(b.px,b.py+.45,b.pz);camera.up.lerp(physicsWorldUp,1-Math.exp(-12*dt));camera.fov=view===1?58:60;"""
    s = s[:b0] + cam + s[b1:]
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_parallel_loop_v12(Path('_site'))
