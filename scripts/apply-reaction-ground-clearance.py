from pathlib import Path

path = Path('_site/game.js')
js = path.read_text(encoding='utf-8')

old = "m.g.rotation.order='YXZ';m.g.position.set(c.x,rxn.lift,c.z);m.g.rotation.set(rxn.pitch,c.heading+rxn.yaw,rxn.roll);"
new = "const rollClear=Math.abs(Math.sin(rxn.roll))*1.12,pitchClear=Math.abs(Math.sin(rxn.pitch))*2.24,groundClear=clamp(rollClear+pitchClear,0,2.62);m.g.rotation.order='YXZ';m.g.position.set(c.x,rxn.lift+groundClear+.025,c.z);m.g.rotation.set(rxn.pitch,c.heading+rxn.yaw,rxn.roll);"

if old not in js:
    raise SystemExit('ground-clearance patch failed: reaction transform marker not found')

js = js.replace(old, new, 1)
path.write_text(js, encoding='utf-8')
print('reaction ground clearance applied')
