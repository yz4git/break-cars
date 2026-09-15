import assert from 'node:assert/strict';
import fs from 'node:fs';

globalThis.location={search:'?course=rampage-3d'};
const stamp=Date.now();
const physics=await import(`../_site/physics.js?minute=${stamp}`);
const racing=await import(`../_site/racing.js?minute=${stamp}`);
const {makeWorld,step}=physics;
const {TRACK}=racing;

assert.equal(TRACK.laps,2,'WRECKING RACING should resolve in two laps');
assert.equal(TRACK.limit,65,'WRECKING RACING should have a roughly one-minute safety cap');
assert.equal(TRACK.grace,8,'post-leader grace should stay short');

const colosseum=makeWorld(0,123,'colosseum');
assert.equal(colosseum.stageLimit,60);
colosseum.time=59.99;
for(const c of colosseum.cars){c.dead=false;c.hp=c.maxHP;c.lastContact=colosseum.time;}
step(colosseum,{},1/60,true);
assert.equal(colosseum.done,true,'COLOSSEUM must resolve at about 60 seconds');

const hunt=makeWorld(0,456,'wreck-hunt');
assert.equal(hunt.stageLimit,60);
hunt.time=59.99;
hunt.cars[0].dead=false;
hunt.cars[0].hp=hunt.cars[0].maxHP;
step(hunt,{},1/60,true);
assert.equal(hunt.done,true,'WRECK HUNT must resolve at about 60 seconds');

const race=makeWorld(0,789,'racing');
assert.equal(race.endAt,65);
race.time=64.99;
for(const c of race.cars){c.dead=false;c.finished=false;}
step(race,{},1/60,true);
assert.equal(race.done,true,'WRECKING RACING must resolve by the 65 second safety cap');

const game=fs.readFileSync(new URL('../_site/game.js',import.meta.url),'utf8');
const courses=fs.readFileSync(new URL('../_site/courses.js',import.meta.url),'utf8');
assert.match(game,/60 SECONDS/);
assert.match(game,/2 LAPS/);
assert.doesNotMatch(game,/150 SECONDS|150秒|4 LAPS|4周/);
assert.doesNotMatch(courses,/4周/);
console.log(`One-minute pacing OK: colosseum=${colosseum.stageLimit}s hunt=${hunt.stageLimit}s racing=${TRACK.laps} laps/${TRACK.limit}s grace=${TRACK.grace}s`);
