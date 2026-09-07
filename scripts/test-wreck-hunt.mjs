import assert from 'node:assert/strict';
import fs from 'node:fs';

const physics = await import(`../_site/physics.js?hunt-test=${Date.now()}`);
const {makeWorld,step} = physics;

const w = makeWorld(0, 91, 'wreck-hunt');
assert.equal(w.mode, 'wreck-hunt');
assert.equal(w.limit, 150);
assert.ok(w.hunt);
assert.equal(w.hunt.combo, 0);
assert.ok(w.cars[0].maxHP > 138, 'hunter should have extra durability');
assert.ok(w.cars.slice(1).every(c => c.maxHP >= 46 && c.maxHP <= 72), 'hunt targets should be soft enough for fast finishers');
assert.equal(w.cars[0].z, 10, 'hunter should start inside the action instead of on the outer ring');
assert.ok(w.cars.slice(1).every(c => Math.hypot(c.x,c.z) >= 19 && Math.hypot(c.x,c.z) <= 26), 'targets should start on the inner combat ring');

const gameSource = fs.readFileSync(new URL('../_site/game.js', import.meta.url), 'utf8');
const physicsSource = fs.readFileSync(new URL('../_site/physics.js', import.meta.url), 'utf8');
const indexSource = fs.readFileSync(new URL('../_site/index.html', import.meta.url), 'utf8');
assert.match(gameSource, /targetMarker/);
assert.match(gameSource, /huntPriority/);
assert.match(gameSource, /HUNT START — WRECK TARGETS/);
assert.match(gameSource, /NEW TARGET/);
assert.match(gameSource, /HUNT SCORE/);
assert.match(gameSource, /Math\.max\(0,9-\(world\.time-h\.lastWreckAt\)\)/);
assert.doesNotMatch(gameSource, /c\.id===huntPriority\|\|c\.hp\/c\.maxHP<=\.45/);
assert.match(physicsSource, /huntDamage/);
assert.match(physicsSource, /w\.mode==='wreck-hunt'\?\.62:\.82/);
assert.match(physicsSource, /c\.id%3===0\?1\.04:\.58/);
assert.match(physicsSource, /lastWreckAt<=9/);
assert.match(physicsSource, /lastWreckAt>9/);
assert.match(physicsSource, /other\.hp=Math\.min\(other\.maxHP,other\.hp\+other\.maxHP\*\.10\)/);
assert.match(physicsSource, /1\.55\+w\.rand\(\)\*\.55/);
assert.match(physicsSource, /r=22\+w\.rand\(\)\*7/);
assert.match(indexSource, /id="score-label"/);

// A deliberately lined-up finisher should award a hunt wreck, start CHAIN,
// and return a small amount of hull so a long score-attack run can continue.
const combat = makeWorld(0, 33, 'wreck-hunt');
const hunter = combat.cars[0];
const victim = combat.cars[1];
hunter.x = 0; hunter.z = 0; hunter.heading = 0; hunter.vx = 0; hunter.vz = 24;
hunter.hp = hunter.maxHP * .42;
const hpBeforeWreck = hunter.hp;
victim.x = 0; victim.z = 3.4; victim.heading = Math.PI; victim.vx = 0; victim.vz = -4; victim.hp = 3;
for (const c of combat.cars.slice(2)) { c.x = 30 + c.id; c.z = 30; }
step(combat, {}, 1 / 60, false);
assert.equal(victim.dead, true, 'low-health target should be finishable in one committed ram');
assert.equal(combat.hunt.wrecks, 1);
assert.equal(combat.hunt.combo, 1);
assert.ok(hunter.score >= 500);
assert.ok(hunter.hp > hpBeforeWreck, 'a player-owned wreck should repair some hunter hull');
assert.ok(victim.respawnAt > combat.time && victim.respawnAt < combat.time + 2.2);

// CHAIN remains alive for nine seconds, then expires.
combat.hunt.lastWreckAt = combat.time;
combat.hunt.combo = 2;
for (let i = 0; i < 8 * 60; i++) step(combat, {}, 1 / 60, false);
assert.equal(combat.hunt.combo, 2, 'chain should survive through eight seconds');
for (let i = 0; i < 2 * 60; i++) step(combat, {}, 1 / 60, false);
assert.equal(combat.hunt.combo, 0, 'chain should expire after nine seconds without another wreck');

// Destroyed targets recycle close to the fight with inward momentum.
const target = w.cars[1];
target.dead = true;
target.wreckAt = 0;
target.respawnAt = 0;
target.x = 39;
target.z = 0;
step(w, {}, 1 / 60, true);
assert.equal(target.dead, false);
assert.equal(target.hp, target.maxHP);
assert.equal(target.respawnAt, Infinity);
assert.ok(w.events.some(e => e.type === 'respawn' && e.car === target.id));
assert.equal(w.hunt.respawns, 1);
assert.ok(Math.hypot(target.x,target.z) >= 21 && Math.hypot(target.x,target.z) <= 30);
assert.ok(Math.hypot(target.vx,target.vz) > 3.5, 'replacement target should launch inward instead of spawning stationary');

// A short autoplay soak verifies finite state and dense, ongoing contact.
for (let i = 0; i < 1200 && !w.done; i++) {
  step(w, {}, 1 / 60, true);
  for (const c of w.cars) {
    assert.ok(Number.isFinite(c.x + c.z + c.heading + c.hp));
    assert.ok(c.hp >= 0 && c.hp <= c.maxHP);
  }
}
assert.ok(w.time > 15);
assert.equal(w.done, false);
assert.ok(w.cars.some(c => c.contacts > 0), 'hunt should generate vehicle contact during a short soak');
console.log(`Wreck Hunt runtime OK: ${w.time.toFixed(1)}s, respawns=${w.hunt.respawns}, wrecks=${w.hunt.wrecks}, playerScore=${w.cars[0].score}`);
