import fs from 'node:fs';

const game = fs.readFileSync('_site/game.js', 'utf8');
const css = fs.readFileSync('_site/mayhem-tour.css', 'utf8');

function expect(label, value) {
  if (!value) throw new Error(`MAYHEM roadmap regression: ${label}`);
  console.log(`ok - ${label}`);
}

const courseIds = [
  'classic', 'crater-crown', 'maelstrom-pit',
  'hunt-classic', 'cross-fire', 'tidal-foundry',
  'rampage-3d', 'sky-forge', 'double-orbit',
];

expect('complete nine-course event table', courseIds.every(id => game.includes(`course:'${id}'`)));
expect('nine-course menu label', game.includes('9 COURSE RUN · RIVAL · LIVE DIRECTOR'));
expect('dynamic Tour length telemetry', game.includes('tourLength:MAYHEM_EVENTS.length'));
expect('persistent RIVAL state', game.includes('rivalHull:1') && game.includes('function mayhemRivalId()'));
expect('RIVAL hull carry-over', game.includes('mayhemState.rivalHull=tourRival?'));
expect('LIVE MAYHEM DIRECTOR', game.includes('function mayhemDirectorTick(dt)'));
for (const state of ['BUILD','PRESSURE','RIVAL RUSH','RELIEF','FINALE']) {
  expect(`Director state ${state}`, game.includes(`'${state}'`));
}
expect('Director telemetry', game.includes('window.__breakCarsMayhemDirector='));
expect('highlight recorder', game.includes('function mayhemReplayCapture(dt)'));
expect('highlight playback', game.includes('function mayhemReplayApply(dt)'));
expect('highlight replay button', game.includes('HIGHLIGHT REPLAY'));
expect('highlight telemetry', game.includes('window.__breakCarsHighlightReplay='));
expect('highlight overlay CSS', css.includes('#mayhem-replay-overlay'));
expect('Director HUD CSS', css.includes('#mayhem-director'));

// v8 product-level presentation and dramaturgy.
expect('nine-event Director pressure curve', game.includes('MAYHEM_PRESSURE_CURVE=[.28,.34,.41,.48,.55,.62,.70,.78,.87]'));
expect('four-act Tour structure', ['ACT I · IGNITION','ACT II · VENDETTA','ACT III · REDLINE','FINAL ACT · DOUBLE ORBIT'].every(x=>game.includes(x)));
expect('Director transition stingers', game.includes('function mayhemDirectorStinger(') && css.includes('#mayhem-director-stinger'));
expect('screen-space RIVAL marker', game.includes('function mayhemRivalMarkerUpdate()') && css.includes('#mayhem-rival-marker'));
expect('RIVAL intermission status', game.includes('function mayhemIntermissionPolish(') && css.includes('.tour-rival-status'));
expect('cinematic replay camera', game.includes('function mayhemReplayCinematicCamera('));
expect('cinematic replay shot grammar', ['CHASE','RIVAL TWO-SHOT','IMPACT CLOSE'].every(x=>game.includes(x)));
expect('HUD-free replay mode', game.includes("document.body.classList.add('mayhem-replay-active')") && css.includes('body.mayhem-replay-active #hud'));
expect('cinematic letterbox', game.includes("lb.id='mayhem-letterbox'") && css.includes('#mayhem-letterbox'));
expect('v8 Director telemetry', game.includes('eventPressure:mayhemTourPressure()') && game.includes('act:mayhemActMeta().short'));

console.log('MAYHEM TOUR roadmap regression test passed.');
