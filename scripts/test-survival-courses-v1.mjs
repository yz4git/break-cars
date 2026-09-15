import assert from 'node:assert/strict';
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'..');
const courses=['last-platform','void-hunt','skyfall-circuit'];

if(!process.env.SURVIVAL_COURSE_CHILD){
 for(const course of courses){
  const run=spawnSync(process.execPath,[fileURLToPath(import.meta.url)],{cwd:root,env:{...process.env,SURVIVAL_COURSE_CHILD:'1',SURVIVAL_COURSE:course},encoding:'utf8'});
  if(run.stdout)process.stdout.write(run.stdout);
  if(run.stderr)process.stderr.write(run.stderr);
  assert.equal(run.status,0,`${course} survival runtime probe failed`);
 }
 const catalogue=fs.readFileSync(path.join(root,'_site/courses.js'),'utf8');
 const physics3d=fs.readFileSync(path.join(root,'_site/physics3d.js'),'utf8');
 const racing=fs.readFileSync(path.join(root,'_site/racing.js'),'utf8');
 const trackView=fs.readFileSync(path.join(root,'_site/track-view.js'),'utf8');
 for(const id of courses)assert.ok(catalogue.includes(`id:'${id}'`),`${id} missing from generated course catalogue`);
 assert.ok(physics3d.includes('function survivalFall'),'fall death hook missing');
 assert.ok(physics3d.includes("type:'fall'"),'fall event missing');
 assert.ok(racing.includes('if(mathCourseV1.survival)return null;'),'survival racing still has invisible edge correction');
 assert.ok(racing.includes('if(mathCourseV1.survival)return false;'),'survival racing recovery must be disabled');
 assert.ok(trackView.includes('if(!survival){edgeTube'),'SKYFALL rails were not removed');
 console.log('Survival course pack v1: all 3 modes passed');
 process.exit(0);
}

const id=process.env.SURVIVAL_COURSE;
globalThis.location={search:`?course=${id}`};
const courseMod=await import(`../_site/courses.js?survival=${id}`);
assert.equal(courseMod.activeCourse.id,id);
assert.equal(courseMod.activeCourse.survival,true);

if(id==='last-platform'||id==='void-hunt'){
 assert.equal(courseMod.courseHeight(0,0),8,`${id} hub deck height`);
 assert.equal(courseMod.courseHeight(32,0),8,`${id} outer ring must support respawns/spawns`);
 const hole=courseMod.courseHeight(Math.sin(Math.PI/12)*25,Math.cos(Math.PI/12)*25);
 assert.equal(hole,null,`${id} needs a real fall-through hole`);
 if(id==='void-hunt')assert.equal(courseMod.courseHeight(0,26),null,'VOID HUNT must keep the jump gap between bridge and ring');
}

if(id==='skyfall-circuit'){
 const race3d=await import(`../_site/racing3d.js?survival=${id}`);
 const spec=race3d.race3DFeatureSpec();
 assert.equal(spec.courseId,id);
 assert.equal(spec.halfWidth,5.8);
 assert.ok(spec.minY>=9.95,`SKYFALL road must remain elevated, minY=${spec.minY}`);
 assert.ok(spec.jump.gapLength>0,'SKYFALL needs a real jump gap');
}

const physics=await import(`../_site/physics.js?survival=${id}`);
const mode=courseMod.activeCourse.mode;
const w=physics.makeWorld(0,91415,mode);
physics.step(w,{gas:0,brake:0,steer:0,hand:0},1/60,true);
const p=w.cars[0],deathY=Number(courseMod.activeCourse.deathY??6.2);
assert.ok(p.p3?.active,`${id} player full-3D body missing`);
assert.equal(p.dead,false,`${id}: player must start alive on the elevated course`);
for(const c of w.cars){
 assert.ok(c.p3?.active,`${id}: car ${c.id} full-3D body missing at spawn`);
 assert.equal(c.dead,false,`${id}: car ${c.id} must not spawn below the survival deck`);
 assert.ok(c.p3.py>deathY+1.0,`${id}: car ${c.id} spawned too low at y=${c.p3.py.toFixed(2)}`);
}

// Simulate a real push-out after the body has left the deck. The killer credit
// should survive because fall death goes through the ordinary hit/wreck path.
p.lastOpponent=1;p.lastContact=w.time;
p.p3.px=52;p.p3.pz=52;p.p3.py=5.55;p.p3.vy=-5;
physics.step(w,{gas:0,brake:0,steer:0,hand:0},1/60,true);
assert.equal(p.dead,true,`${id}: falling below the deck must be one-hit death`);
const fall=w.events.find(e=>e.type==='fall'&&e.car===0);
assert.ok(fall,`${id}: explicit fall event missing`);
assert.equal(fall.by,1,`${id}: recent pusher should receive fall credit`);
assert.ok(w.cars[1].kills>=1,`${id}: push-out must count as a WRECK for the opponent`);

if(id==='void-hunt'){
 assert.equal(w.done,true,'VOID HUNT must end immediately when the player falls');
 const w2=physics.makeWorld(0,91416,mode);physics.step(w2,{},1/60,true);
 const enemy=w2.cars[1];enemy.p3.px=52;enemy.p3.pz=52;enemy.p3.py=5.55;enemy.p3.vy=-5;
 physics.step(w2,{},1/60,true);
 assert.equal(enemy.dead,true,'VOID HUNT enemy fall must wreck the enemy');
 assert.ok(Number.isFinite(enemy.respawnAt)&&enemy.respawnAt>w2.time,'VOID HUNT fallen enemy must remain compatible with respawn loop');
}

if(id==='skyfall-circuit'){
 const racing=await import(`../_site/racing.js?survival=${id}`);
 assert.equal(racing.recoverRaceCar(w,p),false,'SKYFALL must not allow recovery after a fall');
}

console.log(`${id}: elevated-spawn + fall=WRECK runtime passed`);
