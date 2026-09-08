"""Add player-only automatic upright recovery to the final full-physics runtime."""
from pathlib import Path
import re


def regex_once(text: str, pattern: str, repl: str, label: str) -> str:
    out, n = re.subn(pattern, repl, text, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError(f"Auto upright {label}: expected 1 match, found {n}")
    return out


def patch_physics3d(path: Path) -> None:
    s = path.read_text()
    helper = r'''
export function updatePlayerAutoUpright(w,dt=1/60){
  const c=w.cars?.[0],b=c?.p3;
  if(!b?.active||c.dead||c.finished){if(c)c.autoUprightTime=0;return false;}
  const up=bodyUp(b),surface=samplePhysicsSurface(w.mode,b.px,b.py,b.pz,{x:0,y:1,z:0},true);
  const nearSurface=!!surface&&surface.kind!=='race-void'&&Number.isFinite(surface.d)&&Math.abs(surface.d)<1.65;
  const raceProgressKind=w.mode==='racing'?racePointAt(c.trackS??surface?.s??0).kind:null;
  // "Fully upside down" means the roof is substantially below the chassis,
  // no wheel is carrying the car, and the chassis is actually near a drivable surface.
  // Use authoritative race progress, not nearest-surface projection, to identify
  // a real loop: self-crossings can otherwise make a loop car look like it is
  // upside-down on a nearby normal road ribbon.
  const fullyFlipped=up.y<-.62&&b.groundedWheels===0&&nearSurface&&raceProgressKind!=='loop';
  c.autoUprightTime=fullyFlipped?(c.autoUprightTime||0)+dt:0;
  if(c.autoUprightTime<5)return false;

  let q,px,py,pz,heading=c.heading||0;
  if(w.mode==='racing'&&surface.s!=null){
    const lane=Math.max(-6,Math.min(6,surface.lane||0)),p=racePointAt(surface.s,lane);
    q=frameQuat(p.forward,p.up,p.right);px=p.x+p.up.x*(COM_VISUAL_Y+.14);py=p.y+p.up.y*(COM_VISUAL_Y+.14);pz=p.z+p.up.z*(COM_VISUAL_Y+.14);heading=p.heading;c.trackS=p.s;
  }else{
    const n=surface?.normal||{x:0,y:1,z:0},point=surface?.point||{x:b.px,y:baseHeight(b.px,b.pz).h,z:b.pz};
    let f={x:Math.sin(heading),y:0,z:Math.cos(heading)};f=sub(f,mul(n,dot(f,n)));
    if(Math.hypot(f.x,f.y,f.z)<.1)f=Math.abs(n.y)<.8?norm(cross({x:0,y:1,z:0},n)):{x:0,y:0,z:1};else norm(f);
    const right=norm(cross(n,f));q=frameQuat(f,n,right);px=point.x+n.x*(COM_VISUAL_Y+.14);py=point.y+n.y*(COM_VISUAL_Y+.14);pz=point.z+n.z*(COM_VISUAL_Y+.14);
  }
  Object.assign(b,{px,py,pz,qx:q.x,qy:q.y,qz:q.z,qw:q.w,vx:0,vy:0,vz:0,wx:0,wy:0,wz:0,grounded:false,groundedWheels:0,airTime:0});
  c.heading=heading;c.vx=0;c.vz=0;c.omega=0;c.autoUprightTime=0;syncLegacy(c);
  w.events.push({type:'auto-upright',car:0,x:b.px,y:b.py,z:b.pz});
  return true;
}

'''
    s = regex_once(s, r"\nexport function stepFullPhysics\(w,input,dt=1/60,autoplay=false,ctx\) \{", "\n" + helper + "export function stepFullPhysics(w,input,dt=1/60,autoplay=false,ctx) {", "helper insertion")
    s = regex_once(
        s,
        r"(for \(const c of w\.cars\) syncLegacy\(c\);\n  \}\n)(  if \(w\.mode==='racing'\))",
        r"\1  updatePlayerAutoUpright(w,dt);\n\2",
        "step call",
    )
    path.write_text(s)


def patch_game(path: Path) -> None:
    s = path.read_text()
    s = regex_once(
        s,
        r"function events\(\)\{const player=world\.cars\[0\];for\(const e of world\.events\)\{",
        "function events(){const player=world.cars[0];for(const e of world.events){if(e.type==='auto-upright'){toast('AUTO RECOVERY',1.3);shake=Math.max(shake,.08);continue;}",
        "recovery feedback",
    )
    path.write_text(s)


def apply_player_auto_upright(target: Path) -> None:
    patch_physics3d(target / 'physics3d.js')
    patch_game(target / 'game.js')


if __name__ == '__main__':
    apply_player_auto_upright(Path('_site'))
