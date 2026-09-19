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


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Death Colosseum v1.5 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_death_colosseum_combat_v15(target: Path) -> None:
    courses_path = target / 'courses.js'
    courses = courses_path.read_text()
    courses = one(
        courses,
        "if(r>=8&&r<=28.5&&Math.abs(Math.sin(3*a))<.14)return H;",
        "if(r>=8&&r<=28.5&&Math.abs(Math.sin(3*a))<.18)return H;",
        'wider hex bridge collision',
    )
    courses_path.write_text(courses)

    view_path = target / 'course-view.js'
    view = view_path.read_text()
    view = one(
        view,
        "addBridge(a,18,18.8,3.4);",
        "addBridge(a,18,18.8,4.2);",
        'wider hex bridge render',
    )
    view_path.write_text(view)

    game_path = target / 'game.js'
    game = game_path.read_text()
    if game.count("<small>IMPACT SCORE</small>") != 1:
        raise RuntimeError('Death Colosseum v1.5 result IMPACT SCORE label not unique')
    game = game.replace(
        "<small>IMPACT SCORE</small>",
        "<small>${world.mode==='death-colosseum'?'RING OUT SCORE':'IMPACT SCORE'}</small>",
        1,
    )
    if "<small>WRECKS</small>" not in game:
        raise RuntimeError('Death Colosseum v1.5 result WRECKS label missing')
    game = game.replace(
        "<small>WRECKS</small>",
        "<small>${world.mode==='death-colosseum'?'RING OUTS':'WRECKS'}</small>",
        1,
    )
    game_path.write_text(game)

    physics_path = target / 'physics.js'
    physics = physics_path.read_text()

    physics = one(
        physics,
        "const bias=(o.id===0?(w.mode==='wreck-hunt'?(c.id%3===0?1.04:.48):1.08):1)*(1+w.rand()*(w.mode==='wreck-hunt'?.20:.35));\n   const cost=dist*bias+Math.abs(angle(Math.atan2(o.x-c.x,o.z-c.z)-c.heading))*3+edgePenalty+centerPenalty;",
        "const bias=(o.id===0?(w.mode==='wreck-hunt'?(c.id%3===0?1.04:.48):1.08):1)*(1+w.rand()*(w.mode==='wreck-hunt'?.20:.35));\n   const crowdPenalty=w.mode==='death-colosseum'?w.cars.reduce((n,q)=>n+(q!==c&&!q.dead&&q.target===o.id?1:0),0)*8.5:0;\n   const cost=dist*bias+Math.abs(angle(Math.atan2(o.x-c.x,o.z-c.z)-c.heading))*3+edgePenalty+centerPenalty+crowdPenalty;",
        'target crowd dispersion',
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

    integrate_anchor = "skyForgeExitGuide(w,c,acc,ctx);\n  const drag=c.dead ? .22 : .075;"
    integrate_patch = """skyForgeExitGuide(w,c,acc,ctx);
  if(w.mode==='death-colosseum'&&!c.dead){
    if(c.id===0&&b.grounded&&b.groundedWheels>=2&&w.time-c.hitAt>.65){
      const speed=Math.hypot(b.vx,b.vz);
      if(speed>5&&courseSurface(b.px,b.pz)){
        const danger=[.12,.22,.34,.48].some(t=>!courseSurface(b.px+b.vx*t,b.pz+b.vz*t));
        if(danger){const brake=5.8;acc.fx-=b.vx*b.mass*brake;acc.fz-=b.vz*b.mass*brake;}
      }
    }
    const support=courseSurface(b.px,b.pz),nearDeck=!!support&&b.py<support.h+2.6;
    if((b.groundedWheels>=1||nearDeck)&&w.time-c.hitAt>.38){
      const up=bodyUp(b),tilt=Math.max(0,.76-up.y);
      if(tilt>0){
        const strength=(12+30*tilt)*b.mass;
        acc.tx+=up.z*strength;acc.tz-=up.x*strength;
        const settle=Math.exp(-(2.4+5.5*tilt)*dt);b.wx*=settle;b.wz*=settle;
      }
    }
  }
  const drag=c.dead ? .22 : .075;"""
    p3 = one(p3, integrate_anchor, integrate_patch, 'supported edge brake and anti-tip')
    p3_path.write_text(p3)


if __name__ == '__main__':
    apply_death_colosseum_combat_v15(Path('_site'))
