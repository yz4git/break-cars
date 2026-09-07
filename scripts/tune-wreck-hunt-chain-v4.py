"""Wreck Hunt chain-routing pass derived from rendered mobile playtests."""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"Wreck Hunt v4 {label}: expected 1 match, found {n}")
    return text.replace(old, new, 1)


def patch_physics(path: Path) -> None:
    s = path.read_text()

    # While the hunter is in Wreck Hunt, steering assistance should follow the
    # currently selected bounty instead of silently switching to another car.
    s = one(
        s,
        "if(player&&w.mode==='wreck-hunt'&&!c.dead){let best=null,bestCost=Infinity;for(const o of w.cars){",
        "if(player&&w.mode==='wreck-hunt'&&!c.dead){let best=w.cars[w.hunt?.focusId],bestCost=Infinity;if(!best||best.dead){best=null;for(const o of w.cars){",
        "focus steering start",
    )
    s = one(
        s,
        "if(cost<bestCost){bestCost=cost;best=o;}}if(best){",
        "if(cost<bestCost){bestCost=cost;best=o;}}}if(best){",
        "focus steering close",
    )

    helper = """function chooseHuntFocus(w,exclude=-1){
 const p=w.cars[0];let best=-1,bestCost=Infinity;
 for(const o of w.cars){
  if(o.id===0||o.id===exclude||o.dead)continue;
  const dx=o.x-p.x,dz=o.z-p.z,dist=Math.hypot(dx,dz),bearing=Math.abs(angle(Math.atan2(dx,dz)-p.heading)),hp=o.hp/o.maxHP,outer=Math.max(0,Math.hypot(o.x,o.z)-28);
  const cost=dist+hp*4+bearing*2.4+outer*.8+(bearing>2.2?6:0);
  if(cost<bestCost){bestCost=cost;best=o.id;}
 }
 return best;
}

"""
    s = one(s, "function respawnHuntCar(w,c){", helper + "function respawnHuntCar(w,c){", "focus helper")

    s = one(
        s,
        "other.score+=bonus;h.bonusScore+=bonus;other.hp=Math.min(other.maxHP,other.hp+other.maxHP*.10);",
        "other.score+=bonus;h.bonusScore+=bonus;other.hp=Math.min(other.maxHP,other.hp+other.maxHP*.10);h.focusId=chooseHuntFocus(w,c.id);const next=w.cars[h.focusId];if(next&&!next.dead){next.target=0;next.aiTimer=.85;}",
        "next focus after wreck",
    )

    s = one(
        s,
        "if(w.mode==='wreck-hunt'){const h=w.hunt,p=w.cars[0];if(h.combo&&w.time-h.lastWreckAt>9)h.combo=0;for(const c of w.cars.slice(1))if(c.dead&&c.respawnAt<=w.time)respawnHuntCar(w,c);p.lastContact=w.time;if(p.dead||w.time>=w.limit)w.done=true;return;}",
        "if(w.mode==='wreck-hunt'){const h=w.hunt,p=w.cars[0];if(h.combo&&w.time-h.lastWreckAt>9)h.combo=0;for(const c of w.cars.slice(1))if(c.dead&&c.respawnAt<=w.time)respawnHuntCar(w,c);const focus=w.cars[h.focusId];if(!focus||focus.dead||focus.id===0)h.focusId=chooseHuntFocus(w);const locked=w.cars[h.focusId];if(locked&&!locked.dead&&h.combo>0){locked.target=0;locked.aiTimer=Math.max(locked.aiTimer,.35);}p.lastContact=w.time;if(p.dead||w.time>=w.limit)w.done=true;return;}",
        "focus maintenance",
    )

    path.write_text(s)


def patch_game(path: Path) -> None:
    s = path.read_text()

    s = one(
        s,
        "const targetTex=new THREE.CanvasTexture(targetCanvas);targetTex.colorSpace=THREE.SRGBColorSpace;const targetSpriteMat=new THREE.SpriteMaterial({map:targetTex,transparent:true,depthTest:false,depthWrite:false});",
        "const targetTex=new THREE.CanvasTexture(targetCanvas);targetTex.colorSpace=THREE.SRGBColorSpace;const targetSpriteMat=new THREE.SpriteMaterial({map:targetTex,transparent:true,depthTest:false,depthWrite:false});const huntNav=document.createElement('div');huntNav.id='hunt-nav';huntNav.innerHTML='<b>▲</b><span>TARGET</span><small>--m</small>';document.body.appendChild(huntNav);const huntNavArrow=huntNav.querySelector('b'),huntNavLabel=huntNav.querySelector('span'),huntNavDistance=huntNav.querySelector('small');",
        "target navigator DOM",
    )

    s = one(
        s,
        "function visuals(dt){const player=world.cars[0],huntPriority=world.mode==='wreck-hunt'?[...world.cars].filter(c=>c.id!==0&&!c.dead).sort((a,b)=>(a.hp/a.maxHP)*18+Math.hypot(a.x-player.x,a.z-player.z)*.14-(b.hp/b.maxHP)*18-Math.hypot(b.x-player.x,b.z-player.z)*.14)[0]?.id:-1,spectating=",
        "function visuals(dt){huntNav.classList.remove('visible');const player=world.cars[0],huntFocus=world.mode==='wreck-hunt'?world.cars[world.hunt?.focusId]:null,huntPriority=huntFocus&&!huntFocus.dead?huntFocus.id:world.mode==='wreck-hunt'?[...world.cars].filter(c=>c.id!==0&&!c.dead).sort((a,b)=>Math.hypot(a.x-player.x,a.z-player.z)+(a.hp/a.maxHP)*4-(Math.hypot(b.x-player.x,b.z-player.z)+(b.hp/b.maxHP)*4))[0]?.id:-1,spectating=",
        "stable visual focus",
    )

    s = one(
        s,
        "const pulse=2.78+Math.sin(world.time*10+c.id)*.16;m.targetMarker.position.y=4.05+Math.sin(world.time*8+c.id)*.16;m.targetMarker.scale.set(pulse,pulse,1);",
        "const pulse=2.78+Math.sin(world.time*10+c.id)*.16;m.targetMarker.position.y=4.05+Math.sin(world.time*8+c.id)*.16;m.targetMarker.scale.set(pulse,pulse,1);const dx=c.x-player.x,dz=c.z-player.z,dist=Math.hypot(dx,dz),bearing=angle(Math.atan2(dx,dz)-player.heading);huntNav.classList.add('visible');huntNav.classList.toggle('near',dist<12);huntNavArrow.style.transform=`rotate(${bearing}rad)`;huntNavLabel.textContent=`TARGET ${String(c.id+1).padStart(2,'0')}`;huntNavDistance.textContent=`${Math.round(dist)}m`;",
        "target navigator update",
    )

    path.write_text(s)


def apply_wreck_hunt_chain_tuning(target: Path) -> None:
    patch_physics(target / 'physics.js')
    patch_game(target / 'game.js')


if __name__ == '__main__':
    apply_wreck_hunt_chain_tuning(Path('_site'))
