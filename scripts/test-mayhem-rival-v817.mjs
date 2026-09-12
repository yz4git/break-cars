import fs from 'node:fs';

const game = fs.readFileSync('_site/game.js', 'utf8');
const css = fs.readFileSync('_site/mayhem-tour.css', 'utf8');

function expect(label, value) {
  if (!value) throw new Error(`MAYHEM v8.17 regression: ${label}`);
  console.log(`ok - ${label}`);
}

expect('v8.17 chained into generated game', game.includes('window.__breakCarsMayhemV817=true'));
expect('wraps final Director rather than replacing roadmap layers', game.includes('const mayhemDirectorTickV817Base=mayhemDirectorTick') && game.includes('mayhemDirectorTickV817Base(dt);mayhemRivalEngagementTickV817(dt)'));
expect('event-nine FINAL DUEL remains exclusive', game.includes("if(mayhemFinalDuelActive()){mayhemRivalEngagementState='FINAL DUEL'"));
expect('low-hull RELIEF disables extra pressure', game.includes("mayhemDirectorState==='RELIEF'||playerHull<.36"));
expect('racing rival explicitly retargets the player', game.includes('r.battleTarget=0') && game.includes('r.raceAggro=Math.max'));
expect('racing catch-up is bounded and never teleports', game.includes('Math.min(1.35') && game.includes('gap>8&&gap<70') && !game.includes('r.raceDistance=p.raceDistance'));
expect('arena rejoin uses predicted intercept force', game.includes("lead=.22+pressure*.18") && game.includes('dist>12&&dist<52'));
expect('rival engagement telemetry', game.includes('window.__breakCarsMayhemRivalEngagement='));
expect('engagement marker styling', css.includes('data-mayhem-rival-engagement="lock"') && css.includes('data-mayhem-rival-engagement="relief"'));

console.log('MAYHEM v8.17 RIVAL engagement regression passed.');
