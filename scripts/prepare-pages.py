"""Publish the authored game with Wreck Hunt, full 3D physics, and versioned local dependencies."""
from pathlib import Path
import importlib.util
import os
import re
import shutil


def load_function(filename, module_name, function_name):
    module_path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


apply_wreck_hunt = load_function('apply-wreck-hunt.py', 'break_cars_wreck_hunt_patch', 'apply_wreck_hunt')
apply_wreck_hunt_improvements = load_function('improve-wreck-hunt-v2.py', 'break_cars_wreck_hunt_polish_v2', 'apply_wreck_hunt_improvements')
apply_wreck_hunt_final_tuning = load_function('tune-wreck-hunt-post-review-v3.py', 'break_cars_wreck_hunt_final_tuning_v3', 'apply_wreck_hunt_final_tuning')
apply_wreck_hunt_chain_tuning = load_function('tune-wreck-hunt-chain-v4.py', 'break_cars_wreck_hunt_chain_v4', 'apply_wreck_hunt_chain_tuning')
apply_wreck_hunt_rush = load_function('tune-wreck-hunt-rush-v5.py', 'break_cars_wreck_hunt_rush_v5', 'apply_wreck_hunt_rush')
apply_racing3d_projection_fix = load_function('fix-racing3d-projection.py', 'break_cars_racing3d_projection_fix', 'apply_racing3d_projection_fix')
apply_full_physics3d = load_function('apply-racing3d-full-physics.py', 'break_cars_racing3d_full_physics', 'apply_full_physics3d')
apply_racing3d_surface_hint = load_function('fix-racing3d-surface-hint.py', 'break_cars_racing3d_surface_hint', 'apply_racing3d_surface_hint')
apply_smooth_racing3d_boundary = load_function('smooth-racing3d-boundary.py', 'break_cars_smooth_racing3d_boundary', 'apply_smooth_racing3d_boundary')
apply_full_physics_loop_polish = load_function('polish-full-physics-loop-v2.py', 'break_cars_full_physics_loop_polish', 'apply_full_physics_loop_polish')
apply_racing3d_loop_camera = load_function('polish-racing3d-loop-camera-v3.py', 'break_cars_racing3d_loop_camera_v3', 'apply_racing3d_loop_camera')
apply_rampage_raceability = load_function('polish-rampage-raceability-v5.py', 'break_cars_rampage_raceability_v5', 'apply_rampage_raceability')
apply_rampage_loop_boost_v6 = load_function('boost-rampage-loop-v6.py', 'break_cars_rampage_loop_boost_v6', 'apply_rampage_loop_boost_v6')
apply_racing3d_ui = load_function('polish-racing3d-ui.py', 'break_cars_racing3d_ui', 'apply_racing3d_ui')
apply_player_auto_upright = load_function('add-player-auto-upright.py', 'break_cars_player_auto_upright', 'apply_player_auto_upright')
apply_auto_upright_racing_hint = load_function('fix-auto-upright-racing-hint.py', 'break_cars_auto_upright_racing_hint', 'apply_auto_upright_racing_hint')

source = Path('dist')
target = Path('_site')
if target.exists():
    shutil.rmtree(target)
shutil.copytree(source, target)

# Keep the large shared runtime single-source in dist; apply mode integration
# and focused tuning to the deploy copy, failing loudly if upstream drifts.
apply_wreck_hunt(target)
apply_wreck_hunt_improvements(target)
apply_wreck_hunt_final_tuning(target)
apply_wreck_hunt_chain_tuning(target)
apply_wreck_hunt_rush(target)
# Stabilize the self-crossing race projection before the 6DoF layer consumes it.
apply_racing3d_projection_fix(target)
# Full vehicle physics consumes the final Hunt/Rush rules and owns movement,
# suspension, contact impulses and chassis attitude. Then force wheel/chassis
# samples to remain on the same self-crossing branch as each car's trackS.
apply_full_physics3d(target)
apply_racing3d_surface_hint(target)
# Smooth course-edge and pile-up depenetration so hard landings cannot produce
# one-frame visual warps.
apply_smooth_racing3d_boundary(target)
apply_full_physics_loop_polish(target)
# The racing loop uses an exterior, world-up camera so the road surface cannot
# swallow the chase camera while the chassis is vertical or inverted.
apply_racing3d_loop_camera(target)
# Post-review course polish: spread loop traffic, soften only loop contacts,
# and keep the jump landing visible while the car is airborne.
apply_rampage_raceability(target)
# Make the visible BOOST LOOP a high-confidence stunt assist: physical forward
# force targets ~103 km/h on approach and ~112 km/h in the loop.
apply_rampage_loop_boost_v6(target)
apply_racing3d_ui(target)
apply_player_auto_upright(target)
apply_auto_upright_racing_hint(target)

build = os.environ['DEPLOY_SHA'][:12]
for path in target.glob('*.js'):
    text = path.read_text()
    text = re.sub(r"(['\"])(\./[^'\"?]+\.js)(?:\?v=[^'\"]+)?\1", lambda m: f'{m[1]}{m[2]}?v={build}{m[1]}', text)
    path.write_text(text)
index = target / 'index.html'
html = index.read_text()
html = re.sub(r'(href|src)="([^"?]+\.(?:css|js))(?:\?v=[^"]+)?"', lambda m: f'{m[1]}="{m[2]}?v={build}"', html)
# No mid-game reload; clean up only this game's old caches and registrations.
guard = '''<script>
(async()=>{try{
 const current=BUILD_ID,key='break-cars-build';
 if(localStorage.getItem(key)!==current){
  if('caches' in window)for(const name of await caches.keys())if(/break[-_ ]?cars/i.test(name))await caches.delete(name);
  if('serviceWorker' in navigator)for(const r of await navigator.serviceWorker.getRegistrations())if(new URL(r.scope).pathname.includes('/break-cars/'))await r.unregister();
  localStorage.setItem(key,current);
 }
}catch{}})();
</script>'''.replace('BUILD_ID', repr(build))
html = html.replace('<script type="module"', guard + '<script type="module"', 1)
index.write_text(html)
(target / 'build-id.txt').write_text(build + '\n')
print(f'Prepared {len(list(target.iterdir()))} assets, build {build}')
