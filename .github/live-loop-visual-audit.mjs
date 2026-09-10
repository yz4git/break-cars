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

// Let the countdown finish. Each audit sample then advances the actual game by
// only 350 ms. SwiftShader screenshots can themselves take several seconds, so
// pause the game around every capture; otherwise a nominal 10.5 s audit can
// accidentally simulate for minutes while an input key remains held.
await page.waitForTimeout(3900);
await page.keyboard.down('ArrowUp');

const samples = [];
let simulated = 0;
for (let i = 0; i < 30; i += 1) {
  await page.waitForTimeout(350);
  simulated += 0.35;
  await page.keyboard.press('Escape');
  await page.waitForTimeout(80);
  const tag = String(i + 1).padStart(2, '0');
  const speed = await page.locator('#speed b').innerText().catch(() => '');
  const raceState = await page.locator('#race-state').innerText().catch(() => '');
  samples.push({ frame: i + 1, elapsed: Number(simulated.toFixed(2)), speed, raceState });
  await canvas.screenshot({ path: `${outputDir}/${tag}-canvas.png` });
  if (i % 3 === 0) await page.screenshot({ path: `${outputDir}/${tag}-full.png`, fullPage: true });
  await page.keyboard.press('Escape');
  await page.waitForTimeout(80);
}
await page.keyboard.up('ArrowUp').catch(() => {});

// Capture alternate camera views while stationary so the expensive screenshots
// cannot move the car to an unrelated piece of the figure-eight.
await page.keyboard.press('Escape');
await page.keyboard.press('KeyC');
await page.waitForTimeout(120);
await canvas.screenshot({ path: `${outputDir}/40-camera-wide.png` });
await page.keyboard.press('KeyC');
await page.waitForTimeout(120);
await canvas.screenshot({ path: `${outputDir}/41-camera-overhead.png` });
await page.keyboard.press('Escape');

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
