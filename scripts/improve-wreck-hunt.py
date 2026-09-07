"""Polish Wreck Hunt after the base deploy-time integration is applied."""
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Wreck Hunt polish {label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


def patch_physics(path: Path) -> None:
    text = path.read_text()

    # Faster score-attack cadence: targets are deliberately softer than the
    # survival roster, and hits delivered by the hunter get a mode-only boost.
    text = replace_once(
        text,
        "c.maxHP=Math.max(58,Math.round(c.maxHP*.68));",
        "c.maxHP=Math.max(50,Math.round(c.maxHP*.54));",
        "target durability",
    )
    text = replace_once(
        text,
        "const d=damage*protection*playerArmor;",
        "const huntDamage=w.mode==='wreck-hunt'&&other?.id===0&&c.id!==0?1.32:1;const d=damage*protection*playerArmor*huntDamage;",
        "hunter damage boost",
    )
    text = replace_once(
        text,
        "c.respawnAt=w.time+2.6+w.rand()*.9;",
        "c.respawnAt=w.time+1.9+w.rand()*.7;",
        "respawn cadence",
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
        "const wreckMarker=new THREE.Sprite(wreckSpriteMat);wreckMarker.position.set(0,3.7,0);wreckMarker.scale.set(3.35,3.35,1);wreckMarker.visible=false;g.add(wreckMarker);const targetMarker=new THREE.Sprite(targetSpriteMat);targetMarker.position.set(0,3.55,0);targetMarker.scale.set(2.25,2.25,1);targetMarker.visible=false;g.add(targetMarker);",
        "target marker",
    )
    text = replace_once(
        text,
        "scene.add(g);return{g,body,parts,wheels,number,wreckMarker,wrecked:false",
        "scene.add(g);return{g,body,parts,wheels,number,wreckMarker,targetMarker,wrecked:false",
        "target marker return",
    )
    text = replace_once(
        text,
        "m.wreckMarker.visible=c.dead;m.body.rotation.z=",
        "m.wreckMarker.visible=c.dead;const huntTarget=world.mode==='wreck-hunt'&&c.id!==0&&!c.dead&&c.hp/c.maxHP<=.40;m.targetMarker.visible=huntTarget;if(huntTarget){m.targetMarker.position.y=3.5+Math.sin(world.time*8+c.id)*.18;const pulse=2.15+Math.sin(world.time*10+c.id)*.12;m.targetMarker.scale.set(pulse,pulse,1);}m.body.rotation.z=",
        "target visibility",
    )

    # Keep persistent hunt information out of the impact-message lane. The
    # regular HUD already owns WRECKS and SCORE, so the center-top widget is
    # reserved for chain state only.
    text = replace_once(text, "`${p.kills}<span> WRECKS</span>`", "`${p.kills}`", "duplicate wreck label")
    text = replace_once(
        text,
        "$('hunt-combo').textContent=active?`CHAIN ×${h.combo}`:'CHAIN READY';$('hunt-wrecks').textContent=`${h.wrecks} WRECKS · ${p.score.toLocaleString()} PTS`;$('hunt-state').textContent=active?`${left.toFixed(1)}秒以内に次を壊せ`:'次のWRECKからCHAIN開始';$('hunt-info').classList.toggle('hot',active&&h.combo>=3);",
        "$('hunt-combo').textContent=active?`CHAIN ×${h.combo}`:'CHAIN';$('hunt-wrecks').textContent='';$('hunt-state').textContent=active?`${left.toFixed(1)}s`:'READY';$('hunt-info').classList.toggle('active',active);$('hunt-info').classList.toggle('hot',active&&h.combo>=3);",
        "chain HUD",
    )

    # Re-entry should feel like a new target being launched into the arena,
    # not a silent model reset.
    text = replace_once(
        text,
        "if(e.type==='respawn'){rebuildCarVisual(e.car);if(toastTime<.25)toast(`NEW TARGET — CAR ${String(e.car+1).padStart(2,'0')}`,1.1);continue;}",
        "if(e.type==='respawn'){rebuildCarVisual(e.car);blast(e.x,e.z,22);for(let i=0;i<20;i++)emit(e.x,.7,e.z,12,'spark');for(let i=0;i<8;i++)emit(e.x,.9,e.z,8,'flame');for(let i=0;i<7;i++)emit(e.x,1.0,e.z,4,'smoke');if(Math.hypot(e.x-player.x,e.z-player.z)<28)shake=Math.max(shake,.45);sound(660,true);if(toastTime<.25)toast(`NEW TARGET — CAR ${String(e.car+1).padStart(2,'0')}`,1.0);continue;}",
        "respawn presentation",
    )

    # Weak targets also stand out on the radar so the player can immediately
    # transition from one finisher to the next.
    text = replace_once(
        text,
        "ctx.fillStyle=c.id===0?'#ff9263':'#dce4e9';",
        "ctx.fillStyle=c.id===0?'#ff9263':world.mode==='wreck-hunt'&&c.hp/c.maxHP<=.40?'#ffc45d':'#dce4e9';",
        "weak target radar",
    )

    path.write_text(text)


def apply_wreck_hunt_improvements(target: Path) -> None:
    patch_physics(target / 'physics.js')
    patch_game(target / 'game.js')


if __name__ == '__main__':
    apply_wreck_hunt_improvements(Path('_site'))
