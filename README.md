# BREAK CARS — Colosseum & Wrecking Racing

Original 3D demolition derby inspired by classic arena car combat. Twelve cars, one circular stadium, three vehicle classes, directional damage, deformed panels, smoke, sparks, skid marks and synthesized audio. No original game assets or trademarks are used in the game.

## Play

Open the deployed Site. Best on iPhone Safari in landscape. The left pad steers; GAS accelerates; BRAKE slows the car and then reverses; DRIFT loosens the rear tires. Keyboard: WASD/arrows, Space for drift, C for camera, Escape for pause. There are three camera views.

Last survivor wins. At the three-minute limit, surviving cars rank by impact score. If eliminated, your finish position is recorded immediately. Rear bodywork absorbs more damage; front impacts damage the engine and reduce acceleration/top speed. After 22 seconds without a car collision, durability decays until contact resumes. A warning appears after 17 seconds. Highest score is saved locally when storage is available.

## Development

Buildless, self-contained ES modules. Run `npm run build`, then serve `_site/` (for example `python3 -m http.server 8000 --directory _site`). There is no CDN dependency. `node --test tests/physics.test.mjs` runs collision and complete-match simulation checks. `node --check dist/game.js` validates the entry module. Rendering uses the vendored Three.js r160 distribution, licensed under MIT; see `dist/THREE-LICENSE.txt`.

The generated `physics3d.js` owns the existing 6DoF rigid-body simulation, four-wheel suspension, contact impulses and chassis attitude. `game.js` follows that physical pose. The preparation pipeline incorporates the latest loop boost, camera and automatic upright tuning before adding selectable courses.

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


## Selectable 3D courses (September 2026)

Each mode retains its existing course and adds one selectable course in the garage:

- **Colosseum / CRATER CROWN** — a 3.8 m central crown and undulating ring slopes encourage side loading, car-on-car climbing and elevated collisions.
- **Wreck Hunt / TIDAL FOUNDRY** — a washboard lane, diagonal earth bank and east-side rollers create airborne approaches and landing interceptions; chain/rush/respawn rules remain intact.
- **Wrecking Racing / SKY FORGE** — an asymmetric 416 m elevated figure eight, 7.5 m radius loop, three rolling crests, 10.6 m crossover bridge, banking and jump gap. Existing boost assistance, branch-aware projection and lap validation are reused.

Course selection is stored in the URL (`?course=crater-crown`, `tidal-foundry`, `sky-forge`) and reloads into a fresh race. The garage dropdown preserves access to original courses. Arena render meshes and physics normals derive from the same height function. Course definitions live in `dist/courses.js`; the integration is applied last by `scripts/apply-course-pack.py`.

Run `npm run build` to generate the complete `_site` runtime. Pages publishes `_site` and Sites publishes the identical `build` copy; raw `dist/game.js` is the input to the existing integration pipeline, not the final playable runtime. The existing Sites project ID is preserved. `npm run test:courses` verifies terrain mesh alignment, arena pack simulations and a natural Sky Forge lap plus pack flow. Existing physics/Hunt/boost/upright checks also pass. UI lifecycle checks use real Three scene objects with a stubbed WebGL renderer; actual GPU/iPhone visual testing was not performed in this update.
