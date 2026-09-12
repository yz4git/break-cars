import fs from 'node:fs';

const game=fs.readFileSync('_site/game.js','utf8');
const css=fs.readFileSync('_site/mayhem-tour.css','utf8');
const expect=(label,ok)=>{if(!ok)throw new Error(`MAYHEM v8.16 regression: ${label}`);console.log(`ok - ${label}`);};

expect('chapter cadence is compact',game.includes('MAYHEM_RECAP_V816_CHAPTER_MS=560'));
expect('three act boundaries exist',game.includes("3:{kicker:'ACT II',title:'VENDETTA'")&&game.includes("6:{kicker:'ACT III',title:'REDLINE'")&&game.includes("8:{kicker:'FINAL ACT',title:'DOUBLE OR NOTHING'"));
expect('chapter stage precedes matching event',game.includes('mayhemRecapV816ShowChapter(index,row)')&&game.includes('mayhemRecapTimer=setTimeout(()=>mayhemRecapEvent(index),MAYHEM_RECAP_V816_CHAPTER_MS)'));
expect('chapter telemetry',game.includes("mayhemRecapTelemetry('CHAPTER',index")&&game.includes("scene:'chapter'"));
expect('normal event telemetry preserved',game.includes("mayhemRecapTelemetry('EVENT',row.index"));
expect('chapter has dedicated cinematic styling',css.includes('.mayhem-recap-stage[data-kind="chapter"]')&&css.includes('letter-spacing:.34em'));
expect('v8.16 marker',game.includes('window.__breakCarsMayhemV816=true'));

console.log('MAYHEM v8.16 recap chapter regression test passed.');
