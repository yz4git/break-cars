import fs from 'node:fs';

const game=fs.readFileSync('_site/game.js','utf8');
const css=fs.readFileSync('_site/mayhem-tour.css','utf8');
const expect=(label,ok)=>{if(!ok)throw new Error(`MAYHEM v8.14 regression: ${label}`);console.log(`ok - ${label}`);};

const courses=['classic','crater-crown','maelstrom-pit','hunt-classic','cross-fire','tidal-foundry','rampage-3d','sky-forge','double-orbit'];
expect('identity map covers all nine courses',courses.every(id=>game.includes(`'${id}':{family:`)||game.includes(`${id}:{family:`)));
expect('opening and finale have dedicated identities',game.includes("opening:{family:'tour'")&&game.includes("finale:{family:'finale'"));
expect('three event families are present',['colosseum','hunt','racing'].every(f=>game.includes(`family:'${f}'`)));
expect('runtime scene wrapper applies family and label',game.includes('const mayhemRecapV814SceneBase=mayhemRecapV813Scene')&&game.includes("el.dataset.family=meta.family")&&game.includes("backdrop.dataset.label=meta.label"));
expect('identity telemetry is exposed',game.includes('window.__breakCarsMayhemRecapIdentity=')&&game.includes("visual:'v814'"));
expect('v8.14 marker',game.includes('window.__breakCarsMayhemV814=true'));
expect('cinematic bars reduced for iPhone landscape',css.includes('#mayhem-tour-recap:before,#mayhem-tour-recap:after{height:11%}'));
expect('family-specific backdrop grammars',['colosseum','hunt','racing','tour','finale'].every(f=>css.includes(`data-family=\"${f}\"`)));
expect('large course watermark',css.includes('content:attr(data-label)')&&css.includes('clamp(38px,8vw,74px)'));
expect('course cut animation',css.includes('@keyframes mayhemRecapCutV814')&&css.includes('var(--recap-angle)')&&css.includes('var(--recap-scale)'));

console.log('MAYHEM v8.14 recap visual identity regression test passed.');
