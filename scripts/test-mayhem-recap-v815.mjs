import fs from 'node:fs';

const game=fs.readFileSync('_site/game.js','utf8');
const css=fs.readFileSync('_site/mayhem-tour.css','utf8');
const expect=(label,ok)=>{if(!ok)throw new Error(`MAYHEM v8.15 regression: ${label}`);console.log(`ok - ${label}`);};

expect('finale summary helper exists',game.includes('function mayhemRecapV815Summary(stats)'));
expect('same event collapses to peak event',game.includes("kind:'peak'")&&game.includes('PEAK EVENT · ${best.event.name}'));
expect('peak event keeps score and hull context',game.includes('${score.toLocaleString()} PTS · ${hull}% HULL'));
expect('different events retain split summary',game.includes("kind:'split'")&&game.includes('BEST · ${bestText} · TOUGHEST WIN · ${toughText}'));
expect('finale telemetry reports summary kind',game.includes('summary:summary.kind,best:summary.best,toughest:summary.toughest'));
expect('peak summary has dedicated styling',css.includes('.mayhem-recap-stage[data-summary="peak"] em'));
expect('v8.15 marker',game.includes('window.__breakCarsMayhemV815=true'));

console.log('MAYHEM v8.15 recap finale regression test passed.');
