"""Keep the RAMPAGE clearance fix isolated from the other stunt courses.

RAMPAGE keeps the new broad outboard open loop requested by the visual review.
SKY FORGE and DOUBLE ORBIT are restored to the proven forward-progress helix
used by the last fully green build (0ead342f): their ascending and descending
halves remain separated by the moving authored spine and they do not inherit
RAMPAGE's 17 m detour, long merge handles or widened projection needs.

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
const hermite=(p0,t0,p1,t1,scale,u)=>{const u2=u*u,u3=u2*u,h00=2*u3-3*u2+1,h10=u3-2*u2+u,h01=-2*u3+3*u2,h11=u3-u2;return{x:h00*p0.x+h10*scale*t0.x+h01*p1.x+h11*scale*t1.x,y:h00*p0.y+h10*scale*t0.y+h01*p1.y+h11*scale*t1.y,z:h00*p0.z+h10*scale*t0.z+h01*p1.z+h11*scale*t1.z};};
const orthoUp=(seed,tangent,fallback)=>{const p=sub(seed,mul(tangent,dot(seed,tangent)));return len(p)>.15?norm(p):fallback;};
for(const t of ts){
 if(t>TAU+EPS)continue;
 const startCenter=loopCenters.find(c=>Math.abs(t-(c-LOOP_HALF_T))<1e-6),insideLoop=loopCenters.some(c=>t>=c-LOOP_HALF_T-EPS&&t<=c+LOOP_HALF_T+EPS);
 if(startCenter!==undefined&&!insertedLoops.has(startCenter)){
  insertedLoops.add(startCenter);
  const startT=startCenter-LOOP_HALF_T,endT=startCenter+LOOP_HALF_T;

  if(doubleOrbit||skyForge){
   // Proven 0ead-style open helix. The authored spine advances throughout the
   // loop, so the rising and falling halves do not occupy the same corridor.
   const sample=u=>{
    const spineT=startT+(endT-startT)*u,frame=roadFrameAt(spineT),phase=u-Math.sin(TAU*u)/TAU,th=phase*TAU,c=Math.cos(th),sn=Math.sin(th),sideR=LOOP_R*(doubleOrbit?1.35:1.55),vertR=LOOP_R,sideAxis=norm({x:frame.right.x,y:0,z:frame.right.z});
    const center=add(frame.p,mul(frame.up,vertR)),pos=add(add(frame.p,mul(sideAxis,sideR*sn)),mul(frame.up,vertR*(1-c)));
    const loopUp=norm(add(mul(frame.up,c),mul(sideAxis,-sn)));
    return{pos,center,frame,loopUp};
   };
   for(let j=0;j<=LOOP_STEPS;j++){
    const u=j/LOOP_STEPS,du=.25/LOOP_STEPS,here=sample(u),prev=sample(Math.max(0,u-du)),next=sample(Math.min(1,u+du)),tangent=norm(sub(next.pos,prev.pos));
    const radialUp=here.loopUp,roll=.10*Math.sin(Math.PI*u)*Math.sin(TAU*u),up=norm(rotateAround(radialUp,tangent,roll));
    raw.push({x:here.pos.x,y:here.pos.y,z:here.pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent});
   }
  }else{
   // RAMPAGE-only outboard open loop. The whole elevated ring stays outside the
   // figure-eight; long physical legs are the only parts that merge to the road.
   const startFrame=roadFrameAt(startT),endFrame=roadFrameAt(endT),gateVec=sub(endFrame.p,startFrame.p),gateChord=len(gateVec),worldUp={x:0,y:1,z:0};
   const startH=horizontal(startFrame.forward)||norm(startFrame.forward),flatRight=norm(cross(worldUp,startH)),outwardSign=(startFrame.p.x*flatRight.x+startFrame.p.z*flatRight.z)>=0?1:-1,ringForward=norm(rotateAround(startH,worldUp,outwardSign*.16));
   let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=flatRight;const ringUp=norm(cross(ringForward,ringRight));
   const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=clamp(gateChord*.34,7.0,11.5),legRise=1.45,ringSideShift=17.0;
   const desiredEntry=add(add(add(startFrame.p,mul(startH,legLead)),mul(ringUp,legRise)),mul(flatRight,outwardSign*ringSideShift));
   const ringBase=sub(sub(desiredEntry,mul(ringForward,gapAlong)),mul(ringUp,joinRise));
   const ringSep=7.5,crownPush=9.5;
   const circlePos=th=>{const c=Math.cos(th),sn=Math.sin(th),q=clamp((th-open)/(TAU-open*2),0,1),engage=smooth01((q-.12)/.30),lat=outwardSign*ringSep*engage,crown=Math.sin(Math.PI*q),advance=crownPush*crown*crown;return add(add(add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lat)),mul(ringForward,advance));};
   const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),h=.0025,a=circlePos(Math.max(open,th-h)),b=circlePos(Math.min(TAU-open,th+h)),pos=circlePos(th),tangent=norm(sub(b,a)),seed=norm(add(mul(ringUp,c),mul(ringForward,-sn))),up=orthoUp(seed,tangent,ringUp);return{pos,tangent,up};};
   const ringEntry=circleAt(open),ringExit=circleAt(TAU-open),entryDist=len(sub(ringEntry.pos,startFrame.p)),exitDist=len(sub(endFrame.p,ringExit.pos)),entryScale=clamp(entryDist*.88,13.0,24.0),exitScale=clamp(exitDist*.88,14.0,26.0);
   const LEG_STEPS=Math.max(12,Math.round(LOOP_STEPS*.18)),RING_STEPS=Math.max(48,LOOP_STEPS-LEG_STEPS*2);
   const pushLeg=(p0,t0,u0,p1,t1,u1,scale,steps,skipFirst=false)=>{
    for(let j=skipFirst?1:0;j<=steps;j++){
     const q=j/steps,dq=.18/steps,pos=hermite(p0,t0,p1,t1,scale,q),prev=hermite(p0,t0,p1,t1,scale,Math.max(0,q-dq)),next=hermite(p0,t0,p1,t1,scale,Math.min(1,q+dq)),tangent=norm(sub(next,prev)),w=smooth01(q),seed=mixV(u0,u1,w),up=orthoUp(seed,tangent,ringUp);
     raw.push({x:pos.x,y:pos.y,z:pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent});
    }
   };
   const entryForward=norm(add(startFrame.forward,mul(startFrame.up,.20)));
   pushLeg(startFrame.p,entryForward,startFrame.up,ringEntry.pos,ringEntry.tangent,ringEntry.up,entryScale,LEG_STEPS,false);
   for(let j=1;j<=RING_STEPS;j++){
    const q=j/RING_STEPS,th=open+(TAU-open*2)*q,p=circleAt(th);
    raw.push({x:p.pos.x,y:p.pos.y,z:p.pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:p.up,explicitForward:p.tangent});
   }
   pushLeg(ringExit.pos,ringExit.tangent,ringExit.up,endFrame.p,endFrame.forward,endFrame.up,exitScale,LEG_STEPS,true);
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
