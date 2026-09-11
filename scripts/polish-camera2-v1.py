"""Camera 2.0 v1: keep the player visible around extreme 3D geometry.

The authored cameras already know how to frame loops and jumps. This final pass
adds a lightweight visibility resolver on top of those compositions: every
~110 ms it raycasts only against the active arena/track scenery and, when the
line of sight is blocked, slides the camera sideways (with hysteresis) and
slightly upward. It never changes vehicle physics, input, progress or gameplay.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Camera 2.0 v1 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_camera2_v1(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    anchor = "const camTarget=new THREE.Vector3(),lookTarget=new THREE.Vector3(),smoothLook=new THREE.Vector3(),physicsCamUp=new THREE.Vector3(0,1,0),physicsWorldUp=new THREE.Vector3(0,1,0);let uiClock=0;"
    camera2 = anchor + """
const camera2Ray=new THREE.Raycaster(),camera2Dir=new THREE.Vector3(),camera2SideVec=new THREE.Vector3(),camera2CandidateA=new THREE.Vector3(),camera2CandidateB=new THREE.Vector3();let camera2Timer=0,camera2Escape=0,camera2EscapeTarget=0,camera2EscapeSide=1,camera2Blocked=false,camera2Score=0;
function camera2Occlusion(from,to,root){camera2Dir.copy(to).sub(from);const d=camera2Dir.length();if(d<3||!root?.visible)return 0;camera2Dir.multiplyScalar(1/d);camera2Ray.set(from,camera2Dir);camera2Ray.near=2.4;camera2Ray.far=Math.max(2.5,d-1.15);const hits=camera2Ray.intersectObject(root,true);let score=0;for(const h of hits){if(!h.object.visible)continue;score=Math.max(score,1-h.distance/d);if(score>.86)break;}return score;}
function applyCamera2(dt,p){if(view===2||mode==='menu'||mode==='paused'){camera2EscapeTarget=0;camera2Escape*=Math.exp(-7*dt);return;}camera2Timer-=dt;if(camera2Timer<=0){camera2Timer=.11;const root=gameMode==='racing'?raceTrack:arena,base=camera2Occlusion(lookTarget,camTarget,root);camera2Score=base;camera2Blocked=base>.055;if(camera2Blocked){const dx=camTarget.x-lookTarget.x,dz=camTarget.z-lookTarget.z,dl=Math.hypot(dx,dz)||1;camera2SideVec.set(-dz/dl,0,dx/dl);const pose=gameMode==='racing'?trackPoint(p.trackS??0,0):null,stunt=gameMode==='racing'&&(pose?.kind==='loop'||pose?.kind==='jump-ramp'||pose?.kind==='jump-gap'||pose?.kind==='jump-landing'||p.p3?.airTime>.08),reach=stunt?10.5:6.6,lift=stunt?2.7:1.8;camera2CandidateA.copy(camTarget).addScaledVector(camera2SideVec,reach).y+=lift;camera2CandidateB.copy(camTarget).addScaledVector(camera2SideVec,-reach).y+=lift;const sa=camera2Occlusion(lookTarget,camera2CandidateA,root),sb=camera2Occlusion(lookTarget,camera2CandidateB,root),current=camera2EscapeSide>0?sa:sb,other=camera2EscapeSide>0?sb:sa;if(other+.12<current)camera2EscapeSide*=-1;else if(camera2Escape<.15)camera2EscapeSide=sa<=sb?1:-1;camera2EscapeTarget=reach*(.72+Math.min(.28,base*.55));}else camera2EscapeTarget=0;}camera2Escape+=(camera2EscapeTarget-camera2Escape)*(1-Math.exp(-(camera2EscapeTarget>camera2Escape?8.5:5.5)*dt));if(camera2Escape>.03){const dx=camTarget.x-lookTarget.x,dz=camTarget.z-lookTarget.z,dl=Math.hypot(dx,dz)||1;camera2SideVec.set(-dz/dl,0,dx/dl);camTarget.addScaledVector(camera2SideVec,camera2Escape*camera2EscapeSide);camTarget.y+=Math.min(3.2,camera2Escape*.22);}window.__breakCarsCamera2={blocked:camera2Blocked,score:camera2Score,escape:camera2Escape,side:camera2EscapeSide};}
"""
    s = one(s, anchor, camera2, 'camera helper insertion')

    tail = "camera.position.lerp(camTarget,1-Math.exp(-6*dt));smoothLook.lerp(lookTarget,1-Math.exp(-9*dt));"
    s = one(s, tail, "applyCamera2(dt,p);" + tail, 'camera resolver call')
    game.write_text(s)


if __name__ == '__main__':
    apply_camera2_v1(Path('_site'))
