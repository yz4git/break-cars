from pathlib import Path

path = Path('_site/game.js')
js = path.read_text(encoding='utf-8')
start_marker = "for(const c of world.cars){const m=carMeshes[c.id],f=m.fx;"
end_marker = "if(c.dead&&!m.wrecked){"
start = js.find(start_marker)
if start < 0:
    raise SystemExit('reaction variable fix failed: start marker not found')
end = js.find(end_marker, start)
if end < 0:
    raise SystemExit('reaction variable fix failed: end marker not found')
segment = js[start:end]
segment = segment.replace(',f=m.fx;', ',rxn=m.fx;').replace('f.', 'rxn.')
js = js[:start] + segment + js[end:]
path.write_text(js, encoding='utf-8')
print('reaction variable collision fixed')
