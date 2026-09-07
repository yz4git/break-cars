// BREAK CARS full 3D vehicle physics.
// Reproduction of the Works physics3d design: 6DoF rigid bodies, gravity,
// four-wheel suspension, ride-over contacts, uneven ground, jump ramp and loop.
export const FULL_PHYSICS_ID='works-full-physics3d-v3';

const EPS=1e-6;
const WHEEL_RADIUS=.53;
const SUSPENSION_REST=.30;
const BODY_HALF={x:1.05,y:.50,z:2.20};
const COM_VISUAL_Y=.90;
const LOOP={x:25,y:5.5,z:10,r:5.5,halfWidth:3.7};
const RAMP={x:-22,z:-8,halfWidth:3.4,halfLength:5.2,angle:20*Math.PI/180};
const BUMPS=[[-17,11,.48,3.1],[-13,7,.38,2.7],[-17,3,.44,2.9],[-21,7,.30,2.4]];
const WHEELS=[[-1,-.10,1.40],[1,-.10,1.40],[-1,-.10,-1.40],[1,-.10,-1.40]];
const COLLISION_SPHERES=[[0,-.22,1.72,.72],[0,-.02,.82,.92],[0,.13,-.12,1],[0,.08,-1.10,.90],[0,-.05,-1.78,.70]];

const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function norm(v){const l=Math.hypot(v.x,v.y,v.z)||1;v.x/=l;v.y/=l;v.z/=l;return v;}
function dot(a,b){return a.x*b.x+a.y*b.y+a.z*b.z;}
function cross(a,b){return{x:a.y*b.z-a.z*b.y,y:a.z*b.x-a.x*b.z,z:a.x*b.y-a.y*b.x};}
function add(a,b){return{x:a.x+b.x,y:a.y+b.y,z:a.z+b.z};}
function sub(a,b){return{x:a.x-b.x,y:a.y-b.y,z:a.z-b.z};}
function mul(a,s){return{x:a.x*s,y:a.y*s,z:a.z*s};}
function quat(b){return{x:b.qx,y:b.qy,z:b.qz,w:b.qw};}
function qrot(q,v){
 const tx=2*(q.y*v.z-q.z*v.y),ty=2*(q.z*v.x-q.x*v.z),tz=2*(q.x*v.y-q.y*v.x);
 return{x:v.x+q.w*tx+(q.y*tz-q.z*ty),y:v.y+q.w*ty+(q.z*tx-q.x*tz),z:v.z+q.w*tz+(q.x*ty-q.y*tx)};
}
function qinvrot(q,v){return qrot({x:-q.x,y:-q.y,z:-q.z,w:q.w},v);}
function normalizeQ(b){const l=Math.hypot(b.qx,b.qy,b.qz,b.qw)||1;b.qx/=l;b.qy/=l;b.qz/=l;b.qw/=l;}
function integrateQ(b,dt){
 const hx=.5*dt*b.wx,hy=.5*dt*b.wy,hz=.5*dt*b.wz,x=b.qx,y=b.qy,z=b.qz,s=b.qw;
 b.qx=x+s*hx+hy*z-hz*y;b.qy=y+s*hy+hz*x-hx*z;b.qz=z+s*hz+hx*y-hy*x;b.qw=s-hx*x-hy*y-hz*z;normalizeQ(b);
}
function yawQuat(h){return{x:0,y:Math.sin(h*.5),z:0,w:Math.cos(h*.5)};}

function baseHeight(x,z){
 let h=0,gx=0,gz=0;
 for(const [bx,bz,amp,rad] of BUMPS){const dx=x-bx,dz=z-bz,d2=dx*dx+dz*dz,rr=rad*rad;if(d2>rr*3.2)continue;const e=Math.exp(-d2/rr*2.2),v=amp*e;h+=v;gx+=v*(-4.4*dx/rr);gz+=v*(-4.4*dz/rr);}
 return{h,n:norm({x:-gx,y:1,z:-gz})};
}
function floorSurface(x,z){const b=baseHeight(x,z);return{point:{x,y:b.h,z},normal:b.n,kind:'ground'};}
function rampSurface(x,z){
 const lx=x-RAMP.x,lz=z-RAMP.z;if(Math.abs(lx)>RAMP.halfWidth||Math.abs(lz)>RAMP.halfLength)return null;
 const h=(lz+RAMP.halfLength)*Math.tan(RAMP.angle);return{point:{x,y:h,z},normal:{x:0,y:Math.cos(RAMP.angle),z:-Math.sin(RAMP.angle)},kind:'ramp'};
}
function loopSurface(x,y,z){
 if(Math.abs(x-LOOP.x)>LOOP.halfWidth)return null;const dy=y-LOOP.y,dz=z-LOOP.z,r=Math.hypot(dy,dz);if(r<EPS)return null;
 return{point:{x,y:LOOP.y+dy/r*LOOP.r,z:LOOP.z+dz/r*LOOP.r},normal:{x:0,y:-dy/r,z:-dz/r},kind:'loop',radialError:Math.abs(r-LOOP.r)};
}
export function samplePhysicsSurface(mode,x,y,z,up={x:0,y:1,z:0},forChassis=false){
 const floor=floorSurface(x,z),surfaces=[floor];
 if(mode!=='racing'){const ramp=rampSurface(x,z);if(ramp)surfaces.push(ramp);const loop=loopSurface(x,y,z);if(loop&&loop.radialError<2.3)surfaces.push(loop);}
 let best=null,bestScore=Infinity,p={x,y,z};
 for(const s of surfaces){const d=dot(sub(p,s.point),s.normal),align=dot(up,s.normal);if(!forChassis&&align<.10)continue;const score=Math.abs(d)+(s.kind==='loop'?.015:0)+(align<0?.8:0);if(score<bestScore){bestScore=score;best={...s,d,align};}}
 return best||{...floor,d:y-floor.point.y,align:up.y};
}

function inertia(m){const w=BODY_HALF.x*2,h=BODY_HALF.y*2,l=BODY_HALF.z*2;return{x:m*(h*h+l*l)/12,y:m*(w*w+l*l)/12,z:m*(w*w+h*h)/12};}
function makeBody(c,type){
 const mass=Math.max(.65,type.mass||1),I=inertia(mass),q=yawQuat(c.heading||0),ground=baseHeight(c.x,c.z).h;
 return{active:true,px:c.x,py:ground+COM_VISUAL_Y,pz:c.z,qx:q.x,qy:q.y,qz:q.z,qw:q.w,vx:c.vx||0,vy:0,vz:c.vz||0,wx:0,wy:c.omega||0,wz:0,mass,invMass:1/mass,invIx:1/I.x,invIy:1/I.y,invIz:1/I.z,grounded:false,groundedWheels:0,wheelCompression:[0,0,0,0],wheelNormal:[0,0,0,0],airTime:0,lastLandingAt:-99,lastSyncX:c.x,lastSyncZ:c.z,lastSyncVx:c.vx||0,lastSyncVz:c.vz||0};
}
export function ensureFullPhysics(w,types){if(!w.fullPhysics)w.fullPhysics={id:FULL_PHYSICS_ID,enabled:true};for(const c of w.cars)if(!c.p3?.active)c.p3=makeBody(c,types[c.type]);return w.fullPhysics;}
export function resetFullPhysicsBody(w,c,types){c.p3=makeBody(c,types[c.type]);return c.p3;}

function bodyUp(b){return qrot(quat(b),{x:0,y:1,z:0});}
function bodyForward(b){return qrot(quat(b),{x:0,y:0,z:1});}
function pointWorld(b,x,y,z){const r=qrot(quat(b),{x,y,z});return{x:b.px+r.x,y:b.py+r.y,z:b.pz+r.z,r};}
function pointVelocity(b,r){const a=cross({x:b.wx,y:b.wy,z:b.wz},r);return{x:b.vx+a.x,y:b.vy+a.y,z:b.vz+a.z};}
function invInertiaWorld(b,t){const q=quat(b),l=qinvrot(q,t),a={x:l.x*b.invIx,y:l.y*b.invIy,z:l.z*b.invIz};return qrot(q,a);}
function addForce(acc,f,r){acc.fx+=f.x;acc.fy+=f.y;acc.fz+=f.z;if(r){const t=cross(r,f);acc.tx+=t.x;acc.ty+=t.y;acc.tz+=t.z;}}
function impulse(b,j,r){b.vx+=j.x*b.invMass;b.vy+=j.y*b.invMass;b.vz+=j.z*b.invMass;if(r){const a=invInertiaWorld(b,cross(r,j));b.wx+=a.x;b.wy+=a.y;b.wz+=a.z;}}
function syncLegacy(c){const b=c.p3,f=bodyForward(b),flat=Math.hypot(f.x,f.z);c.x=b.px;c.z=b.pz;c.vx=b.vx;c.vz=b.vz;if(flat>.08)c.heading=Math.atan2(f.x,f.z);c.omega=b.wy;b.lastSyncX=c.x;b.lastSyncZ=c.z;b.lastSyncVx=c.vx;b.lastSyncVz=c.vz;}
function adoptExternal(c,types){const b=c.p3;if(Math.hypot(c.x-b.lastSyncX,c.z-b.lastSyncZ)>2.4){c.p3=makeBody(c,types[c.type]);return;}if(Math.hypot(c.vx-b.lastSyncVx,c.vz-b.lastSyncVz)>.18){b.vx=c.vx;b.vz=c.vz;b.wy=c.omega||b.wy;}}
function adoptHitVelocity(c){const b=c.p3;if(Math.hypot(c.vx-b.vx,c.vz-b.vz)>.05){b.vx=c.vx;b.vz=c.vz;}if(Math.abs((c.omega||0)-b.wy)>.05)b.wy=c.omega;}

function wheelForces(w,c,u,ctx,dt,acc){
 const b=c.p3,q=quat(b),up=bodyUp(b),type=ctx.TYPES[c.type],player=c.id===0,damageFactor=.65+.35*ctx.clamp(c.parts.front/100,0,1),rush=player&&w.mode==='wreck-hunt'&&w.hunt?.rushUntil>w.time;
 const power=type.power*(player?(rush?1.52+Math.min(w.hunt?.combo||0,4)*.06:1.22):1),grip=type.grip*(player?(rush?1.22:1.08):1),top=(player?(rush?38+Math.min(w.hunt?.combo||0,4)*1.4:33.5):29)*damageFactor;
 let steer=c.dead?0:(u.steer||0);if(player)steer=-steer;
 if(player&&w.mode==='wreck-hunt'&&!c.dead){const focus=w.cars[w.hunt?.focusId];if(focus&&!focus.dead){const desired=Math.atan2(focus.x-c.x,focus.z-c.z),assist=ctx.clamp(ctx.angle(desired-c.heading)*.42,-.34,.34)*(1-ctx.clamp(Math.abs(u.steer||0),0,1)*.80);steer=ctx.clamp(steer+assist,-1,1);}const rd=Math.hypot(c.x,c.z),edge=ctx.clamp((rd-(ctx.RADIUS-11))/6,0,1);if(edge>0){const desired=Math.atan2(-c.x,-c.z),rescue=ctx.clamp(ctx.angle(desired-c.heading)*.78,-1,1);steer=ctx.clamp(steer+rescue*edge*(Math.abs(u.steer||0)<.55?1:.40),-1,1);}}
 c.steer=steer;c.throttle=c.dead?0:(u.gas||0);const forward=bodyForward(b),forwardSpeed=dot({x:b.vx,y:b.vy,z:b.vz},forward),reverse=player&&w.mode==='wreck-hunt'?21:player&&w.mode!=='racing'?17:12;
 let drive=(c.dead?0:(u.gas||0))*power*damageFactor;if(!c.dead&&u.brake)drive-=forwardSpeed>1?(player?36:33):reverse;if(forwardSpeed>top&&drive>0)drive=0;
 b.grounded=false;b.groundedWheels=0;const spring=95*b.mass,damper=8.5*b.mass;
 for(let i=0;i<WHEELS.length;i++){
  const [x,y,z]=WHEELS[i],a=pointWorld(b,x,y,z),s=samplePhysicsSurface(w.mode,a.x,a.y,a.z,up,false),gap=dot(sub(a,s.point),s.normal)-WHEEL_RADIUS,compression=ctx.clamp(SUSPENSION_REST-gap,0,.34);b.wheelCompression[i]=compression;b.wheelNormal[i]=0;if(compression<=0)continue;
  const pv=pointVelocity(b,a.r),vn=dot(pv,s.normal),normal=Math.max(0,spring*compression-damper*vn);b.wheelNormal[i]=normal;b.grounded=true;b.groundedWheels++;addForce(acc,mul(s.normal,normal),a.r);
  const wa=i<2?steer*.48:0,sn=Math.sin(wa),cs=Math.cos(wa),wf=qrot(q,{x:sn,y:0,z:cs}),wr=qrot(q,{x:cs,y:0,z:-sn});let ft=sub(wf,mul(s.normal,dot(wf,s.normal))),rt=sub(wr,mul(s.normal,dot(wr,s.normal)));norm(ft);norm(rt);
  const vl=dot(pv,ft),vs=dot(pv,rt),maxF=Math.max(5,normal*(u.hand?1.15:2.25)),latScale=u.hand?.32:1,lateral=ctx.clamp(-vs*grip*b.mass*latScale,-maxF,maxF);let longitudinal=drive/4-vl*(u.hand?1:.22)*b.mass;if(u.hand)longitudinal+=ctx.clamp(-vl*4*b.mass,-maxF*.7,maxF*.7);longitudinal=ctx.clamp(longitudinal,-maxF,maxF);addForce(acc,add(mul(ft,longitudinal),mul(rt,lateral)),a.r);
 }
 if(b.grounded){if(b.airTime>.16)b.lastLandingAt=w.time;b.airTime=0;}else b.airTime+=dt;
}

function chassisContact(w,c,ctx){
 const b=c.p3,up=bodyUp(b);let deepest=null;
 for(const x of [-BODY_HALF.x,BODY_HALF.x])for(const y of [-BODY_HALF.y,BODY_HALF.y])for(const z of [-BODY_HALF.z,BODY_HALF.z]){const p=pointWorld(b,x,y,z),s=samplePhysicsSurface(w.mode,p.x,p.y,p.z,up,true),d=dot(sub(p,s.point),s.normal);if(d<0&&(!deepest||d<deepest.d))deepest={p,s,d};}
 if(!deepest)return;const n=deepest.s.normal,pen=-deepest.d;b.px+=n.x*pen*.72;b.py+=n.y*pen*.72;b.pz+=n.z*pen*.72;const pv=pointVelocity(b,deepest.p.r),vn=dot(pv,n);if(vn<0){impulse(b,mul(n,-vn/Math.max(EPS,b.invMass)*.78),deepest.p.r);if(Math.abs(vn)>4&&w.time-c.hitAt>.32){ctx.hit(w,c,(Math.abs(vn)-3)*.30,n.x,n.z);w.events.push({type:'wall',car:c.id,x:b.px,z:b.pz,power:Math.abs(vn),nx:n.x,nz:n.z});}}}
function arenaBoundary(w,c,ctx){if(w.mode==='racing')return;const b=c.p3,r=Math.hypot(b.px,b.pz),limit=ctx.RADIUS-2.45;if(r<=limit)return;const nx=b.px/(r||1),nz=b.pz/(r||1),pen=r-limit;b.px-=nx*pen;b.pz-=nz*pen;const v=b.vx*nx+b.vz*nz;if(v>0){b.vx-=nx*v*1.45;b.vz-=nz*v*1.45;impulse(b,{x:-nx*Math.min(v*.24,3.2),y:0,z:-nz*Math.min(v*.24,3.2)},{x:nx*BODY_HALF.x,y:0,z:nz*BODY_HALF.x});if(v>5&&w.time-c.hitAt>.35){ctx.hit(w,c,(v-4)*.55,nx,nz);w.events.push({type:'wall',car:c.id,x:b.px+nx,z:b.pz+nz,power:v,nx,nz});}}}
function raceBoundary(w,c,ctx){if(w.mode!=='racing')return;syncLegacy(c);const ox=c.x,oz=c.z,wall=ctx.constrainTrack(c),b=c.p3;if(c.x!==ox||c.z!==oz){b.px=c.x;b.pz=c.z;}if(wall&&wall.speed>0){const {nx,nz,speed:v}=wall;b.vx-=nx*v*1.28;b.vz-=nz*v*1.28;if(v>6&&w.time-c.hitAt>.4){ctx.hit(w,c,(v-5)*.30,nx,nz);w.events.push({type:'wall',car:c.id,x:c.x+nx,z:c.z+nz,power:v,nx,nz});}}}

function sphereWorld(b,s){const p=pointWorld(b,s[0],s[1],s[2]);return{x:p.x,y:p.y,z:p.z,r:s[3],rel:p.r};}
function vehiclePair(w,a,b,ctx){
 if(a.finished||b.finished)return;const A=a.p3,B=b.p3;if(!A||!B||Math.abs(A.px-B.px)>6||Math.abs(A.py-B.py)>4||Math.abs(A.pz-B.pz)>6)return;const contacts=[];
 for(const sa of COLLISION_SPHERES){const pa=sphereWorld(A,sa);for(const sb of COLLISION_SPHERES){const pb=sphereWorld(B,sb),dx=pb.x-pa.x,dy=pb.y-pa.y,dz=pb.z-pa.z,d=Math.hypot(dx,dy,dz),over=pa.r+pb.r-d;if(over>0){const k=1/(d||1);contacts.push({pa,pb,n:{x:dx*k,y:dy*k,z:dz*k},over});}}}
 if(!contacts.length)return;contacts.sort((x,y)=>y.over-x.over);const inv=A.invMass+B.invMass,as=A.invMass/inv,bs=B.invMass/inv,rush=w.mode==='wreck-hunt'&&(a.id===0||b.id===0)&&w.hunt?.rushUntil>w.time;let peak=0,pn=contacts[0].n;
 for(const ct of contacts.slice(0,3)){const n=ct.n,cor=ct.over*.34/Math.min(3,contacts.length);A.px-=n.x*cor*as;A.py-=n.y*cor*as;A.pz-=n.z*cor*as;B.px+=n.x*cor*bs;B.py+=n.y*cor*bs;B.pz+=n.z*cor*bs;const closing=dot(sub(pointVelocity(A,ct.pa.rel),pointVelocity(B,ct.pb.rel)),n);if(closing<=0)continue;if(closing>peak){peak=closing;pn=n;}const j=closing*(rush?1.15:1)/Math.max(EPS,inv)*.46,J=mul(n,j);impulse(A,mul(J,-1),ct.pa.rel);impulse(B,J,ct.pb.rel);}
 if(peak<=0)return;const key=a.id*ctx.COUNT+b.id,cool=w.mode==='racing'?.32:.42,min=w.mode==='racing'?2.5:3;if(peak<min||w.time-(w.pairs.get(key)??-10)<cool)return;w.pairs.set(key,w.time);const h=Math.hypot(pn.x,pn.z)||1,nx=pn.x/h,nz=pn.z/h,ma=ctx.TYPES[a.type].mass*(a.id===0?1.12:1),mb=ctx.TYPES[b.type].mass*(b.id===0?1.12:1),damage=(peak-2)*.42*(w.mode==='racing'?1.28:1),da=ctx.hit(w,a,damage*mb,nx,nz,b)||0,db=ctx.hit(w,b,damage*ma,-nx,-nz,a)||0;adoptHitVelocity(a);adoptHitVelocity(b);
 if(w.mode==='racing'&&peak>6){for(const [attacker,victim,ix,iz] of [[a,b,nx,nz],[b,a,-nx,-nz]]){const side=Math.cos(victim.heading)*ix-Math.sin(victim.heading)*iz,front=Math.sin(attacker.heading)*ix+Math.cos(attacker.heading)*iz;if(!attacker.dead&&!victim.dead&&Math.abs(side)>.58&&front>.12){victim.p3.wy=ctx.clamp(victim.p3.wy+Math.sign(side)*peak*.13,-3,3);attacker.score+=250;w.events.push({type:'spin',car:attacker.id,victim:victim.id});}}}
 if(!a.dead||a.hitAt===w.time){a.score+=Math.round(db*12);a.contacts++;a.lastContact=w.time;}if(!b.dead||b.hitAt===w.time){b.score+=Math.round(da*12);b.contacts++;b.lastContact=w.time;}w.events.push({type:'impact',a:a.id,b:b.id,power:peak,x:(A.px+B.px)/2,y:(A.py+B.py)/2,z:(A.pz+B.pz)/2});
}

function integrateBody(w,c,u,ctx,dt){
 const b=c.p3,acc={fx:0,fy:-9.81*b.mass,fz:0,tx:0,ty:0,tz:0};wheelForces(w,c,u,ctx,dt,acc);const drag=c.dead?.22:.075;acc.fx-=b.vx*drag*b.mass;acc.fy-=b.vy*drag*b.mass;acc.fz-=b.vz*drag*b.mass;b.vx+=acc.fx*b.invMass*dt;b.vy+=acc.fy*b.invMass*dt;b.vz+=acc.fz*b.invMass*dt;const aa=invInertiaWorld(b,{x:acc.tx,y:acc.ty,z:acc.tz});b.wx+=aa.x*dt;b.wy+=aa.y*dt;b.wz+=aa.z*dt;const ad=Math.exp(-(c.dead?.28:1.05)*dt);b.wx*=ad;b.wy*=Math.exp(-(c.dead?.32:.72)*dt);b.wz*=ad;b.px+=b.vx*dt;b.py+=b.vy*dt;b.pz+=b.vz*dt;integrateQ(b,dt);chassisContact(w,c,ctx);arenaBoundary(w,c,ctx);raceBoundary(w,c,ctx);syncLegacy(c);
}
function control(w,c,input,dt,autoplay,ctx){const automatic=c.id!==0||autoplay||c.finished;if(c.dead)return{};let u=automatic?(w.mode==='racing'?ctx.racingAI(w,c,dt):ctx.ai(w,c,dt)):input;if(c.id===0&&automatic)u={...u,steer:-(u.steer||0)};return u;}
function maintainHunt(w,ctx){const h=w.hunt,p=w.cars[0];if(h.combo&&w.time-h.lastWreckAt>9)h.combo=0;for(const c of w.cars.slice(1))if(c.dead&&c.respawnAt<=w.time){ctx.respawnHuntCar(w,c);resetFullPhysicsBody(w,c,ctx.TYPES);}if(ctx.chooseHuntFocus){const f=w.cars[h.focusId];if(!f||f.dead||f.id===0)h.focusId=ctx.chooseHuntFocus(w);const locked=w.cars[h.focusId];if(locked&&!locked.dead&&h.combo>0){locked.target=0;locked.aiTimer=Math.max(locked.aiTimer,.35);}}p.lastContact=w.time;if(p.dead||w.time>=w.limit)w.done=true;}

export function stepFullPhysics(w,input,dt=1/60,autoplay=false,ctx){
 if(w.done)return;ensureFullPhysics(w,ctx.TYPES);w.events=[];w.time+=dt;for(const c of w.cars){adoptExternal(c,ctx.TYPES);syncLegacy(c);}const controls=w.cars.map(c=>control(w,c,input,dt,autoplay,ctx));
 for(let substep=0;substep<2;substep++){const h=dt*.5;for(let i=0;i<w.cars.length;i++)integrateBody(w,w.cars[i],controls[i],ctx,h);for(let pass=0;pass<2;pass++)for(let i=0;i<ctx.COUNT;i++)for(let j=i+1;j<ctx.COUNT;j++)vehiclePair(w,w.cars[i],w.cars[j],ctx);for(const c of w.cars)syncLegacy(c);}
 if(w.mode==='racing'){for(const c of w.cars)ctx.advanceRace(w,c,dt);if(w.time>=w.endAt||w.cars.every(c=>c.dead||c.finished))w.done=true;return;}if(w.mode==='wreck-hunt'){maintainHunt(w,ctx);return;}for(const c of w.cars)if(!c.dead&&w.time-c.lastContact>22){c.hp=Math.max(0,c.hp-dt*2.5);if(c.hp<=0){c.dead=true;c.wreckAt=w.time;w.events.push({type:'wreck',car:c.id,by:-1,x:c.x,z:c.z,power:34});}}if(w.cars.filter(c=>!c.dead).length<=1||w.time>=ctx.DURATION)w.done=true;
}

export function getFullPhysicsPose(c){const b=c?.p3;if(!b?.active)return null;const q=quat(b);return{position:{x:b.px,y:b.py,z:b.pz},quaternion:q,forward:qrot(q,{x:0,y:0,z:1}),up:qrot(q,{x:0,y:1,z:0}),wheelCompression:b.wheelCompression,grounded:b.grounded,airTime:b.airTime};}
export function fullPhysicsFeatureSpec(){return{loop:{...LOOP},ramp:{...RAMP},bumps:BUMPS.map(v=>[...v])};}
