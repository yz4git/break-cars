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

console.log('MAYHEM TOUR roadmap regression test passed.');
