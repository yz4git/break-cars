"""SKY FORGE post-loop physical stabilizer.

The vertical loop remains fully free 6DoF.  On the first normal-road section
after the loop, a short visible guide strip applies forward force and a roll
controller only while the chassis is misaligned with the road normal.  It never
writes position, quaternion, velocity, trackS, or raceDistance directly.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'SKY exit v5 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_sky_loop_exit_v5(target: Path) -> None:
    physics = target / 'physics3d.js'
    s = physics.read_text()
    anchor = "wheelForces(w,c,u,ctx,dt,acc);rampageExitStabilizer(w,c,acc,ctx);"
    helper = """wheelForces(w,c,u,ctx,dt,acc);rampageExitStabilizer(w,c,acc,ctx);skyForgeExitGuide(w,c,acc,ctx);"""
    s = one(s, anchor, helper, 'physics hook')

    insert_at = "function rampageExitStabilizer(w,c,acc,ctx){"
    if insert_at not in s:
        raise RuntimeError('SKY exit v5 rampage helper anchor missing')
    sky = """function skyForgeExitGuide(w,c,acc,ctx){
  c.skyForgeExitGuide=false;
  if(w.mode!=='racing'||activeCourse.id!=='sky-forge'||!c?.p3)return;
  const b=c.p3,L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,loop=raceLoopAt(q),after=(q-loop.endS+L)%L,road=racePointAt(q);
  if(after>62||road.kind==='loop')return;
  const bu=bodyUp(b),align=dot(bu,road.up),vel={x:b.vx,y:b.vy,z:b.vz},forwardSpeed=dot(vel,road.forward);
  c.skyForgeExitGuide=true;
  // Keep enough kinetic energy for the corrective roll to happen while the
  // chassis is unloading from the loop, but do not cap or directly set speed.
  const target=align<0?16:13.5;
  if(forwardSpeed<target)addForce(acc,mul(road.forward,(target-forwardSpeed)*b.mass*6.2));
  if(align>.86)return;
  const omega={x:b.wx,y:b.wy,z:b.wz},rollRate=dot(omega,road.forward),gradient=dot(road.forward,cross(bu,road.up));
  let dir=Math.abs(gradient)>.028?Math.sign(gradient):(Math.abs(rollRate)>.12?Math.sign(rollRate):(c.id%2? -1:1));
  const urgency=ctx.clamp((.86-align)/1.86,0,1),desiredRoll=dir*(2.25+urgency*2.05);
  const rollTorque=ctx.clamp((desiredRoll-rollRate)*b.mass*3.15,-8.4*b.mass,8.4*b.mass),T=mul(road.forward,rollTorque);
  acc.tx+=T.x;acc.ty+=T.y;acc.tz+=T.z;
}

"""
    s = s.replace(insert_at, sky + insert_at, 1)
    physics.write_text(s)

    view = target / 'track-view.js'
    s = view.read_text()
    marker = ' // Jump take-off'
    if marker not in s:
        raise RuntimeError('SKY exit v5 visual anchor missing')
    visual = """ if(activeCourse.id==='sky-forge'){
  // Low-profile guide pads make the post-loop assist legible without adding a
  // billboard to the chase-camera sightline.
  for(let ss=spec.loop.endS+2;ss<=spec.loop.endS+58;ss+=4.0)for(const lane of [-5.6,-2.8,0,2.8,5.6]){const p=trackPoint(ss,lane),pad=box(group,p.x,p.y,p.z,.72,.025,.82,(Math.floor((ss-spec.loop.endS)/4)%2)?0xbffbff:0x64e8f2,true);align(pad,p);pad.position.add(new THREE.Vector3(p.up.x*.075,p.up.y*.075,p.up.z*.075));}
 }
""" + marker
    s = one(s, marker, visual, 'guide pads')
    view.write_text(s)


if __name__ == '__main__':
    apply_sky_loop_exit_v5(Path('_site'))
