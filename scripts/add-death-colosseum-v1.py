"""BREAK CARS Death Colosseum v1.

Add a dedicated fourth mode in which every course is elevated and the only
elimination rule is falling below the deck. Normal impact damage can cripple a
car but cannot WRECK it; a fall still goes through the real hit/wreck pipeline
so the last pusher receives credit.
"""
from pathlib import Path
import re


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Death Colosseum v1 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def regex_one(text: str, pattern: str, repl: str, label: str) -> str:
    out, n = re.subn(pattern, repl, text, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError(f'Death Colosseum v1 {label}: expected 1 match, found {n}')
    return out


def apply_death_colosseum_v1(target: Path) -> None:
    # ------------------------------------------------------------------
    # Five elevated fall-only arenas. Spawn points are authored into each
    # course so every car starts on real collision deck, never over a hole.
    # ------------------------------------------------------------------
    courses_path = target / 'courses.js'
    courses = courses_path.read_text()
    marker = "\n];\nconst requested="
    additions = r""",
 {id:'death-wheel',mode:'death-colosseum',name:'DEATH WHEEL',survival:true,fallOnly:true,deathY:6.4,spawns:[[0,32],[16,27.7],[27.7,16],[32,0],[27.7,-16],[16,-27.7],[0,-32],[-16,-27.7],[-27.7,-16],[-32,0],[-27.7,16],[-16,27.7]],hint:'中央島と外周リングを8本の細いスポークで接続。ダメージでは脱落しない。落ちた瞬間だけ一撃WRECK。'},
 {id:'razor-cross',mode:'death-colosseum',name:'RAZOR CROSS',survival:true,fallOnly:true,deathY:6.4,spawns:[[-4,29],[0,29],[4,29],[29,-4],[29,0],[29,4],[-4,-29],[0,-29],[4,-29],[-29,-4],[-29,0],[-29,4]],hint:'十字のナイフエッジと4つの広い端島。交差点で正面衝突し、相手を横へ弾き落とせ。'},
 {id:'broken-orbit',mode:'death-colosseum',name:'BROKEN ORBIT',survival:true,fallOnly:true,deathY:6.4,spawns:[[-19,15],[-8,11],[-8,-11],[-19,-15],[-30,-11],[-30,11],[19,15],[30,11],[30,-11],[19,-15],[8,-11],[8,11]],hint:'左右の巨大リングを3本の細橋だけで接続。内側の穴も外側も即死。橋上の押し合いが勝負。'},
 {id:'sky-tiles',mode:'death-colosseum',name:'SKY TILES',survival:true,fallOnly:true,deathY:6.4,spawns:[[-22,-22],[0,-22],[22,-22],[-22,0],[0,0],[22,0],[-22,22],[0,22],[22,22],[-19,-22],[19,0],[0,19]],hint:'3×3の空中タイルを細いグリッド橋で接続。安全な島と危険な移動路を使い分けろ。'},
 {id:'hex-drop',mode:'death-colosseum',name:'HEX DROP',survival:true,fallOnly:true,deathY:6.4,spawns:[[2.4,27],[-2.4,27],[24.6,15.5],[22.2,11.5],[24.6,-15.5],[22.2,-11.5],[-2.4,-27],[2.4,-27],[-24.6,-15.5],[-22.2,-11.5],[-24.6,15.5],[-22.2,11.5]],hint:'中央ハブ＋6つの孤島。細い6本橋を渡って包囲し、島ごと相手を追い詰めて落とせ。'}
];
const requested="""
    courses = one(courses, marker, additions, 'course catalogue')

    height_fn = r"""function deathColosseumHeight(x,z,id){
 const H=9,r=Math.hypot(x,z),a=Math.atan2(x,z);
 if(id==='death-wheel'){
  if(r<=14||(r>=27&&r<=37)||(r>=13&&r<=29&&Math.abs(Math.sin(4*a))<.18))return H;
  return null;
 }
 if(id==='razor-cross'){
  if((Math.abs(x)<=3.3&&Math.abs(z)<=36)||(Math.abs(z)<=3.3&&Math.abs(x)<=36))return H;
  for(const [px,pz] of [[0,29],[29,0],[0,-29],[-29,0]])if(Math.abs(x-px)<=8&&Math.abs(z-pz)<=8)return H;
  return null;
 }
 if(id==='broken-orbit'){
  const dl=Math.hypot(x+19,z),dr=Math.hypot(x-19,z);
  if((dl>=8.5&&dl<=17)||(dr>=8.5&&dr<=17))return H;
  if(Math.abs(x)<=19&&(Math.abs(z)<=3.2||Math.abs(z-13)<=2.6||Math.abs(z+13)<=2.6))return H;
  return null;
 }
 if(id==='sky-tiles'){
  for(const px of [-22,0,22])for(const pz of [-22,0,22])if(Math.abs(x-px)<=6.2&&Math.abs(z-pz)<=6.2)return H;
  if(Math.abs(x)<=28&&[-22,0,22].some(pz=>Math.abs(z-pz)<=2.2))return H;
  if(Math.abs(z)<=28&&[-22,0,22].some(px=>Math.abs(x-px)<=2.2))return H;
  return null;
 }
 if(id==='hex-drop'){
  if(r<=10)return H;
  for(let i=0;i<6;i++){const q=i/6*Math.PI*2,px=Math.sin(q)*27,pz=Math.cos(q)*27;if(Math.hypot(x-px,z-pz)<=8.2)return H;}
  if(r>=8&&r<=28.5&&Math.abs(Math.sin(3*a))<.14)return H;
  return null;
 }
 return null;
}
"""
    courses = one(courses, 'export function courseHeight(x,z){\n', height_fn + 'export function courseHeight(x,z){\n', 'death height model')
    courses = one(
        courses,
        "export function courseHeight(x,z){\n if(activeCourse.id==='last-platform'||activeCourse.id==='void-hunt')return survivalWheelHeight(x,z,activeCourse.id);\n",
        "export function courseHeight(x,z){\n if(activeCourse.mode==='death-colosseum')return deathColosseumHeight(x,z,activeCourse.id);\n if(activeCourse.id==='last-platform'||activeCourse.id==='void-hunt')return survivalWheelHeight(x,z,activeCourse.id);\n",
        'height dispatch',
    )
    courses_path.write_text(courses)

    # ------------------------------------------------------------------
    # Render each arena from the same analytical dimensions. The lower arena
    # becomes a glowing kill floor so falling reads as a deliberate rule.
    # ------------------------------------------------------------------
    view_path = target / 'course-view.js'
    view = view_path.read_text()
    death_view = r""" const group=new THREE.Group();
 if(activeCourse.mode==='death-colosseum'){
  const H=9,deck=new THREE.MeshStandardMaterial({color:0x323941,roughness:.82,metalness:.18,side:THREE.DoubleSide}),edge=new THREE.MeshStandardMaterial({color:0xff4b32,emissive:0xa5130b,emissiveIntensity:.72,roughness:.48,metalness:.28,side:THREE.DoubleSide});
  const kill=new THREE.Mesh(new THREE.CylinderGeometry(43,43,.36,96),new THREE.MeshStandardMaterial({color:0x170307,emissive:0x7d0a12,emissiveIntensity:1.35,roughness:.88}));kill.position.y=-.13;kill.receiveShadow=true;group.add(kill);
  const addBox=(x,z,w,d,y=H)=>{const m=new THREE.Mesh(new THREE.BoxGeometry(w,.8,d),deck);m.position.set(x,y-.4,z);m.receiveShadow=true;group.add(m);return m;};
  const addPad=(x,z,r)=>{const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,.8,40),deck);m.position.set(x,H-.4,z);m.receiveShadow=true;group.add(m);const e=new THREE.Mesh(new THREE.RingGeometry(r-.42,r,48),edge);e.rotation.x=-Math.PI/2;e.position.set(x,H+.045,z);group.add(e);};
  const addBridge=(a,mid,len,w)=>{const b=addBox(Math.sin(a)*mid,Math.cos(a)*mid,w,len);b.rotation.y=a;};
  if(activeCourse.id==='death-wheel'){
   addPad(0,0,14);const ring=new THREE.Mesh(new THREE.RingGeometry(27,37,96),deck);ring.rotation.x=-Math.PI/2;ring.position.y=H+.015;ring.receiveShadow=true;group.add(ring);for(const rr of [[26.6,27.05],[36.95,37.4]]){const e=new THREE.Mesh(new THREE.RingGeometry(rr[0],rr[1],96),edge);e.rotation.x=-Math.PI/2;e.position.y=H+.05;group.add(e);}for(let i=0;i<8;i++)addBridge(i/8*Math.PI*2,20.5,13.4,3.6);
  }else if(activeCourse.id==='razor-cross'){
   addBox(0,0,6.6,72);addBox(0,0,72,6.6);for(const [x,z] of [[0,29],[29,0],[0,-29],[-29,0]]){addBox(x,z,16,16);const e=new THREE.Mesh(new THREE.RingGeometry(6.9,8.0,4),edge);e.rotation.x=-Math.PI/2;e.rotation.z=Math.PI/4;e.position.set(x,H+.05,z);group.add(e);}
  }else if(activeCourse.id==='broken-orbit'){
   for(const x of [-19,19]){const r=new THREE.Mesh(new THREE.RingGeometry(8.5,17,72),deck);r.rotation.x=-Math.PI/2;r.position.set(x,H+.015,0);r.receiveShadow=true;group.add(r);for(const rr of [[8.15,8.55],[16.95,17.35]]){const e=new THREE.Mesh(new THREE.RingGeometry(rr[0],rr[1],72),edge);e.rotation.x=-Math.PI/2;e.position.set(x,H+.05,0);group.add(e);}}for(const z of [-13,0,13])addBox(0,z,38,5.2);
  }else if(activeCourse.id==='sky-tiles'){
   for(const x of [-22,0,22])for(const z of [-22,0,22])addBox(x,z,12.4,12.4);for(const z of [-22,0,22])addBox(0,z,56,4.4);for(const x of [-22,0,22])addBox(x,0,4.4,56);
  }else if(activeCourse.id==='hex-drop'){
   addPad(0,0,10);for(let i=0;i<6;i++){const a=i/6*Math.PI*2;addPad(Math.sin(a)*27,Math.cos(a)*27,8.2);addBridge(a,18,18.8,3.4);}
  }
  group.userData.deathColosseum={id:activeCourse.id,deckY:H,fallOnly:true,fallIsWreck:true};return group;
 }
"""
    view = one(view, ' const group=new THREE.Group();\n', death_view, 'death arena renderer')
    view_path.write_text(view)

    # ------------------------------------------------------------------
    # Physics: authored spawn points, no hidden arena wall, no hidden legacy
    # ramp/loop in holes, non-lethal collision damage, fatal fall only.
    # ------------------------------------------------------------------
    physics_path = target / 'physics.js'
    physics = physics_path.read_text()
    old_spawn = """ if(activeCourse?.survival&&gameMode!=='racing'){
  const r=32,shift=activeCourse.id==='void-hunt'?Math.PI/24:0;
  for(let i=0;i<w.cars.length;i++){
   const a=i/w.cars.length*Math.PI*2+shift,c=w.cars[i];
   c.x=Math.sin(a)*r;c.z=Math.cos(a)*r;c.vx=0;c.vz=0;c.omega=0;c.heading=a+Math.PI;
   c.dead=false;c.hp=Math.max(1,c.hp);c.lastContact=-99;c.lastOpponent=-1;
  }
 }
"""
    new_spawn = """ if(activeCourse?.survival&&gameMode!=='racing'){
  if(gameMode==='death-colosseum'&&Array.isArray(activeCourse.spawns)&&activeCourse.spawns.length){
   for(let i=0;i<w.cars.length;i++){const c=w.cars[i],[x,z]=activeCourse.spawns[i%activeCourse.spawns.length];c.x=x;c.z=z;c.vx=0;c.vz=0;c.omega=0;c.heading=Math.atan2(-x,-z);c.dead=false;c.hp=c.maxHP;c.lastContact=-99;c.lastOpponent=-1;}
  }else{
   const r=32,shift=activeCourse.id==='void-hunt'?Math.PI/24:0;
   for(let i=0;i<w.cars.length;i++){
    const a=i/w.cars.length*Math.PI*2+shift,c=w.cars[i];
    c.x=Math.sin(a)*r;c.z=Math.cos(a)*r;c.vx=0;c.vz=0;c.omega=0;c.heading=a+Math.PI;
    c.dead=false;c.hp=Math.max(1,c.hp);c.lastContact=-99;c.lastOpponent=-1;
   }
  }
 }
"""
    physics = one(physics, old_spawn, new_spawn, 'safe death spawns')
    physics = one(physics, ' c.hp=Math.max(0,c.hp-d);', " c.hp=w.mode==='death-colosseum'&&!c.fallFatal?Math.max(1,c.hp-d):Math.max(0,c.hp-d);", 'fall-only HP clamp')
    physics = one(physics, "\n const dist=Math.hypot(c.x,c.z),limit=RADIUS-2.45", "\n if(activeCourse?.survival)return;\n const dist=Math.hypot(c.x,c.z),limit=RADIUS-2.45", 'legacy survival boundary removal')
    physics = one(physics, " for(const c of w.cars){\n  if(!c.dead&&w.time-c.lastContact>22){", " if(w.mode!=='death-colosseum')for(const c of w.cars){\n  if(!c.dead&&w.time-c.lastContact>22){", 'disable no-contact death')
    physics_path.write_text(physics)

    p3_path = target / 'physics3d.js'
    p3 = p3_path.read_text()
    old_surface = """  const floor=floorSurface(x,z),surfaces=[floor];
  const ramp=courseSurface(x,z)?null:rampSurface(x,z); if (ramp) surfaces.push(ramp);
  const loop=courseSurface(x,z)?null:loopSurface(x,y,z); if (loop && loop.radialError<2.3) surfaces.push(loop);
"""
    new_surface = """  const floor=floorSurface(x,z),surfaces=[floor],custom=courseSurface(x,z);
  const ramp=(activeCourse?.survival||custom)?null:rampSurface(x,z); if (ramp) surfaces.push(ramp);
  const loop=(activeCourse?.survival||custom)?null:loopSurface(x,y,z); if (loop && loop.radialError<2.3) surfaces.push(loop);
"""
    p3 = one(p3, old_surface, new_surface, 'remove hidden stunt surfaces')
    old_fall = """ ctx.hit(w,c,Math.max(999,c.hp+999),0,1,wrecker&&!wrecker.dead?wrecker:undefined);
 if(c.dead)w.events.push({type:'fall',car:c.id,by:wrecker?.id??-1,x:b.px,y:b.py,z:b.pz,power:55});
"""
    new_fall = """ c.fallFatal=true;
 ctx.hit(w,c,Math.max(999,c.hp+999),0,1,wrecker&&!wrecker.dead?wrecker:undefined);
 c.fallFatal=false;
 if(c.dead)w.events.push({type:'fall',car:c.id,by:wrecker?.id??-1,x:b.px,y:b.py,z:b.pz,power:55});
"""
    p3 = one(p3, old_fall, new_fall, 'fatal fall override')
    p3 = one(p3, "  for (const c of w.cars) if (!c.dead&&w.time-c.lastContact>22) {", "  if(w.mode!=='death-colosseum')for (const c of w.cars) if (!c.dead&&w.time-c.lastContact>22) {", 'full 3D no-contact disable')
    p3_path.write_text(p3)

    # ------------------------------------------------------------------
    # Menu/UI: fourth core mode, compact 2x2 mode grid, mode-specific copy and
    # results. Course picker already filters by activeCourse.mode automatically.
    # ------------------------------------------------------------------
    index_path = target / 'index.html'
    html = index_path.read_text()
    html = one(
        html,
        '<button data-mode="colosseum" class="selected" aria-pressed="true"><b>COLOSSEUM</b><small>生き残りバトル</small></button><button data-mode="racing"',
        '<button data-mode="colosseum" class="selected" aria-pressed="true"><b>COLOSSEUM</b><small>生き残りバトル</small></button><button data-mode="death-colosseum" aria-pressed="false"><b>DEATH COLOSSEUM</b><small>落下だけが即死</small></button><button data-mode="racing"',
        'mode button',
    )
    html = html.replace('<title>BREAK CARS — Wreck Hunt, Wrecking Racing & Colosseum</title>', '<title>BREAK CARS — Death Colosseum, Wreck Hunt, Wrecking Racing & Colosseum</title>', 1)
    index_path.write_text(html)

    game_path = target / 'game.js'
    game = game_path.read_text()
    select_mode = r"""function selectMode(next){if(mode!=='menu')return;if(next!==activeCourse.mode){const first=COURSES.find(c=>c.mode===next);if(first)location.search='?course='+first.id;return;}gameMode=next;document.body.dataset.gameMode=next;document.querySelectorAll('[data-mode]').forEach(b=>{const active=b.dataset.mode===next;b.classList.toggle('selected',active);b.setAttribute('aria-pressed',String(active));});const racing=next==='racing',hunt=next==='wreck-hunt',death=next==='death-colosseum';$('mode-tag').textContent=racing?'RAMPAGE 3D / WRECKING RACING':hunt?'COLOSSEUM / WRECK HUNT':death?'DEATH COLOSSEUM / FALL = WRECK':'COLOSSEUM / SURVIVAL';$('mode-subtitle').textContent=racing?'2 LAPS. FULL CONTACT 3D.':hunt?'60 SECONDS. ENDLESS WRECKS.':death?'12 CARS. NO SAFE FLOOR. ONE SURVIVOR.':'12 CARS. ONE SURVIVOR.';$('mode-lead').textContent=racing?'飛べ。傾け。交差で潰せ。ループを抜けろ。':hunt?'壊し続けろ。CHAINを切らすな。':death?'押し落とせ。落ちたら終わり。':'ぶつけろ。壊せ。生き残れ。';$('mode-hint').innerHTML=racing?'2周 ／ 高低差・ジャンプ・バンク・立体交差・垂直ループ<br>衝突点＋1周400点 ／ 側面スピン +250 ／ 撃破 +500 ／ 完走順位ボーナス':hunt?'60秒スコアアタック ／ 撃破 +500<br>9秒以内の連続WRECKでCHAINボーナス ／ 敵は再投入されます':death?'ダメージだけでは脱落しない ／ コースから落下した瞬間に一撃WRECK<br>押し出しWRECK +500 ／ 最後の1台まで生き残れ':'横・後ろを狙え。正面はエンジンが弱点。<br>左でハンドル ／ 右でアクセルとブレーキ';$('arena-caption').innerHTML=racing?'RAMPAGE 3D<span>JUMP / BANK / CROSS / VERTICAL LOOP</span>':hunt?'THE COLOSSEUM<span>WRECK HUNT / SCORE ATTACK</span>':death?'DEATH COLOSSEUM<span>FALL = INSTANT WRECK</span>':'THE COLOSSEUM<span>LAST CAR STANDING</span>';$('start').innerHTML=racing?'レースに参戦 <span>↗</span>':hunt?'WRECK HUNT開始 <span>↗</span>':death?'DEATH MATCH開始 <span>↗</span>':'アリーナに参戦 <span>↗</span>';resetWorld();}"""
    game = regex_one(game, r"function selectMode\(next\)\{[^\n]+\}", select_mode, 'selectMode rewrite')
    game = one(game, "raceTrack.visible=gameMode==='racing';", "raceTrack.visible=gameMode==='racing';fullPhysicsCourse.visible=gameMode!=='death-colosseum';", 'hide legacy stunt geometry')
    game = one(game, "if($('score-label'))$('score-label').textContent=gameMode==='wreck-hunt'?'HUNT SCORE':'IMPACT SCORE';", "if($('score-label'))$('score-label').textContent=gameMode==='wreck-hunt'?'HUNT SCORE':gameMode==='death-colosseum'?'RING OUT SCORE':'IMPACT SCORE';", 'death HUD score label')
    game = one(game, "$('mode-tag').textContent=activeCourse.name+' / '+activeCourse.mode.toUpperCase();$('arena-caption').textContent=activeCourse.name;", "$('mode-tag').textContent=activeCourse.mode==='death-colosseum'?activeCourse.name+' / DEATH COLOSSEUM':activeCourse.name+' / '+activeCourse.mode.toUpperCase();$('arena-caption').innerHTML=activeCourse.mode==='death-colosseum'?`${activeCourse.name}<span>FALL = INSTANT WRECK</span>`:activeCourse.name;", 'active death course identity')
    game = one(game, "else toast(world.mode==='racing'?`${activeCourse.name} — GO`:world.mode==='wreck-hunt'?'HUNT START — WRECK TARGETS':'側面を狙え。生き残れ。',2);", "else toast(world.mode==='racing'?`${activeCourse.name} — GO`:world.mode==='wreck-hunt'?'HUNT START — WRECK TARGETS':world.mode==='death-colosseum'?'FALL = WRECK — 押し落とせ':'側面を狙え。生き残れ。',2);", 'death opening cue')
    game = one(game, "$('result-kicker').textContent=place===1&&!p.dead?'COLOSSEUM CHAMPION':p.dead?'WRECKED':'TIME UP';", "$('result-kicker').textContent=place===1&&!p.dead?(world.mode==='death-colosseum'?'DEATH COLOSSEUM CHAMPION':'COLOSSEUM CHAMPION'):p.dead?(world.mode==='death-colosseum'?'FALLEN / WRECKED':'WRECKED'):'TIME UP';", 'death result kicker')
    game = one(game, "$('result-detail').textContent=p.dead?'マシンは大破。次は側面を狙って反撃しよう。':world.time>=(world.stageLimit||DURATION)?'タイムアップ。生存車の衝突スコアで順位を決定。':'アリーナを制圧。最後まで走り切った。';", "$('result-detail').textContent=world.mode==='death-colosseum'?(p.dead?'コースアウト。落下は即WRECK。次は相手を先に押し落とせ。':world.time>=(world.stageLimit||DURATION)?'タイムアップ。生存車を優先し、押し出しと衝突スコアで決着。':'最後の1台。DEATH COLOSSEUMを生き残った。'):(p.dead?'マシンは大破。次は側面を狙って反撃しよう。':world.time>=(world.stageLimit||DURATION)?'タイムアップ。生存車の衝突スコアで順位を決定。':'アリーナを制圧。最後まで走り切った。');", 'death result detail')
    game_path.write_text(game)

    css_path = target / 'courses.css'
    css = css_path.read_text()
    css += r'''

/* DEATH COLOSSEUM v1 — four core modes stay thumb-readable on iPhone landscape. */
body:not(.mayhem-tour) .mode-select{grid-template-columns:repeat(2,minmax(0,1fr))!important}
body:not(.mayhem-tour) #mayhem-tour-entry{grid-column:1/-1;min-height:34px;padding:6px 10px!important;display:flex;align-items:center;justify-content:space-between;gap:10px}
body:not(.mayhem-tour) #mayhem-tour-entry small{margin-top:0!important;text-align:right}
.mode-select button[data-mode="death-colosseum"].selected{border-color:#ff443e!important;background:#7d101b42!important;color:#ff9b86!important;box-shadow:inset 0 0 0 1px #ff443e55,0 0 18px #ff221f25}
body[data-game-mode="death-colosseum"] .course-hint{color:#ffd2c8;border-left:3px solid #ff493f;padding-left:8px}
@media(orientation:landscape) and (max-height:430px){body:not(.mayhem-tour) .mode-select{gap:4px!important;margin:5px 0 5px!important}body:not(.mayhem-tour) .mode-select button{padding:5px 7px!important;min-height:32px}body:not(.mayhem-tour) #mayhem-tour-entry{min-height:29px!important;padding:4px 8px!important}.course-hint{line-height:1.25!important}}
'''
    css_path.write_text(css)


if __name__ == '__main__':
    apply_death_colosseum_v1(Path('_site'))
