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
 const w=makeWorld(0,144,activeCourse.mode);let impacts=0,hi=0,lo=100,air=0;
 for(let i=0;i<1800&&!w.done;i++){step(w,{},1/60,true);for(const c of w.cars){const b=c.p3;assert(Number.isFinite(b.px+b.py+b.pz+b.qw));assert(Math.abs(b.py)<30);hi=Math.max(hi,b.py);lo=Math.min(lo,b.py);air=Math.max(air,b.airTime);}impacts+=w.events.filter(e=>e.type==='impact').length;}
 assert(hi-lo>2);assert(impacts>5);console.log(activeCourse.name+': shared mesh/physics heights, 30s pack, impacts='+impacts+', height range='+(hi-lo).toFixed(2)+', air='+air.toFixed(2));
}
