import {activeCourse} from './courses.js';

export const RACE3D_ID='wrecking-racing-math-v1';
const TAU=Math.PI*2,G=9.81,BASE_STEPS=360,LOOP_STEPS=112,CELL=10,EPS=1e-8;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const wrapAngle=a=>Math.atan2(Math.sin(a),Math.cos(a));
const gauss=(t,c,w)=>Math.exp(-Math.pow(wrapAngle(t-c)/w,2));
const len=v=>Math.hypot(v.x,v.y,v.z);
const norm=v=>{const l=len(v)||1;return{x:v.x/l,y:v.y/l,z:v.z/l};};
const add=(a,b)=>({x:a.x+b.x,y:a.y+b.y,z:a.z+b.z});
const sub=(a,b)=>({x:a.x-b.x,y:a.y-b.y,z:a.z-b.z});
const mul=(v,s)=>({x:v.x*s,y:v.y*s,z:v.z*s});
const dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z;
const cross=(a,b)=>({x:a.y*b.z-a.z*b.y,y:a.z*b.x-a.x*b.z,z:a.x*b.y-a.y*b.x});
function rotateAround(v,axis,a){const c=Math.cos(a),s=Math.sin(a),d=dot(axis,v);return add(add(mul(v,c),mul(cross(axis,v),s)),mul(axis,d*(1-c)));}
function angularDistance(a,b){return Math.abs(wrapAngle(a-b));}

const CONFIGS={
 'rampage-3d':{
  name:'RAMPAGE 3D',halfWidth:8.5,designSpeed:25.5,bankMax:31*Math.PI/180,
  loops:[{t:.72,radius:9.4}],jump:{rampStart:4.45,gapStart:4.60,gapEnd:4.73,landEnd:4.94,lift:.95,landingLift:.42},
  plan:t=>({x:72*Math.cos(t)+5*Math.cos(2*t),z:44*Math.sin(t)+4*Math.sin(3*t)}),
  elevation:t=>6.2*gauss(t,2.45,.62)+1.1*gauss(t,3.30,.55)
 },
 'sky-forge':{
  name:'SKY FORGE',halfWidth:8.5,designSpeed:24.5,bankMax:32*Math.PI/180,
  loops:[{t:.72,radius:9.8}],jump:{rampStart:4.15,gapStart:4.31,gapEnd:4.44,landEnd:4.67,lift:.95,landingLift:.42},
  plan:t=>{const u=t+.64;return{x:72*Math.sin(u),z:38*Math.sin(2*u)};},
  elevation:t=>9.5*gauss(t,2.50,.62)+1.3*gauss(t,.15,.65)
 },
 'double-orbit':{
  name:'DOUBLE ORBIT',halfWidth:8.7,designSpeed:26.0,bankMax:30*Math.PI/180,
  loops:[{t:.62,radius:9.6},{t:3.62,radius:9.9}],jump:{rampStart:5.05,gapStart:5.20,gapEnd:5.33,landEnd:5.55,lift:1.05,landingLift:.45},
  plan:t=>({x:80*Math.cos(t)+4*Math.cos(2*t),z:50*Math.sin(t)}),
  elevation:t=>7.0*gauss(t,2.25,.68)+1.0*gauss(t,4.40,.70)
 }
};
const courseId=activeCourse?.mode==='racing'&&CONFIGS[activeCourse.id]?activeCourse.id:'rampage-3d';
const C=CONFIGS[courseId];
export const RACE3D_TRACK={halfWidth:C.halfWidth,loopRadius:C.loops[0].radius};

function jumpProfile(t){
 const j=C.jump;
 if(t>=j.rampStart&&t<j.gapStart){const u=(t-j.rampStart)/(j.gapStart-j.rampStart);return{y:j.lift*u*u,kind:'jump-ramp'};}
 if(t>=j.gapStart&&t<j.gapEnd){const u=(t-j.gapStart)/(j.gapEnd-j.gapStart);return{y:j.lift*(1-u)+j.landingLift*u,kind:'jump-gap'};}
 if(t>=j.gapEnd&&t<j.landEnd){const u=(t-j.gapEnd)/(j.landEnd-j.gapEnd);return{y:j.landingLift*(1-u)*(1-u),kind:'jump-landing'};}
 return{y:0,kind:'track'};
}
function centerAt(t){const q=C.plan(t),j=jumpProfile(t),y=C.elevation(t)+j.y;return{x:q.x,y,z:q.z,t,kind:j.kind};}
function differential(t){
 const h=.0018,p0=centerAt(t-h),p1=centerAt(t),p2=centerAt(t+h);
 const v0=sub(p1,p0),v1=sub(p2,p1),forward=norm(sub(p2,p0));
 const h0=norm({x:v0.x,y:0,z:v0.z}),h1=norm({x:v1.x,y:0,z:v1.z}),ds=Math.max(.001,(Math.hypot(v0.x,v0.z)+Math.hypot(v1.x,v1.z))*.5);
 const signed=Math.atan2(h0.x*h1.z-h0.z*h1.x,h0.x*h1.x+h0.z*h1.z)/ds;
 return{forward,curvature:signed};
}
function gateFade(t){
 let f=1;
 for(const l of C.loops)f*=clamp((angularDistance(t,l.t)-.10)/.16,0,1);
 const j=C.jump;if(t>=j.rampStart-.10&&t<=j.landEnd+.10)f=0;
 return f;
}
function bankAt(t){
 const k=differential(t).curvature,raw=Math.atan(C.designSpeed*C.designSpeed*k/G);
 return clamp(raw,-C.bankMax,C.bankMax)*gateFade(t);
}
function baseSample(t){const p=centerAt(t);return{...p,bank:bankAt(t),explicitUp:null,explicitForward:null,loopIndex:-1};}
function roadFrameAt(t){
 const p=baseSample(t),forward=differential(t).forward,worldUp={x:0,y:1,z:0};let right=norm(cross(worldUp,forward));if(len(right)<.15)right={x:1,y:0,z:0};
 let up=norm(cross(forward,right));up=norm(rotateAround(up,forward,p.bank));right=norm(cross(up,forward));return{p,forward,up,right};
}

const special=new Set([0,TAU,C.jump.rampStart,C.jump.gapStart,C.jump.gapEnd,C.jump.landEnd,...C.loops.map(l=>l.t)]);
const ts=[];for(let i=0;i<=BASE_STEPS;i++)special.add(i/BASE_STEPS*TAU);for(const t of special)ts.push(t);ts.sort((a,b)=>a-b);
const raw=[];
for(const t of ts){
 if(t>TAU+EPS)continue;
 const p=baseSample(t);raw.push(p);
 const loopIndex=C.loops.findIndex(l=>Math.abs(t-l.t)<1e-7);if(loopIndex<0)continue;
 const spec=C.loops[loopIndex],frame=roadFrameAt(t),base={x:p.x,y:p.y,z:p.z},R=spec.radius;
 // A mathematically exact tangent loop. Position, tangent and road normal return
 // to the same gate after 2π, eliminating the old offset/overlap repair stack.
 for(let j=1;j<=LOOP_STEPS;j++){
  const th=j/LOOP_STEPS*TAU,c=Math.cos(th),s=Math.sin(th),pos=add(add(base,mul(frame.forward,R*s)),mul(frame.up,R*(1-c)));
  const tangent=norm(add(mul(frame.forward,c),mul(frame.up,s))),up=norm(add(mul(frame.up,c),mul(frame.forward,-s)));
  raw.push({x:pos.x,y:pos.y,z:pos.z,t,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent,loopIndex});
 }
}

const points=[];
for(let i=0;i<raw.length;i++){
 const p=raw[i],prev=raw[Math.max(0,i-1)],next=raw[Math.min(raw.length-1,i+1)];
 let forward=p.explicitForward||norm(sub(next,prev)),up;
 if(p.explicitUp)up=p.explicitUp;else{let right0=norm(cross({x:0,y:1,z:0},forward));if(len(right0)<.15)right0={x:1,y:0,z:0};const up0=norm(cross(forward,right0));up=norm(rotateAround(up0,forward,p.bank||0));}
 const right=norm(cross(up,forward));points.push({...p,forward,up,right,s:0});
}
let total=0;for(let i=1;i<points.length;i++){total+=len(sub(points[i],points[i-1]));points[i].s=total;}
export const RACE3D_LENGTH=total;
const wrapS=s=>(s%RACE3D_LENGTH+RACE3D_LENGTH)%RACE3D_LENGTH;
function segmentAtS(s){const q=wrapS(s);let lo=0,hi=points.length-1;while(lo+1<hi){const m=(lo+hi)>>1;if(points[m].s<=q)lo=m;else hi=m;}const a=points[lo],b=points[Math.min(lo+1,points.length-1)],d=Math.max(EPS,b.s-a.s),u=clamp((q-a.s)/d,0,1);return{a,b,u,i:lo};}
function mixFrame(a,b,u){const forward=norm({x:a.forward.x+(b.forward.x-a.forward.x)*u,y:a.forward.y+(b.forward.y-a.forward.y)*u,z:a.forward.z+(b.forward.z-a.forward.z)*u}),up=norm({x:a.up.x+(b.up.x-a.up.x)*u,y:a.up.y+(b.up.y-a.up.y)*u,z:a.up.z+(b.up.z-a.up.z)*u});return{forward,up,right:norm(cross(up,forward))};}
function kindBetween(a,b){if(a.kind==='loop'||b.kind==='loop')return'loop';if(a.kind==='jump-gap'||b.kind==='jump-gap')return'jump-gap';if(a.kind==='jump-ramp'||b.kind==='jump-ramp')return'jump-ramp';if(a.kind==='jump-landing'||b.kind==='jump-landing')return'jump-landing';if(Math.max(a.y,b.y)>4.8)return'bridge';return'track';}
export function racePointAt(s,lane=0){const {a,b,u}=segmentAtS(s),f=mixFrame(a,b,u),center={x:a.x+(b.x-a.x)*u,y:a.y+(b.y-a.y)*u,z:a.z+(b.z-a.z)*u},pos=add(center,mul(f.right,lane));return{x:pos.x,y:pos.y,z:pos.z,cx:center.x,cy:center.y,cz:center.z,dx:f.forward.x,dy:f.forward.y,dz:f.forward.z,heading:Math.atan2(f.forward.x,f.forward.z),forward:f.forward,up:f.up,right:f.right,bank:(a.bank||0)+((b.bank||0)-(a.bank||0))*u,kind:kindBetween(a,b),s:wrapS(s),lane};}

const grid=new Map(),segments=[];const key=(ix,iz)=>`${ix},${iz}`;
for(let i=0;i<points.length-1;i++){const a=points[i],b=points[i+1],seg={i,a,b};segments.push(seg);const pad=C.halfWidth+2,minX=Math.min(a.x,b.x)-pad,maxX=Math.max(a.x,b.x)+pad,minZ=Math.min(a.z,b.z)-pad,maxZ=Math.max(a.z,b.z)+pad;for(let ix=Math.floor(minX/CELL);ix<=Math.floor(maxX/CELL);ix++)for(let iz=Math.floor(minZ/CELL);iz<=Math.floor(maxZ/CELL);iz++){const k=key(ix,iz);if(!grid.has(k))grid.set(k,[]);grid.get(k).push(seg);}}
function nearby(x,z){const ix=Math.floor(x/CELL),iz=Math.floor(z/CELL),out=[],seen=new Set();for(let dx=-1;dx<=1;dx++)for(let dz=-1;dz<=1;dz++)for(const s of grid.get(key(ix+dx,iz+dz))||[])if(!seen.has(s.i)){seen.add(s.i);out.push(s);}return out.length?out:segments;}
function sDelta(a,b){let d=wrapS(a)-wrapS(b);if(d>RACE3D_LENGTH/2)d-=RACE3D_LENGTH;if(d<-RACE3D_LENGTH/2)d+=RACE3D_LENGTH;return d;}
export function projectRacePoint(x,y,z,hintS=null,use3D=true){
 const p={x,y:Number.isFinite(y)?y:0,z};let best=null,bestCost=Infinity,hintDetached=false;if(hintS!=null&&use3D){const h=segmentAtS(hintS),hc={x:h.a.x+(h.b.x-h.a.x)*h.u,y:h.a.y+(h.b.y-h.a.y)*h.u,z:h.a.z+(h.b.z-h.a.z)*h.u};hintDetached=len(sub(p,hc))>9;}
 for(const seg of nearby(x,z)){
  const a=seg.a,b=seg.b,v=sub(b,a),w=sub(p,a),vv=use3D?dot(v,v):v.x*v.x+v.z*v.z,numer=use3D?dot(w,v):w.x*v.x+w.z*v.z,u=clamp(numer/Math.max(EPS,vv),0,1),center=add(a,mul(v,u)),f=mixFrame(a,b,u),d=sub(p,center),lane=dot(d,f.right),vertical=dot(d,f.up),s=a.s+(b.s-a.s)*u,flat2=(p.x-center.x)**2+(p.z-center.z)**2,dist2=use3D?flat2+(p.y-center.y)**2:flat2;
  const gap=hintS==null?0:Math.abs(sDelta(s,hintS)),continuity=hintS==null?0:(gap>(hintDetached?30:18)?2500+gap*gap:Math.pow(gap/(hintDetached?12:8),2)*.12),cost=dist2+continuity;
  if(cost<bestCost){bestCost=cost;best={s:wrapS(s),lane,vertical,distance:Math.sqrt(dist2),x:center.x,y:center.y,z:center.z,dx:f.forward.x,dy:f.forward.y,dz:f.forward.z,heading:Math.atan2(f.forward.x,f.forward.z),forward:f.forward,up:f.up,right:f.right,bank:(a.bank||0)+((b.bank||0)-(a.bank||0))*u,kind:kindBetween(a,b),segment:seg.i};}
 }
 return best;
}
export function sampleRaceSurface(x,y,z,up={x:0,y:1,z:0},forChassis=false){const p=projectRacePoint(x,y,z,null,true);if(!p)return null;const allowance=C.halfWidth+(forChassis?2.1:1.35);if(Math.abs(p.lane)>allowance||p.kind==='jump-gap')return null;const lane=clamp(p.lane,-C.halfWidth,C.halfWidth),point={x:p.x+p.right.x*lane,y:p.y+p.right.y*lane,z:p.z+p.right.z*lane},d=(x-point.x)*p.up.x+(y-point.y)*p.up.y+(z-point.z)*p.up.z;return{point,normal:p.up,kind:`race-${p.kind}`,d,align:dot(up,p.up),s:p.s,lane:p.lane};}

const loopGroups=C.loops.map((l,index)=>{const ids=[];for(let i=0;i<points.length;i++)if(points[i].kind==='loop'&&points[i].loopIndex===index)ids.push(i);const a=ids.map(i=>points[i]),gate=points[Math.max(0,ids[0]-1)];return{radius:l.radius,startS:gate.s,endS:a.at(-1).s,maxY:Math.max(gate.y,...a.map(p=>p.y)),minY:Math.min(gate.y,...a.map(p=>p.y))};});
export function raceLoopAt(s){const q=wrapS(s),inside=loopGroups.find(l=>q>=l.startS&&q<=l.endS);if(inside)return inside;return loopGroups.reduce((best,l)=>{const d=(l.startS-q+RACE3D_LENGTH)%RACE3D_LENGTH,b=(best.startS-q+RACE3D_LENGTH)%RACE3D_LENGTH;return d<b?l:best;});}
const gapPts=points.filter(p=>p.kind==='jump-gap'),ordinary=points.filter(p=>p.kind!=='loop'),bridge=ordinary.reduce((a,b)=>b.y>a.y?b:a,ordinary[0]);
let maxGrade=0,minRadius=Infinity;
for(let i=2;i<ordinary.length-2;i++){const a=ordinary[i-1],b=ordinary[i],c=ordinary[i+1],ds=Math.max(.001,(len(sub(b,a))+len(sub(c,b)))*.5),grade=Math.abs(c.y-a.y)/Math.max(.001,Math.hypot(c.x-a.x,c.z-a.z));if(!['jump-ramp','jump-gap','jump-landing'].includes(b.kind))maxGrade=Math.max(maxGrade,grade);const h0=norm({x:b.x-a.x,y:0,z:b.z-a.z}),h1=norm({x:c.x-b.x,y:0,z:c.z-b.z}),ang=Math.acos(clamp(h0.x*h1.x+h0.z*h1.z,-1,1));if(ang>.0001)minRadius=Math.min(minRadius,ds/ang);}
const takeoff=points.findLast?.(p=>p.t<C.jump.gapStart&&p.kind==='jump-ramp')||points.filter(p=>p.t<C.jump.gapStart&&p.kind==='jump-ramp').at(-1),theta=Math.asin(clamp(takeoff?.forward.y||0,-1,1)),designRange=C.designSpeed*C.designSpeed*Math.max(0,Math.sin(2*theta))/G,gapLength=gapPts.length?Math.hypot(gapPts.at(-1).x-gapPts[0].x,gapPts.at(-1).z-gapPts[0].z):0;
const jump={startS:gapPts[0]?.s||0,endS:gapPts.at(-1)?.s||0,gapLength,designRange,takeoffAngle:theta};
export function race3DFeatureSpec(){return{id:RACE3D_ID,courseId,name:C.name,length:RACE3D_LENGTH,halfWidth:C.halfWidth,loopHalfWidth:C.halfWidth,loop:loopGroups[0],loops:loopGroups,jump,bridge:{s:bridge.s,y:bridge.y},bankMax:Math.max(...points.map(p=>Math.abs(p.bank||0))),bankModel:'atan(v^2*kappa/g)',designBankMax:C.bankMax,designSpeed:C.designSpeed,maxGrade,minRadius:Number.isFinite(minRadius)?minRadius:999,minY:Math.min(...points.map(p=>p.y)),maxY:Math.max(...points.map(p=>p.y))};}
export function raceCourseSamples(count=360){const out=[];for(let i=0;i<=count;i++)out.push(racePointAt(i/count*RACE3D_LENGTH));return out;}
