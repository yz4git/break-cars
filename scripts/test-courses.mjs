import assert from 'node:assert/strict';
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
if(!process.env.COURSE_TEST){for(const id of ['crater-crown','tidal-foundry','sky-forge','maelstrom-pit','cross-fire','double-orbit']){const r=spawnSync(process.execPath,[import.meta.filename],{env:{...process.env,COURSE_TEST:id},encoding:'utf8'});process.stdout.write(r.stdout);process.stderr.write(r.stderr);assert.equal(r.status,0,id);}process.exit(0);}
globalThis.location={search:'?course='+process.env.COURSE_TEST};
const html=fs.readFileSync(new URL('../_site/index.html',import.meta.url),'utf8'),version=html.match(/game.js\?v=([^"']+)/)[1];
const load=p=>import(new URL('../_site/'+p+'?v='+version,import.meta.url));
const {activeCourse,courseHeight}=await load('courses.js'),{makeWorld,step}=await load('physics.js');
if(activeCourse.id==='double-orbit'){await import('./test-double-orbit.mjs');}
else if(activeCourse.id==='sky-forge'){await import('./test-sky-raceability.mjs');}
else if(activeCourse.mode==='racing'){await import('./test-rampage-raceability.mjs');}
else{
 const {buildCourseTerrain}=await load('course-view.js'),g=buildCourseTerrain(),pos=g.children[0].geometry.attributes.position;
 for(let i=0;i<pos.count;i+=19)assert(Math.abs(pos.getY(i)-courseHeight(pos.getX(i),pos.getZ(i))-.015)<.001);

 // A terrain course must be a game space, not just a dramatic height field.
 // The arena AI steers directly toward targets and has no terrain pathfinder, so
 // spawn pads and straight approaches to the center must remain driveable.
 const slopeAt=(x,z)=>{const e=.12,gx=(courseHeight(x+e,z)-courseHeight(x-e,z))/(2*e),gz=(courseHeight(x,z+e)-courseHeight(x,z-e))/(2*e);return Math.atan(Math.hypot(gx,gz))*180/Math.PI;};
 let samples=0,steep30=0,steep40=0,maxSlope=0;
 for(let x=-40;x<=40;x+=2)for(let z=-40;z<=40;z+=2){if(Math.hypot(x,z)>40)continue;const d=slopeAt(x,z);samples++;if(d>30)steep30++;if(d>40)steep40++;maxSlope=Math.max(maxSlope,d);}
 const spawnSlopes=[],ingress=[];
 for(let i=0;i<12;i++){
  const a=i/12*Math.PI*2,sx=Math.sin(a)*32,sz=Math.cos(a)*32;spawnSlopes.push(slopeAt(sx,sz));
  let routeMax=0;for(let r=32;r>=0;r-=.5)routeMax=Math.max(routeMax,slopeAt(Math.sin(a)*r,Math.cos(a)*r));ingress.push(routeMax);
 }
 const share30=steep30/samples,share40=steep40/samples,spawnMax=Math.max(...spawnSlopes),ingressMax=Math.max(...ingress);
 assert(share30<.08,`${activeCourse.id}: too much terrain above 30deg (${(share30*100).toFixed(1)}%)`);
 assert(share40<.03,`${activeCourse.id}: too much terrain above 40deg (${(share40*100).toFixed(1)}%)`);
 assert(spawnMax<26,`${activeCourse.id}: cars spawn on unsafe slope ${spawnMax.toFixed(1)}deg`);
 assert(ingressMax<40,`${activeCourse.id}: direct center approach blocked by ${ingressMax.toFixed(1)}deg slope`);

 const w=makeWorld(0,144,activeCourse.mode);let impacts=0,hi=0,lo=100,air=0;
 for(let i=0;i<1800&&!w.done;i++){step(w,{},1/60,true);for(const c of w.cars){const b=c.p3;assert(Number.isFinite(b.px+b.py+b.pz+b.qw));assert(Math.abs(b.py)<30);hi=Math.max(hi,b.py);lo=Math.min(lo,b.py);air=Math.max(air,b.airTime);}impacts+=w.events.filter(e=>e.type==='impact').length;}
 assert(hi-lo>2);assert(impacts>5);
 console.log(activeCourse.name+': playable terrain, impacts='+impacts+', height range='+(hi-lo).toFixed(2)+', max slope='+maxSlope.toFixed(1)+'deg, spawn='+spawnMax.toFixed(1)+'deg, ingress='+ingressMax.toFixed(1)+'deg, steep30='+(share30*100).toFixed(1)+'%');
}
