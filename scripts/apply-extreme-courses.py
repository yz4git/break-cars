"""Multi-loop course integration, applied after existing course selection."""
def apply_extreme_courses(target):
 p=target/'racing3d.js';s=p.read_text()
 s=s.replace("const skyForge=activeCourse.id==='sky-forge';", "const skyForge=activeCourse.id==='sky-forge',doubleOrbit=activeCourse.id==='double-orbit';")
 s=s.replace('loopRadius:skyForge?7.5:6.8','loopRadius:doubleOrbit?8.6:skyForge?7.5:6.8')
 s=s.replace('const LOOP_T=.88,', 'const LOOP_T=.88,')
 s=s.replace('ts.push(LOOP_T);','ts.push(LOOP_T);if(doubleOrbit)ts.push(3.85);')
 s=s.replace('let loopInserted=false;', 'const insertedLoops=new Set();')
 s=s.replace('if(!loopInserted&&Math.abs(t-LOOP_T)<1e-6){', 'if(!insertedLoops.has(t)&&(Math.abs(t-LOOP_T)<1e-6||(doubleOrbit&&Math.abs(t-3.85)<1e-6))){')
 s=s.replace('loopInserted=true;', 'insertedLoops.add(t);')
 s=s.replace('(skyForge?70:62)', '(doubleOrbit?71:skyForge?70:62)').replace('(skyForge?7*Math.sin(2*t):0)', '(doubleOrbit?9*Math.sin(2*t):skyForge?7*Math.sin(2*t):0)').replace('(skyForge?47:40)', '(doubleOrbit?48:skyForge?47:40)')
 s=s.replace('(skyForge?10.5:7.4)', '(doubleOrbit?14.5:skyForge?10.5:7.4)').replace('skyForge?.36:.28','doubleOrbit?.43:skyForge?.36:.28')
 s=s.replace('clamp((skyForge?.43:.34)*Math.sin(2*t),-.44,.44)', 'clamp((doubleOrbit?.72:skyForge?.43:.34)*Math.sin(2*t),doubleOrbit?-.74:-.44,doubleOrbit?.74:.44)*(doubleOrbit?(1-gauss(t,.88,.35))*(1-gauss(t,3.85,.35)):1)')

 # Convert the old closed-circle insertion into an open, progressive twist loop.
 # Entry and exit are separate points on the authored base course.  The centerline
 # advances through the loop while a small lateral S-twist prevents the two lower
 # legs from occupying the same space.  A slightly tighter crown gives the stunt
 # a more realistic teardrop profile while preserving full 6DoF surface normals.
 start=s.index('const raw=[];')
 end=s.index('// Remove accidental duplicate',start)
 open_loop="""const LOOP_HALF_T=.18,LOOP_TWIST=LOOP_R*.32;
const loopCenters=doubleOrbit?[LOOP_T,3.85]:[LOOP_T];
const raw=[];
const ts=[];for(let i=0;i<=BASE_STEPS;i++)ts.push(i/BASE_STEPS*TAU);for(const c of loopCenters)ts.push(c-LOOP_HALF_T,c+LOOP_HALF_T);ts.sort((a,b)=>a-b);
const insertedLoops=new Set();
for(const t of ts){
 if(t>TAU+EPS)continue;
 const startCenter=loopCenters.find(c=>Math.abs(t-(c-LOOP_HALF_T))<1e-6),insideLoop=loopCenters.some(c=>t>=c-LOOP_HALF_T-EPS&&t<=c+LOOP_HALF_T+EPS);
 if(startCenter!==undefined&&!insertedLoops.has(startCenter)){
  insertedLoops.add(startCenter);
  const entry=baseAt(startCenter-LOOP_HALF_T),exit=baseAt(startCenter+LOOP_HALF_T),delta=sub(exit,entry),worldUp={x:0,y:1,z:0},f=norm({x:delta.x,y:0,z:delta.z}),side=norm(cross(worldUp,f));
  const sample=u=>{
   const th=-Math.PI/2+u*TAU,c=Math.cos(th),sn=Math.sin(th),crown=Math.sin(Math.PI*u),radialScale=1-.16*crown,verticalScale=1-.08*crown,drift=add(entry,mul(delta,u)),lateral=LOOP_TWIST*crown*crown*Math.sin(TAU*u);
   const pos=add(add(add(drift,mul(f,LOOP_R*radialScale*c)),mul(worldUp,LOOP_R*verticalScale*(1+sn))),mul(side,lateral)),center=add(drift,mul(worldUp,LOOP_R*verticalScale));
   return{pos,center};
  };
  for(let j=0;j<=LOOP_STEPS;j++){
   const u=j/LOOP_STEPS,du=.25/LOOP_STEPS,here=sample(u),prev=sample(Math.max(0,u-du)),next=sample(Math.min(1,u+du)),tangent=norm(sub(next.pos,prev.pos));
   const radialUp=norm(sub(here.center,here.pos)),roll=.20*Math.sin(Math.PI*u)*Math.sin(TAU*u),up=norm(rotateAround(radialUp,tangent,roll));
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
