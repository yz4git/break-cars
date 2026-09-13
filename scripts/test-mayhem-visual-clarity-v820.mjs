import fs from 'node:fs';

const game = fs.readFileSync('_site/game.js', 'utf8');
const css = fs.readFileSync('_site/mayhem-tour.css', 'utf8');
const style = fs.readFileSync('_site/style.css', 'utf8');
const marker = '/* MAYHEM TOUR v8.20';
const start = game.indexOf(marker);
const v820 = start >= 0 ? game.slice(start) : '';

function expect(label, value) {
  if (!value) throw new Error(`MAYHEM v8.20 regression: ${label}`);
  console.log(`ok - ${label}`);
}

expect('v8.20 section exists', start >= 0);
expect('visual-priority telemetry is exposed', v820.includes('window.__breakCarsMayhemV820'));
expect('Director stinger owns transient priority', v820.includes('mayhem-v820-stinger-active') && v820.includes('mayhemDirectorStingerV820Base'));
expect('battle-flow cue owns transient priority', v820.includes('mayhem-v820-flow-active') && v820.includes('mayhemRivalBattleCueV820Base'));
expect('stinger suppresses lower-priority overlays', css.includes('mayhem-v820-stinger-active #mayhem-director') && css.includes('mayhem-v820-stinger-active #mayhem-rival-flow') && css.includes('mayhem-v820-stinger-active #mayhem-rival-marker'));
expect('flow cue suppresses Director and world marker', css.includes('mayhem-v820-flow-active:not(.mayhem-v820-stinger-active) #mayhem-director') && css.includes('mayhem-v820-flow-active:not(.mayhem-v820-stinger-active) #mayhem-rival-marker'));
expect('short landscape stinger is compact', css.includes('#mayhem-director-stinger small,#mayhem-director-stinger span{display:none}') && css.includes('#mayhem-director-stinger b{margin:0;font-size:12px'));
expect('short landscape speed HUD is reduced', style.includes('#speed b{font-size:34px') && style.includes('#condition{bottom:max(22px'));
expect('touch controls are not resized by v8.20', !style.slice(style.lastIndexOf('/* MAYHEM v8.20')).includes('#steer{') && !style.slice(style.lastIndexOf('/* MAYHEM v8.20')).includes('.pedals button{'));
expect('v8.20 changes no gameplay physics or damage', !v820.includes('battleTarget=') && !v820.includes('.vx+=') && !v820.includes('.vz+=') && !v820.includes('hp-=') && !v820.includes('raceDistance='));

console.log('MAYHEM v8.20 visual-clarity regression passed.');
