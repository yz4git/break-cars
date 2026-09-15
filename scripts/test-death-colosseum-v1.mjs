import assert from 'node:assert/strict';
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'..');
const site=path.join(root,'_site');
const courses=['death-wheel','razor-cross','broken-orbit','sky-tiles','hex-drop'];
const holes={
 'death-wheel':[Math.sin(Math.PI/8)*20,Math.cos(Math.PI/8)*20],
 'razor-cross':[12,12],
 'broken-orbit':[0,8],
 'sky-tiles':[11,11],
 'hex-drop':[Math.sin(Math.PI/6)*18,Math.cos(Math.PI/6)*18],
};

if(!process.env.DEATH_COLOSSEUM_CHILD){
 for(const course of courses){
  const run=spawnSync(process.execPath,[fileURLToPath(import.meta.url)],{cwd:root,env:{...process.env,DEATH_COLOSSEUM_CHILD:'1',DEATH_COLOSSEUM_COURSE:course},encoding:'utf8'});
  if(run.stdout)process.stdout.write(run.stdout);
  if(run.stderr)process.stderr.write(run.stderr);
  assert.equal(run.status,0,`${course} Death Colosseum runtime probe failed`);
 }
 const catalogue=fs.readFileSync(path.join(site,'courses.js'),'utf8');
 const index=fs.readFileSync(path.join(site,'index.html'),'utf8');
 const physics=fs.readFileSync(path.join(site,'physics.js'),'utf8');
 const physics3d=fs.readFileSync(path.join(site,'physics3d.js'),'utf8');
 const view=fs.readFileSync(path.join(site,'course-view.js'),'utf8');
 for(const id of courses)assert.ok(catalogue.includes(`id:'${id}'`),`${id} missing from Death Colosseum catalogue`);
 assert.ok(index.includes('data-mode="death-colosseum"'),'Death Colosseum mode button missing');
 assert.ok(physics.includes("w.mode==='death-colosseum'&&!c.fallFatal"),'fall-only HP clamp missing');
 assert.ok(physics3d.includes('c.fallFatal=true'),'fatal fall override missing');
 assert.ok(view.includes("activeCourse.mode==='death-colosseum'"),'Death Colosseum renderer missing');
 console.log('Death Colosseum v1: 5 fall-only courses passed');
 process.exit(0);
}

const id=process.env.DEATH_COLOSSEUM_COURSE;
globalThis.location={search:`?course=${id}`};
const base=`file://${site}`;
const courseMod=await import(`${base}/courses.js?death=${id}`);
assert.equal(courseMod.activeCourse.id,id);
assert.equal(courseMod.activeCourse.mode,'death-colosseum');
assert.equal(courseMod.activeCourse.survival,true);
assert.equal(courseMod.activeCourse.fallOnly,true);
assert.equal(courseMod.activeCourse.spawns.length,12);
for(const [x,z] of courseMod.activeCourse.spawns)assert.equal(courseMod.courseHeight(x,z),9,`${id}: spawn ${x},${z} is not on deck`);
const [hx,hz]=holes[id];
assert.equal(courseMod.courseHeight(hx,hz),null,`${id}: authored fall-through hole missing`);

const physics=await import(`${base}/physics.js?death=${id}`);
const w=physics.makeWorld(0,91626,'death-colosseum');
physics.step(w,{gas:0,brake:0,steer:0,hand:0},1/60,true);
const deathY=courseMod.activeCourse.deathY;
for(const c of w.cars){
 assert.equal(c.dead,false,`${id}: car ${c.id} spawned dead`);
 assert.ok(c.p3?.active,`${id}: car ${c.id} missing full 3D body`);
 assert.ok(c.p3.py>deathY+1,`${id}: car ${c.id} spawned too low (${c.p3.py})`);
}

const p=w.cars[0];
physics.hit(w,p,99999,1,0,w.cars[1]);
assert.equal(p.dead,false,`${id}: impact damage must not eliminate in Death Colosseum`);
assert.equal(p.hp,1,`${id}: impact damage should clamp at 1 HP`);

p.lastOpponent=1;p.lastContact=w.time;p.p3.px=52;p.p3.pz=52;p.p3.py=5.5;p.p3.vy=-5;
const kills=w.cars[1].kills;
physics.step(w,{},1/60,true);
assert.equal(p.dead,true,`${id}: falling below deck must instantly WRECK`);
const fall=w.events.find(e=>e.type==='fall'&&e.car===0);
assert.ok(fall,`${id}: fall event missing`);
assert.equal(fall.by,1,`${id}: last pusher did not receive fall credit`);
assert.equal(w.cars[1].kills,kills+1,`${id}: ring-out did not count as WRECK`);
console.log(`${id}: spawn + fall-only elimination + pusher credit passed`);
