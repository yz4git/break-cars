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

// SwiftShader canvas screenshots can take several seconds. Freeze the page's
// *next* requestAnimationFrame callbacks without entering the game's pause mode:
// already-scheduled frames run once, queue their successor here, then stop. This
// leaves the actual WebGL frame visible while expensive screenshot encoding runs.
// Restoring the queued callbacks resumes the game from exactly that frame.
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
  // Give any RAF already scheduled before the override time to execute once and
  // place its successor in the queue.
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

await page.waitForTimeout(3900);
await page.keyboard.down('ArrowUp');

const samples = [];
let simulated = 0;
for (let i = 0; i < 30; i += 1) {
  await page.waitForTimeout(350);
  simulated += 0.35;
  await freezeRaf();
  const tag = String(i + 1).padStart(2, '0');
  const speed = await page.locator('#speed b').innerText().catch(() => '');
  const raceState = await page.locator('#race-state').innerText().catch(() => '');
  samples.push({ frame: i + 1, elapsed: Number(simulated.toFixed(2)), speed, raceState });
  await canvas.screenshot({ path: `${outputDir}/${tag}-canvas.png` });
  await resumeRaf();
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

const diagnostics = {
  url,
  renderer,
  viewport: await page.evaluate(() => ({ width: innerWidth, height: innerHeight, dpr: devicePixelRatio })),
  samples,
  consoleErrors,
  pageErrors,
};
await writeFile(`${outputDir}/diagnostics.json`, JSON.stringify(diagnostics, null, 2));
await browser.close();
if (pageErrors.length) throw new Error(`page errors: ${pageErrors.join(' | ')}`);
console.log(`BREAK CARS live WebGL audit OK: ${samples.length} gameplay frames`);
