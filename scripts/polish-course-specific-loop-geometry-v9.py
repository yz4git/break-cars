"""Keep the RAMPAGE clearance fix isolated from the other stunt courses.

RAMPAGE now uses a conventional toy-track style vertical loop: the authored road
itself rises into the loop, runs one open revolution, and returns directly to
the authored outgoing road. There are no separate lower entry/exit splines and
therefore no X-shaped underpass beneath the ring. A broad gate interval plus a
smooth outboard envelope keeps the full ribbon clear of the nearby figure-eight
branch. A gentle depth twist sends the rising and falling halves to opposite
sides of the loop plane, like a real open/twisted stunt track, while both loop
gates remain exact continuations of the original road.

SKY FORGE and DOUBLE ORBIT keep the proven forward-progress helix, with a small
symmetric lower-leg rise so the ordinary road visibly flows up into (and back
down out of) the loop instead of reading flat at the gates.

This transform runs after v8 and replaces only the generated loop-centerline
construction. Rendering/collision continue to consume the same centerline.
"""
from pathlib import Path


def apply_course_specific_loop_geometry_v9(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()
    start = s.index('const LOOP_HALF_T=')
    end = s.index('// Remove accidental duplicate', start)

    block = r"""const LOOP_HALF_T=(doubleOrbit||skyForge)?.18:.36,LOOP_OPEN_ANGLE=.42,LOOP_LANE_SCALE=(!doubleOrbit&&!skyForge)?.58:1;
const loopCenters=doubleOrbit?[LOOP_T,3.85]:[LOOP_T];
const raw=[];
const ts=[];for(let i=0;i<=BASE_STEPS;i++)ts.push(i/BASE_STEPS*TAU);for(const c of loopCenters)ts.push(c-LOOP_HALF_T,c+LOOP_HALF_T);ts.sort((a,b)=>a-b);
const insertedLoops=new Set();
const roadFrameAt=t=>{
 const dt=.0015,p=baseAt(t),a=baseAt(t-dt),b=baseAt(t+dt),forward=norm(sub(b,a)),worldUp={x:0,y:1,z:0};
 let right=norm(cross(worldUp,forward));if(len(right)<.2)right={x:1,y:0,z:0};
 let up=norm(cross(forward,right));up=norm(rotateAround(up,forward,p.bank||0));right=norm(cross(up,forward));
 return{p,forward,up,right};
};
const mixV=(a,b,u)=>norm({x:a.x+(b.x-a.x)*u,y:a.y+(b.y-a.y)*u,z:a.z+(b.z-a.z)*u});
const smooth01=x=>{x=clamp(x,0,1);return x*x*(3-2*x);};
const horizontal=v=>{const h={x:v.x,y:0,z:v.z},l=len(h);return l>.2?mul(h,1/l):null;};
const orthoUp=(seed,tangent,fallback)=>{const p=sub(seed,mul(tangent,dot(seed,tangent)));return len(p)>.15?norm(p):fallback;};
for(const t of ts){
 if(t>TAU+EPS)continue;
 const startCenter=loopCenters.find(c=>Math.abs(t-(c-LOOP_HALF_T))<1e-6),insideLoop=loopCenters.some(c=>t>=c-LOOP_HALF_T-EPS&&t<=c+LOOP_HALF_T+EPS);
 if(startCenter!==undefined&&!insertedLoops.has(startCenter)){
  insertedLoops.add(startCenter);
  const startT=startCenter-LOOP_HALF_T,endT=startCenter+LOOP_HALF_T;

  if(doubleOrbit||skyForge){
   // Proven forward-progress open helix. The authored spine advances throughout
   // the revolution, so rising/falling halves stay out of the same corridor.
   // Add only a low, smooth gate lift. Its derivative is zero at u=0/1, so the
   // loop remains exactly tangent to the ordinary road while visibly climbing
   // within the first couple of metres (and descending naturally at the exit).
   const lowerLegLift=x=>(doubleOrbit?.82:.48)*smooth01(x/.055)*(1-smooth01((x-.11)/.09));
   const sample=u=>{
    const spineT=startT+(endT-startT)*u,frame=roadFrameAt(spineT),phase=u-Math.sin(TAU*u)/TAU,th=phase*TAU,c=Math.cos(th),sn=Math.sin(th),sideR=LOOP_R*(doubleOrbit?1.35:1.55),vertR=LOOP_R,sideAxis=norm({x:frame.right.x,y:0,z:frame.right.z}),gateLift=lowerLegLift(u)+lowerLegLift(1-u);
    const center=add(frame.p,mul(frame.up,vertR)),pos=add(add(add(frame.p,mul(sideAxis,sideR*sn)),mul(frame.up,vertR*(1-c))),mul(frame.up,gateLift));
    const loopUp=norm(add(mul(frame.up,c),mul(sideAxis,-sn)));
    return{pos,center,frame,loopUp};
   };
   for(let j=0;j<=LOOP_STEPS;j++){
    const u=j/LOOP_STEPS,du=.25/LOOP_STEPS,here=sample(u),prev=sample(Math.max(0,u-du)),next=sample(Math.min(1,u+du)),tangent=norm(sub(next.pos,prev.pos));
    const radialUp=here.loopUp,roll=.10*Math.sin(Math.PI*u)*Math.sin(TAU*u),up=norm(rotateAround(radialUp,tangent,roll));
    raw.push({x:here.pos.x,y:here.pos.y,z:here.pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent});
   }
  }else{
   // RAMPAGE is one continuous road surface, not a ring object placed on top of
   // a road. The base spine moves from the incoming gate to the outgoing gate
   // while a vertical revolution is added in the forward/up plane. A smooth
   // outboard bow clears the nearby figure-eight branch; an antisymmetric depth
   // twist separates the rising and falling halves instead of letting them form
   // an X at the bottom. All offsets have zero derivative at both gates.
   const startFrame=roadFrameAt(startT),endFrame=roadFrameAt(endT),worldUp={x:0,y:1,z:0};
   const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),sumH=add(startH,endH),loopForward=len(sumH)>.2?norm(sumH):startH;
   let flatRight=norm(cross(worldUp,loopForward));if(len(flatRight)<.2)flatRight=startFrame.right;
   const ringUp=norm(cross(loopForward,flatRight)),outwardSign=(startFrame.p.x*flatRight.x+startFrame.p.z*flatRight.z)>=0?1:-1;
   const gateLift=x=>.82*smooth01(x/.055)*(1-smooth01((x-.12)/.085));
   const sample=u=>{
    const spineT=startT+(endT-startT)*u,frame=roadFrameAt(spineT),phase=u-Math.sin(TAU*u)/TAU,th=phase*TAU,c=Math.cos(th),sn=Math.sin(th),en=Math.sin(Math.PI*u),env=en*en,outboard=14*env,twist=18*Math.sin(TAU*u)*env,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*.64;
    const lateral=outwardSign*(outboard+twist),pos=add(add(add(add(frame.p,mul(loopForward,horizR*sn)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lateral)),mul(ringUp,gateRise));
    const radial=norm(add(mul(ringUp,c),mul(loopForward,-sn))),loopWeight=smooth01(u/.095)*smooth01((1-u)/.095),upSeed=mixV(frame.up,radial,loopWeight);
    return{pos,frame,upSeed};
   };
   for(let j=0;j<=LOOP_STEPS;j++){
    const u=j/LOOP_STEPS,du=.25/LOOP_STEPS,here=sample(u),prev=sample(Math.max(0,u-du)),next=sample(Math.min(1,u+du)),tangent=norm(sub(next.pos,prev.pos)),up=orthoUp(here.upSeed,tangent,here.frame.up);
    raw.push({x:here.pos.x,y:here.pos.y,z:here.pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent});
   }
  }
  continue;
 }
 if(insideLoop)continue;
 const p=baseAt(t);raw.push({...p,explicitUp:null});
}

"""
    path.write_text(s[:start] + block + s[end:])


if __name__ == '__main__':
    apply_course_specific_loop_geometry_v9(Path('_site'))