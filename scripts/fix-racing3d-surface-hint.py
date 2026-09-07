"""Keep tire/chassis contact sampling on the car's current RAMPAGE 3D branch."""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Racing3D surface hint {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_racing3d_surface_hint(target: Path) -> None:
    course = target / 'racing3d.js'
    s = course.read_text()
    s = one(
        s,
        "export function sampleRaceSurface(x,y,z,up={x:0,y:1,z:0},forChassis=false){\n const p=projectRacePoint(x,y,z,null,true);if(!p)return null;",
        "export function sampleRaceSurface(x,y,z,up={x:0,y:1,z:0},forChassis=false,hintS=null){\n const p=projectRacePoint(x,y,z,hintS,true);if(!p)return null;",
        'race surface signature',
    )
    course.write_text(s)

    physics = target / 'physics3d.js'
    s = physics.read_text()
    s = one(
        s,
        "export function samplePhysicsSurface(mode,x,y,z,up={x:0,y:1,z:0},forChassis=false) {\n  if (mode==='racing') {\n    const race=sampleRaceSurface(x,y,z,up,forChassis);",
        "export function samplePhysicsSurface(mode,x,y,z,up={x:0,y:1,z:0},forChassis=false,hintS=null) {\n  if (mode==='racing') {\n    const race=sampleRaceSurface(x,y,z,up,forChassis,hintS);",
        'physics surface signature',
    )
    s = one(
        s,
        "samplePhysicsSurface(w.mode,a.x,a.y,a.z,up,false)",
        "samplePhysicsSurface(w.mode,a.x,a.y,a.z,up,false,w.mode==='racing'?c.trackS:null)",
        'wheel contact hint',
    )
    s = one(
        s,
        "samplePhysicsSurface(w.mode,p.x,p.y,p.z,up,true)",
        "samplePhysicsSurface(w.mode,p.x,p.y,p.z,up,true,w.mode==='racing'?c.trackS:null)",
        'chassis contact hint',
    )
    physics.write_text(s)


if __name__ == '__main__':
    apply_racing3d_surface_hint(Path('_site'))
