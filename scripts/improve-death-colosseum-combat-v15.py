"""Death Colosseum v1.5 combat readability tuning.

Live screenshot review showed three remaining problems:
- several AI cars commit to the same opponent at once and form a central pile;
- a strong multi-car contact can leave an otherwise-live car nearly vertical;
- after a clean player run, ordinary momentum can carry the car over an edge
  while the user is already trying to slow down.

Keep FALL = instant WRECK. These assists only operate while the chassis still
has deck support; recent opponent hits deliberately bypass the player edge
brake so real push-outs remain lethal.
"""
from pathlib import Path
import re


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Death Colosseum v1.5 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_death_colosseum_combat_v15(target: Path) -> None:
    physics_path = target / 'physics.js'
    physics = physics_path.read_text()

    physics, n = re.subn(
        r"(\\s*const bias=.*?;\\n)(\\s*const cost=)(.*?)(;)",
        lambda m: m.group(1) + "   const crowdPenalty=w.mode==='death-colosseum'?w.cars.reduce((n,q)=>n+(q!==c&&!q.dead&&q.target===o.id?1:0),0)*8.5:0;\\n" + m.group(2) + m.group(3) + "+crowdPenalty" + m.group(4),
        physics,
        count=1,
    )
    if n != 1:
        probe = physics.find('function ai')
        context = physics[max(0, probe-200):probe+4200] if probe >= 0 else physics[:4200]
        raise RuntimeError(f'Death Colosseum v1.5 target crowd dispersion: expected AI cost once, found {n}; context={context!r}')
    physics = one(
        physics,
        "if(reengage>0){",
        "if(w.mode!=='death-colosseum'&&reengage>0){",
        'disable generic center magnet',
    )
    physics = one(
        physics,
        "const edge=clamp((radius-(RADIUS-12))/7,0,1);",
        "const edge=w.mode==='death-colosseum'?0:clamp((radius-(RADIUS-12))/7,0,1);",
        'disable circular edge pull',
    )
    physics = one(
        physics,
        "if(radius>RADIUS-5.5){aimX=-c.x*.25;aimZ=-c.z*.25;}",
        "if(w.mode!=='death-colosseum'&&radius>RADIUS-5.5){aimX=-c.x*.25;aimZ=-c.z*.25;}",
        'disable circular emergency aim',
    )
    physics = one(
        physics,
        "c.dead=false;c.hp=c.maxHP;c.lastContact=-99;c.lastOpponent=-1;}",
        "c.dead=false;c.hp=c.maxHP;c.lastContact=-99;c.lastOpponent=-1;c.aiTimer=i===0?0:(i%4)*.18;}",
        'stagger AI launch',
    )
    physics_path.write_text(physics)

    p3_path = target / 'physics3d.js'
    p3 = p3_path.read_text()

    old_integrate = """function integrateBody(w,c,u,ctx,dt) {
  const b=c.p3,acc={fx:0,fy:-9.81*b.mass,fz:0,tx:0,ty:0,tz:0}; wheelForces(w,c,u,ctx,dt,acc);
  const drag=c.dead ? .22 : .075;"""
    new_integrate = """function integrateBody(w,c,u,ctx,dt) {
  const b=c.p3,acc={fx:0,fy:-9.81*b.mass,fz:0,tx:0,ty:0,tz:0}; wheelForces(w,c,u,ctx,dt,acc);
  if(w.mode==='death-colosseum'&&!c.dead){
    if(c.id===0&&b.grounded&&b.groundedWheels>=2&&w.time-c.hitAt>.65){
      const speed=Math.hypot(b.vx,b.vz);
      if(speed>5&&courseSurface(b.px,b.pz)){
        const danger=[.18,.30,.42].some(t=>!courseSurface(b.px+b.vx*t,b.pz+b.vz*t));
        if(danger){const brake=4.2;acc.fx-=b.vx*b.mass*brake;acc.fz-=b.vz*b.mass*brake;}
      }
    }
    if(b.grounded&&b.groundedWheels>=2&&w.time-c.hitAt>.28){
      const up=bodyUp(b),tilt=Math.max(0,.76-up.y);
      if(tilt>0){
        const strength=(10+24*tilt)*b.mass;
        acc.tx+=up.z*strength;acc.tz-=up.x*strength;
        const settle=Math.exp(-(2.4+5.5*tilt)*dt);b.wx*=settle;b.wz*=settle;
      }
    }
  }
  const drag=c.dead ? .22 : .075;"""
    p3 = one(p3, old_integrate, new_integrate, 'supported edge brake and anti-tip')
    p3_path.write_text(p3)


if __name__ == '__main__':
    apply_death_colosseum_combat_v15(Path('_site'))
