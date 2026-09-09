"""Make RAMPAGE read as one continuous toy-track vertical loop.

The authored road must become the loop itself: no flat chord underneath and no
detached hoop.  Keep the upper revolution essentially vertical, but open the
bottom in the direction of travel.  Entry and exit transition legs are short
and tangent-continuous; the lower circular legs receive a symmetric longitudinal
splay that fades out before the upper half.  This gives the wide race ribbon
clearance without turning the whole stunt into a corkscrew.

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

    new = """const open=.58,entryEnd=.075,exitStart=.925,arc=TAU-open*2,entryLead=1.6,exitLead=1.2,joinLift=.52,forwardSplay=13.5,lowerWindow=.36;
   const entryAnchor=add(add(startFrame.p,mul(startFrame.forward,entryLead)),mul(ringUp,joinLift)),desiredExit=add(add(endFrame.p,mul(endFrame.forward,-exitLead)),mul(ringUp,joinLift));
   const sinOpen=Math.sin(open),cosOpen=Math.cos(open),circleExit=mul(loopForward,-2*LOOP_R*sinOpen),drift=sub(sub(desiredExit,entryAnchor),circleExit),lowerBump=x=>x>0&&x<lowerWindow?Math.sin(Math.PI*x/lowerWindow)**2:0;
   const ringPoint=q=>{
    const th=open+arc*q,c=Math.cos(th),sn=Math.sin(th),splay=lowerBump(q)-lowerBump(1-q),circle=add(mul(loopForward,LOOP_R*(sn-sinOpen)-forwardSplay*splay),mul(ringUp,LOOP_R*(cosOpen-c))),pos=add(add(entryAnchor,circle),mul(drift,q));
    const radial=norm(add(mul(ringUp,c),mul(loopForward,-sn)));return{pos,up:radial};
   };
   const ringEntry=ringPoint(0),ringExit=ringPoint(1),dq=.001,entryT=norm(sub(ringPoint(dq).pos,ringEntry.pos)),exitT=norm(sub(ringExit.pos,ringPoint(1-dq).pos));
   const hermiteOpen=(p0,t0,p1,t1,s0,s1,q)=>{const q2=q*q,q3=q2*q,h00=2*q3-3*q2+1,h10=q3-2*q2+q,h01=-2*q3+3*q2,h11=q3-q2;return{x:p0.x*h00+t0.x*s0*h10+p1.x*h01+t1.x*s1*h11,y:p0.y*h00+t0.y*s0*h10+p1.y*h01+t1.y*s1*h11,z:p0.z*h00+t0.z*s0*h10+p1.z*h01+t1.z*s1*h11};};
   const entryScale=clamp(len(sub(ringEntry.pos,startFrame.p))*1.25,2.6,5.0),exitScale=clamp(len(sub(endFrame.p,ringExit.pos))*1.25,2.6,5.0);
   const sample=u=>{
    if(u<=entryEnd){const q=clamp(u/entryEnd,0,1),seed=mixV(startFrame.up,ringEntry.up,smooth01(q)),pos=hermiteOpen(startFrame.p,startFrame.forward,ringEntry.pos,entryT,entryScale,entryScale,q);return{pos,frame:{up:seed},upSeed:seed};}
    if(u>=exitStart){const q=clamp((u-exitStart)/(1-exitStart),0,1),seed=mixV(ringExit.up,endFrame.up,smooth01(q)),pos=hermiteOpen(ringExit.pos,exitT,endFrame.p,endFrame.forward,exitScale,exitScale,q);return{pos,frame:{up:seed},upSeed:seed};}
    const q=(u-entryEnd)/(exitStart-entryEnd),ring=ringPoint(q);return{pos:ring.pos,frame:{up:ring.up},upSeed:ring.up};
   };"""

    s = one(s, old, new, 'lower-open vertical ring')
    path.write_text(s)


if __name__ == '__main__':
    apply_rampage_reference_loop_v10(Path('_site'))
