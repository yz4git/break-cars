"""Camera 2.0 v2: keep the player visible around extreme 3D geometry.

The authored cameras still choose the composition. This final visibility pass
samples several *actual* escape positions on both sides of that composition,
then eases toward the nearest clear candidate with side-switch hysteresis.
Unlike v1 it never tests a far point and stops part-way behind another support.
It only raycasts scenery and never changes vehicle physics/input/progress.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Camera 2.0 v2 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_camera2_v1(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    anchor = "const camTarget=new THREE.Vector3(),lookTarget=new THREE.Vector3(),smoothLook=new THREE.Vector3(),physicsCamUp=new THREE.Vector3(0,1,0),physicsWorldUp=new THREE.Vector3(0,1,0);let uiClock=0;"
    camera2 = anchor + """
const camera2Ray=new THREE.Raycaster(),camera2Dir=new THREE.Vector3(),camera2SideVec=new THREE.Vector3(),camera2Candidate=new THREE.Vector3();let camera2Timer=0,camera2Escape=0,camera2EscapeTarget=0,camera2Lift=0,camera2LiftTarget=0,camera2EscapeSide=1,camera2Blocked=false,camera2Score=0,camera2ChosenScore=0;
function camera2Occlusion(from,to,root){camera2Dir.copy(to).sub(from);const d=camera2Dir.length();if(d<3||!root?.visible)return 0;camera2Dir.multiplyScalar(1/d);camera2Ray.set(from,camera2Dir);camera2Ray.near=2.4;camera2Ray.far=Math.max(2.5,d-.45);const hits=camera2Ray.intersectObject(root,true);let score=0;for(const h of hits){if(!h.object.visible)continue;score=Math.max(score,1-h.distance/d);if(score>.90)break;}return score;}
function applyCamera2(dt,p){if(view===2||mode==='menu'||mode==='paused'){camera2EscapeTarget=0;camera2LiftTarget=0;camera2Escape*=Math.exp(-7*dt);camera2Lift*=Math.exp(-7*dt);return;}camera2Timer-=dt;if(camera2Timer<=0){camera2Timer=.10;const root=gameMode==='racing'?raceTrack:arena,base=camera2Occlusion(lookTarget,camTarget,root);camera2Score=base;camera2Blocked=base>.055;if(camera2Blocked){const dx=camTarget.x-lookTarget.x,dz=camTarget.z-lookTarget.z,dl=Math.hypot(dx,dz)||1;camera2SideVec.set(-dz/dl,0,dx/dl);const pose=gameMode==='racing'?trackPoint(p.trackS??0,0):null,stunt=gameMode==='racing'&&(pose?.kind==='loop'||pose?.kind==='jump-ramp'||pose?.kind==='jump-gap'||pose?.kind==='jump-landing'||p.p3?.airTime>.08),steps=stunt?[8.5,12.5,17]:[5.2,7.8,11.2];let bestScore=base+.22,bestSide=camera2EscapeSide,bestOffset=0,bestLift=0;for(const side of [camera2EscapeSide,-camera2EscapeSide])for(let i=0;i<steps.length;i++){const offset=steps[i],lift=(stunt?1.7:1.15)+offset*(stunt?.17:.13);camera2Candidate.copy(camTarget).addScaledVector(camera2SideVec,offset*side);camera2Candidate.y+=lift;const occ=camera2Occlusion(lookTarget,camera2Candidate,root),switchPenalty=side===camera2EscapeSide?0:(camera2Escape>.4?.08:.025),distancePenalty=i*.018,score=occ*3.6+switchPenalty+distancePenalty;if(score<bestScore){bestScore=score;bestSide=side;bestOffset=offset;bestLift=lift;if(occ<.018)break;}}camera2ChosenScore=bestScore;if(bestOffset>0&&bestScore<base*3.6+.06){camera2EscapeSide=bestSide;camera2EscapeTarget=bestOffset;camera2LiftTarget=bestLift;}else{camera2EscapeTarget=0;camera2LiftTarget=Math.min(stunt?5.2:3.5,2+base*5.5);}}else{camera2ChosenScore=0;camera2EscapeTarget=0;camera2LiftTarget=0;}}camera2Escape+=(camera2EscapeTarget-camera2Escape)*(1-Math.exp(-(camera2EscapeTarget>camera2Escape?10:5.5)*dt));camera2Lift+=(camera2LiftTarget-camera2Lift)*(1-Math.exp(-(camera2LiftTarget>camera2Lift?9:5)*dt));if(camera2Escape>.03){const dx=camTarget.x-lookTarget.x,dz=camTarget.z-lookTarget.z,dl=Math.hypot(dx,dz)||1;camera2SideVec.set(-dz/dl,0,dx/dl);camTarget.addScaledVector(camera2SideVec,camera2Escape*camera2EscapeSide);}if(camera2Lift>.02)camTarget.y+=camera2Lift;window.__breakCarsCamera2={blocked:camera2Blocked,score:camera2Score,chosenScore:camera2ChosenScore,escape:camera2Escape,target:camera2EscapeTarget,lift:camera2Lift,side:camera2EscapeSide};}
"""
    s = one(s, anchor, camera2, 'camera helper insertion')

    tail = "camera.position.lerp(camTarget,1-Math.exp(-6*dt));smoothLook.lerp(lookTarget,1-Math.exp(-9*dt));"
    s = one(s, tail, "applyCamera2(dt,p);" + tail, 'camera resolver call')
    game.write_text(s)


if __name__ == '__main__':
    apply_camera2_v1(Path('_site'))