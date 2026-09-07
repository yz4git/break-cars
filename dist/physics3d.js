// BREAK CARS full 3D vehicle physics.
// Rebuild of the Works "Colosseum mode reproduction" physics3d layer:
// rigid body + gravity + four-wheel suspension + 3D car contacts + ride-over
// + uneven ground + jump ramp + physical vertical loop.
export const FULL_PHYSICS_ID='works-full-physics3d-v2';

const EPS=1e-6;
const WHEEL_RADIUS=.53;
const SUSPENSION_REST=.30;
const BODY_HALF={x:1.05,y:.50,z:2.20};
const COM_VISUAL_Y=.90;
const LOOP={x:25,y:5.5,z:10,r:5.5,halfWidth:3.7};
const RAMP={x:-22,z:-8,halfWidth:3.4,halfLength:5.2,angle:20*Math.PI/180};
// Keep the authored Wreck Hunt opening lane (x≈0, z 10 -> -8) clean.
const BUMPS=[[-17,11,.48,3.1],[-13,7,.38,2.7],[-17,3,.44,2.9],[-21,7,.30,2.4]];
const WHEELS=[[-1.0,-.10,1.40],[1.0,-.10,1.40],[-1.0,-.10,-1.40],[1.0,-.10,-1.40]];
// A few overlapping convex lobes approximate a low nose and higher cabin.
// Cross-height contacts create real vertical impulses so cars can climb/ride over each other.
const COLLISION_SPHERES=[
 [0,-.22,1.72,.72],[0,-.02,.82,.92],[0,.13,-.12,1.00],[0,.08,-1.10,.90],[0,-.05,-1.78,.70]
];

const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const hypot3=(x,y,z)=>Math.hypot(x,y,z);
function norm(v){const l=hypot3(v.x,v.y,v.z)||1;v.x/=l;v.y/=l;v.z/=l;return v;}
function dot(a,b){return a.x*b.x+a.y*b.y+a.z*b.z;}
function cross(a,b){return{x:a.y*b.z-a.z*b.y,y:a.z*b.x-a.x*b.z,z:a.x*b.y-a.y*b.x};}
function add(a,b){return{x:a.x+b.x,y:a.y+b.y,z:a.z+b.z};}
function sub(a,b){return{x:a.x-b.x,y:a.y-b.y,z:a.z-b.z};}
function scale(a,s){return{x:a.x*s,y:a.y*s,z:a.z*s};}

function qrot(q,v){
 const tx=2*(q.y*v.z-q.z*v.y),ty=2*(q.z*v.x-q.x*v.z),tz=2*(q.x*v.y-q.y*v.x);
 return{x:v.x+q.w*tx+(q.y*tz-q.z*ty),y:v.y+q.w*ty+(q.z*tx-q.x*tz),z:v.z+q.w*tz+(q.x*ty-q.y*tx)};
}
function qinvrot(q,v){return qrot({x:-q.x,y:-q.y,z:-q.z,w:q.w},v);}
function normalizeBodyQuaternion(b){const l=Math.hypot(b.qx,b.qy,b.qz,b.qw)||1;b.qx/=l;b.qy/=l;b.qz/=l;b.qw/=l;}
function integrateBodyQuaternion(b,dt){
 // Angular velocity is stored in world coordinates: qDot = 0.5 * omega * q.
 const hx=.5*dt*b.wx,hy=.5*dt*b.wy,hz=.5*dt*b.wz;
 const x=b.qx,y=b.qy,z=b.qz,s=b.qw;
 b.qx=x+s*hx+hy*z-hz*y;
 b.qy=y+s*hy+hz*x-hx*z;
 b.qz=z+s*hz+hx*y-hy*x;
 b.qw=s-hx*x-hy*y-hz*z;
 normalizeBodyQuaternion(b);
}
function yawQuat(h){return{x:0,y:Math.sin(h*.5),z:0,w:Math.cos(h*.5)};}
function quatOf(b){return{x:b.qx,y:b.qy,z:b.qz,w:b.qw};}

function baseHeight(x,z){
 let h=0,gx=0,gz=0;
 for(const [bx,bz,amp,rad] of BUMPS){
  const dx=x-bx,dz=z-bz,d2=dx*dx+dz*dz,rr=rad*rad;
  if(d2>rr*3.2)continue;
  const e=Math.exp(-d2/rr*2.2),v=amp*e;
  h+=v;gx+=v*(-4.4*dx/rr);gz+=v*(-4.4*dz/rr);
 }
 return{h,n:norm({x:-gx,y:1,z:-gz})};
}
function rampSurface(x,z){
 const lx=x-RAMP.x,lz=z-RAMP.z;
 if(Math.abs(lx)>RAMP.halfWidth||Math.abs(lz)>RAMP.halfLength)return null;
 const h=(lz+RAMP.halfLength)*Math.tan(RAMP.angle);
 return{point:{x,y:h,z},normal:{x:0,y:Math.cos(RAMP.angle),z:-Math.sin(RAMP.angle)},kind:'ramp'};
}
function loopSurface(x,y,z){
 if(Math.abs(x-LOOP.x)>LOOP.halfWidth)return null;
 const dy=y-LOOP.y,dz=z-LOOP.z,rr=Math.hypot(dy,dz);
 if(rr<EPS)return null;
 // The car runs on the inside of the loop; road normal always points to its center.
 const sy=LOOP.y+dy/rr*LOOP.r,sz=LOOP.z+dz/rr*LOOP.r;
 return{point:{x,y:sy,z:sz},normal:{x:0,y:-dy/rr,z:-dz/rr},kind:'loop',radialError:Math.abs(rr-LOOP.r)};
}
function floorSurface(x,z){const b=baseHeight(x,z);return{point:{x,y:b.h,z},normal:b.n,kind:'ground'};}

export function samplePhysicsSurface(mode,x,y,z,up={x:0,y:1,z:0},forChassis=false){
 const candidates=[floorSurface(x,z)];
 if(mode!=='racing'){
  const ramp=rampSurface(x,z);if(ramp)candidates.push(ramp);
  const loop=loopSurface(x,y,z);if(loop&&loop.radialError<2.3)candidates.push(loop);
 }
 let best=null,bestScore=Infinity;
 const p={x,y,z};
 for(const s of candidates){
  const d=dot(sub(p,s.point),s.normal),align=dot(up,s.normal);
  if(!forChassis&&align<.10)continue;
  const score=Math.abs(d)+(s.kind==='loop'?.015:0)+(align<0?.8:0);
  if(score<bestScore){bestScore=score;best={...s,d,align};}
 }
 const floor=candidates[0];
 return best||{...floor,d:y-floor.point.y,align:up.y};
}

function inertiaFor(mass){
 const w=BODY_HALF.x*2,h=BODY_HALF.y*2,l=BODY_HALF.z*2;
 return{x:mass*(h*h+l*l)/12,y:mass*(w*w+l*l)/12,z:mass*(w*w+h*h)/12};
}
function makeBody(c,type){
 const mass=Math.max(.65,type.mass||1),I=inertiaFor(mass),q=yawQuat(c.heading||0),floor=baseHeight(c.x,c.z).h;
 return{active:true,px:c.x,py:floor+COM_VISUAL_Y,pz:c.z,qx:q.x,qy:q.y,qz:q.z,qw:q.w,vx:c.vx||0,vy:0,vz:c.vz||0,wx:0,wy:c.omega||0,wz:0,mass,invMass:1/mass,invIx:1/I.x,invIy:1/I.y,invIz:1/I.z,grounded:false,groundedWheels:0,wheelCompression:[0,0,0,0],wheelNormal:[0,0,0,0],airTime:0,lastLandingAt:-99,lastSyncX:c.x,lastSyncZ:c.z,lastSyncVx:c.vx||0,lastSyncVz:c.vz||0};
}
export function ensureFullPhysics(w,types){
 if(!w.fullPhysics)w.fullPhysics={id:FULL_PHYSICS_ID,enabled:true};
 for(const c of w.cars)if(!c.p3||!c.p3.active)c.p3=makeBody(c,types[c.type]);
 return w.fullPhysics;
}
export function resetFullPhysicsBody(w,c,types){c.p3=makeBody(c,types[c.type]);return c.p3;}

function bodyUp(b){return qrot(quatOf(b),{x:0,y:1,z:0});}
function bodyForward(b){return qrot(quatOf(b),{x:0,y:0,z:1});}
function pointWorld(b,lx,ly,lz){const r=qrot(quatOf(b),{x:lx,y:ly,z:lz});return{x:b.px+r.x,y:b.py+r.y,z:b.pz+r.z,r};}
function pointVelocity(b,r){const av=cross({x:b.wx,y:b.wy,z:b.wz},r);return{x:b.vx+av.x,y:b.vy+av.y,z:b.vz+av.z};}
function worldInvInertia(b,t){const q=quatOf(b),l=qinvrot(q,t),a={x:l.x*b.invIx,y:l.y*b.invIy,z:l.z*b.invIz};return qrot(q,a);}
function addForce(acc,f,r=null){acc.fx+=f.x;acc.fy+=f.y;acc.fz+=f.z;if(r){const t=cross(r,f);acc.tx+=t.x;acc.ty+=t.y;acc.tz+=t.z;}}
function impulse(b,j,r=null){b.vx+=j.x*b.invMass;b.vy+=j.y*b.invMass;b.vz+=j.z*b.invMass;if(r){const t=cross(r,j),a=worldInvInertia(b,t);b.wx+=a.x;b.wy+=a.y;b.wz+=a.z;}}
function syncLegacy(c){
 const b=c.p3,f=bodyForward(b),flat=Math.hypot(f.x,f.z);
 c.x=b.px;c.z=b.pz;c.vx=b.vx;c.vz=b.vz;if(flat>.08)c.heading=Math.atan2(f.x,f.z);c.omega=b.wy;
 b.lastSyncX=c.x;b.lastSyncZ=c.z;b.lastSyncVx=c.vx;b.lastSyncVz=c.vz;
}
function adoptExternalLegacy(c,types){
 const b=c.p3;if(!b)return;
 if(Math.hypot(c.x-b.lastSyncX,c.z-b.lastSyncZ)>2.4){c.p3=makeBody(c,types[c.type]);return;}
 if(Math.hypot(c.vx-b.lastSyncVx,c.vz-b.lastSyncVz)>.18){b.vx=c.vx;b.vz=c.vz;b.wy=c.omega||b.wy;}
}
function adoptHitVelocity(c){const b=c.p3;if(!b)return;if(Math.hypot(c.vx-b.vx,c.vz-b.vz)>.05){b.vx=c.vx;b.vz=c.vz;}if(Math.abs((c.omega||0)-b.wy)>.05)b.wy=c.omega;}

function wheelForces(w,c,u,ctx,dt,acc){
 const b=c.p3,q=quatOf(b),up=bodyUp(b),type=ctx.TYPES[c.type],player=c.id===0,damageFactor=.65+.35*ctx.clamp(c.parts.front/100,0,1);
 const rush=player&&w.mode==='wreck-hunt'&&w.hunt?.rushUntil>w.time;
 const power=type.power*(player?(rush?1.52+Math.min(w.hunt?.combo||0,4)*.06:1.22):1);
 const grip=type.grip*(player?(rush?1.22:1.08):1),topSpeed=(player?(rush?38+Math.min(w.hunt?.combo||0,4)*1.4:33.5):29)*damageFactor;
 let rawSteer=c.dead?0:(u.steer||0);if(player)rawSteer=-rawSteer;
 if(player&&w.mode==='wreck-hunt'&&!c.dead){
  const focus=w.cars[w.hunt?.focusId];
  if(focus&&!focus.dead){const desired=Math.atan2(focus.x-c.x,focus.z-c.z),assist=ctx.clamp(ctx.angle(desired-c.heading)*.42,-.34,.34)*(1-ctx.clamp(Math.abs(u.steer||0),0,1)*.80);rawSteer=ctx.clamp(rawSteer+assist,-1,1);}
  const rd=Math.hypot(c.x,c.z),edge=ctx.clamp((rd-(ctx.RADIUS-11))/6,0,1);if(edge>0){const desired=Math.atan2(-c.x,-c.z),rescue=ctx.clamp(ctx.angle(desired-c.heading)*.78,-1,1);rawSteer=ctx.clamp(rawSteer+rescue*edge*(Math.abs(u.steer||0)<.55?1:.40),-1,1);}
 }
 c.steer=rawSteer;c.throttle=c.dead?0:(u.gas||0);
 const forward=bodyForward(b),forwardSpeed=b.vx*forward.x+b.vy*forward.y+b.vz*forward.z;
 const reversePower=player&&w.mode==='wreck-hunt'?21:player&&w.mode!=='racing'?17:12;
 let drive=(c.dead?0:(u.gas||0))*power*damageFactor;if(!c.dead&&u.brake)drive-=forwardSpeed>1?(player?36:33):reversePower;if(forwardSpeed>topSpeed&&drive>0)drive=0;
 b.groundedWheels=0;b.grounded=false;const spring=95*b.mass,damper=8.5*b.mass;
 for(let i=0;i<WHEELS.length;i++){
  const [lx,ly,lz]=WHEELS[i],anchor=pointWorld(b,lx,ly,lz),surf=samplePhysicsSurface(w.mode,anchor.x,anchor.y,anchor.z,up,false);
  const gap=surf?dot(sub(anchor,surf.point),surf.normal)-WHEEL_RADIUS:999,compression=ctx.clamp(SUSPENSION_REST-gap,0,.34);b.wheelCompression[i]=compression;b.wheelNormal[i]=0;if(compression<=0)continue;
  const pv=pointVelocity(b,anchor.r),vn=dot(pv,surf.normal),normalForce=Math.max(0,spring*compression-damper*vn);b.wheelNormal[i]=normalForce;b.groundedWheels++;b.grounded=true;addForce(acc,scale(surf.normal,normalForce),anchor.r);
  const steer=i<2?rawSteer*.48:0,sf=Math.sin(steer),cf=Math.cos(steer),wf=qrot(q,{x:sf,y:0,z:cf}),wr=qrot(q,{x:cf,y:0,z:-sf});
  let ft=sub(wf,scale(surf.normal,dot(wf,surf.normal))),rt=sub(wr,scale(surf.normal,dot(wr,surf.normal)));norm(ft);norm(rt);
  const vl=dot(pv,ft),vs=dot(pv,rt),maxF=Math.max(5,normalForce*(u.hand?1.15:2.25)),lateralScale=u.hand?.32:1;
  const lateral=ctx.clamp(-vs*grip*b.mass*lateralScale,-maxF,maxF);let longitudinal=drive/4-vl*(u.hand?1.0:.22)*b.mass;
  if(u.hand)longitudinal+=ctx.clamp(-vl*4*b.mass,-maxF*.7,maxF*.7);longitudinal=ctx.clamp(longitudinal,-maxF,maxF);addForce(acc,add(scale(ft,longitudinal),scale(rt,lateral)),anchor.r);
 }
 if(!b.grounded)b.airTime+=dt;else{if(b.airTime>.16)b.lastLandingAt=w.time;b.airTime=0;}
}

function chassisContacts(w,c,ctx){
 const b=c.p3,up=bodyUp(b);let deepest=null;
 for(const x of [-BODY_HALF.x,BODY_HALF.x])for(const y of [-BODY_HALF.y,BODY_HALF.y])for(const z of [-BODY_HALF.z,BODY_HALF.z]){
  const p=pointWorld(b,x,y,z),s=samplePhysicsSurface(w.mode,p.x,p.y,p.z,up,true);if(!s)continue;const d=dot(sub(p,s.point),s.normal);if(d<0&&(!deepest||d<deepest.d))deepest={d,p,s};
 }
 if(!deepest)return;const n=deepest.s.normal,pen=-deepest.d;b.px+=n.x*pen*.72;b.py+=n.y*pen*.72;b.pz+=n.z*pen*.72;
 const pv=pointVelocity(b,deepest.p.r),vn=dot(pv,n);if(vn<0){const j=-(1.08)*vn/Math.max(EPS,b.invMass);impulse(b,scale(n,j*.72),deepest.p.r);if(Math.abs(vn)>4&&w.time-c.hitAt>.32){ctx.hit(w,c,(Math.abs(vn)-3)*.30,n.x,n.z);w.events.push({type:'wall',car:c.id,x:b.px,z:b.pz,power:Math.abs(vn),nx:n.x,nz:n.z});}}
}
function arenaBoundary(w,c,ctx){
 if(w.mode==='racing')return;const b=c.p3,r=Math.hypot(b.px,b.pz),limit=ctx.RADIUS-2.45;if(r<=limit)return;const nx=b.px/(r||1),nz=b.pz/(r||1),pen=r-limit;b.px-=nx*pen;b.pz-=nz*pen;
 const vn=b.vx*nx+b.vz*nz;if(vn>0){b.vx-=nx*vn*1.45;b.vz-=nz*vn*1.45;impulse(b,{x:-nx*Math.min(vn*.24,3.2),y:0,z:-nz*Math.min(vn*.24,3.2)},{x:nx*BODY_HALF.x,y:0,z:nz*BODY_HALF.x});if(vn>5&&w.time-c.hitAt>.35){ctx.hit(w,c,(vn-4)*.55,nx,nz);w.events.push({type:'wall',car:c.id,x:b.px+nx,z:b.pz+nz,power:vn,nx,nz});}}
}
function racingBoundary(w,c,ctx){
 if(w.mode!=='racing')return;syncLegacy(c);const beforeX=c.x,beforeZ=c.z,wall=ctx.constrainTrack(c),b=c.p3;if(c.x!==beforeX||c.z!==beforeZ){b.px=c.x;b.pz=c.z;}
 if(wall&&wall.speed>0){const {nx,nz,speed:v}=wall;b.vx-=nx*v*1.28;b.vz-=nz*v*1.28;if(v>6&&w.time-c.hitAt>.4){ctx.hit(w,c,(v-5)*.30,nx,nz);w.events.push({type:'wall',car:c.id,x:c.x+nx,z:c.z+nz,power:v,nx,nz});}}
}

function sphereWorld(b,s){const p=pointWorld(b,s[0],s[1],s[2]);return{x:p.x,y:p.y,z:p.z,r:s[3],rel:p.r};}
function resolveVehiclePair(w,a,b,ctx){
 if(a.finished||b.finished)return;const A=a.p3,B=b.p3;if(!A||!B)return;if(Math.abs(A.px-B.px)>6||Math.abs(A.py-B.py)>4||Math.abs(A.pz-B.pz)>6)return;
 const contacts=[];
 for(const sa of COLLISION_SPHERES){const pa=sphereWorld(A,sa);for(const sb of COLLISION_SPHERES){const pb=sphereWorld(B,sb),dx=pb.x-pa.x,dy=pb.y-pa.y,dz=pb.z-pa.z,dist=Math.hypot(dx,dy,dz),over=pa.r+pb.r-dist;if(over>0){const inv=1/(dist||1);contacts.push({pa,pb,n:{x:dx*inv,y:dy*inv,z:dz*inv},over});}}}
 if(!contacts.length)return;contacts.sort((x,y)=>y.over-x.over);const inv=A.invMass+B.invMass,Ashare=A.invMass/inv,Bshare=B.invMass/inv,rush=w.mode==='wreck-hunt'&&(a.id===0||b.id===0)&&w.hunt?.rushUntil>w.time;
 let peakClosing=0,peakN=contacts[0].n;
 for(const ct of contacts.slice(0,3)){
  const n=ct.n,correction=ct.over*.34/Math.min(3,contacts.length);A.px-=n.x*correction*Ashare;A.py-=n.y*correction*Ashare;A.pz-=n.z*correction*Ashare;B.px+=n.x*correction*Bshare;B.py+=n.y*correction*Bshare;B.pz+=n.z*correction*Bshare;
  const va=pointVelocity(A,ct.pa.rel),vb=pointVelocity(B,ct.pb.rel),closing=dot(sub(va,vb),n);if(closing<=0)continue;if(closing>peakClosing){peakClosing=closing;peakN=n;}
  const j=closing*(rush?1.15:1.0)/Math.max(EPS,inv)*.46,J=scale(n,j);impulse(A,scale(J,-1),ct.pa.rel);impulse(B,J,ct.pb.rel);
 }
 const closing=peakClosing;if(closing<=0)return;const key=a.id*ctx.COUNT+b.id,cool=w.mode==='racing'?.32:.42,min=w.mode==='racing'?2.5:3;if(closing<min||w.time-(w.pairs.get(key)??-10)<cool)return;w.pairs.set(key,w.time);
 const hx=Math.hypot(peakN.x,peakN.z)||1,nx=peakN.x/hx,nz=peakN.z/hx,massA=ctx.TYPES[a.type].mass*(a.id===0?1.12:1),massB=ctx.TYPES[b.type].mass*(b.id===0?1.12:1),damage=(closing-2)*.42*(w.mode==='racing'?1.28:1);
 const da=ctx.hit(w,a,damage*massB,nx,nz,b)||0,db=ctx.hit(w,b,damage*massA,-nx,-nz,a)||0;adoptHitVelocity(a);adoptHitVelocity(b);
 if(w.mode==='racing'&&closing>6){for(const [attacker,victim,ix,iz] of [[a,b,nx,nz],[b,a,-nx,-nz]]){const side=Math.cos(victim.heading)*ix-Math.sin(victim.heading)*iz,forward=Math.sin(attacker.heading)*ix+Math.cos(attacker.heading)*iz;if(!attacker.dead&&!victim.dead&&Math.abs(side)>.58&&forward>.12){victim.p3.wy=ctx.clamp(victim.p3.wy+Math.sign(side)*closing*.13,-3,3);attacker.score+=250;w.events.push({type:'spin',car:attacker.id,victim:victim.id});}}}
 if(!a.dead||a.hitAt===w.time){a.score+=Math.round(db*12);a.contacts++;a.lastContact=w.time;}if(!b.dead||b.hitAt===w.time){b.score+=Math.round(da*12);b.contacts++;b.lastContact=w.time;}
 w.events.push({type:'impact',a:a.id,b:b.id,power:closing,x:(A.px+B.px)/2,z:(A.pz+B.pz)/2,y:(A.py+B.py)/2});
}

function integrateBody(w,c,u,ctx,dt){
 const b=c.p3,acc={fx:0,fy:-9.81*b.mass,fz:0,tx:0,ty:0,tz:0};wheelForces(w,c,u,ctx,dt,acc);
 const drag=c.dead?.22:.075;acc.fx-=b.vx*drag*b.mass;acc.fy-=b.vy*drag*b.mass;acc.fz-=b.vz*drag*b.mass;
 b.vx+=acc.fx*b.invMass*dt;b.vy+=acc.fy*b.invMass*dt;b.vz+=acc.fz*b.invMass*dt;const aa=worldInvInertia(b,{x:acc.tx,y:acc.ty,z:acc.tz});b.wx+=aa.x*dt;b.wy+=aa.y*dt;b.wz+=aa.z*dt;
 const angD=Math.exp(-(c.dead?.28:1.05)*dt);b.wx*=angD;b.wy*=Math.exp(-(c.dead?.32:.72)*dt);b.wz*=angD;b.px+=b.vx*dt;b.py+=b.vy*dt;b.pz+=b.vz*dt;integrateBodyQuaternion(b,dt);
 chassisContacts(w,c,ctx);arenaBoundary(w,c,ctx);racingBoundary(w,c,ctx);syncLegacy(c);
}
function controlFor(w,c,input,dt,autoplay,ctx){const automatic=c.id!==0||autoplay||c.finished;if(c.dead)return{};let u=automatic?(w.mode==='racing'?ctx.racingAI(w,c,dt):ctx.ai(w,c,dt)):input;if(c.id===0&&automatic)u={...u,steer:-(u.steer||0)};return u;}
function maintainHunt(w,ctx){
 const h=w.hunt,p=w.cars[0];if(h.combo&&w.time-h.lastWreckAt>9)h.combo=0;
 for(const c of w.cars.slice(1))if(c.dead&&c.respawnAt<=w.time){ctx.respawnHuntCar(w,c);resetFullPhysicsBody(w,c,ctx.TYPES);}
 if(ctx.chooseHuntFocus){const focus=w.cars[h.focusId];if(!focus||focus.dead||focus.id===0)h.focusId=ctx.chooseHuntFocus(w);const locked=w.cars[h.focusId];if(locked&&!locked.dead&&h.combo>0){locked.target=0;locked.aiTimer=Math.max(locked.aiTimer,.35);}}
 p.lastContact=w.time;if(p.dead||w.time>=w.limit)w.done=true;
}

export function stepFullPhysics(w,input,dt=1/60,autoplay=false,ctx){
 if(w.done)return;ensureFullPhysics(w,ctx.TYPES);w.events=[];w.time+=dt;
 for(const c of w.cars){adoptExternalLegacy(c,ctx.TYPES);syncLegacy(c);}const controls=w.cars.map(c=>controlFor(w,c,input,dt,autoplay,ctx));
 for(let sub=0;sub<2;sub++){
  const h=dt*.5;for(let i=0;i<w.cars.length;i++)integrateBody(w,w.cars[i],controls[i],ctx,h);
  for(let pass=0;pass<2;pass++)for(let i=0;i<ctx.COUNT;i++)for(let j=i+1;j<ctx.COUNT;j++)resolveVehiclePair(w,w.cars[i],w.cars[j],ctx);
  for(const c of w.cars)syncLegacy(c);
 }
 if(w.mode==='racing'){for(const c of w.cars)ctx.advanceRace(w,c,dt);if(w.time>=w.endAt||w.cars.every(c=>c.dead||c.finished))w.done=true;return;}
 if(w.mode==='wreck-hunt'){maintainHunt(w,ctx);return;}
 for(const c of w.cars)if(!c.dead&&w.time-c.lastContact>22){c.hp=Math.max(0,c.hp-dt*2.5);if(c.hp<=0){c.dead=true;c.wreckAt=w.time;w.events.push({type:'wreck',car:c.id,by:-1,x:c.x,z:c.z,power:34});}}
 if(w.cars.filter(c=>!c.dead).length<=1||w.time>=ctx.DURATION)w.done=true;
}

export function getFullPhysicsPose(c){const b=c?.p3;if(!b?.active)return null,q=quatOf(b);return{position:{x:b.px,y:b.py,z:b.pz},quaternion:q,forward:qrot(q,{x:0,y:0,z:1}),up:qrot(q,{x:0,y:1,z:0}),wheelCompression:b.wheelCompression,grounded:b.grounded,airTime:b.airTime};}
export function fullPhysicsFeatureSpec(){return{loop:{...LOOP},ramp:{...RAMP},bumps:BUMPS.map(v=>[...v])};}
