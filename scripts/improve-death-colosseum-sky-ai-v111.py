"""Death Colosseum v1.11 SKY TILES AI bridge discipline.

Repeated live audits show SKY TILES starts safely but loses too many AI cars a
few seconds later. The geometry is now readable and wide enough; the remaining
issue is full-speed AI steering on narrow orthogonal bridges.

Keep normal combat aggression on the 3x3 pads, but slow AI and reduce steering
aggression only while a car is in the bridge/transition corridors. A 1.8 m cautious rim inside each pad forces cars to line up with a bridge
before they reach an edge, preventing diagonal corner exits and outer-edge
overshoots.
Sharp bridge corrections also brake briefly instead of trying to steer through
at speed; this targets unforced falls without softening pad combat.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n=text.count(old)
    if n!=1:
        raise RuntimeError(f'Death Colosseum v1.11 {label}: expected 1 match, found {n}')
    return text.replace(old,new,1)


def apply_death_colosseum_sky_ai_v111(target: Path) -> None:
    physics_path=target/'physics.js'
    physics=physics_path.read_text()
    old="return{gas:Math.abs(delta)>1.2?.58:1,brake:0,steer:clamp(delta*1.95,-1,1),hand:(Math.abs(delta)>1.18&&speed>11)||edge>.72?1:0};"
    new="const skyTiles=w.mode==='death-colosseum'&&activeCourse?.id==='sky-tiles';const skyPad=skyTiles&&[-22,0,22].some(px=>Math.abs(c.x-px)<=4.8)&&[-22,0,22].some(pz=>Math.abs(c.z-pz)<=4.8);const skyBridge=skyTiles&&!skyPad,skyTurn=Math.abs(delta);return{gas:skyBridge?(skyTurn>.72?.26:.58):(skyTurn>1.2?.58:1),brake:skyBridge&&skyTurn>.9&&speed>7?1:0,steer:skyBridge?clamp(delta*1.25,-.60,.60):clamp(delta*1.95,-1,1),hand:skyBridge?0:((skyTurn>1.18&&speed>11)||edge>.72?1:0)};"
    physics=one(physics,old,new,'SKY TILES AI bridge control')
    physics_path.write_text(physics)


if __name__=='__main__':
    apply_death_colosseum_sky_ai_v111(Path('_site'))
