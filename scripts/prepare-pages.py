"""Publish the authored game with Wreck Hunt and versioned local dependencies."""
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
apply_wreck_hunt_final_tuning = load_function('tune-wreck-hunt-post-review.py', 'break_cars_wreck_hunt_final_tuning', 'apply_wreck_hunt_final_tuning')

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
