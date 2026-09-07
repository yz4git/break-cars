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
