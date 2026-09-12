import fs from 'node:fs';

const game = fs.readFileSync('_site/game.js', 'utf8');
const css = fs.readFileSync('_site/mayhem-tour.css', 'utf8');
const v818Marker = '/* MAYHEM TOUR v8.18';
const v818Start = game.indexOf(v818Marker);
const v818 = v818Start >= 0 ? game.slice(v818Start) : '';

function expect(label, value) {
  if (!value) throw new Error(`MAYHEM v8.18 regression: ${label}`);
  console.log(`ok - ${label}`);
}

expect('v8.18 section exists', v818Start >= 0);
expect('v8.18 chained into generated game', game.includes('window.__breakCarsMayhemV818=true'));
expect('wraps v8.17 Director layer', game.includes('const mayhemDirectorTickV818Base=mayhemDirectorTick') && game.includes('mayhemDirectorTickV818Base(dt);mayhemRivalBattleTickV818(dt)'));
expect('five-beat RIVAL flow', ['INBOUND','LOCKED','CLASH','BREAKAWAY','REMATCH'].every(x => game.includes(`'${x}'`)));
expect('CONTACT is edge-triggered instead of replaying old events', game.includes("engagement==='CONTACT'&&mayhemRivalBattlePrevEngagement!=='CONTACT'") && game.includes('now-mayhemRivalBattleLastClash>.72'));
expect('series clash count resets on a new Tour', game.includes("eventIndex===0&&mayhemRivalBattleEvent!==0") && game.includes('mayhemRivalBattleSeriesClashes=0'));
expect('racing creates a separation beat', game.includes("mayhemRivalBattlePhase==='BREAKAWAY'") && game.includes('r.battleTarget=-1') && game.includes('r.battleTimer=Math.max'));
expect('racing explicitly reacquires player for rematch', game.includes("mayhemRivalBattlePhase==='REMATCH'") && game.includes('gap>-8&&gap<28') && game.includes('r.battleTarget=0'));
expect('RELIEF remains authoritative', game.includes("mayhemDirectorState==='RELIEF'||mayhemRivalEngagementState==='RELIEF'"));
expect('FINAL DUEL remains authoritative', game.includes("if(mayhemFinalDuelActive()){mayhemRivalBattleSetV818('FINAL DUEL'"));
expect('flow telemetry is exposed', game.includes('window.__breakCarsMayhemRivalBattleFlow=payload'));
expect('stale v8.17 contact telemetry is synchronized', game.includes('mayhemRivalEngagementContacts=mayhemRivalBattleSeriesClashes'));
expect('compact transient cue is styled', css.includes('#mayhem-rival-flow') && css.includes('data-mayhem-rival-flow="breakaway"') && css.includes('data-mayhem-rival-flow="rematch"'));
expect('cue is hidden during result/replay/recap', css.includes('body.mayhem-tour-result #mayhem-rival-flow') && css.includes('body.mayhem-replay-active #mayhem-rival-flow') && css.includes('body.mayhem-recap-active #mayhem-rival-flow'));
expect('v8.18 adds no teleport or player slowdown', !v818.includes('r.x=p.x') && !v818.includes('r.z=p.z') && !v818.includes('p.vx*=') && !v818.includes('p.vz*='));

console.log('MAYHEM v8.18 RIVAL battle-flow regression passed.');
