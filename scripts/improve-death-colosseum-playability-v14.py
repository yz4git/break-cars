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
import re


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
    body_pattern = r"(function makeBody\\(c,type\\)\\s*\\{.*?return\\s*\\{.*?\\bpx:c\\.x,\\s*py:)(.*?)(,\\s*pz:c\\.z)"
    body_repl = r"\\1(activeCourse?.survival?(courseSurface(c.x,c.z)?.h??baseHeight(c.x,c.z).h):baseHeight(c.x,c.z).h)+COM_VISUAL_Y\\3"
    p3, n = re.subn(body_pattern, body_repl, p3, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError(f'Death Colosseum v1.4 elevated body creation: expected makeBody py once, found {n}')
    p3_path.write_text(p3)

    physics_path = target / 'physics.js'
    physics = physics_path.read_text()
    marker = "function ai(w,c,dt){"
    helper = r"""function deathColosseumSafeAim(w,c,aimX,aimZ){
 if(w.mode!=='death-colosseum'||activeCourse?.id!=='death-wheel')return{x:aimX,z:aimZ};
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
