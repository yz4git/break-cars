"""Post-review RAMPAGE 3D raceability polish.

Keep the loop physical/full-contact, but make the opening grid + approach +
loop a stunt flow zone rather than a first-lap traffic jam. Targeted combat
returns immediately after the first loop exit. Also keep jump landings clear.
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
    old = "const loopGap=forwardGap(COURSE_SPEC.loop.startS,p.s),loopApproach=p.kind!=='loop'&&loopGap>0&&loopGap<50,loopLane=c.id===0?0:(c.loopLane??0);\n if(loopApproach){"
    new = "const loopGap=forwardGap(COURSE_SPEC.loop.startS,p.s),loopApproach=p.kind!=='loop'&&loopGap>0&&loopGap<50,loopLane=c.id===0?0:(c.loopLane??0),openingStunt=c.raceDistance>-60&&c.raceDistance<COURSE_SPEC.loop.endS+10;\n if(openingStunt&&!loopApproach&&p.kind!=='loop'){\n  c.battleTarget=-1;c.aiReverse=0;\n  const launchLane=c.raceDistance<5?c.lane:loopLane,target=trackPoint(p.s+clamp(12+speed*.32,13,21),launchLane),delta=angle(Math.atan2(target.x-c.x,target.z-c.z)-c.heading),laneFix=clamp((launchLane-p.lane)*.10,-.30,.30);\n  return{gas:1,brake:0,steer:clamp(delta*1.5+laneFix,-.68,.68),hand:0};\n }\n if(loopApproach){"
    s = one(s, old, new, 'opening stunt AI')
    racing.write_text(s)

    physics = target / 'physics3d.js'
    s = physics.read_text()
    import_line = "import {sampleRaceSurface,racePointAt,race3DFeatureSpec} from './racing3d.js?v=wr3d-v1';\n"
    helper = import_line + "const RAMPAGE_RACE_SPEC=race3DFeatureSpec();\nconst rampageStuntSafety=c=>{const rd=c?.raceDistance??0;if(rd>-60&&rd<RAMPAGE_RACE_SPEC.loop.endS+10)return true;const L=RAMPAGE_RACE_SPEC.length,q=((c?.trackS??0)%L+L)%L;let gap=RAMPAGE_RACE_SPEC.loop.startS-q;if(gap<0)gap+=L;return racePointAt(q).kind==='loop'||gap<38;};\n"
    s = one(s, import_line, helper, 'stunt safety helper')
    s = one(
        s,
        "if (a.finished||b.finished) return; const A=a.p3,B=b.p3; if (!A||!B||Math.abs(A.px-B.px)>6||Math.abs(A.py-B.py)>4||Math.abs(A.pz-B.pz)>6) return;\n  const contacts=[];",
        "if (a.finished||b.finished) return; const A=a.p3,B=b.p3; if (!A||!B||Math.abs(A.px-B.px)>6||Math.abs(A.py-B.py)>4||Math.abs(A.pz-B.pz)>6) return;\n  const stuntPair=w.mode==='racing'&&rampageStuntSafety(a)&&rampageStuntSafety(b),contacts=[];",
        'stunt pair detection',
    )
    s = one(
        s,
        "const j=closing*(rush ? 1.15 : 1)/Math.max(EPS,inv)*.46,J=mul(n,j); impulse(A,mul(J,-1),ct.pa.rel); impulse(B,J,ct.pb.rel);",
        "const j=closing*(rush ? 1.15 : 1)/Math.max(EPS,inv)*(stuntPair?.20:.46),J=mul(n,j); if(stuntPair){impulse(A,mul(J,-1));impulse(B,J);}else{impulse(A,mul(J,-1),ct.pa.rel);impulse(B,J,ct.pb.rel);}",
        'stunt contact impulse and torque',
    )
    s = one(
        s,
        "damage=(peak-2)*.42*(w.mode==='racing' ? 1.28 : 1);",
        "damage=(peak-2)*.42*(w.mode==='racing' ? (stuntPair?.24:1.28) : 1);",
        'stunt contact damage',
    )
    s = one(s, "if (w.mode==='racing'&&peak>6) for", "if (w.mode==='racing'&&!stuntPair&&peak>6) for", 'stunt spin suppression')
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
