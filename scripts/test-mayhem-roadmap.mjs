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

// v8.2 actual-screen review fixes.
expect('v8.2 peak-centered replay', game.includes('mayhemReplayV82FrozenPeak') && game.includes('peakProgress:'));
expect('v8.2 pre and post roll', game.includes('mayhemReplayV82PostFrames=18') && game.includes('peak-14') && game.includes('peak+17'));
expect('v8.2 adaptive framing', game.includes('separation=Math.max(.1,mayhemReplaySide.length())') && game.includes('mayhemReplayV82LastShot!==nextShot'));
expect('v8.2 immediate final pressure', game.includes("if(eventIndex===MAYHEM_EVENTS.length-1){next='FINALE';intensity=.97;}"));
expect('v8.2 short-menu cleanup', css.includes('body.mayhem-tour:not(.playing) .course-hint{display:none!important}'));
expect('v8.2 telemetry marker', game.includes('window.__breakCarsMayhemV82=true'));

// v8.3-v8.5 editorial and rivalry continuity.
expect('v8.3 complete replay window', game.includes('const minFrames=24') && game.includes('v83:true'));
expect('v8.4 adaptive IMPACT CLOSE framing', game.includes('6.1+separation*.58') && game.includes('46+separation*.38'));
expect('v8.5 rivalry score state', game.includes('rivalryPlayer:0') && game.includes('rivalryRival:0'));
expect('v8.5 rivalry outcome', game.includes('function mayhemRivalryOutcome(') && game.includes('rivalResult:rivalryWinner'));
expect('v8.5 series telemetry', game.includes('series:mayhemRivalryScore()'));
expect('v8.5 final rivalry verdict', game.includes("'RIVAL DEFEATED':'RIVAL WINS'"));
expect('v8.5 series card styling', css.includes('.tour-rival-status[data-series="player"]'));

// v8.6 DOUBLE ORBIT FINAL DUEL.
expect('v8.6 final duel activation', game.includes('function mayhemFinalDuelActive()') && game.includes('MAYHEM_EVENTS.length-1'));
expect('v8.6 three duel phases', ['PHASE I · LOCK ON','PHASE II · RAM PRESSURE','PHASE III · LAST STAND'].every(x=>game.includes(x)));
expect('v8.6 bounded rival contact pressure', game.includes('dist<16&&Math.abs(side)<7') && game.includes('dist>10&&dist<42'));
expect('v8.6 final duel telemetry', game.includes('window.__breakCarsMayhemFinalDuel=') && game.includes('finalDuel:window.__breakCarsMayhemFinalDuel||null'));
expect('v8.6 final event CTA', game.includes('SETTLE THE RIVALRY'));
expect('v8.6 final result verdict', game.includes('FINAL DUEL ${last===\'PLAYER\'?\'WON\':\'LOST\'}'));
expect('v8.6 final duel styling', css.includes('#mayhem-director[data-final-duel="1"]') && css.includes('.tour-rival-status[data-final-duel="1"]'));

// v8.7 FINAL SHOWDOWN CINEMATICS.
expect('v8.7 confrontation intro camera', game.includes('function mayhemShowdownIntroTick(dt)') && game.includes("mode==='countdown'"));
expect('v8.7 showdown intro copy', game.includes('FINAL SHOWDOWN') && css.includes('#mayhem-showdown-intro'));
expect('v8.7 last orbit escalation', game.includes('LAST ORBIT') && game.includes('progress>=.86') && css.includes('mayhem-showdown-last-stand'));
expect('v8.7 finish-focused frozen replay', game.includes('function mayhemShowdownFreezeFinish()') && game.includes('src.length-34') && game.includes('finishCut:true'));
expect('v8.7 final replay slow motion', game.includes('function mayhemShowdownReplayRate()') && game.includes("p>=.72?.42:p>=.5?.68:1"));
expect('v8.7 automatic ending replay', game.includes('function mayhemShowdownScheduleEndingReplay()') && game.includes("mayhemParams.get('tourAudit')==='1'"));
expect('v8.7 win loss ending cards', ['MAYHEM TOUR CHAMPION','RIVAL OWNS THE NIGHT'].every(x=>game.includes(x)) && css.includes('#mayhem-showdown-ending'));
expect('v8.7 final replay capability', game.includes('SHOWDOWN REPLAY') && game.includes('SLOW MOTION'));
expect('v8.7 showdown telemetry', game.includes('window.__breakCarsMayhemShowdown='));
expect('v8.7.1 live replay caption preserves slow motion', game.includes('FINISH CUT · ${mayhemRivalName()} · SLOW MOTION · ${mayhemReplayShot}'));

// v8.8 FINAL SHOWDOWN replay safety.
expect('v8.8 showdown replay camera', game.includes('function mayhemShowdownReplayCameraV88('));
expect('v8.8 three showdown replay shots', ['SHOWDOWN CHASE','SHOWDOWN TWO-SHOT','FINISH IMPACT'].every(x=>game.includes(x)));
expect('v8.8 face-off HUD cleanup', css.includes('body.mayhem-showdown-intro #hud'));
expect('v8.8 telemetry marker', game.includes('window.__breakCarsMayhemV88=true'));

// v8.9 complete nine-event TOUR RECAP.
expect('v8.9 recap final result panel', game.includes('function mayhemRecapAttach(') && css.includes('.tour-recap-panel'));
expect('v8.9 real nine-event result source', game.includes('function mayhemRecapResults()') && game.includes('MAYHEM_EVENTS.map((event,index)'));
expect('v8.9 recap statistics', game.includes('function mayhemRecapStats()') && game.includes('best,toughest'));
expect('v8.9 highlight film sequence', ['function mayhemRecapOpening()','function mayhemRecapEvent(index)','function mayhemRecapFinale()'].every(x=>game.includes(x)));
expect('v8.9 recap telemetry', game.includes('window.__breakCarsMayhemRecap=') && game.includes("mayhemRecapTelemetry('FINAL'"));
expect('v8.9 recap CTA', game.includes('PLAY TOUR RECAP') && game.includes('9 EVENT HIGHLIGHT FILM'));
expect('v8.9 recap overlay styling', css.includes('#mayhem-tour-recap') && css.includes('body.mayhem-recap-active #hud'));
expect('v8.9 telemetry marker', game.includes('window.__breakCarsMayhemV89=true'));

// v8.10 FINAL presentation cleanup.
expect('v8.10 clean-high showdown chase', game.includes("camera:'CLEAN-HIGH'") && game.includes('17.5+separation*.18') && game.includes('mayhemReplayMid).addScaledVector(mayhemReplayForward,-back).addScaledVector(mayhemReplaySide,.6)'));
expect('v8.10 isolated ending verdict', game.includes("document.body.classList.add('mayhem-showdown-ending-active')") && game.includes('},3600);window.__breakCarsMayhemShowdown=') && css.includes('body.mayhem-showdown-ending-active #modal'));
expect('v8.10 compact final replay CTA', game.includes('<b>SHOWDOWN REPLAY</b><small>FINAL CUT · SLOW MOTION</small>') && css.includes('.tour-final .tour-replay-button b'));
expect('v8.10 telemetry marker', game.includes('window.__breakCarsMayhemV810=true'));

// v8.11 Tour-owned result presentation.
expect('v8.11 suppresses duplicated base result', ['#result-title','#result-detail','#result-stats','#race-results'].every(x=>css.includes(`body.mayhem-tour-result ${x}`)));
expect('v8.11 keeps Tour intermission flush', css.includes('body.mayhem-tour-result #tour-intermission{margin-top:0!important}'));
expect('v8.11 telemetry marker', game.includes('window.__breakCarsMayhemV811=true'));

// v8.12 ending owns the whole frame.
expect('v8.12 ending HUD cleanup', css.includes('body.mayhem-showdown-ending-active #hud') && css.includes('visibility:hidden!important'));
expect('v8.12 telemetry marker', game.includes('window.__breakCarsMayhemV812=true'));

// v8.13 readable, course-coded recap film.
expect('v8.13 recap editorial cadence', game.includes('MAYHEM_RECAP_V813_OPENING_MS=2400') && game.includes('MAYHEM_RECAP_V813_EVENT_MS=980') && game.includes('MAYHEM_RECAP_V813_FINAL_MS=2600'));
expect('v8.13 course-coded recap backdrop', game.includes('function mayhemRecapV813Scene(') && css.includes('.mayhem-recap-backdrop') && courseIds.every(id=>css.includes(`data-course="${id}"`)));
expect('v8.13 recap telemetry', game.includes("scene:'opening'") && game.includes('course:row.event.course') && game.includes("scene:'finale'"));
expect('v8.13 telemetry marker', game.includes('window.__breakCarsMayhemV813=true'));

console.log('MAYHEM TOUR roadmap regression test passed.');
