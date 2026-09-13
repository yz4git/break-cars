"""BREAK CARS v8.21: impact cinema without touching gameplay physics.

The 852x393 visual review showed that collision reactions are physically strong,
but light contact, hard hits and wrecks still share almost the same camera/audio
grammar. This pass adds a short visual-only impact sequence: hold, focus, recoil,
recover. Simulation, input, damage, velocities and course geometry remain under
the existing systems.

The effect is deliberately restrained on walls and repeated contact, suppresses
itself during MAYHEM replay/result presentation, and adds only a low-frequency
body thump on top of the existing crash noise.
"""
from pathlib import Path


def apply_impact_cinema_v821(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += r'''

/* BREAK CARS v8.21 — impact cinema: visual hold -> focus -> recoil -> recover */
const impactCinemaV821={active:false,age:99,duration:.28,hold:.03,intensity:0,tier:'IDLE',kind:'impact',x:0,z:0,hitDirX:0,hitDirZ:1,lastWorldTime:-99,holdPos:new THREE.Vector3()};
const impactCinemaFocusV821=new THREE.Vector3(),impactCinemaLookV821=new THREE.Vector3(),impactCinemaForwardV821=new THREE.Vector3(),impactCinemaRightV821=new THREE.Vector3(),impactCinemaUpV821=new THREE.Vector3(0,1,0);
const impactCinemaTelemetryV821=window.__breakCarsImpactCinemaV821={version:'8.21',hits:0,lastTier:'IDLE',lastPower:0,phase:'IDLE',visualHitStop:true,physicsChanged:false,inputBlocked:false};
function impactCinemaSuppressedV821(){return mode==='menu'||mode==='paused'||mode==='result'||document.body.classList.contains('mayhem-replay-active')||(typeof mayhemReplayPlaying!=='undefined'&&mayhemReplayPlaying);}
function impactCinemaCandidateScoreV821(e,p){
 if(!e)return 0;const power=Number(e.power)||0,x=Number.isFinite(e.x)?e.x:p.x,z=Number.isFinite(e.z)?e.z:p.z,near=Math.hypot(x-p.x,z-p.z);
 const direct=e.a===0||e.b===0||e.car===0,caused=e.type==='wreck'&&e.by===0&&near<24,nearby=near<11&&power>=16;
 if(!direct&&!caused&&!nearby)return 0;return power+(e.type==='wreck'?34:e.type==='impact'?10:0)+(direct?12:0)+(caused?8:0)-Math.min(near,20)*.15;
}
function impactCinemaBodySoundV821(power,wreck,intensity){
 if(!audioCtx||muted)return;try{const now=audioCtx.currentTime,g=audioCtx.createGain(),osc=audioCtx.createOscillator();osc.type='triangle';osc.frequency.setValueAtTime(64-16*intensity,now);osc.frequency.exponentialRampToValueAtTime(wreck?27:32,now+.13+.05*intensity);g.gain.setValueAtTime(.0001,now);g.gain.exponentialRampToValueAtTime(.028+.052*intensity+(wreck?.018:0),now+.004);g.gain.exponentialRampToValueAtTime(.0001,now+.13+.08*intensity);osc.connect(g).connect(audioCtx.destination);osc.start(now);osc.stop(now+.23);osc.onended=()=>{osc.disconnect();g.disconnect();};}catch{}
}
function impactCinemaTriggerV821(e){
 if(impactCinemaSuppressedV821())return;const p=world.cars[0],power=Number(e.power)||0,wreck=e.type==='wreck';let intensity=clamp((power+(wreck?10:0)-5)/30,.12,1);if(e.type==='wall')intensity*=.72;
 if(world.time-impactCinemaV821.lastWorldTime<.10&&impactCinemaV821.active&&intensity<impactCinemaV821.intensity+.12)return;
 let dx=(Number.isFinite(e.x)?e.x:p.x)-p.x,dz=(Number.isFinite(e.z)?e.z:p.z)-p.z;if(Math.hypot(dx,dz)<.08&&e.type==='impact'){const other=e.a===0?world.cars[e.b]:e.b===0?world.cars[e.a]:null;if(other){dx=other.x-p.x;dz=other.z-p.z;}}
 let len=Math.hypot(dx,dz);if(len<.08){dx=Math.sin(p.heading);dz=Math.cos(p.heading);len=1;}dx/=len;dz/=len;
 const tier=wreck?'WRECK':intensity>.74?'MASSIVE':intensity>.39?'HARD':'CONTACT';Object.assign(impactCinemaV821,{active:true,age:0,duration:.19+.18*intensity+(wreck?.07:0),hold:.014+.036*intensity+(wreck?.014:0),intensity,tier,kind:e.type||'impact',x:Number.isFinite(e.x)?e.x:p.x,z:Number.isFinite(e.z)?e.z:p.z,hitDirX:dx,hitDirZ:dz,lastWorldTime:world.time});impactCinemaV821.holdPos.copy(camera.position);
 impactCinemaTelemetryV821.hits++;impactCinemaTelemetryV821.lastTier=tier;impactCinemaTelemetryV821.lastPower=power;impactCinemaTelemetryV821.phase='HOLD';document.body.dataset.impactCinemaV821=tier.toLowerCase();
 // Replace part of the old random shake with a readable directional camera recoil.
 shake=Math.min(shake,.38+.44*intensity+(wreck?.12:0));impactCinemaBodySoundV821(power,wreck,intensity);
}
function impactCinemaStopV821(){impactCinemaV821.active=false;impactCinemaTelemetryV821.phase='IDLE';delete document.body.dataset.impactCinemaV821;const flash=$('flash');if(flash)flash.style.removeProperty('box-shadow');}
function impactCinemaApplyV821(dt){
 const s=impactCinemaV821;if(!s.active)return;if(impactCinemaSuppressedV821()){impactCinemaStopV821();return;}s.age+=dt;const life=clamp(1-s.age/s.duration,0,1),holdLife=s.age<s.hold?1-s.age/Math.max(.001,s.hold):0;
 const phase=s.age<s.hold?'HOLD':s.age<s.hold+.075?'FOCUS':s.age<s.duration*.68?'RECOIL':'RECOVER';impactCinemaTelemetryV821.phase=phase;
 camera.getWorldDirection(impactCinemaForwardV821);impactCinemaRightV821.crossVectors(impactCinemaForwardV821,impactCinemaUpV821).normalize();
 if(holdLife>0)camera.position.lerp(s.holdPos,holdLife*(.46+.20*s.intensity));
 const side=Math.sign(s.hitDirX*impactCinemaRightV821.x+s.hitDirZ*impactCinemaRightV821.z)||1,recoil=(.035+.23*s.intensity)*life*life*Math.sin(clamp(s.age/(s.hold+.085),0,1)*Math.PI);camera.position.addScaledVector(impactCinemaRightV821,-side*recoil);camera.position.y+=recoil*.16;
 const focusIn=clamp((s.age-s.hold)/.055,0,1),focusOut=clamp((s.duration-s.age)/.13,0,1),focusWeight=focusIn*focusOut*(s.kind==='wall'?.07:.10+.14*s.intensity);impactCinemaFocusV821.set(s.x,.72,s.z);impactCinemaLookV821.copy(smoothLook).lerp(impactCinemaFocusV821,focusWeight);camera.lookAt(impactCinemaLookV821);
 const fovKick=holdLife*(-2.0-4.2*s.intensity)+Math.sin(Math.max(0,s.age-s.hold)*20)*life*(.7+1.9*s.intensity);camera.fov=clamp(camera.fov+fovKick,46,82);camera.updateProjectionMatrix();
 const flash=$('flash');if(flash){const pulse=holdLife*(.12+.24*s.intensity)+life*(.025+.055*s.intensity),base=Number.parseFloat(flash.style.opacity)||0;flash.style.opacity=String(Math.max(base,pulse));flash.style.boxShadow=s.tier==='WRECK'?'inset 0 0 150px 34px #ff472dcc':s.tier==='MASSIVE'?'inset 0 0 135px 28px #ff6a3aaa':'inset 0 0 115px 22px #f59a5a77';}
 if(s.age>=s.duration)impactCinemaStopV821();
}
const impactCinemaEventsV821Base=events;
events=function(){let best=null,bestScore=0;const p=world.cars[0];for(const e of world.events||[]){const score=impactCinemaCandidateScoreV821(e,p);if(score>bestScore){best=e;bestScore=score;}}impactCinemaEventsV821Base();if(best)impactCinemaTriggerV821(best);};
const impactCinemaVisualsV821Base=visuals;
visuals=function(dt){impactCinemaVisualsV821Base(dt);impactCinemaApplyV821(dt);};
'''
    game.write_text(s)


if __name__ == '__main__':
    apply_impact_cinema_v821(Path('_site'))
