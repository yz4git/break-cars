# BREAK CARS — Colosseum

Original 3D demolition derby inspired by classic arena car combat. Twelve cars, one circular stadium, three vehicle classes, directional damage, deformed panels, smoke, sparks, skid marks and synthesized audio. No original game assets or trademarks are used in the game.

## Play

Open the deployed Site. Best on iPhone Safari in landscape. The left pad steers; GAS accelerates; BRAKE slows the car and then reverses; DRIFT loosens the rear tires. Keyboard: WASD/arrows, Space for drift, C for camera, Escape for pause. There are three camera views.

Last survivor wins. At the three-minute limit, surviving cars rank by impact score. If eliminated, your finish position is recorded immediately. Rear bodywork absorbs more damage; front impacts damage the engine and reduce acceleration/top speed. After 22 seconds without a car collision, durability decays until contact resumes. A warning appears after 17 seconds. Highest score is saved locally when storage is available.

## Development

Buildless, self-contained ES modules. Serve `dist/` with any static HTTP server (for example `python3 -m http.server 8000 --directory dist`). There is no CDN dependency. `node --test tests/physics.test.mjs` runs collision and complete-match simulation checks. `node --check dist/game.js` validates the entry module. Rendering uses the vendored Three.js r160 distribution, licensed under MIT; see `dist/THREE-LICENSE.txt`.

`dist/physics.js` is a deterministic 60 Hz planar oriented-box simulation, including linear collision impulses, angular response, wall impacts, directional damage and opponent steering. Rendering is full 3D; cars stay on the arena surface rather than simulating suspension or rollovers. `dist/game.js` owns visuals, audio, UI and captured-pointer input. Pointer cancellation, focus loss and page hiding release all controls and pause the match.

## Hosting

The existing `.openai/hosting.json` identifies this game's Site; preserve its project ID. The exact same `dist/` can be deployed to GitHub Pages with the included workflow. A repository administrator must choose GitHub Actions as the Pages source if it has not yet been enabled.

## Verification and limits

Automated checks cover drive/brake/reverse, collision damage/separation and seeded complete matches. Actual iPhone Safari performance and visual playtesting still require device verification. No service worker is installed, so there is no stale offline cache or automatic reload during a match.
