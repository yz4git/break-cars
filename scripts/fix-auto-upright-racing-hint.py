"""Keep player auto-upright recovery on the current RAMPAGE 3D branch."""
from pathlib import Path


def apply_auto_upright_racing_hint(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()
    old = "const up=bodyUp(b),surface=samplePhysicsSurface(w.mode,b.px,b.py,b.pz,{x:0,y:1,z:0},true);"
    new = "const up=bodyUp(b),surface=samplePhysicsSurface(w.mode,b.px,b.py,b.pz,{x:0,y:1,z:0},true,w.mode==='racing'?c.trackS:null);"
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'Auto upright racing hint: expected 1 match, found {count}')
    path.write_text(s.replace(old, new, 1))


if __name__ == '__main__':
    apply_auto_upright_racing_hint(Path('_site'))
