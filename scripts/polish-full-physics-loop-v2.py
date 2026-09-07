"""Post-review polish for the Works-style full physics loop presentation."""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"Full physics loop polish {label}: expected 1 match, found {n}")
    return text.replace(old, new, 1)


def apply_full_physics_loop_polish(target: Path) -> None:
    path = target / 'game.js'
    s = path.read_text()

    s = one(
        s,
        "{const l=fullPhysicsSpec.loop;for(const xo of [-3.45,0,3.45]){const rail=new THREE.Mesh(new THREE.TorusGeometry(l.r,.12,6,72),mat(xo===0?0xff7545:0x555f63,.7,.25));rail.rotation.y=Math.PI/2;rail.position.set(l.x+xo,l.y,l.z);rail.castShadow=true;rail.receiveShadow=true;fullPhysicsCourse.add(rail);}for(let i=0;i<36;i++){const a=i/36*Math.PI*2,slat=box(fullPhysicsCourse,l.x,l.y-l.r*Math.cos(a),l.z+l.r*Math.sin(a),l.halfWidth*2,.10,.32,i%6===0?0xd56a42:0x72736c,true);slat.rotation.x=-a;}}",
        "{const l=fullPhysicsSpec.loop;for(const xo of [-3.45,3.45]){const rail=new THREE.Mesh(new THREE.TorusGeometry(l.r,.10,6,72),mat(0x555f63,.7,.25));rail.rotation.y=Math.PI/2;rail.position.set(l.x+xo,l.y,l.z);rail.castShadow=true;rail.receiveShadow=true;fullPhysicsCourse.add(rail);}for(let i=0;i<40;i++){const a=i/40*Math.PI*2,slat=box(fullPhysicsCourse,l.x,l.y-l.r*Math.cos(a),l.z+l.r*Math.sin(a),l.halfWidth*2,.055,.22,i%10===0?0xd56a42:0x72736c,true);slat.rotation.x=-a;}}",
        "loop visual rails",
    )

    simple="const distance=view===1?16:9.8,lift=view===1?9:4.5+speed*.015;"
    racing="const distance=view===1?16:9.8,lift=view===1?9:4.5+speed*.015,looping=gameMode==='racing'&&Math.abs(uy)<.72,camDistance=looping?distance*.72:distance,camLift=looping?lift*.58:lift;"
    unified="const loopDx=b.px-fullPhysicsSpec.loop.x,loopRad=Math.hypot(b.py-fullPhysicsSpec.loop.y,b.pz-fullPhysicsSpec.loop.z),inArenaLoop=gameMode!=='racing'&&Math.abs(loopDx)<fullPhysicsSpec.loop.halfWidth+1&&loopRad<fullPhysicsSpec.loop.r+1.8,racingLoop=gameMode==='racing'&&Math.abs(uy)<.72,distance=view===1?16:inArenaLoop?8.4:9.8,lift=view===1?9:inArenaLoop?1.85:4.5+speed*.015,camDistance=racingLoop?distance*.72:distance,camLift=racingLoop?lift*.58:lift;"
    if racing in s:
        s=one(s,racing,unified,"combined loop chase camera")
    else:
        s=one(s,simple,unified.replace(',camDistance=racingLoop?distance*.72:distance,camLift=racingLoop?lift*.58:lift',''),"loop chase camera")

    path.write_text(s)


if __name__ == '__main__':
    apply_full_physics_loop_polish(Path('_site'))
