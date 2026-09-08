"""Multi-loop course integration, applied after existing course selection."""
def apply_extreme_courses(target):
 p=target/'racing3d.js';s=p.read_text()
 s=s.replace("const skyForge=activeCourse.id==='sky-forge';", "const skyForge=activeCourse.id==='sky-forge',doubleOrbit=activeCourse.id==='double-orbit';")
 s=s.replace('loopRadius:skyForge?7.5:6.8','loopRadius:doubleOrbit?8.6:skyForge?7.5:7.2')
 s=s.replace('const LOOP_T=.88,', 'const LOOP_T=.88,')
 s=s.replace('ts.push(LOOP_T);','ts.push(LOOP_T);if(doubleOrbit)ts.push(3.85);')
 s=s.replace('let loopInserted=false;', 'const insertedLoops=new Set();')
 s=s.replace('if(!loopInserted&&Math.abs(t-LOOP_T)<1e-6){', 'if(!insertedLoops.has(t)&&(Math.abs(t-LOOP_T)<1e-6||(doubleOrbit&&Math.abs(t-3.85)<1e-6))){')
 s=s.replace('loopInserted=true;', 'insertedLoops.add(t);')
 s=s.replace('(skyForge?70:62)', '(doubleOrbit?71:skyForge?70:62)').replace('(skyForge?7*Math.sin(2*t):0)', '(doubleOrbit?9*Math.sin(2*t):skyForge?7*Math.sin(2*t):0)').replace('(skyForge?47:40)', '(doubleOrbit?48:skyForge?47:40)')
 s=s.replace('(skyForge?10.5:7.4)', '(doubleOrbit?14.5:skyForge?10.5:7.4)').replace('skyForge?.36:.28','doubleOrbit?.43:skyForge?.36:.28')
 s=s.replace('clamp((skyForge?.43:.34)*Math.sin(2*t),-.44,.44)', 'clamp((doubleOrbit?.72:skyForge?.43:.34)*Math.sin(2*t),doubleOrbit?-.74:-.44,doubleOrbit?.74:.44)*(doubleOrbit?(1-gauss(t,.88,.35))*(1-gauss(t,3.85,.35)):1)')

 # A real toy-track loop is not a closed circle laid on top of a road.  Its
 # bottom arc is open: the incoming road becomes one lower leg, joins the ring
 # on the near/ascending side, travels around the ring, then leaves through a
 # separate descending leg.  The two legs are allowed to cross/offset at the
 # bottom exactly like the reference track, but the drivable face is continuous.
 #
 # Crucially the ring orientation comes from the INCOMING ROAD DIRECTION, not
 # from the vector between the two gate positions.  Using the gate chord as the
 # ring axis was what could make the car drive into the back face of the loop.
 start=s.index('const raw=[];')
 end=s.index('// Remove accidental duplicate',start)
 open_loop="""const LOOP_HALF_T=.10,LOOP_OPEN_ANGLE=.42;
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
  const startT=startCenter-LOOP_HALF_T,endT=startCenter+LOOP_HALF_T,startFrame=roadFrameAt(startT),endFrame=roadFrameAt(endT),gateVec=sub(endFrame.p,startFrame.p),gateChord=len(gateVec),worldUp={x:0,y:1,z:0};

  // The ring faces exactly where the car is already travelling.  The outgoing
  // road is handled by its own lower leg and is never allowed to rotate the
  // ring behind the incoming road.
  const startH=horizontal(startFrame.forward)||norm(startFrame.forward),endH=horizontal(endFrame.forward)||norm(endFrame.forward),ringForward=startH;
  let ringRight=norm(cross(worldUp,ringForward));if(len(ringRight)<.2)ringRight=startFrame.right;const ringUp=norm(cross(ringForward,ringRight));

  // Cut the bottom arc out of the circle.  Anchor the ring solely from the
  // incoming leg, with a deliberate rise before the circular part begins.  The
  // outgoing leg absorbs the positional mismatch on the far lower side.  This
  // is the two-leg construction visible in the reference photo.
  const open=LOOP_OPEN_ANGLE,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),legLead=clamp(gateChord*.22,1.8,3.6),legRise=.85;
  const desiredEntry=add(add(startFrame.p,mul(startH,legLead)),mul(ringUp,legRise));
  const ringBase=sub(sub(desiredEntry,mul(ringForward,gapAlong)),mul(ringUp,joinRise));
  const circleAt=th=>{const c=Math.cos(th),sn=Math.sin(th),pos=add(add(ringBase,mul(ringForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),tangent=norm(add(mul(ringForward,c),mul(ringUp,sn))),up=norm(add(mul(ringUp,c),mul(ringForward,-sn)));return{pos,tangent,up};};
  const ringEntry=circleAt(open),ringExit=circleAt(TAU-open),entryDist=len(sub(ringEntry.pos,startFrame.p)),exitDist=len(sub(endFrame.p,ringExit.pos)),entryScale=clamp(entryDist*.46,2.1,4.2),exitScale=clamp(exitDist*.42,2.2,5.0);
  const LEG_STEPS=Math.max(12,Math.round(LOOP_STEPS*.18)),RING_STEPS=Math.max(48,LOOP_STEPS-LEG_STEPS*2);
  const pushLeg=(p0,t0,u0,p1,t1,u1,scale,steps,skipFirst=false)=>{
   for(let j=skipFirst?1:0;j<=steps;j++){
    const q=j/steps,dq=.18/steps,pos=hermite(p0,t0,p1,t1,scale,q),prev=hermite(p0,t0,p1,t1,scale,Math.max(0,q-dq)),next=hermite(p0,t0,p1,t1,scale,Math.min(1,q+dq)),tangent=norm(sub(next,prev)),w=smooth01(q),seed=mixV(u0,u1,w),up=orthoUp(seed,tangent,ringUp);
    raw.push({x:pos.x,y:pos.y,z:pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent});
   }
  };

  // Entry leg: the existing road first advances and rises; only then does it
  // join the ascending side of the ring.  No segment can turn behind the gate.
  pushLeg(startFrame.p,startFrame.forward,startFrame.up,ringEntry.pos,ringEntry.tangent,ringEntry.up,entryScale,LEG_STEPS,false);

  // Main ring: nearly planar and vertical; there is intentionally no bottom arc.
  for(let j=1;j<=RING_STEPS;j++){
   const q=j/RING_STEPS,th=open+(TAU-open*2)*q,p=circleAt(th);
   raw.push({x:p.pos.x,y:p.pos.y,z:p.pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:p.up,explicitForward:p.tangent});
  }

  // Exit leg: descend from the opposite lower side, then curve forward into the
  // authored outgoing road.  It is a separate physical leg, as in the photo.
  pushLeg(ringExit.pos,ringExit.tangent,ringExit.up,endFrame.p,endFrame.forward,endFrame.up,exitScale,LEG_STEPS,true);
  continue;
 }
 if(insideLoop)continue;
 const p=baseAt(t);raw.push({...p,explicitUp:null});
}

"""
 s=s[:start]+open_loop+s[end:]
 marker='export function race3DFeatureSpec(){'
 assert marker in s
 s=s.replace(marker,"const loopGroups=[...new Set(loopPts.map(p=>p.t))].map(t=>{const a=loopPts.filter(p=>p.t===t);return{radius:LOOP_R,startS:a[0].s,endS:a.at(-1).s,maxY:Math.max(...a.map(p=>p.y))};});\nexport function raceLoopAt(s){const q=wrapS(s),inside=loopGroups.find(l=>q>=l.startS&&q<=l.endS);return inside||loopGroups.reduce((a,b)=>wrapS(b.startS-q)<wrapS(a.startS-q)?b:a);}\n"+marker)
 s=s.replace('loop:{radius:LOOP_R,startS:loopStart,endS:loopEnd,maxY:Math.max(...loopPts.map(p=>p.y))}', 'loop:loopGroups[0],loops:loopGroups')
 p.write_text(s)
 # AI, boost forces and camera all select the current/next actual loop.
 p=target/'racing.js';s=p.read_text();s="import {raceLoopAt} from './racing3d.js';\n"+s;s=s.replace('forwardGap(COURSE_SPEC.loop.startS,p.s)','forwardGap(raceLoopAt(p.s).startS,p.s)');p.write_text(s)
 p=target/'physics3d.js';s=p.read_text();s="import {raceLoopAt} from './racing3d.js';\n"+s
 s=s.replace('RAMPAGE_RACE_SPEC.loop.startS','raceLoopAt(c.trackS??0).startS').replace('RAMPAGE_RACE_SPEC.loop.endS','raceLoopAt(c.trackS??0).endS');p.write_text(s)
 p=target/'game.js';s=p.read_text();s="import {raceLoopAt} from './racing3d.js';\n"+s;s=s.replace('raceLoopSpec=fullPhysicsSpec.race?.loop','raceLoopSpec=gameMode===\'racing\'?raceLoopAt(p.trackS??0):null');p.write_text(s)
 p=target/'track-view.js';s=p.read_text()
 a=s.index(' // Explicit loop ribs');b=s.index(' // Jump take-off',a)
 block=s[a:b].replace('spec.loop','loop')
 s=s[:a]+" for(const loop of spec.loops||[spec.loop]){\n"+block+" }\n"+s[b:]
 s=s.replace("activeCourse.id==='sky-forge'?0x72d8d3:0xff7042", "activeCourse.id==='double-orbit'?0xdb83ff:activeCourse.id==='sky-forge'?0x72d8d3:0xff7042")
 p.write_text(s)
