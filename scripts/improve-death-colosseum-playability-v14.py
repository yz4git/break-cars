"""Death Colosseum v1.4 playability and pre-start placement fixes.

Fix two issues found by the live iPhone-landscape visual audit:
1. Full-3D bodies were created at the legacy ground plane during countdown,
   leaving the car/camera under the elevated arena until the first live physics
   frames pulled them onto the deck.
2. DEATH WHEEL AI still pursued opponents by straight chords across the center
   hole, so several cars self-eliminated almost immediately even after their
   initial headings were made tangential.

The wheel also gets a slightly wider outer ring. It is still unguarded and a
fall is still instant WRECK, but normal steering has enough recovery room to
create actual pushing battles instead of accidental opening suicides.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Death Colosseum v1.4 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_death_colosseum_playability_v14(target: Path) -> None:
    courses_path = target / 'courses.js'
    courses = courses_path.read_text()
    courses = one(
        courses,
        "if(r<=14||(r>=27&&r<=37)||(r>=13&&r<=29&&Math.abs(Math.sin(4*a))<.18))return H;",
        "if(r<=14||(r>=25.5&&r<=38.5)||(r>=13&&r<=29&&Math.abs(Math.sin(4*a))<.18))return H;",
        'wider death wheel collision ring',
    )
    courses_path.write_text(courses)

    view_path = target / 'course-view.js'
    view = view_path.read_text()
    view = one(
        view,
        "const ring=new THREE.Mesh(new THREE.RingGeometry(27,37,96),deck);ring.rotation.x=-Math.PI/2;ring.position.y=H+.015;ring.receiveShadow=true;group.add(ring);for(const rr of [[26.6,27.05],[36.95,37.4]])",
        "const ring=new THREE.Mesh(new THREE.RingGeometry(25.5,38.5,96),deck);ring.rotation.x=-Math.PI/2;ring.position.y=H+.015;ring.receiveShadow=true;group.add(ring);for(const rr of [[25.05,25.55],[38.45,38.95]])",
        'wider death wheel rendered ring',
    )
    view_path.write_text(view)

    p3_path = target / 'physics3d.js'
    p3 = p3_path.read_text()
    p3 = one(
        p3,
        "}else{q=yawQuat(c.heading||0);py=baseHeight(c.x,c.z).h+COM_VISUAL_Y;}",
        "}else{q=yawQuat(c.heading||0);const survivalDeck=activeCourse?.survival?courseSurface(c.x,c.z):null;py=(survivalDeck?.h??baseHeight(c.x,c.z).h)+COM_VISUAL_Y;}",
        'elevated body creation',
    )
    p3_path.write_text(p3)

    # Create the 6DoF pose during reset, not on the first live physics tick.
    # Countdown/menu cameras can then use the authored elevated pose without
    # moving cars or advancing match time.
    game_path = target / 'game.js'
    game = game_path.read_text()
    game = one(
        game,
        "import {fullPhysicsFeatureSpec} from './physics3d.js?v=works-full3d';",
        "import {ensureFullPhysics,fullPhysicsFeatureSpec} from './physics3d.js?v=works-full3d';",
        'full physics initializer import',
    )
    game = one(
        game,
        "world=makeWorld(selection,seed++,gameMode);",
        "world=makeWorld(selection,seed++,gameMode);ensureFullPhysics(world,TYPES);",
        'pre-countdown full physics pose',
    )
    game = one(
        game,
        "if(mode==='menu'){menuTime+=dt;const a=.35+Math.sin(menuTime*.11)*.25;camTarget.set(p.x+Math.sin(a)*13,7,p.z+Math.cos(a)*13);lookTarget.set(p.x-2.5,1,p.z-2.5);camera.fov=50;camera.up.lerp(physicsWorldUp,1-Math.exp(-6*dt));}",
        "if(mode==='menu'){menuTime+=dt;const a=.35+Math.sin(menuTime*.11)*.25,menuY=p.p3?.active?p.p3.py:.9;camTarget.set(p.x+Math.sin(a)*13,menuY+6,p.z+Math.cos(a)*13);lookTarget.set(p.x-2.5,menuY+.2,p.z-2.5);camera.fov=50;camera.up.lerp(physicsWorldUp,1-Math.exp(-6*dt));}",
        'elevated menu camera',
    )
    game_path.write_text(game)

    # Elevated arenas need a little more steering margin on touch controls.
    p3 = p3_path.read_text()
    p3 = one(
        p3,
        "let steer=c.dead ? 0 : (u.steer||0); if (player) steer=-steer;",
        "let steer=c.dead ? 0 : (u.steer||0); if (player) steer=-steer;if(player&&w.mode==='death-colosseum')steer*=.78;",
        'death colosseum player steering margin',
    )
    p3_path.write_text(p3)

    physics_path = target / 'physics.js'
    physics = physics_path.read_text()
    marker = "function ai(w,c,dt){"
    helper = r"""function deathColosseumSafeAim(w,c,aimX,aimZ){
 if(w.mode!=='death-colosseum')return{x:aimX,z:aimZ};
 if(activeCourse?.id==='sky-tiles'){
  const lanes=[-22,0,22],nearest=v=>lanes.reduce((a,b)=>Math.abs(v-b)<Math.abs(v-a)?b:a,lanes[0]);
  const row=nearest(c.z),col=nearest(c.x),dx=aimX-c.x,dz=aimZ-c.z;
  const onRow=Math.abs(c.z-row)<=3.4,onCol=Math.abs(c.x-col)<=3.4;
  if((onRow&&!onCol)||(onRow&&onCol&&Math.abs(dx)>=Math.abs(dz)))return{x:c.x+clamp(dx,-14,14),z:row};
  return{x:col,z:c.z+clamp(dz,-14,14)};
 }
 if(activeCourse?.id!=='death-wheel')return{x:aimX,z:aimZ};
 const r=Math.hypot(c.x,c.z)||1,rx=c.x/r,rz=c.z/r,tx=rz,tz=-rx;
 const toX=aimX-c.x,toZ=aimZ-c.z,targetTangent=toX*tx+toZ*tz;
 const fx=Math.sin(c.heading),fz=Math.cos(c.heading),forwardTangent=fx*tx+fz*tz;
 let dir=Math.abs(targetTangent)>5?Math.sign(targetTangent):Math.sign(forwardTangent||1);
 if(dir*forwardTangent<0&&Math.abs(targetTangent)<13)dir=Math.sign(forwardTangent||1);
 const centerRadius=32,radial=clamp((centerRadius-r)*.82,-5.5,5.5),look=15;
 return{x:c.x+tx*dir*look+rx*radial,z:c.z+tz*dir*look+rz*radial};
}

function ai(w,c,dt){"""
    physics = one(physics, marker, helper, 'safe aim helper')
    physics = one(
        physics,
        " const desired=Math.atan2(aimX-c.x,aimZ-c.z);",
        " const safeAim=deathColosseumSafeAim(w,c,aimX,aimZ);aimX=safeAim.x;aimZ=safeAim.z;\n const desired=Math.atan2(aimX-c.x,aimZ-c.z);",
        'safe death wheel pursuit',
    )
    physics_path.write_text(physics)


if __name__ == '__main__':
    apply_death_colosseum_playability_v14(Path('_site'))
