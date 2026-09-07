"""Final Wreck Hunt balance pass after rendered iPhone-landscape review."""
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Wreck Hunt final polish {label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


def patch_physics(path: Path) -> None:
    text = path.read_text()
    text = replace_once(
        text,
        "const playerArmor=c.id===0?.82:1;",
        "const playerArmor=c.id===0?(w.mode==='wreck-hunt'?.62:.82):1;",
        "hunter armor",
    )
    text = replace_once(
        text,
        "const bias=(o.id===0?(w.mode==='wreck-hunt'?.52:1.08):1)*(1+w.rand()*(w.mode==='wreck-hunt'?.22:.35));",
        "const bias=(o.id===0?(w.mode==='wreck-hunt'?(c.id%3===0?1.04:.58):1.08):1)*(1+w.rand()*(w.mode==='wreck-hunt'?.22:.35));",
        "distributed aggro",
    )
    text = replace_once(
        text,
        "other.score+=bonus;h.bonusScore+=bonus;",
        "other.score+=bonus;h.bonusScore+=bonus;other.hp=Math.min(other.maxHP,other.hp+other.maxHP*.10);",
        "wreck repair",
    )
    text = replace_once(text, "w.time-h.lastWreckAt<=7", "w.time-h.lastWreckAt<=9", "chain score window")
    text = replace_once(text, "w.time-h.lastWreckAt>7", "w.time-h.lastWreckAt>9", "chain expiry")
    path.write_text(text)


def patch_game(path: Path) -> None:
    text = path.read_text()
    text = replace_once(
        text,
        "const huntTarget=world.mode==='wreck-hunt'&&c.id!==0&&!c.dead&&(c.id===huntPriority||c.hp/c.maxHP<=.45);",
        "const huntTarget=world.mode==='wreck-hunt'&&c.id!==0&&!c.dead&&c.id===huntPriority;",
        "single target marker",
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
