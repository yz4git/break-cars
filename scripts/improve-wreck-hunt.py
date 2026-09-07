"""Polish Wreck Hunt after the base deploy-time integration is applied."""
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Wreck Hunt polish {label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


def patch_physics(path: Path) -> None:
    text = path.read_text()

    # Wreck Hunt should create player-owned wrecks quickly. Targets are softer,
    # hunter impacts are amplified, and AI-vs-AI impacts stay dramatic without
    # stealing most of the available kills.
    text = replace_once(
        text,
        "c.maxHP=Math.max(58,Math.round(c.maxHP*.68));",
        "c.maxHP=Math.max(46,Math.round(c.maxHP*.48));",
        "target durability",
    )
    text = replace_once(
        text,
        "const d=damage*protection*playerArmor;",
        "let huntDamage=1;if(w.mode==='wreck-hunt'&&c.id!==0&&other)huntDamage=other.id===0?1.55:.52;const d=damage*protection*playerArmor*huntDamage;",
        "hunter damage boost",
    )
    text = replace_once(
        text,
        "c.respawnAt=w.time+2.6+w.rand()*.9;",
        "c.respawnAt=w.time+1.55+w.rand()*.55;",
        "respawn cadence",
    )

    # Bring the opening fight inward so the first useful contact happens fast.
    text = replace_once(
        text,
        "c.hp=c.maxHP;c.respawnAt=Infinity;}}",
        "c.hp=c.maxHP;c.respawnAt=Infinity;}p.x=0;p.z=10;p.heading=Math.PI;for(const c of cars.slice(1)){const a=(c.id-.4)/(COUNT-1)*Math.PI*2,r=20+(c.id%3)*2.4;c.x=Math.sin(a)*r;c.z=Math.cos(a)*r;c.heading=Math.atan2(p.x-c.x,p.z-c.z);}}",
        "opening formation",
    )

    # In Hunt, opponents should feed the combat lane instead of mostly avoiding
    # the player. They still collide with each other, but prefer the hunter as a
    # target often enough to keep the arena active.
    text = replace_once(
        text,
        "const bias=(o.id===0?1.08:1)*(1+w.rand()*.35);",
        "const bias=(o.id===0?(w.mode==='wreck-hunt'?.52:1.08):1)*(1+w.rand()*(w.mode==='wreck-hunt'?.22:.35));",
        "hunt player target bias",
    )

    # Respawn closer to the active fight and already moving toward the center.
    text = replace_once(
        text,
        "const player=w.cars[0];let a=w.rand()*Math.PI*2,r=31;",
        "const player=w.cars[0];let a=w.rand()*Math.PI*2,r=25;",
        "respawn initial radius",
    )
    text = replace_once(
        text,
        "r=30+w.rand()*5;",
        "r=22+w.rand()*7;",
        "respawn radius",
    )
    text = replace_once(
        text,
        "heading:a+Math.PI,vx:0,vz:0,omega:0",
        "heading:a+Math.PI,vx:-Math.sin(a)*4,vz:-Math.cos(a)*4,omega:0",
        "respawn launch velocity",
    )

    # Extra arena-edge recovery only for the score-attack mode. This keeps a
    # failed pass from turning into several dead seconds against the wall.
    text = replace_once(
        text,
        "const wallSteerBoost=player&&w.mode!=='racing'?1+clamp((Math.hypot(c.x,c.z)-(RADIUS-10))/7,0,.42):1;",
        "const wallSteerBoost=player&&w.mode!=='racing'?1+clamp((Math.hypot(c.x,c.z)-(RADIUS-10))/7,0,.42)*(w.mode==='wreck-hunt'?1.8:1):1;",
        "hunt wall steering",
    )
    text = replace_once(
        text,
        "const reversePower=player&&w.mode!=='racing'?17:12;",
        "const reversePower=player&&w.mode==='wreck-hunt'?21:player&&w.mode!=='racing'?17:12;",
        "hunt reverse power",
    )
    text = replace_once(
        text,
        "const assist=(1.8+edge*5.2)*(speed<6?1.35:1);",
        "const assist=(w.mode==='wreck-hunt'?4.6+edge*9.8:1.8+edge*5.2)*(speed<6?(w.mode==='wreck-hunt'?1.9:1.35):1);",
        "hunt inward assist",
    )
    text = replace_once(
        text,
        "if(player){const rebound=1.8+Math.min(v,14)*.16;c.vx-=nx*rebound;c.vz-=nz*rebound;}",
        "if(player){const rebound=(w.mode==='wreck-hunt'?3.4:1.8)+Math.min(v,14)*(w.mode==='wreck-hunt'?.24:.16);c.vx-=nx*rebound;c.vz-=nz*rebound;}",
        "hunt wall rebound",
    )

    path.write_text(text)


def patch_game(path: Path) -> None:
    text = path.read_text()

    text = replace_once(
        text,
        "gameMode=next;document.querySelectorAll('[data-mode]')",
        "gameMode=next;document.body.dataset.gameMode=next;document.querySelectorAll('[data-mode]')",
        "mode body marker",
    )

    target_material = """const targetCanvas=document.createElement('canvas');targetCanvas.width=targetCanvas.height=256;const tctx=targetCanvas.getContext('2d');tctx.strokeStyle='#ffc45d';tctx.lineWidth=12;tctx.beginPath();tctx.arc(128,106,62,-Math.PI*.88,Math.PI*.88);tctx.stroke();tctx.fillStyle='#ff6a38';tctx.beginPath();tctx.moveTo(128,18);tctx.lineTo(110,50);tctx.lineTo(146,50);tctx.closePath();tctx.fill();tctx.font='900 34px Arial';tctx.textAlign='center';tctx.fillStyle='#fff4cc';tctx.fillText('TARGET',128,221);const targetTex=new THREE.CanvasTexture(targetCanvas);targetTex.colorSpace=THREE.SRGBColorSpace;const targetSpriteMat=new THREE.SpriteMaterial({map:targetTex,transparent:true,depthTest:false,depthWrite:false});"""
    text = replace_once(
        text,
        "const wreckSpriteMat=new THREE.SpriteMaterial({map:wreckTex,transparent:true,depthTest:false,depthWrite:false});",
        "const wreckSpriteMat=new THREE.SpriteMaterial({map:wreckTex,transparent:true,depthTest:false,depthWrite:false});" + target_material,
        "target material",
    )
    text = replace_once(
        text,
        "const wreckMarker=new THREE.Sprite(wreckSpriteMat);wreckMarker.position.set(0,3.7,0);wreckMarker.scale.set(3.35,3.35,1);wreckMarker.visible=false;g.add(wreckMarker);",
        "const wreckMarker=new THREE.Sprite(wreckSpriteMat);wreckMarker.position.set(0,3.7,0);wreckMarker.scale.set(3.35,3.35,1);wreckMarker.visible=false;g.add(wreckMarker);const targetMarker=new THREE.Sprite(targetSpriteMat);targetMarker.position.set(0,3.55,0);targetMarker.scale.set(2.35,2.35,1);targetMarker.visible=false;g.add(targetMarker);",
        "target marker",
    )
    text = replace_once(
        text,
        "scene.add(g);return{g,body,parts,wheels,number,wreckMarker,wrecked:false",
        "scene.add(g);return{g,body,parts,wheels,number,wreckMarker,targetMarker,wrecked:false",
        "target marker return",
    )

    # Always nominate one reachable target. As targets become weak, all
    # finishable cars also receive markers so chaining has an obvious route.
    text = replace_once(
        text,
        "function visuals(dt){const player=world.cars[0],spectating=",
        "function visuals(dt){const player=world.cars[0],huntPriority=world.mode==='wreck-hunt'?[...world.cars].filter(c=>c.id!==0&&!c.dead).sort((a,b)=>(a.hp/a.maxHP)*18+Math.hypot(a.x-player.x,a.z-player.z)*.14-(b.hp/b.maxHP)*18-Math.hypot(b.x-player.x,b.z-player.z)*.14)[0]?.id:-1,spectating=",
        "hunt priority target",
    )
    text = replace_once(
        text,
        "m.wreckMarker.visible=c.dead;m.body.rotation.z=",
        "m.wreckMarker.visible=c.dead;const huntTarget=world.mode==='wreck-hunt'&&c.id!==0&&!c.dead&&(c.id===huntPriority||c.hp/c.maxHP<=.45);m.targetMarker.visible=huntTarget;if(huntTarget){m.targetMarker.position.y=3.5+Math.sin(world.time*8+c.id)*.18;const pulse=(c.id===huntPriority?2.35:2.15)+Math.sin(world.time*10+c.id)*.12;m.targetMarker.scale.set(pulse,pulse,1);}m.body.rotation.z=",
        "target visibility",
    )

    # The regular HUD owns WRECKS and SCORE. Center-top is only CHAIN state.
    text = replace_once(text, "`${p.kills}<span> WRECKS</span>`", "`${p.kills}`", "duplicate wreck label")
    text = replace_once(
        text,
        "$('hunt-combo').textContent=active?`CHAIN ×${h.combo}`:'CHAIN READY';$('hunt-wrecks').textContent=`${h.wrecks} WRECKS · ${p.score.toLocaleString()} PTS`;$('hunt-state').textContent=active?`${left.toFixed(1)}秒以内に次を壊せ`:'次のWRECKからCHAIN開始';$('hunt-info').classList.toggle('hot',active&&h.combo>=3);",
        "$('hunt-combo').textContent=active?`CHAIN ×${h.combo}`:'CHAIN';$('hunt-wrecks').textContent='';$('hunt-state').textContent=active?`${left.toFixed(1)}s`:'READY';$('hunt-info').classList.toggle('active',active);$('hunt-info').classList.toggle('hot',active&&h.combo>=3);",
        "chain HUD",
    )

    # Compact arcade-language opening message leaves the actual fight visible.
    text = replace_once(
        text,
        "world.mode==='wreck-hunt'?'150秒！ 壊し続けろ。CHAINを切らすな。'",
        "world.mode==='wreck-hunt'?'HUNT START — WRECK TARGETS'",
        "hunt opening toast",
    )

    # Re-entry feels like a launched replacement target, not a silent reset.
    text = replace_once(
        text,
        "if(e.type==='respawn'){rebuildCarVisual(e.car);if(toastTime<.25)toast(`NEW TARGET — CAR ${String(e.car+1).padStart(2,'0')}`,1.1);continue;}",
        "if(e.type==='respawn'){rebuildCarVisual(e.car);blast(e.x,e.z,22);for(let i=0;i<20;i++)emit(e.x,.7,e.z,12,'spark');for(let i=0;i<8;i++)emit(e.x,.9,e.z,8,'flame');for(let i=0;i<7;i++)emit(e.x,1.0,e.z,4,'smoke');if(Math.hypot(e.x-player.x,e.z-player.z)<28)shake=Math.max(shake,.45);sound(660,true);if(toastTime<.25)toast(`NEW TARGET — CAR ${String(e.car+1).padStart(2,'0')}`,1.0);continue;}",
        "respawn presentation",
    )

    # Weak targets remain highlighted on the radar as secondary finishers.
    text = replace_once(
        text,
        "ctx.fillStyle=c.id===0?'#ff9263':'#dce4e9';",
        "ctx.fillStyle=c.id===0?'#ff9263':world.mode==='wreck-hunt'&&c.hp/c.maxHP<=.45?'#ffc45d':'#dce4e9';",
        "weak target radar",
    )

    # Mode-specific score label makes the scoring objective instantly clear.
    text = replace_once(
        text,
        "$('position-label').textContent=gameMode==='racing'?'RACE POSITION':gameMode==='wreck-hunt'?'WRECKS':'SURVIVORS';",
        "$('position-label').textContent=gameMode==='racing'?'RACE POSITION':gameMode==='wreck-hunt'?'WRECKS':'SURVIVORS';if($('score-label'))$('score-label').textContent=gameMode==='wreck-hunt'?'HUNT SCORE':'IMPACT SCORE';",
        "hunt score label",
    )

    path.write_text(text)


def apply_wreck_hunt_improvements(target: Path) -> None:
    patch_physics(target / 'physics.js')
    patch_game(target / 'game.js')


if __name__ == '__main__':
    apply_wreck_hunt_improvements(Path('_site'))
