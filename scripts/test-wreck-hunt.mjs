import assert from 'node:assert/strict';

const physics = await import(`../_site/physics.js?hunt-test=${Date.now()}`);
const {makeWorld,step} = physics;

const w = makeWorld(0, 91, 'wreck-hunt');
assert.equal(w.mode, 'wreck-hunt');
assert.equal(w.limit, 150);
assert.ok(w.hunt);
assert.equal(w.hunt.combo, 0);
assert.ok(w.cars[0].maxHP > 138, 'hunter should have extra durability');
assert.ok(w.cars.slice(1).every(c => c.maxHP >= 58 && c.maxHP <= 102), 'targets should be easier to wreck than survival cars');

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
