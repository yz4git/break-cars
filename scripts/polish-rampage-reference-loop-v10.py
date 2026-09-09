"""Make RAMPAGE read as one continuous toy-track vertical loop.

v9 places the stunt on the outer, nearly straight lobe of the figure-eight.
This transform shapes that interval into an open vertical revolution: the normal
road itself rises through a short entry blend, becomes the loop, and returns
through a deliberately longer exit blend. There is no flat chord under the ring
and no detached hoop mesh.

The production RAMPAGE radius is already enlarged by v8. Here the extra opening
needed by the wide race ribbon is confined to the two LOWER legs only. A smooth
zero-slope bump pushes the ascending lower leg backward and the descending lower
leg forward, then fades completely before the upper sides of the ring. The
slightly larger lower-leg splay preserves visible ribbon clearance while the
outgoing transition begins farther upstream. The upper half therefore remains a
clean vertical circle instead of inheriting the old full-height corkscrew-like
distortion.

The outgoing leg begins flattening earlier in world space than the entry leg.
This gives a fast physical car enough distance to rotate its velocity and chassis
back onto the ordinary road without relying on a rail-like corrective force.
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

    new = """const open=.70,entryEnd=.12,exitStart=.80,arc=TAU-open*2,entryLead=2.2,exitLead=5.8,joinLift=.48,forwardSplay=9.3,lowerWindow=.30;
   const entryAnchor=add(add(startFrame.p,mul(startFrame.forward,entryLead)),mul(ringUp,joinLift)),desiredExit=add(add(endFrame.p,mul(endFrame.forward,-exitLead)),mul(ringUp,joinLift));
   const sinOpen=Math.sin(open),cosOpen=Math.cos(open),circleExit=mul(loopForward,-2*LOOP_R*sinOpen),drift=sub(sub(desiredExit,entryAnchor),circleExit),lowerBump=x=>x>0&&x<lowerWindow?Math.sin(Math.PI*x/lowerWindow)**2:0;
   const ringPoint=q=>{
    const th=open+arc*q,c=Math.cos(th),sn=Math.sin(th),splay=lowerBump(q)-lowerBump(1-q),circle=add(mul(loopForward,LOOP_R*(sn-sinOpen)-forwardSplay*splay),mul(ringUp,LOOP_R*(cosOpen-c))),pos=add(add(entryAnchor,circle),mul(drift,q));
    const radial=norm(add(mul(ringUp,c),mul(loopForward,-sn)));return{pos,up:radial};
   };
   const ringEntry=ringPoint(0),ringExit=ringPoint(1),dq=.001,entryT=norm(sub(ringPoint(dq).pos,ringEntry.pos)),exitT=norm(sub(ringExit.pos,ringPoint(1-dq).pos));
   const hermiteOpen=(p0,t0,p1,t1,s0,s1,q)=>{const q2=q*q,q3=q2*q,h00=2*q3-3*q2+1,h10=q3-2*q2+q,h01=-2*q3+3*q2,h11=q3-q2;return{x:p0.x*h00+t0.x*s0*h10+p1.x*h01+t1.x*s1*h11,y:p0.y*h00+t0.y*s0*h10+p1.y*h01+t1.y*s1*h11,z:p0.z*h00+t0.z*s0*h10+p1.z*h01+t1.z*s1*h11};};
   const entryScale=clamp(len(sub(ringEntry.pos,startFrame.p))*.9,1.8,3.6),exitChord=len(sub(endFrame.p,ringExit.pos)),exitRingScale=clamp(exitChord*1.08,4.8,7.5),exitRoadScale=clamp(exitChord*.86,4.0,6.5);
   const sample=u=>{
    if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),seed=mixV(startFrame.up,ringEntry.up,smooth01(q)),pos=hermiteOpen(startFrame.p,startFrame.forward,ringEntry.pos,entryT,entryScale,entryScale,q);return{pos,frame:{up:seed},upSeed:seed};}
    if(u>=exitStart){const q=clamp((u-exitStart)/(1-exitStart),0,1),seed=mixV(ringExit.up,endFrame.up,smooth01(q)),pos=hermiteOpen(ringExit.pos,exitT,endFrame.p,endFrame.forward,exitRingScale,exitRoadScale,q);return{pos,frame:{up:seed},upSeed:seed};}
    const q=(u-entryEnd)/(exitStart-entryEnd),ring=ringPoint(q);return{pos:ring.pos,frame:{up:ring.up},upSeed:ring.up};
   };"""

    s = one(s, old, new, 'lower-open vertical ring')
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v10(Path('_site'))
