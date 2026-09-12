import fs from 'node:fs';

const game = fs.readFileSync('_site/game.js', 'utf8');
const css = fs.readFileSync('_site/mayhem-tour.css', 'utf8');
const marker = '/* MAYHEM TOUR v8.19';
const start = game.indexOf(marker);
const v819 = start >= 0 ? game.slice(start) : '';

function expect(label, value) {
  if (!value) throw new Error(`MAYHEM v8.19 regression: ${label}`);
  console.log(`ok - ${label}`);
}

expect('v8.19 section exists', start >= 0);
expect('v8.19 chained into generated game', game.includes('window.__breakCarsMayhemV819=true'));
expect('records edge-triggered event clash count', v819.includes('result.battleClashes=clashes') && v819.includes('mayhemRivalBattleEventClashes'));
expect('records rivalry label in result history', v819.includes('result.rivalBattleLabel=mayhemRivalHistoryLabelV819(clashes)'));
expect('event labels cover four rivalry densities', ['WARZONE','GRUDGE MATCH','FIRST BLOOD','CLEAN RUN'].every(x => v819.includes(`'${x}'`)));
expect('PIT shows event clash history', v819.includes('EVENT CLASHES ${clashes}'));
expect('final result shows tour clash history', v819.includes('TOUR CLASHES ${total}'));
expect('tour clash total derives only from stored results', v819.includes("(mayhemState?.results||[]).reduce") && v819.includes('Number(r?.battleClashes)||0'));
expect('existing RIVAL intermission card is reused', v819.includes('const mayhemIntermissionPolishV819Base=mayhemIntermissionPolish') && v819.includes("card=host?.querySelector('.tour-rival-status')"));
expect('history is saved after base result generation', v819.includes('mayhemAfterEventV819Base();') && v819.includes('mayhemSave();'));
expect('history telemetry is exposed', v819.includes('window.__breakCarsMayhemRivalHistory='));
expect('compact history styling exists', css.includes('.tour-rival-status .rival-flow-stat') && css.includes('data-level="high"'));
expect('v8.19 changes no AI or physics', !v819.includes('battleTarget=') && !v819.includes('.vx+=') && !v819.includes('.vz+=') && !v819.includes('hp-=') && !v819.includes('raceDistance='));

console.log('MAYHEM v8.19 RIVAL clash-history regression passed.');
