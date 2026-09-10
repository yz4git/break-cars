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

// Read the WebGL canvas from inside the page rather than using Playwright's
// screenshot pipeline for every frame. SwiftShader screenshots can take several
// seconds; keeping capture in the page avoids turning a 10.5 s drive into a
// minutes-long uncontrolled run. The game itself is never paused here.
async function captureCanvas(path) {
  const dataUrl = await page.evaluate(() => {
    const source = document.querySelector('#scene');
    if (!source) throw new Error('scene canvas missing');
    const copy = document.createElement('canvas');
    copy.width = source.width;
    copy.height = source.height;
    const ctx = copy.getContext('2d');
    ctx.drawImage(source, 0, 0);
    return copy.toDataURL('image/png');
  });
  const comma = dataUrl.indexOf(',');
  await writeFile(path, Buffer.from(dataUrl.slice(comma + 1), 'base64'));
}

await page.waitForTimeout(3900);
await page.keyboard.down('ArrowUp');

const samples = [];
let simulated = 0;
for (let i = 0; i < 30; i += 1) {
  await page.waitForTimeout(350);
  simulated += 0.35;
  const tag = String(i + 1).padStart(2, '0');
  const speed = await page.locator('#speed b').innerText().catch(() => '');
  const raceState = await page.locator('#race-state').innerText().catch(() => '');
  samples.push({ frame: i + 1, elapsed: Number(simulated.toFixed(2)), speed, raceState });
  await captureCanvas(`${outputDir}/${tag}-canvas.png`);
}
await page.keyboard.up('ArrowUp').catch(() => {});

// Alternate camera views are captured after the controlled drive with no input.
await page.keyboard.press('KeyC');
await page.waitForTimeout(120);
await captureCanvas(`${outputDir}/40-camera-wide.png`);
await page.keyboard.press('KeyC');
await page.waitForTimeout(120);
await captureCanvas(`${outputDir}/41-camera-overhead.png`);

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
