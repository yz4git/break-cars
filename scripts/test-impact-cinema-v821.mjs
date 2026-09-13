import fs from 'node:fs';

const game = fs.readFileSync('_site/game.js', 'utf8');
const marker = '/* BREAK CARS v8.21';
const start = game.indexOf(marker);
const v821 = start >= 0 ? game.slice(start) : '';

function expect(label, value) {
  if (!value) throw new Error(`BREAK CARS v8.21 regression: ${label}`);
  console.log(`ok - ${label}`);
}

expect('v8.21 section exists', start >= 0);
expect('impact telemetry is exposed', v821.includes('window.__breakCarsImpactCinemaV821'));
expect('event wrapper preserves existing collision handling', v821.includes('const impactCinemaEventsV821Base=events') && v821.includes('impactCinemaEventsV821Base();'));
expect('visual wrapper preserves existing camera and HUD handling', v821.includes('const impactCinemaVisualsV821Base=visuals') && v821.includes('impactCinemaVisualsV821Base(dt);'));
expect('impact sequence has four readable phases', ['HOLD','FOCUS','RECOIL','RECOVER'].every(x => v821.includes(`'${x}'`)));
expect('repeated contacts are rate limited', v821.includes('lastWorldTime') && v821.includes("world.time-impactCinemaV821.lastWorldTime<.10"));
expect('MAYHEM replay suppresses live impact camera', v821.includes("mayhem-replay-active") && v821.includes("mayhemReplayPlaying"));
expect('random shake is capped rather than amplified', v821.includes('shake=Math.min(shake'));
expect('directional recoil and impact focus are present', v821.includes('impactCinemaRightV821') && v821.includes('impactCinemaFocusV821') && v821.includes('camera.lookAt(impactCinemaLookV821)'));
expect('visual hit-stop is camera-only', v821.includes('holdPos') && v821.includes('visualHitStop:true') && v821.includes('physicsChanged:false') && v821.includes('inputBlocked:false'));
expect('low-frequency impact body layer exists', v821.includes("osc.type='triangle'") && v821.includes('frequency.exponentialRampToValueAtTime'));
expect('v8.21 does not mutate simulation velocity, damage, race distance or inputs', !v821.includes('.vx+=') && !v821.includes('.vz+=') && !v821.includes('hp-=') && !v821.includes('raceDistance=') && !v821.includes('input.gas=') && !v821.includes('input.steer='));

console.log('BREAK CARS v8.21 impact-cinema regression passed.');
