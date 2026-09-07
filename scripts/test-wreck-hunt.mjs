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
assert.ok(w.cars.slice(1).every(c => c.maxHP >= 50 && c.maxHP <= 81), 'hunt targets should be substantially softer than survival cars');

// The deployed runtime must contain the score-attack polish, not only the menu.
const gameSource = fs.readFileSync(new URL('../_site/game.js', import.meta.url), 'utf8');
const physicsSource = fs.readFileSync(new URL('../_site/physics.js', import.meta.url), 'utf8');
assert.match(gameSource, /targetMarker/);
assert.match(gameSource, /TARGET/);
assert.match(gameSource, /dataset\.gameMode/);
assert.match(gameSource, /NEW TARGET/);
assert.match(physicsSource, /huntDamage/);
assert.match(physicsSource, /1\.9\+w\.rand\(\)\*\.7/);

// A deliberately lined-up finisher should award a hunt wreck and begin CHAIN.
const combat = makeWorld(0, 33, 'wreck-hunt');
const hunter = combat.cars[0];
const victim = combat.cars[1];
hunter.x = 0; hunter.z = 0; hunter.heading = 0; hunter.vx = 0; hunter.vz = 24;
victim.x = 0; victim.z = 3.4; victim.heading = Math.PI; victim.vx = 0; victim.vz = -4; victim.hp = 3;
for (const c of combat.cars.slice(2)) { c.x = 30 + c.id; c.z = 30; }
step(combat, {}, 1 / 60, false);
assert.equal(victim.dead, true, 'low-health target should be finishable in one committed ram');
assert.equal(combat.hunt.wrecks, 1);
assert.equal(combat.hunt.combo, 1);
assert.ok(hunter.score >= 500);
assert.ok(victim.respawnAt > combat.time && victim.respawnAt < combat.time + 2.7);

// Verify destroyed targets are actually recycled back into the hunt.
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

// A short autoplay soak should keep the state finite and should not end just
// because most targets are temporarily wrecked.
for (let i = 0; i < 900 && !w.done; i++) {
  step(w, {}, 1 / 60, true);
  for (const c of w.cars) {
    assert.ok(Number.isFinite(c.x + c.z + c.heading + c.hp));
    assert.ok(c.hp >= 0 && c.hp <= c.maxHP);
  }
}
assert.ok(w.time > 10);
assert.equal(w.done, false);
console.log(`Wreck Hunt runtime OK: ${w.time.toFixed(1)}s, respawns=${w.hunt.respawns}, wrecks=${w.hunt.wrecks}`);
