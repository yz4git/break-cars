import fs from 'node:fs';

const game = fs.readFileSync('_site/game.js', 'utf8');
const css = fs.readFileSync('_site/style.css', 'utf8');
const marker = '/* BREAK CARS v8.22';
const start = game.indexOf(marker);
const v822 = start >= 0 ? game.slice(start) : '';

function expect(label, value) {
  if (!value) throw new Error(`BREAK CARS v8.22 regression: ${label}`);
  console.log(`ok - ${label}`);
}

expect('v8.22 section exists', start >= 0);
expect('toast wall clock telemetry is exposed', v822.includes('window.__breakCarsToastClockV822'));
expect('existing toast implementation is preserved', v822.includes('const toastV822Base=toast') && v822.includes('toastV822Base(text,actual)'));
expect('toast expiry uses performance.now real time', v822.includes('toastWallDeadlineV822=performance.now()') && v822.includes('now>=toastWallDeadlineV822'));
expect('wall clock tick uses animation frames rather than simulation dt', v822.includes('requestAnimationFrame(toastWallClockTickV822)'));
expect('WRECK HUNT opening is shortened to under one second', v822.includes("huntOpeningSeconds:.95") && v822.includes('Math.min(duration,.95)'));
expect('MAYHEM suppresses duplicate HUNT opening', v822.includes("typeof mayhemActive==='function'&&mayhemActive()"));
expect('HUNT opening has compact landscape styling', css.includes('#toast.hunt-opening-v822') && css.includes('max-height:430px'));
expect('v8.22 does not touch simulation or driving input', !v822.includes('step(world') && !v822.includes('.vx+=') && !v822.includes('.vz+=') && !v822.includes('hp-=') && !v822.includes('input.gas=') && !v822.includes('input.steer='));
expect('v8.22 does not alter impact cinema', !v822.includes('impactCinemaV821.') && !v822.includes('camera.fov='));

console.log('BREAK CARS v8.22 transient-HUD regression passed.');
