"""Robust production integration for full 3D physics + the dedicated Wrecking Racing 3D course."""
from pathlib import Path
import importlib.util
import re


def load_legacy_full_patch():
    path=Path(__file__).with_name('apply-full-physics3d.py')
    spec=importlib.util.spec_from_file_location('break_cars_full_patch_base',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

base=load_legacy_full_patch()


def once(text,old,new,label):
    n=text.count(old)
    if n!=1:raise RuntimeError(f'Racing3D {label}: expected 1 match, found {n}')
    return text.replace(old,new,1)


def regex_once(text,pattern,repl,label):
    out,n=re.subn(pattern,repl,text,count=1,flags=re.S)
    if n!=1:raise RuntimeError(f'Racing3D {label}: expected 1 regex match, found {n}')
    return out


def patch_physics3d(path:Path):
    s=path.read_text()
    s="import {sampleRaceSurface,racePointAt,race3DFeatureSpec} from './racing3d.js?v=wr3d-v1';\n"+s
    s=once(s,"works-full-physics3d-v4","works-full-physics3d-v5-racing3d","physics id")

    s=regex_once(s,r"export function samplePhysicsSurface\(mode,x,y,z,up=\{x:0,y:1,z:0\},forChassis=false\) \{.*?\n\}\n\nfunction inertia",'''export function samplePhysicsSurface(mode,x,y,z,up={x:0,y:1,z:0},forChassis=false) {
  if (mode==='racing') {
    const race=sampleRaceSurface(x,y,z,up,forChassis);
    if (race) return race;
    const point={x,y:-7.5,z},normal={x:0,y:1,z:0};
    return {point,normal,kind:'race-void',d:y+7.5,align:up.y};
  }
  const floor=floorSurface(x,z),surfaces=[floor];
  const ramp=rampSurface(x,z); if (ramp) surfaces.push(ramp);
  const loop=loopSurface(x,y,z); if (loop && loop.radialError<2.3) surfaces.push(loop);
  let best=null,bestScore=Infinity; const p={x,y,z};
  for (const s of surfaces) {
    const d=dot(sub(p,s.point),s.normal),align=dot(up,s.normal);
    if (!forChassis && align<.10) continue;
    const score=Math.abs(d) + (s.kind==='loop' ? .015 : 0) + (align<0 ? .8 : 0);
    if (score<bestScore) { bestScore=score; best={...s,d,align}; }
  }
  return best || {...floor,d:y-floor.point.y,align:up.y};
}

function inertia''','race surface')

    old_body='''function makeBody(c,type) {
  const mass=Math.max(.65,type.mass||1),I=inertia(mass),q=yawQuat(c.heading||0),ground=baseHeight(c.x,c.z).h;
  return {active:true,px:c.x,py:ground+COM_VISUAL_Y,pz:c.z,qx:q.x,qy:q.y,qz:q.z,qw:q.w,vx:c.vx||0,vy:0,vz:c.vz||0,wx:0,wy:c.omega||0,wz:0,mass,invMass:1/mass,invIx:1/I.x,invIy:1/I.y,invIz:1/I.z,grounded:false,groundedWheels:0,wheelCompression:[0,0,0,0],wheelNormal:[0,0,0,0],airTime:0,lastLandingAt:-99,lastSyncX:c.x,lastSyncZ:c.z,lastSyncVx:c.vx||0,lastSyncVz:c.vz||0};
}
export function ensureFullPhysics(w,types) { if (!w.fullPhysics) w.fullPhysics={id:FULL_PHYSICS_ID,enabled:true}; for (const c of w.cars) if (!c.p3 || !c.p3.active) c.p3=makeBody(c,types[c.type]); return w.fullPhysics; }
export function resetFullPhysicsBody(w,c,types) { c.p3=makeBody(c,types[c.type]); return c.p3; }'''
    new_body='''function frameQuat(forward,up,right) {
  const m00=right.x,m01=up.x,m02=forward.x,m10=right.y,m11=up.y,m12=forward.y,m20=right.z,m21=up.z,m22=forward.z,tr=m00+m11+m22;let x,y,z,w,s;
  if(tr>0){s=Math.sqrt(tr+1)*2;w=.25*s;x=(m21-m12)/s;y=(m02-m20)/s;z=(m10-m01)/s;}
  else if(m00>m11&&m00>m22){s=Math.sqrt(1+m00-m11-m22)*2;w=(m21-m12)/s;x=.25*s;y=(m01+m10)/s;z=(m02+m20)/s;}
  else if(m11>m22){s=Math.sqrt(1+m11-m00-m22)*2;w=(m02-m20)/s;x=(m01+m10)/s;y=.25*s;z=(m12+m21)/s;}
  else{s=Math.sqrt(1+m22-m00-m11)*2;w=(m10-m01)/s;x=(m02+m20)/s;y=(m12+m21)/s;z=.25*s;}
  const l=Math.hypot(x,y,z,w)||1;return{x:x/l,y:y/l,z:z/l,w:w/l};
}
function makeBody(c,type,mode='colosseum') {
  const mass=Math.max(.65,type.mass||1),I=inertia(mass);let q,px=c.x,py,pz=c.z;
  if(mode==='racing'){
    const p=racePointAt(c.trackS??0,c.lane??0);q=frameQuat(p.forward,p.up,p.right);px=p.x+p.up.x*COM_VISUAL_Y;py=p.y+p.up.y*COM_VISUAL_Y;pz=p.z+p.up.z*COM_VISUAL_Y;
  }else{q=yawQuat(c.heading||0);py=baseHeight(c.x,c.z).h+COM_VISUAL_Y;}
  return {active:true,px,py,pz,qx:q.x,qy:q.y,qz:q.z,qw:q.w,vx:c.vx||0,vy:0,vz:c.vz||0,wx:0,wy:c.omega||0,wz:0,mass,invMass:1/mass,invIx:1/I.x,invIy:1/I.y,invIz:1/I.z,grounded:false,groundedWheels:0,wheelCompression:[0,0,0,0],wheelNormal:[0,0,0,0],airTime:0,lastLandingAt:-99,lastSyncX:c.x,lastSyncZ:c.z,lastSyncVx:c.vx||0,lastSyncVz:c.vz||0};
}
export function ensureFullPhysics(w,types) { if (!w.fullPhysics) w.fullPhysics={id:FULL_PHYSICS_ID,enabled:true}; for (const c of w.cars) if (!c.p3 || !c.p3.active) c.p3=makeBody(c,types[c.type],w.mode); return w.fullPhysics; }
export function resetFullPhysicsBody(w,c,types) { c.p3=makeBody(c,types[c.type],w.mode); return c.p3; }'''
    s=once(s,old_body,new_body,'race spawn frame')
    s=once(s,'function adoptExternal(c,types) {','function adoptExternal(c,types,mode) {','adopt signature')
    s=once(s,'c.p3=makeBody(c,types[c.type]); return;','c.p3=makeBody(c,types[c.type],mode); return;','adopt race pose')

    s=regex_once(s,r"function raceBoundary\(w,c,ctx\) \{.*?\n\}\n\nfunction sphereWorld",'''function raceBoundary(w,c,ctx) {
  if (w.mode!=='racing') return; syncLegacy(c); const ox=c.x,oz=c.z,wall=ctx.constrainTrack(c),b=c.p3;
  if (wall?.correction) { b.px+=wall.correction.x; b.py+=wall.correction.y; b.pz+=wall.correction.z; c.x=b.px;c.z=b.pz; }
  else if (c.x!==ox||c.z!==oz) { b.px=c.x; b.pz=c.z; }
  if (wall&&wall.speed>0) { const {nx,ny=0,nz,speed:v}=wall; b.vx-=nx*v*1.28; b.vy-=ny*v*1.28; b.vz-=nz*v*1.28; if (v>6&&w.time-c.hitAt>.4) { ctx.hit(w,c,(v-5)*.30,nx,nz); w.events.push({type:'wall',car:c.id,x:b.px,y:b.py,z:b.pz,power:v,nx,ny,nz}); } }
}

function sphereWorld''','3D race boundary')
    s=once(s,'for (const c of w.cars) { adoptExternal(c,ctx.TYPES); syncLegacy(c); }','for (const c of w.cars) { adoptExternal(c,ctx.TYPES,w.mode); syncLegacy(c); }','adopt mode call')
    s=once(s,'export function fullPhysicsFeatureSpec() { return {loop:{...LOOP},ramp:{...RAMP},bumps:BUMPS.map(v=>[...v])}; }','export function fullPhysicsFeatureSpec() { return {loop:{...LOOP},ramp:{...RAMP},bumps:BUMPS.map(v=>[...v]),race:race3DFeatureSpec()}; }','feature spec')
    path.write_text(s)


def apply_full_physics3d(target:Path):
    patch_physics3d(target/'physics3d.js')
    base.patch_physics(target/'physics.js')
    base.patch_game(target/'game.js')
