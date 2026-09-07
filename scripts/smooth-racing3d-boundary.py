"""Remove one-frame RAMPAGE 3D correction warps while preserving physical response."""
from pathlib import Path


def apply_smooth_racing3d_boundary(target: Path) -> None:
    path = target / 'physics3d.js'
    s = path.read_text()

    old_boundary = """function raceBoundary(w,c,ctx) {
  if (w.mode!=='racing') return; syncLegacy(c); const ox=c.x,oz=c.z,wall=ctx.constrainTrack(c),b=c.p3;
  if (wall?.correction) { b.px+=wall.correction.x; b.py+=wall.correction.y; b.pz+=wall.correction.z; c.x=b.px;c.z=b.pz; }
  else if (c.x!==ox||c.z!==oz) { b.px=c.x; b.pz=c.z; }
  if (wall&&wall.speed>0) { const {nx,ny=0,nz,speed:v}=wall; b.vx-=nx*v*1.28; b.vy-=ny*v*1.28; b.vz-=nz*v*1.28; if (v>6&&w.time-c.hitAt>.4) { ctx.hit(w,c,(v-5)*.30,nx,nz); w.events.push({type:'wall',car:c.id,x:b.px,y:b.py,z:b.pz,power:v,nx,ny,nz}); } }
}"""
    new_boundary = """function raceBoundary(w,c,ctx) {
  if (w.mode!=='racing') return; syncLegacy(c); const ox=c.x,oz=c.z,wall=ctx.constrainTrack(c),b=c.p3;
  if (wall?.correction) {
    // constrainTrack reports the full penetration vector. Applying all of it in
    // one physics substep looks like a teleport on hard landings/pile-ups, so
    // depenetrate by at most 0.38 m per substep while velocity response does
    // the rest. Two 120 Hz substeps cap correction at 0.76 m per rendered frame.
    const cx=wall.correction.x,cy=wall.correction.y,cz=wall.correction.z,len=Math.hypot(cx,cy,cz),maxStep=.38,k=len>maxStep?maxStep/len:1;
    b.px+=cx*k;b.py+=cy*k;b.pz+=cz*k;c.x=b.px;c.z=b.pz;
  } else if (c.x!==ox||c.z!==oz) { b.px=c.x; b.pz=c.z; }
  if (wall&&wall.speed>0) { const {nx,ny=0,nz,speed:v}=wall; b.vx-=nx*v*1.28; b.vy-=ny*v*1.28; b.vz-=nz*v*1.28; if (v>6&&w.time-c.hitAt>.4) { ctx.hit(w,c,(v-5)*.30,nx,nz); w.events.push({type:'wall',car:c.id,x:b.px,y:b.py,z:b.pz,power:v,nx,ny,nz}); } }
}"""
    count = s.count(old_boundary)
    if count != 1:
        raise RuntimeError(f'Smooth Racing3D boundary: expected 1 match, found {count}')
    s = s.replace(old_boundary, new_boundary, 1)

    old_pair = "const n=ct.n,cor=ct.over*.34/Math.min(3,contacts.length);"
    new_pair = "const n=ct.n,rawCor=ct.over*.34/Math.min(3,contacts.length),cor=w.mode==='racing'?Math.min(rawCor,.14):rawCor;"
    count = s.count(old_pair)
    if count != 1:
        raise RuntimeError(f'Smooth Racing3D vehicle depenetration: expected 1 match, found {count}')
    s = s.replace(old_pair, new_pair, 1)

    path.write_text(s)


if __name__ == '__main__':
    apply_smooth_racing3d_boundary(Path('_site'))
