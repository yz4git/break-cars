"""Final Wreck Hunt balance pass after rendered iPhone-landscape review."""
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Wreck Hunt final polish {label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


def patch_physics(path: Path) -> None:
    text = path.read_text()

    # Keep the hunter alive long enough for a score-attack run, but make the
    # player the primary finisher instead of letting CPU-vs-CPU damage dominate.
    text = replace_once(
        text,
        "const playerArmor=c.id===0?.82:1;",
        "const playerArmor=c.id===0?(w.mode==='wreck-hunt'?.62:.82):1;",
        "hunter armor",
    )
    text = replace_once(
        text,
        "let huntDamage=1;if(w.mode==='wreck-hunt'&&c.id!==0&&other)huntDamage=other.id===0?1.55:.52;const d=damage*protection*playerArmor*huntDamage;",
        "let huntDamage=1;if(w.mode==='wreck-hunt'&&c.id!==0&&other)huntDamage=other.id===0?1.82:.28;const d=damage*protection*playerArmor*huntDamage;",
        "hunter finisher advantage",
    )
    text = replace_once(
        text,
        "const bias=(o.id===0?(w.mode==='wreck-hunt'?.52:1.08):1)*(1+w.rand()*(w.mode==='wreck-hunt'?.22:.35));",
        "const bias=(o.id===0?(w.mode==='wreck-hunt'?(c.id%3===0?1.04:.48):1.08):1)*(1+w.rand()*(w.mode==='wreck-hunt'?.20:.35));",
        "distributed aggro",
    )
    text = replace_once(
        text,
        "other.score+=bonus;h.bonusScore+=bonus;",
        "other.score+=bonus;h.bonusScore+=bonus;other.hp=Math.min(other.maxHP,other.hp+other.maxHP*.10);",
        "wreck repair",
    )

    # Put one damaged bounty directly in the hunter's opening lane so the mode
    # demonstrates its core loop in the first few seconds instead of after a lap
    # around the arena.
    text = replace_once(
        text,
        "c.heading=Math.atan2(p.x-c.x,p.z-c.z);}}",
        "c.heading=Math.atan2(p.x-c.x,p.z-c.z);}const openingTarget=cars[1];Object.assign(openingTarget,{x:0,z:-8,heading:0,vx:0,vz:1.5,hp:Math.max(10,openingTarget.maxHP*.38)});w.hunt.focusId=openingTarget.id;}",
        "opening bounty",
    )

    # Respawn closer so the next target re-enters the action before CHAIN expires.
    text = replace_once(text, "r=22+w.rand()*7;", "r=18+w.rand()*6;", "respawn radius")

    # Light steering magnetism only when a target is in the forward cone. It is
    # strongest with neutral steering and fades when the player deliberately
    # steers, so it helps touch/keyboard driving without taking control away.
    text = replace_once(
        text,
        "const rawSteering=c.dead?0:(u.steer||0);\n const steering=player?-rawSteering:rawSteering;\n const wallSteerBoost=player&&w.mode!=='racing'?1+clamp((Math.hypot(c.x,c.z)-(RADIUS-10))/7,0,.42)*(w.mode==='wreck-hunt'?1.8:1):1;\n const yaw=steering*t.turn*(player?1.09:1)*wallSteerBoost*(u.hand?2.02:1.5)*clamp(Math.abs(forward)/4.6,0,1)*Math.sign(forward);",
        "const rawSteering=c.dead?0:(u.steer||0);\n let steering=player?-rawSteering:rawSteering,huntEdge=0;\n if(player&&w.mode==='wreck-hunt'&&!c.dead){let best=null,bestCost=Infinity;for(const o of w.cars){if(o.id===0||o.dead)continue;const dx=o.x-c.x,dz=o.z-c.z,dist=Math.hypot(dx,dz);if(dist>25)continue;const bearing=angle(Math.atan2(dx,dz)-c.heading);if(Math.abs(bearing)>1.18)continue;const cost=dist+Math.abs(bearing)*7+(o.hp/o.maxHP)*5;if(cost<bestCost){bestCost=cost;best=o;}}if(best){const desired=Math.atan2(best.x-c.x,best.z-c.z),assist=clamp(angle(desired-c.heading)*.48,-.38,.38)*(1-clamp(Math.abs(rawSteering),0,1)*.78);steering=clamp(steering+assist,-1,1);}const edgeDist=Math.hypot(c.x,c.z);huntEdge=clamp((edgeDist-(RADIUS-11))/6,0,1);if(huntEdge>0){const centerHeading=Math.atan2(-c.x,-c.z),rescue=clamp(angle(centerHeading-c.heading)*.8,-1,1);steering=clamp(steering+rescue*huntEdge*(Math.abs(rawSteering)<.55?1:.42),-1,1);}}\n const wallSteerBoost=player&&w.mode!=='racing'?1+clamp((Math.hypot(c.x,c.z)-(RADIUS-10))/7,0,.42)*(w.mode==='wreck-hunt'?2.15:1):1;\n const motionSign=Math.abs(forward)<.45&&huntEdge>.2?1:Math.sign(forward);\n const yaw=steering*t.turn*(player?1.09:1)*wallSteerBoost*(u.hand?2.02:1.5)*clamp(Math.abs(forward)/4.6+huntEdge*.48,0,1)*motionSign;",
        "hunt steering assist",
    )
    text = replace_once(
        text,
        "if(player){const rebound=(w.mode==='wreck-hunt'?3.4:1.8)+Math.min(v,14)*(w.mode==='wreck-hunt'?.24:.16);c.vx-=nx*rebound;c.vz-=nz*rebound;}",
        "if(player){const rebound=(w.mode==='wreck-hunt'?4.2:1.8)+Math.min(v,14)*(w.mode==='wreck-hunt'?.28:.16);c.vx-=nx*rebound;c.vz-=nz*rebound;if(w.mode==='wreck-hunt'){const desired=Math.atan2(-c.x,-c.z);c.heading=angle(c.heading+angle(desired-c.heading)*clamp(.16+v*.012,.16,.34));}}",
        "wall heading rescue",
    )

    text = replace_once(text, "w.time-h.lastWreckAt<=7", "w.time-h.lastWreckAt<=9", "chain score window")
    text = replace_once(text, "w.time-h.lastWreckAt>7", "w.time-h.lastWreckAt>9", "chain expiry")
    path.write_text(text)


def patch_game(path: Path) -> None:
    text = path.read_text()

    # One explicit target at a time. Multiple TARGET labels made the objective
    # visually ambiguous during the rendered review.
    text = replace_once(
        text,
        "const huntTarget=world.mode==='wreck-hunt'&&c.id!==0&&!c.dead&&(c.id===huntPriority||c.hp/c.maxHP<=.45);",
        "const huntTarget=world.mode==='wreck-hunt'&&c.id!==0&&!c.dead&&c.id===huntPriority;",
        "single target marker",
    )
    text = replace_once(
        text,
        "const pulse=(c.id===huntPriority?2.35:2.15)+Math.sin(world.time*10+c.id)*.12;m.targetMarker.scale.set(pulse,pulse,1);",
        "const pulse=2.78+Math.sin(world.time*10+c.id)*.16;m.targetMarker.position.y=4.05+Math.sin(world.time*8+c.id)*.16;m.targetMarker.scale.set(pulse,pulse,1);",
        "priority target visibility",
    )

    # Keep center-screen messaging for the player's actions. CPU wreck notices
    # and frequent respawn text were stealing attention from the hunt target.
    text = replace_once(
        text,
        "if(toastTime<.25)toast(`NEW TARGET — CAR ${String(e.car+1).padStart(2,'0')}`,1.0);continue;}",
        "continue;}",
        "quiet respawn toast",
    )
    text = replace_once(
        text,
        "else if(e.car!==0&&toastTime<.2)toast(`CAR ${String(e.car+1).padStart(2,'0')} DESTROYED`,1.6);",
        "else if(e.car!==0&&world.mode!=='wreck-hunt'&&toastTime<.2)toast(`CAR ${String(e.car+1).padStart(2,'0')} DESTROYED`,1.6);",
        "quiet cpu wreck toast",
    )

    # Guarantee the score label is mode-correct every UI tick rather than only
    # at start, which also makes retry/home transitions robust.
    text = replace_once(
        text,
        "$('score').textContent=String(p.score).padStart(5,'0');const remain=",
        "$('score').textContent=String(p.score).padStart(5,'0');if($('score-label'))$('score-label').textContent=world.mode==='wreck-hunt'?'HUNT SCORE':'IMPACT SCORE';const remain=",
        "live hunt score label",
    )

    text = replace_once(
        text,
        "Math.max(0,7-(world.time-h.lastWreckAt))",
        "Math.max(0,9-(world.time-h.lastWreckAt))",
        "chain HUD window",
    )
    text = text.replace("7秒以内の連続WRECK", "9秒以内の連続WRECK")
    text = text.replace("7秒以内に次を撃破", "9秒以内に次を撃破")
    path.write_text(text)


def apply_wreck_hunt_final_tuning(target: Path) -> None:
    patch_physics(target / 'physics.js')
    patch_game(target / 'game.js')


if __name__ == '__main__':
    apply_wreck_hunt_final_tuning(Path('_site'))
