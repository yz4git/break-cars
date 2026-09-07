"""Apply the Wreck Hunt mode to the deploy copy without duplicating the large game runtime."""
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Wreck Hunt patch {label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


def patch_game(path: Path) -> None:
    text = path.read_text()

    text = replace_once(
        text,
        "arena.visible=gameMode==='colosseum';raceTrack.visible=gameMode==='racing';",
        "arena.visible=gameMode!=='racing';raceTrack.visible=gameMode==='racing';",
        "arena visibility",
    )

    text = replace_once(text, "const racing=next==='racing';", "const racing=next==='racing',hunt=next==='wreck-hunt';", "mode flags")
    text = replace_once(text, "$('mode-tag').textContent=racing?'IRON LOOP / WRECKING RACING':'COLOSSEUM / SURVIVAL';", "$('mode-tag').textContent=racing?'IRON LOOP / WRECKING RACING':hunt?'COLOSSEUM / WRECK HUNT':'COLOSSEUM / SURVIVAL';", "mode tag")
    text = replace_once(text, "$('mode-subtitle').textContent=racing?'4 LAPS. FULL CONTACT.':'12 CARS. ONE SURVIVOR.';", "$('mode-subtitle').textContent=racing?'4 LAPS. FULL CONTACT.':hunt?'150 SECONDS. ENDLESS WRECKS.':'12 CARS. ONE SURVIVOR.';", "mode subtitle")
    text = replace_once(text, "$('mode-lead').textContent=racing?'追い抜け。ぶつけろ。勝ち取れ。':'ぶつけろ。壊せ。生き残れ。';", "$('mode-lead').textContent=racing?'追い抜け。ぶつけろ。勝ち取れ。':hunt?'壊し続けろ。CHAINを切らすな。':'ぶつけろ。壊せ。生き残れ。';", "mode lead")
    text = replace_once(
        text,
        "$('mode-hint').innerHTML=racing?'4周 ／ 衝突点＋1周400点＋完走順位ボーナス<br>側面スピン +200 ／ 撃破 +500 ／ 逆走は周回に加算されません':'横・後ろを狙え。正面はエンジンが弱点。<br>左でハンドル ／ 右でアクセルとブレーキ';",
        "$('mode-hint').innerHTML=racing?'4周 ／ 衝突点＋1周400点＋完走順位ボーナス<br>側面スピン +200 ／ 撃破 +500 ／ 逆走は周回に加算されません':hunt?'150秒スコアアタック ／ 撃破 +500<br>7秒以内の連続WRECKでCHAINボーナス ／ 敵は再投入されます':'横・後ろを狙え。正面はエンジンが弱点。<br>左でハンドル ／ 右でアクセルとブレーキ';",
        "mode hint",
    )
    text = replace_once(text, "$('arena-caption').innerHTML=racing?'IRON LOOP<span>WRECKING RACING / 4 LAPS</span>':'THE COLOSSEUM<span>LAST CAR STANDING</span>';", "$('arena-caption').innerHTML=racing?'IRON LOOP<span>WRECKING RACING / 4 LAPS</span>':hunt?'THE COLOSSEUM<span>WRECK HUNT / SCORE ATTACK</span>':'THE COLOSSEUM<span>LAST CAR STANDING</span>';", "arena caption")
    text = replace_once(text, "$('start').innerHTML=racing?'レースに参戦 <span>↗</span>':'アリーナに参戦 <span>↗</span>';", "$('start').innerHTML=racing?'レースに参戦 <span>↗</span>':hunt?'WRECK HUNT開始 <span>↗</span>':'アリーナに参戦 <span>↗</span>';", "start label")

    text = replace_once(
        text,
        "scene.add(g);return{g,body,parts,wheels,number,wreckMarker,wrecked:false,fx:{lift:0,vy:0,roll:0,pitch:0,yaw:0,rollV:0,pitchV:0,yawV:0,wreckSide:c.id%2?1:-1,wreckTilt:0,wreckPitch:0}};}\nlet world=makeWorld()",
        "scene.add(g);return{g,body,parts,wheels,number,wreckMarker,wrecked:false,fx:{lift:0,vy:0,roll:0,pitch:0,yaw:0,rollV:0,pitchV:0,yawV:0,wreckSide:c.id%2?1:-1,wreckTilt:0,wreckPitch:0}};}\nfunction rebuildCarVisual(id){const old=carMeshes[id];if(old){scene.remove(old.g);old.number.material.map.dispose();old.number.material.dispose();old.number.geometry.dispose();}carMeshes[id]=buildCar(world.cars[id]);}\nlet world=makeWorld()",
        "respawn visual helper",
    )

    text = replace_once(
        text,
        "$('race-info').classList.toggle('hidden',gameMode!=='racing');$('recover').classList.toggle('hidden',gameMode!=='racing');$('position-label').textContent=gameMode==='racing'?'RACE POSITION':'SURVIVORS';",
        "$('race-info').classList.toggle('hidden',gameMode!=='racing');$('hunt-info').classList.toggle('hidden',gameMode!=='wreck-hunt');$('recover').classList.toggle('hidden',gameMode!=='racing');$('position-label').textContent=gameMode==='racing'?'RACE POSITION':gameMode==='wreck-hunt'?'WRECKS':'SURVIVORS';",
        "start HUD",
    )

    text = replace_once(
        text,
        "$('result-detail').textContent=world.mode==='racing'?'4周。衝突点＋1周400点＋完走順位ボーナスで総合順位を決定。1位3500点、2位2900点、3位2400点。側面スピンは200点、撃破は500点。先頭ゴール後22秒で終了。':'側面を狙い、正面のエンジンを守ろう。22秒間接触がないと耐久力が減り始めます。';",
        "$('result-detail').textContent=world.mode==='racing'?'4周。衝突点＋1周400点＋完走順位ボーナスで総合順位を決定。1位3500点、2位2900点、3位2400点。側面スピンは200点、撃破は500点。先頭ゴール後22秒で終了。':world.mode==='wreck-hunt'?'150秒で何台壊せるか。7秒以内に次を撃破するとCHAINが上がり、追加ボーナスを獲得。敵は外周から再投入されます。':'側面を狙い、正面のエンジンを守ろう。22秒間接触がないと耐久力が減り始めます。';",
        "pause help",
    )

    text = replace_once(text, "if(world.mode==='racing'){finishRacing();return;}", "if(world.mode==='racing'){finishRacing();return;}if(world.mode==='wreck-hunt'){finishHunt();return;}", "finish dispatch")

    finish_hunt = """function finishHunt(){const p=world.cars[0],h=world.hunt||{wrecks:p.kills,bestCombo:0,bonusScore:0};let best=0;try{best=Number(localStorage.getItem('break-cars-hunt-best')||0);if(p.score>best)localStorage.setItem('break-cars-hunt-best',String(p.score));}catch{}$('result-kicker').textContent=p.dead?'HUNTER WRECKED':'WRECK HUNT / TIME UP';$('result-title').textContent=`${h.wrecks} WRECKS`;$('result-detail').textContent=p.dead?'ハンター大破。それでも撃破スコアは記録される。':`150秒終了。BEST CHAIN ×${Math.max(1,h.bestCombo)} ／ CHAIN BONUS ${h.bonusScore.toLocaleString()}`;$('result-stats').innerHTML=`<div><b>${p.score.toLocaleString()}</b><small>HUNT SCORE</small></div><div><b>${h.wrecks}</b><small>WRECKS</small></div><div><b>${Math.max(best,p.score).toLocaleString()}</b><small>BEST</small></div>`;$('race-results').classList.add('hidden');$('resume').classList.add('hidden');$('modal').classList.remove('hidden');}\n"""
    text = replace_once(text, "function finishRacing(){", finish_hunt + "function finishRacing(){", "hunt result")

    text = replace_once(
        text,
        "function events(){const player=world.cars[0];for(const e of world.events){",
        "function events(){const player=world.cars[0];for(const e of world.events){if(e.type==='respawn'){rebuildCarVisual(e.car);if(toastTime<.25)toast(`NEW TARGET — CAR ${String(e.car+1).padStart(2,'0')}`,1.1);continue;}",
        "respawn events",
    )
    text = replace_once(
        text,
        "if(e.by===0)toast('WRECK +500',2.2);else if(e.car!==0&&toastTime<.2)toast(`CAR ${String(e.car+1).padStart(2,'0')} DESTROYED`,1.6);",
        "if(e.by===0){if(world.mode==='wreck-hunt'){const chain=world.hunt?.combo||1,bonus=Math.max(0,(chain-1)*200);toast(`WRECK ×${chain}  +${500+bonus}`,2.2);}else toast('WRECK +500',2.2);}else if(e.car!==0&&toastTime<.2)toast(`CAR ${String(e.car+1).padStart(2,'0')} DESTROYED`,1.6);",
        "wreck toast",
    )

    text = replace_once(
        text,
        "$('alive').innerHTML=`${world.mode==='racing'?trackPosition(world).findIndex(c=>c.id===0)+1:world.cars.filter(c=>!c.dead).length}<span>/${COUNT}</span>`;",
        "$('alive').innerHTML=world.mode==='wreck-hunt'?`${p.kills}<span> WRECKS</span>`:`${world.mode==='racing'?trackPosition(world).findIndex(c=>c.id===0)+1:world.cars.filter(c=>!c.dead).length}<span>/${COUNT}</span>`;",
        "hunt HUD wreck count",
    )
    text = replace_once(
        text,
        "const remain=Math.max(0,Math.ceil((world.mode==='racing'?world.endAt:DURATION)-world.time));",
        "const remain=Math.max(0,Math.ceil((world.mode==='racing'?world.endAt:(world.limit||DURATION))-world.time));",
        "hunt timer",
    )
    text = replace_once(
        text,
        "$('recover').disabled=p.dead||p.finished||world.time-p.recoveryAt<5;}drawRadar();",
        "$('recover').disabled=p.dead||p.finished||world.time-p.recoveryAt<5;}if(world.mode==='wreck-hunt'){const h=world.hunt,left=Math.max(0,7-(world.time-h.lastWreckAt)),active=h.combo>0&&left>0;$('hunt-combo').textContent=active?`CHAIN ×${h.combo}`:'CHAIN READY';$('hunt-wrecks').textContent=`${h.wrecks} WRECKS · ${p.score.toLocaleString()} PTS`;$('hunt-state').textContent=active?`${left.toFixed(1)}秒以内に次を壊せ`:'次のWRECKからCHAIN開始';$('hunt-info').classList.toggle('hot',active&&h.combo>=3);}drawRadar();",
        "hunt live HUD",
    )

    text = replace_once(
        text,
        "toast(world.mode==='racing'?'4周！ 追い抜け、ぶつけろ。':'側面を狙え。生き残れ。',2);",
        "toast(world.mode==='racing'?'4周！ 追い抜け、ぶつけろ。':world.mode==='wreck-hunt'?'150秒！ 壊し続けろ。CHAINを切らすな。':'側面を狙え。生き残れ。',2);",
        "hunt opening toast",
    )
    text = replace_once(
        text,
        "if(world.mode!=='racing'&&world.time-world.cars[0].lastContact>17&&toastTime<=0)",
        "if(world.mode==='colosseum'&&world.time-world.cars[0].lastContact>17&&toastTime<=0)",
        "no-contact warning scope",
    )

    path.write_text(text)


def patch_physics(path: Path) -> None:
    text = path.read_text()

    text = replace_once(
        text,
        " const w={cars,time:0,events:[],pairs:new Map(),rand,done:false,mode:gameMode,limit:DURATION};\n return gameMode==='racing'?setupRace(w):w;",
        " const w={cars,time:0,events:[],pairs:new Map(),rand,done:false,mode:gameMode,limit:DURATION};\n if(gameMode==='wreck-hunt'){w.limit=150;w.hunt={combo:0,bestCombo:0,lastWreckAt:-99,wrecks:0,respawns:0,bonusScore:0};const p=cars[0];p.maxHP=Math.round(p.maxHP*1.18);p.hp=p.maxHP;for(const c of cars.slice(1)){c.maxHP=Math.max(58,Math.round(c.maxHP*.68));c.hp=c.maxHP;c.respawnAt=Infinity;}}\n return gameMode==='racing'?setupRace(w):w;",
        "hunt world setup",
    )

    text = replace_once(
        text,
        "  if(other&&!other.dead){other.kills++;other.score+=500;}\n  w.events.push({type:'wreck',car:c.id,by:other?.id??-1,x:c.x,z:c.z,power:40});",
        "  if(other&&!other.dead){other.kills++;other.score+=500;if(w.mode==='wreck-hunt'&&other.id===0&&c.id!==0){const h=w.hunt;h.combo=w.time-h.lastWreckAt<=7?Math.min(8,h.combo+1):1;h.lastWreckAt=w.time;h.wrecks++;h.bestCombo=Math.max(h.bestCombo,h.combo);const bonus=(h.combo-1)*200;other.score+=bonus;h.bonusScore+=bonus;}}\n  if(w.mode==='wreck-hunt'&&c.id!==0)c.respawnAt=w.time+2.6+w.rand()*.9;\n  w.events.push({type:'wreck',car:c.id,by:other?.id??-1,x:c.x,z:c.z,power:40});",
        "hunt kill scoring",
    )

    text = text.replace("player&&w.mode==='colosseum'?17:12", "player&&w.mode!=='racing'?17:12")
    text = text.replace("player&&w.mode==='colosseum'?15:12.5", "player&&w.mode!=='racing'?15:12.5")
    text = text.replace("player&&w.mode==='colosseum'?1+clamp", "player&&w.mode!=='racing'?1+clamp")

    respawn_fn = """function respawnHuntCar(w,c){
 const player=w.cars[0];let a=w.rand()*Math.PI*2,r=31;
 for(let tries=0;tries<12;tries++){a=w.rand()*Math.PI*2;r=30+w.rand()*5;const x=Math.sin(a)*r,z=Math.cos(a)*r;if(Math.hypot(x-player.x,z-player.z)<10)continue;let clear=true;for(const o of w.cars){if(o===c||o.dead)continue;if(Math.hypot(x-o.x,z-o.z)<6){clear=false;break;}}if(clear)break;}
 Object.assign(c,{x:Math.sin(a)*r,z:Math.cos(a)*r,heading:a+Math.PI,vx:0,vz:0,omega:0,hp:c.maxHP,parts:{front:100,rear:100,left:100,right:100},dead:false,target:-1,aiTimer:.15+w.rand()*.25,reverse:0,stuck:0,lastContact:w.time,hitAt:-10,wreckAt:0,throttle:0,steer:0,respawnAt:Infinity});
 w.hunt.respawns++;w.events.push({type:'respawn',car:c.id,x:c.x,z:c.z});
}

"""
    text = replace_once(text, "export function step(w,input,dt=1/60,autoplay=false){", respawn_fn + "export function step(w,input,dt=1/60,autoplay=false){", "respawn helper")

    text = replace_once(
        text,
        " if(w.mode==='racing'){\n  for(const c of w.cars)advanceRace(w,c,dt);\n  if(w.time>=w.endAt||w.cars.every(c=>c.dead||c.finished))w.done=true;\n  return;\n }\n for(const c of w.cars){",
        " if(w.mode==='racing'){\n  for(const c of w.cars)advanceRace(w,c,dt);\n  if(w.time>=w.endAt||w.cars.every(c=>c.dead||c.finished))w.done=true;\n  return;\n }\n if(w.mode==='wreck-hunt'){const h=w.hunt,p=w.cars[0];if(h.combo&&w.time-h.lastWreckAt>7)h.combo=0;for(const c of w.cars.slice(1))if(c.dead&&c.respawnAt<=w.time)respawnHuntCar(w,c);p.lastContact=w.time;if(p.dead||w.time>=w.limit)w.done=true;return;}\n for(const c of w.cars){",
        "hunt step",
    )

    path.write_text(text)


def apply_wreck_hunt(target: Path) -> None:
    patch_game(target / 'game.js')
    patch_physics(target / 'physics.js')


if __name__ == '__main__':
    apply_wreck_hunt(Path('_site'))
