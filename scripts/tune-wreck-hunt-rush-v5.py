"""Wreck Hunt v5: convert every player wreck into forward momentum and stronger feedback."""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"Wreck Hunt v5 {label}: expected 1 match, found {n}")
    return text.replace(old, new, 1)


def patch_physics(path: Path) -> None:
    s = path.read_text()

    s = one(
        s,
        "w.hunt={combo:0,bestCombo:0,lastWreckAt:-99,wrecks:0,respawns:0,bonusScore:0};",
        "w.hunt={combo:0,bestCombo:0,lastWreckAt:-99,wrecks:0,respawns:0,bonusScore:0,rushUntil:-99};",
        "rush state",
    )

    s = one(
        s,
        "let huntDamage=1;if(w.mode==='wreck-hunt'&&c.id!==0&&other)huntDamage=other.id===0?1.82:.28;const d=damage*protection*playerArmor*huntDamage;",
        "let huntDamage=1;if(w.mode==='wreck-hunt'&&c.id!==0&&other)huntDamage=other.id===0?(1.82+Math.min(w.hunt?.combo||0,4)*.14):.28;const d=damage*protection*playerArmor*huntDamage;",
        "chain finisher scaling",
    )

    s = one(
        s,
        "other.score+=bonus;h.bonusScore+=bonus;other.hp=Math.min(other.maxHP,other.hp+other.maxHP*.10);h.focusId=chooseHuntFocus(w,c.id);const next=w.cars[h.focusId];if(next&&!next.dead){next.target=0;next.aiTimer=.85;}",
        "other.score+=bonus;h.bonusScore+=bonus;other.hp=Math.min(other.maxHP,other.hp+other.maxHP*.10);h.focusId=chooseHuntFocus(w,c.id);h.rushUntil=w.time+1.65;const next=w.cars[h.focusId];if(next&&!next.dead){next.target=0;next.aiTimer=.85;const dx=next.x-other.x,dz=next.z-other.z,dist=Math.max(.001,Math.hypot(dx,dz)),kick=5.2+Math.min(h.combo,4)*.8;other.vx+=dx/dist*kick;other.vz+=dz/dist*kick;}",
        "wreck rush launch",
    )

    s = one(
        s,
        "const power=t.power*(player?1.22:1),grip=t.grip*(player?1.08:1),topSpeed=(player?33.5:29)*damageFactor;",
        "const huntRush=player&&w.mode==='wreck-hunt'&&w.hunt?.rushUntil>w.time;const power=t.power*(player?(huntRush?1.52+Math.min(w.hunt?.combo||0,4)*.06:1.22):1),grip=t.grip*(player?(huntRush?1.22:1.08):1),topSpeed=(player?(huntRush?38+Math.min(w.hunt?.combo||0,4)*1.4:33.5):29)*damageFactor;",
        "rush drivetrain",
    )

    s = one(
        s,
        "const impulse=closing*(w.mode==='racing'?1.48:1.35)/sum;",
        "const impulse=closing*(w.mode==='racing'?1.48:w.mode==='wreck-hunt'&&(a.id===0||b.id===0)&&w.hunt?.rushUntil>w.time?1.56:1.35)/sum;",
        "rush collision punch",
    )

    path.write_text(s)


def patch_game(path: Path) -> None:
    s = path.read_text()

    s = one(
        s,
        "if(e.by===0){if(world.mode==='wreck-hunt'){const chain=world.hunt?.combo||1,bonus=Math.max(0,(chain-1)*200);toast(`WRECK ×${chain}  +${500+bonus}`,2.2);}else toast('WRECK +500',2.2);}",
        "if(e.by===0){if(world.mode==='wreck-hunt'){const chain=world.hunt?.combo||1,bonus=Math.max(0,(chain-1)*200),callout=chain>=4?'RAMPAGE':chain>=3?'TRIPLE SMASH':chain>=2?'CHAIN WRECK':'WRECK';toast(`${callout} ×${chain}  +${500+bonus}`,2.2);shake=Math.max(shake,.78+Math.min(chain,4)*.18);sound(110+chain*28,true);}else toast('WRECK +500',2.2);}",
        "wreck callout",
    )

    s = one(
        s,
        "$('hunt-info').classList.toggle('hot',active&&h.combo>=3);",
        "$('hunt-info').classList.toggle('hot',active&&h.combo>=3);document.body.classList.toggle('hunt-rush',h.rushUntil>world.time);",
        "rush visual state",
    )

    path.write_text(s)


def apply_wreck_hunt_rush(target: Path) -> None:
    patch_physics(target / 'physics.js')
    patch_game(target / 'game.js')


if __name__ == '__main__':
    apply_wreck_hunt_rush(Path('_site'))
