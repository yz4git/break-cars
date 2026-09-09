"""Build the RAMPAGE stunt as the road itself, in the toy-track reference form.

The previous full-circle-on-a-moving-spine variants could only gain clearance by
making the lower road travel sideways for too long. This version removes the
bottom part of the vertical circle and replaces it with two real transition
legs. The incoming road rises into the front side of the ring; after the crown,
the descending side returns through a laterally offset lower leg and merges into
the authored outgoing road. There is no flat chord under the ring and no
separate hoop mesh.

Only the lower part carries a modest twist. The vertical crown remains almost
planar. The ring is biased outward from the figure-eight crossing, and a short
zero-slope entry lift makes the road visibly start climbing immediately instead
of travelling flat beneath the stunt. Hermite legs still use the actual gate
tangents, so both ends remain continuous with the normal road.

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

    new = """const open=.88,entryEnd=.20,exitStart=.78,gapAlong=LOOP_R*Math.sin(open),joinRise=LOOP_R*(1-Math.cos(open)),sideMag=7.5,baseOut=15,baseLead=gapAlong+15,gateLift=x=>2.0*smooth01(x/.055)*(1-smooth01((x-.12)/.085));
   const ringBase=add(add(startFrame.p,mul(loopForward,baseLead)),mul(flatRight,outwardSign*baseOut));
   const ringPoint=(th,q)=>{const c=Math.cos(th),sn=Math.sin(th),side=outwardSign*sideMag*Math.cos(Math.PI*q),pos=add(add(add(ringBase,mul(loopForward,LOOP_R*sn)),mul(ringUp,LOOP_R*(1-c))),mul(flatRight,side)),up=norm(add(mul(ringUp,c),mul(loopForward,-sn)));return{pos,up};};
   const ringEntry=ringPoint(open,0),ringExit=ringPoint(TAU-open,1),entryT=norm(add(mul(loopForward,Math.cos(open)),mul(ringUp,Math.sin(open)))),exitT=norm(add(mul(loopForward,Math.cos(open)),mul(ringUp,-Math.sin(open))));
   const hermiteOpen=(p0,t0,p1,t1,s0,s1,q)=>{const q2=q*q,q3=q2*q,h00=2*q3-3*q2+1,h10=q3-2*q2+q,h01=-2*q3+3*q2,h11=q3-q2;return{x:p0.x*h00+t0.x*s0*h10+p1.x*h01+t1.x*s1*h11,y:p0.y*h00+t0.y*s0*h10+p1.y*h01+t1.y*s1*h11,z:p0.z*h00+t0.z*s0*h10+p1.z*h01+t1.z*s1*h11};};
   const entryDist=len(sub(ringEntry.pos,startFrame.p)),exitDist=len(sub(endFrame.p,ringExit.pos)),entryScale=clamp(entryDist*.62,9,25),exitScale=clamp(exitDist*.62,9,25);
   const sample=u=>{
    const gateRise=gateLift(u)+gateLift(1-u);
    if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),w=smooth01(q),seed=mixV(startFrame.up,ringEntry.up,w),base=hermiteOpen(startFrame.p,startFrame.forward,ringEntry.pos,entryT,entryScale,entryScale,q),pos=add(base,mul(ringUp,gateRise));return{pos,frame:{up:seed},upSeed:seed};}
    if(u>=exitStart){const q=clamp((u-exitStart)/(1-exitStart),0,1),w=smooth01(q),seed=mixV(ringExit.up,endFrame.up,w),base=hermiteOpen(ringExit.pos,exitT,endFrame.p,endFrame.forward,exitScale,exitScale,q),pos=add(base,mul(ringUp,gateRise));return{pos,frame:{up:seed},upSeed:seed};}
    const q=(u-entryEnd)/(exitStart-entryEnd),th=open+(TAU-open*2)*q,ring=ringPoint(th,q);return{pos:ring.pos,frame:{up:ring.up},upSeed:ring.up};
   };"""

    s = one(s, old, new, 'open vertical ring and transition legs')
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v10(Path('_site'))
