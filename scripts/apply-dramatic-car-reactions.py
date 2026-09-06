from pathlib import Path

path = Path('_site/game.js')
js = path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global js
    if old not in js:
        raise SystemExit(f'reaction patch failed: {label} marker not found')
    js = js.replace(old, new, 1)

replace_once(
    "scene.add(g);return{g,body,parts,wheels,number,wreckMarker,wrecked:false};}",
    "scene.add(g);return{g,body,parts,wheels,number,wreckMarker,wrecked:false,fx:{lift:0,vy:0,roll:0,pitch:0,yaw:0,rollV:0,pitchV:0,yawV:0,wreckSide:c.id%2?1:-1}};}",
    'car reaction state',
)

old_events = "function events(){const player=world.cars[0];for(const e of world.events){if(e.type==='impact'||e.type==='wall'){const n=Math.min(34,Math.max(8,Math.round(e.power*1.15)));for(let i=0;i<n;i++)emit(e.x,.75,e.z,e.power,'spark');if(e.power>10)for(let i=0;i<Math.min(10,Math.round(e.power/2.8));i++)emit(e.x,.7,e.z,e.power,'debris');if(e.a===0||e.b===0||e.car===0){shake=Math.min(.95,e.power*.035);sound(e.power);if(e.type==='impact')toast(e.power>18?'MASSIVE IMPACT':e.power>10?'HARD HIT':'CONTACT',.8);}else if(Math.hypot(e.x-player.x,e.z-player.z)<20)sound(e.power*.3);}if(e.type==='wreck'){for(let i=0;i<52;i++)emit(e.x,.9,e.z,e.power,'spark');for(let i=0;i<22;i++)emit(e.x,1,e.z,e.power,'flame');for(let i=0;i<20;i++)emit(e.x,.7,e.z,e.power,'debris');for(let i=0;i<12;i++)emit(e.x,1.1,e.z,e.power,'smoke');blast(e.x,e.z,e.power);const near=Math.hypot(e.x-player.x,e.z-player.z);if(e.car===0||near<26){shake=Math.max(shake,near<10?1.35:.9);sound(55);}if(e.by===0)toast('WRECK +500',2.2);else if(e.car!==0&&toastTime<.2)toast(`CAR ${String(e.car+1).padStart(2,'0')} DESTROYED`,1.6);}}}"

new_events = "function kickReaction(id,power,dx,dz,wreck=false){const c=world.cars[id],m=carMeshes[id];if(!c||!m)return;const f=m.fx,p=clamp((power-5)/18,0,1),len=Math.hypot(dx,dz)||1,nx=dx/len,nz=dz/len,right=Math.cos(c.heading)*nx-Math.sin(c.heading)*nz,front=Math.sin(c.heading)*nx+Math.cos(c.heading)*nz,side=Math.sign(right)||((id&1)?1:-1);f.vy=Math.max(f.vy,2.2+p*6.2+(wreck?3.2:0));f.lift=Math.max(f.lift,.02);f.rollV+=side*(2.4+p*6.4+(wreck?5.8:0));f.pitchV+=-Math.sign(front||1)*(1+p*3.5)+(Math.random()-.5)*1.2;f.yawV+=side*(.8+p*2.8);if(wreck)f.wreckSide=side;}\nfunction events(){const player=world.cars[0];for(const e of world.events){if(e.type==='impact'||e.type==='wall'){const n=Math.min(38,Math.max(10,Math.round(e.power*1.25)));for(let i=0;i<n;i++)emit(e.x,.75,e.z,e.power,'spark');if(e.power>9)for(let i=0;i<Math.min(14,Math.round(e.power/2.2));i++)emit(e.x,.7,e.z,e.power,'debris');if(e.type==='impact'){const a=world.cars[e.a],b=world.cars[e.b];if(a&&b){let dx=b.x-a.x,dz=b.z-a.z,len=Math.hypot(dx,dz)||1;dx/=len;dz/=len;kickReaction(e.a,e.power,-dx,-dz,a.dead);kickReaction(e.b,e.power,dx,dz,b.dead);if(e.power>8){const push=clamp((e.power-8)*.26,0,5.8);a.vx-=dx*push;a.vz-=dz*push;b.vx+=dx*push;b.vz+=dz*push;}}}else{const c=world.cars[e.car];if(c){const len=Math.hypot(c.x,c.z)||1,nx=c.x/len,nz=c.z/len;kickReaction(e.car,e.power,nx,nz,c.dead);if(e.power>9){const rebound=clamp((e.power-8)*.20,0,4.5);c.vx-=nx*rebound;c.vz-=nz*rebound;}}}if(e.a===0||e.b===0||e.car===0){shake=Math.min(1.2,e.power*.045);sound(e.power);if(e.type==='impact')toast(e.power>18?'MASSIVE IMPACT':e.power>10?'HARD HIT':'CONTACT',.8);}else if(Math.hypot(e.x-player.x,e.z-player.z)<20)sound(e.power*.3);}if(e.type==='wreck'){for(let i=0;i<60;i++)emit(e.x,.9,e.z,e.power,'spark');for(let i=0;i<28;i++)emit(e.x,1,e.z,e.power,'flame');for(let i=0;i<26;i++)emit(e.x,.7,e.z,e.power,'debris');for(let i=0;i<16;i++)emit(e.x,1.1,e.z,e.power,'smoke');blast(e.x,e.z,e.power);const c=world.cars[e.car];if(c){const speed=Math.hypot(c.vx,c.vz),dx=speed>.5?c.vx/speed:Math.sin(c.heading),dz=speed>.5?c.vz/speed:Math.cos(c.heading);kickReaction(e.car,e.power,dx,dz,true);c.vx+=dx*2.2;c.vz+=dz*2.2;c.omega=clamp(c.omega+(e.car%2?1:-1)*1.6,-3,3);}const near=Math.hypot(e.x-player.x,e.z-player.z);if(e.car===0||near<26){shake=Math.max(shake,near<10?1.55:1.05);sound(62);}if(e.by===0)toast('WRECK +500',2.2);else if(e.car!==0&&toastTime<.2)toast(`CAR ${String(e.car+1).padStart(2,'0')} DESTROYED`,1.6);}}}"
replace_once(old_events, new_events, 'events')

old_visual = "function visuals(dt){const p=world.cars[0];smokeClock+=dt;skidClock+=dt;for(const c of world.cars){const m=carMeshes[c.id];m.g.position.set(c.x,0,c.z);m.g.rotation.y=c.heading;if(c.dead&&!m.wrecked){"
new_visual = "function visuals(dt){const p=world.cars[0];smokeClock+=dt;skidClock+=dt;for(const c of world.cars){const m=carMeshes[c.id],f=m.fx;f.vy-=18*dt;f.lift+=f.vy*dt;if(f.lift<=0){f.lift=0;if(f.vy<0){if(Math.abs(f.vy)>2.4){f.vy*=-.22;f.rollV*=.72;f.pitchV*=.72;}else f.vy=0;}}f.roll+=f.rollV*dt;f.pitch+=f.pitchV*dt;f.yaw+=f.yawV*dt;f.rollV*=Math.exp(-(c.dead?1.25:3.6)*dt);f.pitchV*=Math.exp(-(c.dead?1.55:4.0)*dt);f.yawV*=Math.exp(-(c.dead?1.8:4.5)*dt);if(c.dead){const targetRoll=f.wreckSide*1.48;f.roll+=(targetRoll-f.roll)*(1-Math.exp(-2.35*dt));f.pitch+=(-.13-f.pitch)*(1-Math.exp(-2.1*dt));}else if(f.lift===0){f.roll*=Math.exp(-5.1*dt);f.pitch*=Math.exp(-5.4*dt);f.yaw*=Math.exp(-5.8*dt);}m.g.rotation.order='YXZ';m.g.position.set(c.x,f.lift,c.z);m.g.rotation.set(f.pitch,c.heading+f.yaw,f.roll);if(c.dead&&!m.wrecked){"
replace_once(old_visual, new_visual, 'visual integration')

replace_once(
    "m.body.rotation.z=c.dead?(c.id%2?.15:-.15):-c.omega*Math.hypot(c.vx,c.vz)*.0015;m.body.rotation.x=c.dead?-.08:c.throttle*.012+Math.sin(world.time*23+c.id)*Math.hypot(c.vx,c.vz)*.0007;",
    "m.body.rotation.z=c.dead?(c.id%2?.12:-.12):-c.omega*Math.hypot(c.vx,c.vz)*.0025;m.body.rotation.x=c.dead?-.05:c.throttle*.016+Math.sin(world.time*23+c.id)*Math.hypot(c.vx,c.vz)*.0011;",
    'body reaction tuning',
)

path.write_text(js, encoding='utf-8')
print('dramatic car reactions applied')
