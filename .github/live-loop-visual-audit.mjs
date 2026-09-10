import { mkdir, writeFile } from 'node:fs/promises';
import { chromium } from 'playwright';

const baseUrl = process.env.BREAK_CARS_AUDIT_URL || 'https://yz4git.github.io/break-cars/';
const outputDir = process.env.BREAK_CARS_AUDIT_DIR || 'artifacts/live-loop-visual-audit';
await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  args: [
    '--use-angle=swiftshader',
    '--enable-webgl',
    '--enable-unsafe-swiftshader',
    '--ignore-gpu-blocklist',
    '--disable-dev-shm-usage',
  ],
});
const context = await browser.newContext({
  viewport: { width: 852, height: 393 },
  deviceScaleFactor: 2,
  isMobile: true,
  hasTouch: true,
});
const page = await context.newPage();
const consoleErrors = [];
const pageErrors = [];
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', e => pageErrors.push(String(e)));

const url = `${baseUrl}${baseUrl.includes('?') ? '&' : '?'}course=rampage-3d&visualAudit=${Date.now()}`;
await page.goto(url, { waitUntil: 'networkidle', timeout: 60_000 });
await page.screenshot({ path: `${outputDir}/00-title.png`, fullPage: true });

const renderer = await page.evaluate(() => {
  const canvas = document.querySelector('#scene');
  const gl = canvas?.getContext('webgl2') || canvas?.getContext('webgl');
  return gl ? 'webgl' : 'none';
});
if (renderer !== 'webgl') throw new Error(`WebGL renderer unavailable: ${renderer}`);

const racing = page.locator('[data-mode="racing"]');
await racing.waitFor({ state: 'visible', timeout: 15_000 });
await racing.click({ force: true });
await page.waitForTimeout(250);
await page.locator('#start').click({ force: true });

const canvas = page.locator('#scene');
await canvas.waitFor({ state: 'visible', timeout: 20_000 });
await page.screenshot({ path: `${outputDir}/01-race-countdown.png`, fullPage: true });

// SwiftShader screenshot encoding is expensive. Keep all 30 physics/HUD samples,
// but freeze and encode only representative visual checkpoints through the Omega.
async function freezeRaf() {
  await page.evaluate(() => {
    if (window.__breakCarsAuditRafFrozen) return;
    window.__breakCarsAuditOriginalRaf = window.requestAnimationFrame;
    window.__breakCarsAuditQueuedRafs = [];
    let serial = 1;
    window.requestAnimationFrame = cb => {
      window.__breakCarsAuditQueuedRafs.push(cb);
      return -serial++;
    };
    window.__breakCarsAuditRafFrozen = true;
  });
  await page.waitForTimeout(100);
}

async function resumeRaf() {
  await page.evaluate(() => {
    if (!window.__breakCarsAuditRafFrozen) return;
    const original = window.__breakCarsAuditOriginalRaf;
    const queued = window.__breakCarsAuditQueuedRafs || [];
    window.requestAnimationFrame = original;
    window.__breakCarsAuditRafFrozen = false;
    window.__breakCarsAuditQueuedRafs = [];
    for (const cb of queued) original.call(window, cb);
  });
}

async function readSample() {
  return page.evaluate(() => ({
    speed: document.querySelector('#speed b')?.textContent ?? '',
    raceState: document.querySelector('#race-state')?.textContent ?? '',
    telemetry: window.__breakCarsAuditState?.() ?? null,
  }));
}

await page.waitForTimeout(3900);
await page.keyboard.down('ArrowUp');

const samples = [];
const captureFrames = new Set([7, 10, 12, 14, 16, 18, 21, 25, 30]);
let simulated = 0;
for (let i = 0; i < 30; i += 1) {
  const frame = i + 1;
  await page.waitForTimeout(350);
  simulated += 0.35;
  const capture = captureFrames.has(frame);
  if (capture) await freezeRaf();
  const sample = await readSample();
  samples.push({ frame, elapsed: Number(simulated.toFixed(2)), ...sample });
  if (capture) {
    const tag = String(frame).padStart(2, '0');
    await canvas.screenshot({ path: `${outputDir}/${tag}-canvas.png` });
    await resumeRaf();
  }
}
await page.keyboard.up('ArrowUp').catch(() => {});

await freezeRaf();
await page.keyboard.press('KeyC');
await page.waitForTimeout(80);
await canvas.screenshot({ path: `${outputDir}/40-camera-wide.png` });
await page.keyboard.press('KeyC');
await page.waitForTimeout(80);
await canvas.screenshot({ path: `${outputDir}/41-camera-overhead.png` });
await resumeRaf();

const physicsSamples = samples.filter(s => s.telemetry);
const loopSamples = physicsSamples.filter(s => s.telemetry.roadKind === 'loop');
const inverted = loopSamples.some(s => s.telemetry.upY < -0.55);
let currentStall = 0;
let maxLoopStallSamples = 0;
for (const s of loopSamples) {
  if (s.telemetry.speedMps < 1.4) currentStall += 1;
  else currentStall = 0;
  maxLoopStallSamples = Math.max(maxLoopStallSamples, currentStall);
}
const raceProgress = physicsSamples.length > 1
  ? physicsSamples.at(-1).telemetry.raceDistance - physicsSamples[0].telemetry.raceDistance
  : 0;
const hudErrors = physicsSamples.flatMap(s => {
  const hud = Number.parseFloat(s.speed);
  return Number.isFinite(hud) ? [Math.abs(hud - s.telemetry.speedMps * 3.6)] : [];
});
const loopHudErrors = loopSamples.flatMap(s => {
  const hud = Number.parseFloat(s.speed);
  return Number.isFinite(hud) ? [Math.abs(hud - s.telemetry.speedMps * 3.6)] : [];
});
const traversal = {
  telemetrySamples: physicsSamples.length,
  loopSamples: loopSamples.length,
  visualCaptureFrames: [...captureFrames],
  inverted,
  maxLoopStallSamples,
  maxLoopStallSeconds: Number((maxLoopStallSamples * 0.35).toFixed(2)),
  raceProgress: Number(raceProgress.toFixed(2)),
  minLoopSpeedMps: loopSamples.length ? Number(Math.min(...loopSamples.map(s => s.telemetry.speedMps)).toFixed(2)) : null,
  maxLoopSpeedMps: loopSamples.length ? Number(Math.max(...loopSamples.map(s => s.telemetry.speedMps)).toFixed(2)) : null,
  maxHudSpeedErrorKmh: hudErrors.length ? Number(Math.max(...hudErrors).toFixed(2)) : null,
  maxLoopHudSpeedErrorKmh: loopHudErrors.length ? Number(Math.max(...loopHudErrors).toFixed(2)) : null,
};

const diagnostics = {
  url,
  renderer,
  viewport: await page.evaluate(() => ({ width: innerWidth, height: innerHeight, dpr: devicePixelRatio })),
  traversal,
  samples,
  consoleErrors,
  pageErrors,
};
await writeFile(`${outputDir}/diagnostics.json`, JSON.stringify(diagnostics, null, 2));
await browser.close();

const failures = [];
if (physicsSamples.length !== samples.length) failures.push(`telemetry missing on ${samples.length - physicsSamples.length}/${samples.length} frames`);
if (loopSamples.length < 3) failures.push(`Omega was not captured reliably: ${loopSamples.length} loop samples`);
if (!inverted) failures.push('player never reached an inverted Omega attitude');
if (maxLoopStallSamples >= 5) failures.push(`player stalled in Omega for ${traversal.maxLoopStallSeconds}s`);
if (traversal.maxLoopHudSpeedErrorKmh !== null && traversal.maxLoopHudSpeedErrorKmh > 12) failures.push(`3D HUD speed diverged by ${traversal.maxLoopHudSpeedErrorKmh} km/h in Omega`);
if (consoleErrors.length) failures.push(`console errors: ${consoleErrors.join(' | ')}`);
if (pageErrors.length) failures.push(`page errors: ${pageErrors.join(' | ')}`);
if (failures.length) throw new Error(failures.join(' ; '));
console.log(`BREAK CARS live WebGL audit OK: ${samples.length} telemetry frames, ${captureFrames.size} visual checkpoints, Omega samples=${loopSamples.length}, inverted=${inverted}, progress=${traversal.raceProgress}m, max loop stall=${traversal.maxLoopStallSeconds}s, HUD error=${traversal.maxLoopHudSpeedErrorKmh}km/h`);
