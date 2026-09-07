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

    # The first rendered loop review exposed a center rail directly in the driving
    # line and thick deck slats passing in front of the chase camera. Keep only
    # side rails and make the deck visually lighter while preserving the same
    # physical contact surface from physics3d.js.
    s = one(
        s,
        "{const l=fullPhysicsSpec.loop;for(const xo of [-3.45,0,3.45]){const rail=new THREE.Mesh(new THREE.TorusGeometry(l.r,.12,6,72),mat(xo===0?0xff7545:0x555f63,.7,.25));rail.rotation.y=Math.PI/2;rail.position.set(l.x+xo,l.y,l.z);rail.castShadow=true;rail.receiveShadow=true;fullPhysicsCourse.add(rail);}for(let i=0;i<36;i++){const a=i/36*Math.PI*2,slat=box(fullPhysicsCourse,l.x,l.y-l.r*Math.cos(a),l.z+l.r*Math.sin(a),l.halfWidth*2,.10,.32,i%6===0?0xd56a42:0x72736c,true);slat.rotation.x=-a;}}",
        "{const l=fullPhysicsSpec.loop;for(const xo of [-3.45,3.45]){const rail=new THREE.Mesh(new THREE.TorusGeometry(l.r,.10,6,72),mat(0x555f63,.7,.25));rail.rotation.y=Math.PI/2;rail.position.set(l.x+xo,l.y,l.z);rail.castShadow=true;rail.receiveShadow=true;fullPhysicsCourse.add(rail);}for(let i=0;i<40;i++){const a=i/40*Math.PI*2,slat=box(fullPhysicsCourse,l.x,l.y-l.r*Math.cos(a),l.z+l.r*Math.sin(a),l.halfWidth*2,.055,.22,i%10===0?0xd56a42:0x72736c,true);slat.rotation.x=-a;}}",
        "loop visual rails",
    )

    # With the car upside down, adding the normal 4.5m chassis-up camera lift
    # placed the camera almost exactly at the loop center, forcing the deck to
    # occlude the car. Keep the roll-following camera, but stay much closer to
    # the chassis while inside the loop volume.
    s = one(
        s,
        "const distance=view===1?16:9.8,lift=view===1?9:4.5+speed*.015;",
        "const loopDx=b.px-fullPhysicsSpec.loop.x,loopRad=Math.hypot(b.py-fullPhysicsSpec.loop.y,b.pz-fullPhysicsSpec.loop.z),inLoop=Math.abs(loopDx)<fullPhysicsSpec.loop.halfWidth+1&&loopRad<fullPhysicsSpec.loop.r+1.8,distance=view===1?16:inLoop?8.4:9.8,lift=view===1?9:inLoop?1.85:4.5+speed*.015;",
        "loop chase camera",
    )

    path.write_text(s)


if __name__ == '__main__':
    apply_full_physics_loop_polish(Path('_site'))
