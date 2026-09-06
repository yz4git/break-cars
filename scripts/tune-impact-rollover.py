from pathlib import Path

path = Path('_site/game.js')
js = path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global js
    if old not in js:
        raise SystemExit(f'rollover tuning failed: {label} marker not found')
    js = js.replace(old, new, 1)

replace_once(
    "wreckSide:c.id%2?1:-1}};}",
    "wreckSide:c.id%2?1:-1,wreckTilt:0,wreckPitch:0}};}",
    'reaction state',
)

old_kick = "function kickReaction(id,power,dx,dz,wreck=false){const c=world.cars[id],m=carMeshes[id];if(!c||!m)return;const f=m.fx,p=clamp((power-5)/18,0,1),len=Math.hypot(dx,dz)||1,nx=dx/len,nz=dz/len,right=Math.cos(c.heading)*nx-Math.sin(c.heading)*nz,front=Math.sin(c.heading)*nx+Math.cos(c.heading)*nz,side=Math.sign(right)||((id&1)?1:-1);f.vy=Math.max(f.vy,2.2+p*6.2+(wreck?3.2:0));f.lift=Math.max(f.lift,.02);f.rollV+=side*(2.4+p*6.4+(wreck?5.8:0));f.pitchV+=-Math.sign(front||1)*(1+p*3.5)+(Math.random()-.5)*1.2;f.yawV+=side*(.8+p*2.8);if(wreck)f.wreckSide=side;}"
new_kick = "function kickReaction(id,power,dx,dz,wreck=false){const c=world.cars[id],m=carMeshes[id];if(!c||!m)return;const f=m.fx,len=Math.hypot(dx,dz)||1,nx=dx/len,nz=dz/len,right=Math.cos(c.heading)*nx-Math.sin(c.heading)*nz,front=Math.sin(c.heading)*nx+Math.cos(c.heading)*nz,side=Math.sign(right)||((id&1)?1:-1),sideFactor=Math.abs(right),frontFactor=Math.abs(front),severity=clamp((power-7)/20,0,1),rollFactor=severity*(.18+sideFactor*.82),pitchFactor=severity*(.2+frontFactor*.8);if(power>9){f.vy=Math.max(f.vy,.5+severity*(1.6+sideFactor*2.8)+(wreck?severity*1.6:0));f.lift=Math.max(f.lift,.01);}f.rollV+=side*rollFactor*(.7+severity*3.9);f.pitchV+=-Math.sign(front||1)*pitchFactor*(.55+severity*2.7)+(Math.random()-.5)*severity*.45;f.yawV+=side*severity*(.22+sideFactor*1.35);if(wreck){f.wreckSide=side;const rollover=severity*sideFactor;if(rollover>.62){const t=clamp((rollover-.62)/.38,0,1);f.wreckTilt=1.08+t*.45;f.wreckPitch=clamp(-front*.16,-.12,.12);}else{f.wreckTilt=0;f.wreckPitch=0;}}}"
replace_once(old_kick, new_kick, 'impact reaction')

replace_once(
    "kickReaction(e.car,e.power,dx,dz,true);c.vx+=dx*2.2;c.vz+=dz*2.2;",
    "const wreckPower=clamp(6+speed*.78,8,30);kickReaction(e.car,wreckPower,dx,dz,true);c.vx+=dx*2.2;c.vz+=dz*2.2;",
    'wreck severity',
)

replace_once(
    "if(c.dead){const targetRoll=rxn.wreckSide*1.48;rxn.roll+=(targetRoll-rxn.roll)*(1-Math.exp(-2.35*dt));rxn.pitch+=(-.13-rxn.pitch)*(1-Math.exp(-2.1*dt));}",
    "if(c.dead){const targetRoll=rxn.wreckSide*rxn.wreckTilt,targetPitch=rxn.wreckPitch;rxn.roll+=(targetRoll-rxn.roll)*(1-Math.exp(-(rxn.wreckTilt>0?2.35:3.4)*dt));rxn.pitch+=(targetPitch-rxn.pitch)*(1-Math.exp(-3.2*dt));if(rxn.wreckTilt===0&&rxn.lift===0){rxn.rollV*=Math.exp(-4.8*dt);rxn.pitchV*=Math.exp(-5.0*dt);}}",
    'wreck target angle',
)

path.write_text(js, encoding='utf-8')
print('impact-scaled rollover tuning applied')
