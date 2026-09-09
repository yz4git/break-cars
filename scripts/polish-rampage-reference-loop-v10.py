"""Make RAMPAGE read as one continuous toy-track vertical loop.

The road itself forms the stunt. There is no hidden flat chord and no separate
hoop. The broad authored-road interval is removed, then rebuilt as a single
smooth gate-to-gate Hermite spine carrying one vertical revolution. This avoids
inheriting the old figure-eight turns inside the loop interval, which previously
made the exit tangent briefly point backward even though the visible lower legs
were separated.

The incoming and outgoing lower ramps peel to opposite sides only near the
bottom, then converge into an almost planar crown. A smooth outboard bow keeps
the whole stunt away from the nearby figure-eight branch while every offset has
zero slope at both gates, so ordinary road -> loop -> ordinary road remains a
single continuous surface.

SKY FORGE and DOUBLE ORBIT are deliberately untouched.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'RAMPAGE reference loop v10 {label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)


def apply_rampage_reference_loop_v10(target: Path) -> None:
    path = target / 'racing3d.js'
    s = path.read_text()

    old = """const gateLift=x=>.82*smooth01(x/.055)*(1-smooth01((x-.12)/.085));
   const sample=u=>{
    const spineT=startT+(endT-startT)*u,frame=roadFrameAt(spineT),phase=u-Math.sin(TAU*u)/TAU,th=phase*TAU,c=Math.cos(th),sn=Math.sin(th),en=Math.sin(Math.PI*u),env=en*en,outboard=14*env,twist=32*Math.sin(TAU*u)*env,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*.64;
    const lateral=outwardSign*(outboard+twist),pos=add(add(add(add(frame.p,mul(loopForward,horizR*sn)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lateral)),mul(ringUp,gateRise));
    const radial=norm(add(mul(ringUp,c),mul(loopForward,-sn))),loopWeight=smooth01(u/.095)*smooth01((1-u)/.095),upSeed=mixV(frame.up,radial,loopWeight);
    return{pos,frame,upSeed};
   };"""

    new = """const gateChord=len(sub(endFrame.p,startFrame.p)),baseHandle=clamp(gateChord*.78,17,25),gateLift=x=>.72*smooth01(x/.060)*(1-smooth01((x-.13)/.095));
   const hermiteBase=u=>{const u2=u*u,u3=u2*u,h00=2*u3-3*u2+1,h10=u3-2*u2+u,h01=-2*u3+3*u2,h11=u3-u2;return{x:startFrame.p.x*h00+startFrame.forward.x*baseHandle*h10+endFrame.p.x*h01+endFrame.forward.x*baseHandle*h11,y:startFrame.p.y*h00+startFrame.forward.y*baseHandle*h10+endFrame.p.y*h01+endFrame.forward.y*baseHandle*h11,z:startFrame.p.z*h00+startFrame.forward.z*baseHandle*h10+endFrame.p.z*h01+endFrame.forward.z*baseHandle*h11};};
   const sample=u=>{
    const base=hermiteBase(u),baseUp=mixV(startFrame.up,endFrame.up,smooth01(u)),frame={up:baseUp},phase=u-Math.sin(TAU*u)/TAU,th=phase*TAU,c=Math.cos(th),sn=Math.sin(th),en=Math.sin(Math.PI*u),env=en*en,entryW=clamp(u/.42,0,1),exitW=clamp((1-u)/.42,0,1),entrySplay=14*Math.sin(Math.PI*entryW)**2*(u<.42?1:0),exitSplay=-14*Math.sin(Math.PI*exitW)**2*((1-u)<.42?1:0),outboard=20*env,twist=2.2*Math.sin(TAU*u)*env,gateRise=gateLift(u)+gateLift(1-u),horizR=LOOP_R*1.02;
    const lateral=outwardSign*(outboard+twist+entrySplay+exitSplay),pos=add(add(add(add(base,mul(loopForward,horizR*sn)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,lateral)),mul(ringUp,gateRise));
    const radial=norm(add(mul(ringUp,c),mul(loopForward,-sn))),loopWeight=smooth01(u/.095)*smooth01((1-u)/.095),upSeed=mixV(baseUp,radial,loopWeight);
    return{pos,frame,upSeed};
   };"""

    s = one(s, old, new, 'smooth gate-to-gate loop spine')
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v10(Path('_site'))
