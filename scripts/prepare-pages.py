"""Publish the authored game with Wreck Hunt and versioned local dependencies."""
from pathlib import Path
import os
import re
import shutil
from apply_wreck_hunt import apply_wreck_hunt

source = Path('dist')
target = Path('_site')
if target.exists():
    shutil.rmtree(target)
shutil.copytree(source, target)

# Keep the large shared runtime single-source in dist; apply the Wreck Hunt
# integration to the deploy copy and fail loudly if upstream code drifts.
apply_wreck_hunt(target)

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
