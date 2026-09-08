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

 # Build the loop exactly like a real toy/race-track vertical loop: the road
 # itself leaves the ordinary spine, turns through one vertical revolution in
 # the forward/up plane, and returns to the outgoing road.  There is no lateral
 # helix and no second flat ribbon underneath.  A cubic Hermite gate spine gives
 # exact position/tangent continuity at both ends while the circular offset is
 # zero at the gates.  The mild phase easing keeps the bottom transitions smooth
 # without flattening the crown or turning the loop into a side-to-side spiral.
 start=s.index('const raw=[];')
 end=s.index('// Remove accidental duplicate',start)
 open_loop="""const LOOP_HALF_T=.10;
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
for(const t of ts){
 if(t>TAU+EPS)continue;
 const startCenter=loopCenters.find(c=>Math.abs(t-(c-LOOP_HALF_T))<1e-6),insideLoop=loopCenters.some(c=>t>=c-LOOP_HALF_T-EPS&&t<=c+LOOP_HALF_T+EPS);
 if(startCenter!==undefined&&!insertedLoops.has(startCenter)){
  insertedLoops.add(startCenter);
  const startT=startCenter-LOOP_HALF_T,endT=startCenter+LOOP_HALF_T,startFrame=roadFrameAt(startT),endFrame=roadFrameAt(endT),gateChord=len(sub(endFrame.p,startFrame.p)),gateScale=Math.max(gateChord,LOOP_R*1.15);
  const sample=u=>{
   const u2=u*u,u3=u2*u,h00=2*u3-3*u2+1,h10=u3-2*u2+u,h01=-2*u3+3*u2,h11=u3-u2;
   const base={x:h00*startFrame.p.x+h10*gateScale*startFrame.forward.x+h01*endFrame.p.x+h11*gateScale*endFrame.forward.x,y:h00*startFrame.p.y+h10*gateScale*startFrame.forward.y+h01*endFrame.p.y+h11*gateScale*endFrame.forward.y,z:h00*startFrame.p.z+h10*gateScale*startFrame.forward.z+h01*endFrame.p.z+h11*gateScale*endFrame.forward.z};
   const forwardAxis=mixV(startFrame.forward,endFrame.forward,u),upSeed=mixV(startFrame.up,endFrame.up,u);let sideAxis=norm(cross(upSeed,forwardAxis));if(len(sideAxis)<.2)sideAxis=startFrame.right;const planeUp=norm(cross(forwardAxis,sideAxis));
   const phase=u-.18*Math.sin(TAU*u)/TAU,th=phase*TAU,c=Math.cos(th),sn=Math.sin(th),pos=add(add(base,mul(forwardAxis,LOOP_R*sn)),mul(planeUp,LOOP_R*(1-c)));
   const loopUp=norm(add(mul(planeUp,c),mul(forwardAxis,-sn))),center=add(base,mul(planeUp,LOOP_R));
   return{pos,center,forwardAxis,planeUp,loopUp};
  };
  for(let j=0;j<=LOOP_STEPS;j++){
   const u=j/LOOP_STEPS,du=.25/LOOP_STEPS,here=sample(u),prev=sample(Math.max(0,u-du)),next=sample(Math.min(1,u+du)),tangent=norm(sub(next.pos,prev.pos));
   const roll=.035*Math.sin(Math.PI*u)*Math.sin(TAU*u),up=norm(rotateAround(here.loopUp,tangent,roll));
   raw.push({x:here.pos.x,y:here.pos.y,z:here.pos.z,t:startCenter,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent});
  }
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
