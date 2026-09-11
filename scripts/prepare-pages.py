"""Publish the authored game with Wreck Hunt, full 3D physics, and versioned local dependencies."""
from pathlib import Path
import importlib.util
import os
import re
import shutil
import subprocess


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
apply_nine_course_review_polish = load_function('polish-nine-course-review-v1.py', 'break_cars_nine_course_review_v1', 'apply_nine_course_review_polish')
apply_nine_course_review_v2 = load_function('polish-nine-course-review-v2.py', 'break_cars_nine_course_review_v2', 'apply_nine_course_review_v2')
apply_rampage_exit_stabilizer_v3 = load_function('stabilize-rampage-loop-exit-v3.py', 'break_cars_rampage_exit_v3', 'apply_rampage_exit_stabilizer_v3')
apply_sky_loop_exit_v5 = load_function('stabilize-sky-loop-exit-v5.py', 'break_cars_sky_exit_v5', 'apply_sky_loop_exit_v5')
apply_sky_loop_attitude_v6 = load_function('stabilize-sky-loop-attitude-v6.py', 'break_cars_sky_attitude_v6', 'apply_sky_loop_attitude_v6')
apply_double_orbit_pack_v7 = load_function('tune-double-orbit-pack-v7.py', 'break_cars_double_orbit_pack_v7', 'apply_double_orbit_pack_v7')
apply_double_orbit_final_jump_v8 = load_function('stabilize-double-orbit-final-jump-v8.py', 'break_cars_double_orbit_final_jump_v8', 'apply_double_orbit_final_jump_v8')
apply_racing_sign_visibility_v4 = load_function('polish-racing-sign-visibility-v4.py', 'break_cars_racing_sign_visibility_v4', 'apply_racing_sign_visibility_v4')
apply_reference_loop_geometry_v8 = load_function('polish-reference-loop-geometry-v8.py', 'break_cars_reference_loop_geometry_v8', 'apply_reference_loop_geometry_v8')
apply_course_specific_loop_geometry_v9 = load_function('polish-course-specific-loop-geometry-v9.py', 'break_cars_course_specific_loop_geometry_v9', 'apply_course_specific_loop_geometry_v9')
apply_rampage_reference_loop_v10 = load_function('polish-rampage-reference-loop-v10.py', 'break_cars_rampage_reference_loop_v10', 'apply_rampage_reference_loop_v10')
apply_rampage_reference_loop_v11 = load_function('polish-rampage-reference-loop-v11.py', 'break_cars_rampage_reference_loop_v11', 'apply_rampage_reference_loop_v11')
apply_rampage_parallel_loop_v12 = load_function('polish-rampage-parallel-loop-v12.py', 'break_cars_rampage_parallel_loop_v12', 'apply_rampage_parallel_loop_v12')
apply_rampage_omega_entry_v13 = load_function('tune-rampage-omega-entry-v13.py', 'break_cars_rampage_omega_entry_v13', 'apply_rampage_omega_entry_v13')
apply_double_orbit_reference_v23 = load_function('polish-double-orbit-reference-v23.py', 'break_cars_double_orbit_reference_v23', 'apply_double_orbit_reference_v23')
apply_double_orbit_planar_v24 = load_function('polish-double-orbit-planar-v24.py', 'break_cars_double_orbit_planar_v24', 'apply_double_orbit_planar_v24')
apply_double_orbit_reference_view_v25 = load_function('polish-double-orbit-reference-view-v25.py', 'break_cars_double_orbit_reference_view_v25', 'apply_double_orbit_reference_view_v25')
apply_double_orbit_parallel_road_v26 = load_function('polish-double-orbit-parallel-road-v26.py', 'break_cars_double_orbit_parallel_road_v26', 'apply_double_orbit_parallel_road_v26')
apply_double_orbit_split_loop_v27 = load_function('polish-double-orbit-split-loop-v27.py', 'break_cars_double_orbit_split_loop_v27', 'apply_double_orbit_split_loop_v27')
apply_mayhem_tour_v1 = load_function('apply-mayhem-tour-v1.py', 'break_cars_mayhem_tour_v1', 'apply_mayhem_tour_v1')
apply_mayhem_tour_finalize_v1 = load_function('finalize-mayhem-tour-v1.py', 'break_cars_mayhem_tour_finalize_v1', 'apply_mayhem_tour_finalize_v1')

source = Path('dist')
target = Path('_site')
if target.exists():
    shutil.rmtree(target)
shutil.copytree(source, target)

apply_wreck_hunt(target)
apply_wreck_hunt_improvements(target)
apply_wreck_hunt_final_tuning(target)
apply_wreck_hunt_chain_tuning(target)
apply_wreck_hunt_rush(target)
apply_racing3d_projection_fix(target)
apply_full_physics3d(target)
apply_racing3d_surface_hint(target)
apply_smooth_racing3d_boundary(target)
apply_full_physics_loop_polish(target)
apply_racing3d_loop_camera(target)
apply_rampage_raceability(target)
apply_rampage_loop_boost_v6(target)
apply_racing3d_ui(target)
apply_player_auto_upright(target)
apply_auto_upright_racing_hint(target)

apply_course_pack = load_function('apply-course-pack.py', 'break_cars_courses', 'apply_course_pack')
apply_course_pack(target)
apply_extreme_courses = load_function('apply-extreme-courses.py', 'break_cars_extreme_courses', 'apply_extreme_courses')
apply_extreme_courses(target)
apply_reference_loop_geometry_v8(target)
apply_course_specific_loop_geometry_v9(target)
apply_rampage_reference_loop_v10(target)
apply_nine_course_review_polish(target)
apply_nine_course_review_v2(target)
apply_rampage_exit_stabilizer_v3(target)
apply_sky_loop_exit_v5(target)
apply_sky_loop_attitude_v6(target)
apply_double_orbit_pack_v7(target)
apply_double_orbit_final_jump_v8(target)
apply_racing_sign_visibility_v4(target)
apply_rampage_reference_loop_v11(target)
# Final RAMPAGE geometry rule from the visual reference: two straight parallel
# road centrelines 2W apart, joined by C2 lower legs to one 5W planar Omega.
apply_rampage_parallel_loop_v12(target)
# The C2 lower leg has a faster tangent rotation than the old twisted ribbon;
# guide velocity through it with forces only, after final geometry is known.
apply_rampage_omega_entry_v13(target)
# DOUBLE ORBIT is the two-loop course from the supplied toy-track reference.
# First move the two insertion gates together, then replace the legacy helix
# with two parallel circular rings and a force-only traversal guide.
apply_double_orbit_reference_v23(target)
apply_double_orbit_planar_v24(target)
# Straighten the ordinary road through the twin-loop stage before applying its
# final sign/camera sightline polish. The blend back to the authored lobe stays
# outside both loop gates.
apply_double_orbit_parallel_road_v26(target)
# Split each loop's incoming and returning lower roads by one full road width,
# enlarging the ring and gate spacing so the two road decks never overlap.
apply_double_orbit_split_loop_v27(target)
# Keep both open throats visible and stage each active ring from the side away
# from its sibling so the other loop never blocks the stunt camera.
apply_double_orbit_reference_view_v25(target)

# MAYHEM TOUR is a final gameplay layer over the already-polished events. It
# does not rewrite their course geometry or mode rules; it only carries the car,
# hull and pit upgrades across CRATER CROWN -> WRECK HUNT -> DOUBLE ORBIT.
apply_mayhem_tour_v1(target)
apply_mayhem_tour_finalize_v1(target)

# Keep final public visual verification tied to the exact deploy SHA, including
# late RAMPAGE dressing/visibility changes that do not alter vehicle physics.
build = (os.environ.get('DEPLOY_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())[:12]
for path in target.glob('*.js'):
    text = path.read_text()
    text = re.sub(r"(['\"])(\./[^'\"?]+\.js)(?:\?v=[^'\"]+)?\1", lambda m: f'{m[1]}{m[2]}?v={build}{m[1]}', text)
    path.write_text(text)
index = target / 'index.html'
html = index.read_text()
html = re.sub(r'(href|src)="([^"?]+\.(?:css|js))(?:\?v=[^"]+)?"', lambda m: f'{m[1]}="{m[2]}?v={build}"', html)
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
shutil.copytree(target, Path('build'), dirs_exist_ok=True)