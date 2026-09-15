"""Survival course spawn normalization v1.1.

The ordinary WRECK HUNT opening choreography intentionally moves some rivals
off the default radial grid.  On an elevated fall-is-WRECK course that can put
a car over a real hole before the first physics frame.  Normalize only survival
non-racing starts onto the supported outer annulus after every ordinary setup
layer has finished.
"""
from pathlib import Path
import re


def apply_survival_spawn_fix_v11(target: Path) -> None:
    path = target / 'physics.js'
    text = path.read_text()

    if not re.search(r"import\s*\{[^}]*\bactiveCourse\b[^}]*\}\s*from\s*['\"]\./courses\.js", text):
        text = "import {activeCourse} from './courses.js';\n" + text

    anchor = " return gameMode==='racing'?setupRace(w):w;"
    n = text.count(anchor)
    if n != 1:
        raise RuntimeError(f'Survival spawn v1.1: expected final world return once, found {n}')

    replacement = """ if(activeCourse?.survival&&gameMode!=='racing'){
  const r=32,shift=activeCourse.id==='void-hunt'?Math.PI/24:0;
  for(let i=0;i<w.cars.length;i++){
   const a=i/w.cars.length*Math.PI*2+shift,c=w.cars[i];
   c.x=Math.sin(a)*r;c.z=Math.cos(a)*r;c.vx=0;c.vz=0;c.omega=0;c.heading=a+Math.PI;
   c.dead=false;c.hp=Math.max(1,c.hp);c.lastContact=-99;c.lastOpponent=-1;
  }
 }
 return gameMode==='racing'?setupRace(w):w;"""
    text = text.replace(anchor, replacement, 1)
    path.write_text(text)

    final = path.read_text()
    if "activeCourse?.survival&&gameMode!=='racing'" not in final or "const r=32" not in final:
        raise RuntimeError('Survival spawn v1.1: final spawn normalization missing')


if __name__ == '__main__':
    apply_survival_spawn_fix_v11(Path('_site'))
