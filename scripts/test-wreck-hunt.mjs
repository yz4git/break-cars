import assert from 'node:assert/strict';
import fs from 'node:fs';

const physics = await import(`../_site/physics.js?hunt-test=${Date.now()}`);
const {makeWorld,step} = physics;

const w = makeWorld(0, 91, 'wreck-hunt');
assert.equal(w.mode, 'wreck-hunt');
assert.equal(w.limit, 150);
assert.ok(w.hunt);
assert.equal(w.hunt.combo, 0);
assert.equal(w.hunt.focusId, 1, 'opening bounty should be the initial focus');
assert.ok(w.cars[0].maxHP > 138, 'hunter should have extra durability');
assert.ok(w.cars.slice(1).every(c => c.maxHP >= 46 && c.maxHP <= 72), 'hunt targets should be soft enough for fast finishers');
assert.equal(w.cars[0].z, 10, 'hunter should start inside the action instead of on the outer ring');
assert.equal(w.cars[1].x, 0, 'opening bounty should be lined up with the hunter');
assert.equal(w.cars[1].z, -8, 'opening bounty should be reachable in the first rush');
assert.ok(w.cars[1].hp / w.cars[1].maxHP <= .4, 'opening bounty should already be finishable');
assert.ok(w.cars.slice(2).every(c => Math.hypot(c.x,c.z) >= 19 && Math.hypot(c.x,c.z) <= 26), 'other targets should stay on the inner combat ring');

const gameSource = fs.readFileSync(new URL('../_site/game.js', import.meta.url), 'utf8');
const physicsSource = fs.readFileSync(new URL('../_site/physics.js', import.meta.url), 'utf8');
const indexSource = fs.readFileSync(new URL('../_site/index.html', import.meta.url), 'utf8');
const huntCss = fs.readFileSync(new URL('../_site/wreck-hunt.css', import.meta.url), 'utf8');
assert.match(gameSource, /targetMarker/);
assert.match(gameSource, /huntPriority/);
assert.match(gameSource, /hunt-nav/);
assert.match(gameSource, /huntNavArrow/);
assert.match(gameSource, /TARGET \$\{String\(c\.id\+1\)/);
assert.match(gameSource, /HUNT START — WRECK TARGETS/);
assert.match(gameSource, /HUNT SCORE/);
assert.match(gameSource, /Math\.max\(0,9-\(world\.time-h\.lastWreckAt\)\)/);
assert.match(gameSource, /RAMPAGE/);
assert.match(gameSource, /TRIPLE SMASH/);
assert.match(gameSource, /CHAIN WRECK/);
assert.match(gameSource, /hunt-rush/);
assert.doesNotMatch(gameSource, /c\.id===huntPriority\|\|c\.hp\/c\.maxHP<=\.45/);
assert.doesNotMatch(gameSource, /NEW TARGET — CAR/);
assert.match(physicsSource, /chooseHuntFocus/);
assert.match(physicsSource, /h\.focusId=chooseHuntFocus/);
assert.match(physicsSource, /locked\.target=0/);
assert.match(physicsSource, /rushUntil/);
assert.match(physicsSource, /huntRush/);
assert.match(physicsSource, /kick=5\.2\+Math\.min\(h\.combo,4\)\*\.8/);
assert.match(physicsSource, /1\.82\+Math\.min\(w\.hunt\?\.combo\|\|0,4\)\*\.14/);
assert.match(physicsSource, /1\.52\+Math\.min\(w\.hunt\?\.combo\|\|0,4\)\*\.06/);
assert.match(physicsSource, /w\.mode==='wreck-hunt'\?\.62:\.82/);
assert.match(physicsSource, /c\.id%3===0\?1\.04:\.48/);
assert.match(physicsSource, /lastWreckAt<=9/);
assert.match(physicsSource, /lastWreckAt>9/);
assert.match(physicsSource, /other\.hp=Math\.min\(other\.maxHP,other\.hp\+other\.maxHP\*\.10\)/);
assert.match(physicsSource, /r=18\+w\.rand\(\)\*6/);
assert.match(physicsSource, /huntEdge/);
assert.match(physicsSource, /bestCost/);
assert.match(indexSource, /id="score-label"/);
assert.match(huntCss, /#hunt-nav/);
assert.match(huntCss, /#hunt-nav\.visible/);
assert.match(huntCss, /body\.hunt-rush/);
assert.match(huntCss, /hunt-rush-lines/);

// With no steering input, the opening bounty should be contacted and finished
// quickly enough that the player experiences the Wreck Hunt loop immediately.
const opening = makeWorld(0, 77, 'wreck-hunt');
for (let i = 0; i < 5 * 60 && !opening.done && opening.hunt.wrecks === 0; i++) {
  step(opening, {gas:1,brake:0,hand:0,steer:0}, 1 / 60, false);
}
assert.ok(opening.cars[0].contacts > 0, 'straight opening rush should reach a target');
assert.ok(opening.cars[0].score > 0, 'opening contact should award player impact score');
assert.ok(opening.hunt.wrecks >= 1, 'opening bounty should be wrecked within five seconds');
assert.ok(opening.hunt.focusId > 0, 'a new bounty should be selected immediately after the opening wreck');
assert.equal(opening.cars[opening.hunt.focusId].dead, false, 'next bounty must be a live target');
assert.ok(opening.hunt.rushUntil > opening.time, 'a player wreck should immediately trigger Wreck Rush');

// A deliberately lined-up finisher should award a hunt wreck, start CHAIN,
// repair some hull, trigger rush and lock the next bounty onto the hunter.
const combat = makeWorld(0, 33, 'wreck-hunt');
const hunter = combat.cars[0];
const victim = combat.cars[1];
hunter.x = 0; hunter.z = 0; hunter.heading = 0; hunter.vx = 0; hunter.vz = 24;
hunter.hp = hunter.maxHP * .42;
const hpBeforeWreck = hunter.hp;
victim.x = 0; victim.z = 3.4; victim.heading = Math.PI; victim.vx = 0; victim.vz = -4; victim.hp = 3;
for (const c of combat.cars.slice(2)) { c.x = 18 + c.id; c.z = 12 + c.id * .35; c.dead = false; }
step(combat, {}, 1 / 60, false);
assert.equal(victim.dead, true, 'low-health target should be finishable in one committed ram');
assert.equal(combat.hunt.wrecks, 1);
assert.equal(combat.hunt.combo, 1);
assert.ok(hunter.score >= 500);
assert.ok(hunter.hp > hpBeforeWreck, 'a player-owned wreck should repair some hunter hull');
assert.ok(combat.hunt.rushUntil > combat.time + 1.5, 'wreck rush should last long enough to launch toward the next target');
assert.ok(victim.respawnAt > combat.time && victim.respawnAt < combat.time + 2.2);
assert.ok(combat.hunt.focusId >= 2, 'focus should move away from the wrecked bounty');
const nextBounty = combat.cars[combat.hunt.focusId];
assert.equal(nextBounty.dead, false);
assert.equal(nextBounty.target, 0, 'chain bounty should actively re-engage the hunter');
assert.ok(nextBounty.aiTimer >= .3, 'chain bounty lock should persist instead of instantly retargeting');

// CHAIN remains alive for nine seconds, then expires. Freeze all targets so the
// timer test cannot accidentally extend itself with another real wreck.
for (const c of combat.cars.slice(1)) { c.dead = true; c.respawnAt = Infinity; c.vx = 0; c.vz = 0; }
combat.hunt.focusId = -1;
combat.hunt.lastWreckAt = combat.time;
combat.hunt.combo = 2;
for (let i = 0; i < 8 * 60; i++) step(combat, {}, 1 / 60, false);
assert.equal(combat.hunt.combo, 2, 'chain should survive through eight seconds');
for (let i = 0; i < 2 * 60; i++) step(combat, {}, 1 / 60, false);
assert.equal(combat.hunt.combo, 0, 'chain should expire after nine seconds without another wreck');

// Destroyed targets recycle closer to the fight and enter with inward momentum.
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
assert.ok(Math.hypot(target.x,target.z) >= 17 && Math.hypot(target.x,target.z) <= 25);
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
console.log(`Wreck Hunt runtime OK: ${w.time.toFixed(1)}s, respawns=${w.hunt.respawns}, wrecks=${w.hunt.wrecks}, playerScore=${w.cars[0].score}, openingWrecks=${opening.hunt.wrecks}, focus=${w.hunt.focusId}`);
