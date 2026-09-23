"""Death Colosseum v1.11 SKY TILES AI bridge discipline.

Repeated live audits show SKY TILES starts safely but loses too many AI cars a
few seconds later. The geometry is now readable and wide enough; the remaining
issue is full-speed AI steering on narrow orthogonal bridges.

Keep normal combat aggression on the 3x3 pads, but slow AI and reduce steering
aggression only while a car is in the bridge/transition corridors. A small
margin inside each pad keeps cars cautious before their wheels reach an edge.
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
    new="const skyTiles=w.mode==='death-colosseum'&&activeCourse?.id==='sky-tiles';const skyPad=skyTiles&&[-22,0,22].some(px=>Math.abs(c.x-px)<=6.1)&&[-22,0,22].some(pz=>Math.abs(c.z-pz)<=6.1);const skyBridge=skyTiles&&!skyPad;return{gas:skyBridge?(Math.abs(delta)>.72?.46:.76):(Math.abs(delta)>1.2?.58:1),brake:0,steer:skyBridge?clamp(delta*1.45,-.72,.72):clamp(delta*1.95,-1,1),hand:skyBridge?0:((Math.abs(delta)>1.18&&speed>11)||edge>.72?1:0)};"
    physics=one(physics,old,new,'SKY TILES AI bridge control')
    physics_path.write_text(physics)


if __name__=='__main__':
    apply_death_colosseum_sky_ai_v111(Path('_site'))
