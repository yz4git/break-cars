"""Death Colosseum v1.3 opening-line improvements.

The original authored spawn points were safe, but every car was pointed toward
the world origin. That is correct only for radial arenas. On DEATH WHEEL and
BROKEN ORBIT it aims through ring holes, and on SKY TILES corner starts it aims
diagonally between orthogonal bridges. Give each topology an opening heading
that follows real deck instead. AI can still choose opponents immediately; the
first acceleration impulse no longer begins by steering into empty space.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Death Colosseum v1.3 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_death_colosseum_openings_v13(target: Path) -> None:
    physics_path = target / 'physics.js'
    physics = physics_path.read_text()

    marker = "export function makeWorld(type=0,seed=42,gameMode='colosseum'){"
    helper = r"""function deathOpeningHeading(id,x,z){
 if(id==='death-wheel')return Math.atan2(z,-x); // tangent to the outer ring
 if(id==='broken-orbit'){
  const cx=x<0?-19:19,lx=x-cx;
  return Math.atan2(z,-lx); // tangent to the local left/right ring
 }
 if(id==='sky-tiles'){
  let dx=0,dz=0;
  // Pick an orthogonal bridge toward the center instead of the missing diagonal.
  if(Math.abs(x)>=Math.abs(z)&&Math.abs(x)>6)dx=-Math.sign(x);
  else if(Math.abs(z)>6)dz=-Math.sign(z);
  else dz=1;
  return Math.atan2(dx,dz);
 }
 return Math.atan2(-x,-z); // radial courses: RAZOR CROSS / HEX DROP
}

export function makeWorld(type=0,seed=42,gameMode='colosseum'){"""
    physics = one(physics, marker, helper, 'opening heading helper')
    physics = one(
        physics,
        "c.heading=Math.atan2(-x,-z);c.dead=false;",
        "c.heading=deathOpeningHeading(activeCourse.id,x,z);c.dead=false;",
        'authored opening headings',
    )
    physics_path.write_text(physics)


if __name__ == '__main__':
    apply_death_colosseum_openings_v13(Path('_site'))
