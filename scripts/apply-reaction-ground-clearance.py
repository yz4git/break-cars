from pathlib import Path

path = Path('_site/game.js')
js = path.read_text(encoding='utf-8')

old = "const m=carMeshes[c.id],f=m.fx;f.vy-=18*dt;f.lift+=f.vy*dt;if(f.lift<=0){f.lift=0;if(f.vy<0){if(Math.abs(f.vy)>2.4){f.vy*=-.22;f.rollV*=.72;f.pitchV*=.72;}else f.vy=0;}}f.roll+=f.rollV*dt;f.pitch+=f.pitchV*dt;f.yaw+=f.yawV*dt;f.rollV*=Math.exp(-(c.dead?1.25:3.6)*dt);f.pitchV*=Math.exp(-(c.dead?1.55:4.0)*dt);f.yawV*=Math.exp(-(c.dead?1.8:4.5)*dt);if(c.dead){const targetRoll=f.wreckSide*1.48;f.roll+=(targetRoll-f.roll)*(1-Math.exp(-2.35*dt));f.pitch+=(-.13-f.pitch)*(1-Math.exp(-2.1*dt));}else if(f.lift===0){f.roll*=Math.exp(-5.1*dt);f.pitch*=Math.exp(-5.4*dt);f.yaw*=Math.exp(-5.8*dt);}m.g.rotation.order='YXZ';m.g.position.set(c.x,f.lift,c.z);m.g.rotation.set(f.pitch,c.heading+f.yaw,f.roll);"

new = "const m=carMeshes[c.id],rx=m.fx;rx.vy-=18*dt;rx.lift+=rx.vy*dt;if(rx.lift<=0){rx.lift=0;if(rx.vy<0){if(Math.abs(rx.vy)>2.4){rx.vy*=-.22;rx.rollV*=.72;rx.pitchV*=.72;}else rx.vy=0;}}rx.roll+=rx.rollV*dt;rx.pitch+=rx.pitchV*dt;rx.yaw+=rx.yawV*dt;rx.rollV*=Math.exp(-(c.dead?1.25:3.6)*dt);rx.pitchV*=Math.exp(-(c.dead?1.55:4.0)*dt);rx.yawV*=Math.exp(-(c.dead?1.8:4.5)*dt);if(c.dead){const targetRoll=rx.wreckSide*1.48;rx.roll+=(targetRoll-rx.roll)*(1-Math.exp(-2.35*dt));rx.pitch+=(-.13-rx.pitch)*(1-Math.exp(-2.1*dt));}else if(rx.lift===0){rx.roll*=Math.exp(-5.1*dt);rx.pitch*=Math.exp(-5.4*dt);rx.yaw*=Math.exp(-5.8*dt);}const rollClear=Math.abs(Math.sin(rx.roll))*1.12,pitchClear=Math.abs(Math.sin(rx.pitch))*2.24,groundClear=clamp(rollClear+pitchClear,0,2.62);m.g.rotation.order='YXZ';m.g.position.set(c.x,rx.lift+groundClear+.025,c.z);m.g.rotation.set(rx.pitch,c.heading+rx.yaw,rx.roll);"

if old not in js:
    raise SystemExit('ground-clearance patch failed: reaction visual marker not found')

js = js.replace(old, new, 1)
path.write_text(js, encoding='utf-8')
print('reaction ground clearance applied')
