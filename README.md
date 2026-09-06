# BREAK CARS — Colosseum & Wrecking Racing

Original 3D demolition derby inspired by classic arena car combat. Twelve cars, one circular stadium, three vehicle classes, directional damage, deformed panels, smoke, sparks, skid marks and synthesized audio. No original game assets or trademarks are used in the game.

## Play

Open the deployed Site. Best on iPhone Safari in landscape. The left pad steers; GAS accelerates; BRAKE slows the car and then reverses; DRIFT loosens the rear tires. Keyboard: WASD/arrows, Space for drift, C for camera, Escape for pause. There are three camera views.

Last survivor wins. At the three-minute limit, surviving cars rank by impact score. If eliminated, your finish position is recorded immediately. Rear bodywork absorbs more damage; front impacts damage the engine and reduce acceleration/top speed. After 22 seconds without a car collision, durability decays until contact resumes. A warning appears after 17 seconds. Highest score is saved locally when storage is available.

## Development

Buildless, self-contained ES modules. Serve `dist/` with any static HTTP server (for example `python3 -m http.server 8000 --directory dist`). There is no CDN dependency. `node --test tests/physics.test.mjs` runs collision and complete-match simulation checks. `node --check dist/game.js` validates the entry module. Rendering uses the vendored Three.js r160 distribution, licensed under MIT; see `dist/THREE-LICENSE.txt`.

`dist/physics.js` is a deterministic 60 Hz planar oriented-box simulation, including linear collision impulses, angular response, wall impacts, directional damage and opponent steering. Rendering is full 3D with impact-scaled airborne, roll and pitch reactions and ground-clearance correction. The planar collision footprint remains on the road; this is an arcade reaction system rather than full suspension physics. `dist/game.js` owns visuals, audio, UI and captured-pointer input. Pointer cancellation, focus loss and page hiding release all controls. Pausing is manual to avoid touch-related focus changes opening the pause menu.

## Hosting

The existing `.openai/hosting.json` identifies this game's Site; preserve its project ID. The exact same `dist/` can be deployed to GitHub Pages with the included workflow. A repository administrator must choose GitHub Actions as the Pages source if it has not yet been enabled.

## Verification and limits

Automated checks cover drive/brake/reverse, collision damage/separation and seeded complete matches. Actual iPhone Safari performance and visual playtesting still require device verification. No service worker is installed, so there is no stale offline cache or automatic reload during a match.


## Wrecking Racing (v1.1)

Select **WRECKING RACING** at the title screen. Iron Loop is a 12-car, four-lap oval with solid inner and outer barriers. All three classes, player upgrades, reversed steering preference, touch layout, cameras and destruction effects carry over.

- Final total = impact score + 400 points per completed lap + finishing bonus.
- Finishing bonuses for places 1–12: 3500, 2900, 2400, 2000, 1700, 1400, 1150, 900, 700, 500, 350, 200.
- A qualifying side impact that spins an opponent adds 200; a wreck adds 500. Ordinary collision points still scale with damage.
- The race ends when all cars finish/are destroyed, 22 seconds after the first finisher, or after 150 seconds. Cars that do not finish receive impact/lap points, but no finishing bonus.
- The HUD shows road position and lap; results rank the combined total. Completing the race first does not guarantee the overall win.
- Finished or destroyed players spectate the remaining runners. Finished cars leave the track. The race mode has no no-contact durability penalty.
- Ordered quarter-lap gates and signed progress prevent reverse/line-oscillation scoring and infield shortcuts. Recovery restores heading at the current course position, costs up to 200 points and has a five-second cooldown.
- Race records use a separate localStorage key, preserving Colosseum best scores.

`dist/racing.js` owns course geometry, gates, race AI and scoring. `dist/track-view.js` renders the same geometry. Nine automated tests cover both modes, including complete CPU races, reverse abuse and scoring. Runtime flow checks were performed with a stubbed renderer; actual GPU/mobile visual QA was not performed in this update.

The former Pages-only reaction patches have been incorporated into `dist/game.js`. Historical patch scripts are retained but no longer run in the workflow. Both Sites and Pages use the same authored game. `scripts/prepare-pages.py` copies it and versions **all** local JavaScript module imports and CSS references, retaining game-scoped cache cleanup with no forced reload.
