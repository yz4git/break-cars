"""Post-review RAMPAGE 3D raceability polish.

Keep the loop physical/full-contact, but make it a stunt section rather than a
first-lap mass grave. Also make the jump landing visually obvious and keep the
chase camera looking at the landing road while airborne.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE raceability {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_raceability(target: Path) -> None:
    racing = target / 'racing.js'
    s = racing.read_text()
    s = one(s, "const loopLanes=[-4.4,-1.5,1.5,4.4];", "const loopLanes=[-5.8,-2.9,2.9,5.8];", 'loop lane spread')
    racing.write_text(s)

    physics = target / 'physics3d.js'
    s = physics.read_text()
    s = one(
        s,
        "if (a.finished||b.finished) return; const A=a.p3,B=b.p3; if (!A||!B||Math.abs(A.px-B.px)>6||Math.abs(A.py-B.py)>4||Math.abs(A.pz-B.pz)>6) return; const contacts=[];",
        "if (a.finished||b.finished) return; const A=a.p3,B=b.p3; if (!A||!B||Math.abs(A.px-B.px)>6||Math.abs(A.py-B.py)>4||Math.abs(A.pz-B.pz)>6) return; const loopPair=w.mode==='racing'&&racePointAt(a.trackS??0).kind==='loop'&&racePointAt(b.trackS??0).kind==='loop',contacts=[];",
        'loop pair detection',
    )
    s = one(
        s,
        "const n=ct.n,rawCor=ct.over*.34/Math.min(3,contacts.length),cor=w.mode==='racing'?Math.min(rawCor,.14):rawCor;",
        "const n=ct.n,rawCor=ct.over*.34/Math.min(3,contacts.length),cor=w.mode==='racing'?Math.min(rawCor,loopPair?.10:.14):rawCor;",
        'loop depenetration',
    )
    s = one(
        s,
        "const j=closing*(rush ? 1.15 : 1)/Math.max(EPS,inv)*.46,J=mul(n,j);",
        "const j=closing*(rush ? 1.15 : 1)/Math.max(EPS,inv)*(loopPair?.22:.46),J=mul(n,j);",
        'loop contact impulse',
    )
    s = one(
        s,
        "damage=(peak-2)*.42*(w.mode==='racing' ? 1.28 : 1);",
        "damage=(peak-2)*.42*(w.mode==='racing' ? (loopPair?.24:1.28) : 1);",
        'loop contact damage',
    )
    s = one(s, "if (w.mode==='racing'&&peak>6) for", "if (w.mode==='racing'&&!loopPair&&peak>6) for", 'loop spin suppression')
    physics.write_text(s)

    view = target / 'track-view.js'
    s = view.read_text()
    takeoff = "for(let k=0;k<5;k++)for(const lane of [-5.4,0,5.4]){const s=spec.jump.startS-8+k*1.55,p=trackPoint(s,lane);if(p.kind==='jump-gap')continue;const marker=box(group,p.x,p.y,p.z,1.05,.025,.72,k%2?0xffa45e:0xe8e3d3);align(marker,p);marker.position.add(new THREE.Vector3(p.up.x*.07,p.up.y*.07,p.up.z*.07));}"
    landing = takeoff + "\n for(let k=0;k<6;k++)for(const lane of [-5.4,0,5.4]){const s=spec.jump.endS+1.0+k*1.65,p=trackPoint(s,lane);const marker=box(group,p.x,p.y,p.z,1.12,.028,.78,k%2?0xe8e3d3:0xff7042);align(marker,p);marker.position.add(new THREE.Vector3(p.up.x*.075,p.up.y*.075,p.up.z*.075));}"
    s = one(s, takeoff, landing, 'landing markers')
    view.write_text(s)

    game = target / 'game.js'
    s = game.read_text()
    s = one(
        s,
        "racePose=gameMode==='racing'?trackPoint(p.trackS??0,0):null,racingLoop=!!raceLoopSpec&&!!racePose&&p.trackS>=raceLoopSpec.startS-7&&p.trackS<=raceLoopSpec.endS+7,distance=",
        "racePose=gameMode==='racing'?trackPoint(p.trackS??0,0):null,raceKind=racePose?.kind,racingLoop=!!raceLoopSpec&&!!racePose&&p.trackS>=raceLoopSpec.startS-7&&p.trackS<=raceLoopSpec.endS+7,racingJump=gameMode==='racing'&&(raceKind==='jump-ramp'||raceKind==='jump-gap'||raceKind==='jump-landing'||b.airTime>.08),distance=",
        'jump camera detection',
    )
    s = one(
        s,
        "camera.up.lerp(physicsWorldUp,1-Math.exp(-8*dt));camera.fov=62;}else{const camDistance=distance,camLift=lift;",
        "camera.up.lerp(physicsWorldUp,1-Math.exp(-8*dt));camera.fov=62;}else if(racingJump){const landingPose=trackPoint((p.trackS??0)+14,0);camTarget.set(b.px-racePose.forward.x*7,b.py+5.8,b.pz-racePose.forward.z*7);lookTarget.set(landingPose.x+landingPose.up.x*1.15,landingPose.y+landingPose.up.y*1.15,landingPose.z+landingPose.up.z*1.15);camera.up.lerp(physicsWorldUp,1-Math.exp(-9*dt));camera.fov=64;}else{const camDistance=distance,camLift=lift;",
        'jump landing look-ahead',
    )
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_raceability(Path('_site'))
