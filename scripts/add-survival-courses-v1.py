"""BREAK CARS survival course pack v1.

Add one fall-is-death course to each core mode without changing the normal
courses.  Non-racing survival courses are 8m elevated wheel/ring platforms with
real holes.  SKYFALL CIRCUIT is a narrow 10m-high math track with no invisible
edge correction.  Once a chassis falls below the deck, the existing hit/wreck
pipeline is used so push-outs still award WRECK credit and WRECK HUNT respawns
continue to work.
"""
from pathlib import Path
import re


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Survival courses {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def regex_one(text: str, pattern: str, repl: str, label: str) -> str:
    out, n = re.subn(pattern, repl, text, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError(f'Survival courses {label}: expected 1 match, found {n}')
    return out


def apply_survival_courses_v1(target: Path) -> None:
    # ------------------------------------------------------------------
    # Course catalogue + analytical collision decks for non-racing modes.
    # ------------------------------------------------------------------
    courses_path = target / 'courses.js'
    courses = courses_path.read_text()
    marker = "\n];\nconst requested="
    additions = """,
 {id:'last-platform',mode:'colosseum',name:'LAST PLATFORM',survival:true,deathY:6.2,hint:'高架の中央島＋外周リング。柵なし。押し落とされたら一撃WRECK。最後の1台まで生き残れ。'},
 {id:'void-hunt',mode:'wreck-hunt',name:'VOID HUNT',survival:true,deathY:6.2,hint:'高架外周リングと分断ブリッジ。落下は一撃WRECK。60秒、敵を落としてCHAINを稼げ。'},
 {id:'skyfall-circuit',mode:'racing',name:'SKYFALL CIRCUIT',survival:true,deathY:6.2,hint:'地上10mの柵なし高速路。2周・約1分。コースアウトは一撃WRECK、復帰なし。'}
];
const requested="""
    courses = one(courses, marker, additions, 'course catalogue')

    smooth_marker = "const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};\n"
    helper = smooth_marker + """function survivalWheelHeight(x,z,kind){
 const r=Math.hypot(x,z),a=Math.atan2(x,z),H=8;
 if(kind==='last-platform'){
  if(r<=15||(r>=27&&r<=37)||(r<=28.4&&Math.abs(Math.sin(6*a))<.33))return H;
  return null;
 }
 if(kind==='void-hunt'){
  if(r<=12||(r>=27&&r<=37)||(r<=24.5&&Math.abs(Math.sin(6*a))<.24))return H;
  return null;
 }
 return null;
}
"""
    courses = one(courses, smooth_marker, helper, 'survival height helper')
    courses = one(
        courses,
        "export function courseHeight(x,z){\n",
        "export function courseHeight(x,z){\n if(activeCourse.id==='last-platform'||activeCourse.id==='void-hunt')return survivalWheelHeight(x,z,activeCourse.id);\n",
        'course height dispatch',
    )
    old_surface = "export function courseSurface(x,z){const h=courseHeight(x,z);if(h===null)return null;const e=.06,gx=(courseHeight(x+e,z)-courseHeight(x-e,z))/(2*e),gz=(courseHeight(x,z+e)-courseHeight(x,z-e))/(2*e),n=Math.hypot(gx,1,gz);return{h,n:{x:-gx/n,y:1/n,z:-gz/n}};}"
    new_surface = """export function courseSurface(x,z){
 const h=courseHeight(x,z);if(h===null)return null;const e=.06;
 const sample=(sx,sz)=>{const q=courseHeight(sx,sz);return q===null?h:q;};
 const gx=(sample(x+e,z)-sample(x-e,z))/(2*e),gz=(sample(x,z+e)-sample(x,z-e))/(2*e),n=Math.hypot(gx,1,gz);
 return{h,n:{x:-gx/n,y:1/n,z:-gz/n}};
}"""
    courses = one(courses, old_surface, new_surface, 'hole-safe surface normals')
    courses_path.write_text(courses)

    # ------------------------------------------------------------------
    # Visible platforms.  There are no guard rails: the geometry clearly
    # communicates that the edge itself is the combat rule.
    # ------------------------------------------------------------------
    view_path = target / 'course-view.js'
    view = view_path.read_text()
    old_start = " const group=new THREE.Group();if(courseHeight(0,0)===null)return group;"
    new_start = r""" const group=new THREE.Group();
 if(activeCourse.survival&&activeCourse.mode!=='racing'){
  const hunt=activeCourse.id==='void-hunt',hub=hunt?12:15,bridgeEnd=hunt?24.5:28.4,bridgeW=hunt?2.9:4.0,H=8;
  const deck=new THREE.MeshStandardMaterial({color:hunt?0x39434f:0x4b4541,roughness:.86,metalness:.08,side:THREE.DoubleSide});
  const edge=new THREE.MeshStandardMaterial({color:hunt?0xff4f72:0xffa13c,roughness:.70,metalness:.18,side:THREE.DoubleSide});
  const hubMesh=new THREE.Mesh(new THREE.CylinderGeometry(hub,hub,.8,48),deck);hubMesh.position.y=H-.4;hubMesh.receiveShadow=true;group.add(hubMesh);
  const ring=new THREE.Mesh(new THREE.RingGeometry(27,37,96),deck);ring.rotation.x=-Math.PI/2;ring.position.y=H+.015;ring.receiveShadow=true;group.add(ring);
  for(const [ri,ro] of [[26.65,27.05],[36.95,37.35]]){const e=new THREE.Mesh(new THREE.RingGeometry(ri,ro,96),edge);e.rotation.x=-Math.PI/2;e.position.y=H+.045;group.add(e);}
  const bridgeLen=bridgeEnd-hub,mid=(bridgeEnd+hub)/2;
  for(let i=0;i<12;i++){
   const a=i/12*Math.PI*2,b=new THREE.Mesh(new THREE.BoxGeometry(bridgeW,.8,bridgeLen),deck);b.position.set(Math.sin(a)*mid,H-.4,Math.cos(a)*mid);b.rotation.y=a;b.receiveShadow=true;group.add(b);
   const stripe=new THREE.Mesh(new THREE.BoxGeometry(Math.max(.22,bridgeW*.12),.06,bridgeLen*.82),edge);stripe.position.set(Math.sin(a)*mid,H+.045,Math.cos(a)*mid);stripe.rotation.y=a;group.add(stripe);
  }
  const hubEdge=new THREE.Mesh(new THREE.RingGeometry(hub-.42,hub,72),edge);hubEdge.rotation.x=-Math.PI/2;hubEdge.position.y=H+.045;group.add(hubEdge);
  group.userData.survivalCourse={id:activeCourse.id,deckY:H,fallIsWreck:true};return group;
 }
 if(courseHeight(0,0)===null)return group;"""
    view = one(view, old_start, new_start, 'survival platform rendering')
    view_path.write_text(view)

    # ------------------------------------------------------------------
    # Math racing course.  It remains compatible with the existing loop,
    # jump, tactical-contact and RIVAL layers, but the entire road is high and
    # considerably narrower than the normal courses.
    # ------------------------------------------------------------------
    racing3d_path = target / 'racing3d.js'
    racing3d = racing3d_path.read_text()
    config_marker = "};\nconst courseId=activeCourse?.mode==='racing'&&CONFIGS[activeCourse.id]?activeCourse.id:'rampage-3d';"
    skyfall = """,
 'skyfall-circuit':{
  name:'SKYFALL CIRCUIT',halfWidth:5.8,designSpeed:23.0,bankMax:24*Math.PI/180,
  loops:[{t:1.20,radius:8.8}],jump:{rampStart:4.62,gapStart:4.76,gapEnd:4.87,landEnd:5.06,lift:.88,landingLift:.38},
  plan:t=>({x:64*Math.cos(t)+8*Math.cos(3*t),z:40*Math.sin(t)}),
  elevation:t=>10+2.7*gauss(t,2.55,.55)+1.4*gauss(t,5.55,.42)
 }
};
const courseId=activeCourse?.mode==='racing'&&CONFIGS[activeCourse.id]?activeCourse.id:'rampage-3d';"""
    racing3d = one(racing3d, config_marker, skyfall, 'SKYFALL math config')
    racing3d_path.write_text(racing3d)

    # The final math track view normally draws rails and a ground slab. SKYFALL
    # deliberately has neither: only the elevated road and distant abyss plane.
    track_path = target / 'track-view.js'
    track = track_path.read_text()
    track = one(
        track,
        " const group=new THREE.Group(),spec=race3DFeatureSpec(),samples=560,W=RACE3D_TRACK.halfWidth;\n",
        " const group=new THREE.Group(),spec=race3DFeatureSpec(),samples=560,W=RACE3D_TRACK.halfWidth,survival=activeCourse.survival===true;\n",
        'track survival flag',
    )
    palette_marker = "  'double-orbit':{road:0x39384a,edge:0xd98bff,rail:0x797187,accent:0xffc0ff,land:0x4c4958}\n"
    track = one(
        track,
        palette_marker,
        "  'double-orbit':{road:0x39384a,edge:0xd98bff,rail:0x797187,accent:0xffc0ff,land:0x4c4958},\n  'skyfall-circuit':{road:0x30333a,edge:0xff4d62,rail:0x5b626b,accent:0xffd35c,land:0x090b10}\n",
        'SKYFALL palette',
    )
    old_land = " const land=box(group,(minX+maxX)/2,-3.1,(minZ+maxZ)/2,maxX-minX,.55,maxZ-minZ,P.land);land.receiveShadow=true;"
    new_land = " if(!survival){const land=box(group,(minX+maxX)/2,-3.1,(minZ+maxZ)/2,maxX-minX,.55,maxZ-minZ,P.land);land.receiveShadow=true;}else{const abyss=box(group,(minX+maxX)/2,-18,(minZ+maxZ)/2,maxX-minX+40,.25,maxZ-minZ+40,P.land);abyss.receiveShadow=true;}"
    track = one(track, old_land, new_land, 'SKYFALL abyss')
    old_rails = "ribbon(-W,W,P.road,.01);ribbon(-W,-W+.48,0xe5e1d1,.035);ribbon(W-.48,W,0xe5e1d1,.035);ribbon(-W+.48,-W+.84,P.edge,.043);ribbon(W-.84,W-.48,P.edge,.043);edgeTube(-W-.42,P.rail);edgeTube(W+.42,P.rail);"
    new_rails = "ribbon(-W,W,P.road,.01);ribbon(-W,-W+.48,0xe5e1d1,.035);ribbon(W-.48,W,0xe5e1d1,.035);ribbon(-W+.48,-W+.84,P.edge,.043);ribbon(W-.84,W-.48,P.edge,.043);if(!survival){edgeTube(-W-.42,P.rail);edgeTube(W+.42,P.rail);}"
    track = one(track, old_rails, new_rails, 'remove SKYFALL rails')
    track_path.write_text(track)

    # ------------------------------------------------------------------
    # Runtime rules: no invisible wall rescue, no race recovery, and falling
    # below the deck goes through the real hit() path for scoring/respawn.
    # ------------------------------------------------------------------
    physics3d_path = target / 'physics3d.js'
    physics3d = physics3d_path.read_text()
    physics3d = one(
        physics3d,
        "import {courseSurface} from './courses.js';",
        "import {activeCourse,courseSurface} from './courses.js';",
        'physics active course import',
    )
    physics3d = regex_one(
        physics3d,
        r"function arenaBoundary\(w,c,ctx\) \{\s*if \(w\.mode==='racing'\) return;",
        "function arenaBoundary(w,c,ctx) {\n  if (w.mode==='racing'||activeCourse?.survival) return;",
        'remove survival arena wall',
    )
    hit_anchor = "const da=ctx.hit(w,a,damage*mb,nx,nz,b)||0,db=ctx.hit(w,b,damage*ma,-nx,-nz,a)||0;"
    physics3d = one(
        physics3d,
        hit_anchor,
        "a.lastOpponent=b.id;b.lastOpponent=a.id;" + hit_anchor,
        'remember push-out opponent',
    )
    maintain_anchor = "function maintainHunt(w,ctx) {"
    survival_fn = r"""function survivalFall(w,c,ctx){
 if(!activeCourse?.survival||c.dead||c.finished||!c.p3)return;
 const b=c.p3,deathY=Number(activeCourse.deathY??6.2);if(b.py>=deathY)return;
 const recent=Number.isInteger(c.lastOpponent)&&w.time-(c.lastContact??-99)<3.25,wrecker=recent?w.cars[c.lastOpponent]:null;
 ctx.hit(w,c,Math.max(999,c.hp+999),0,1,wrecker&&!wrecker.dead?wrecker:undefined);
 if(c.dead)w.events.push({type:'fall',car:c.id,by:wrecker?.id??-1,x:b.px,y:b.py,z:b.pz,power:55});
}
function maintainHunt(w,ctx) {"""
    physics3d = one(physics3d, maintain_anchor, survival_fn, 'fall death rule')
    substep_anchor = "    for (const c of w.cars) syncLegacy(c);\n  }\n  if (w.mode==='racing')"
    physics3d = one(
        physics3d,
        substep_anchor,
        "    for (const c of w.cars) { syncLegacy(c); survivalFall(w,c,ctx); }\n  }\n  if (w.mode==='racing')",
        'fall check after physics',
    )
    physics3d_path.write_text(physics3d)

    racing_path = target / 'racing.js'
    racing = racing_path.read_text()
    racing = one(
        racing,
        "export function constrainTrack(c){\n",
        "export function constrainTrack(c){\n if(mathCourseV1.survival)return null;\n",
        'remove survival race edge correction',
    )
    racing = one(
        racing,
        "export function recoverRaceCar(w,c){\n",
        "export function recoverRaceCar(w,c){\n if(mathCourseV1.survival)return false;\n",
        'disable survival race recovery',
    )
    racing_path.write_text(racing)

    # Keep the recovery UI out of the way on the no-recovery race and make the
    # fatal-edge rule explicit in the course selection text.
    game_path = target / 'game.js'
    game = game_path.read_text()
    game = game.replace(
        "$('recover').classList.toggle('hidden',gameMode!=='racing');",
        "$('recover').classList.toggle('hidden',gameMode!=='racing'||activeCourse.survival);",
    )
    game_path.write_text(game)

    css_path = target / 'courses.css'
    css = css_path.read_text()
    css += "\n.course-hint{max-width:760px}.course-hint:has(+ #survival-rule){margin-bottom:4px}\n"
    css_path.write_text(css)

    # Fail build-time if a later generator silently removes the core rule.
    checks = {
        'courses.js': ["id:'last-platform'", "id:'void-hunt'", "id:'skyfall-circuit'", 'survivalWheelHeight'],
        'physics3d.js': ['function survivalFall', "activeCourse?.survival", "type:'fall'"],
        'racing.js': ['if(mathCourseV1.survival)return null;', 'if(mathCourseV1.survival)return false;'],
        'racing3d.js': ["'skyfall-circuit':{", 'halfWidth:5.8', 'elevation:t=>10+'],
        'track-view.js': ['survival=activeCourse.survival===true', 'if(!survival){edgeTube'],
    }
    for filename, needles in checks.items():
        text = (target / filename).read_text()
        for needle in needles:
            if needle not in text:
                raise RuntimeError(f'Survival courses: {needle!r} missing from generated {filename}')


if __name__ == '__main__':
    apply_survival_courses_v1(Path('_site'))
