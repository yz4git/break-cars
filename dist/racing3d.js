// BREAK CARS — dedicated 3D Wrecking Racing course.
// A sampled self-crossing ribbon with elevation, banking, jump gap and a true vertical loop.
export const RACE3D_ID='wrecking-racing-3d-v1';
export const RACE3D_TRACK={halfWidth:8.5,loopRadius:7.2};

const TAU=Math.PI*2, BASE_STEPS=260, LOOP_STEPS=76, CELL=9, EPS=1e-7;
const LOOP_T=.88, LOOP_R=RACE3D_TRACK.loopRadius;
const JUMP={rampStart:4.62,gapStart:4.90,gapEnd:5.10,landEnd:5.34};
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

function baseAt(t){
 const x=62*Math.sin(t),z=40*Math.sin(t)*Math.cos(t);
 let y=7.4*gauss(t,Math.PI,.28)+2.4*gauss(t,1.82,.48)+1.6*gauss(t,4.02,.55);
 let kind=y>5?'bridge':'track';
 if(t>=JUMP.rampStart&&t<JUMP.gapStart){const u=(t-JUMP.rampStart)/(JUMP.gapStart-JUMP.rampStart);y+=2.8*u;kind='jump-ramp';}
 else if(t>=JUMP.gapStart&&t<JUMP.gapEnd){const u=(t-JUMP.gapStart)/(JUMP.gapEnd-JUMP.gapStart);y+=2.8*(1-u)+.75*u;kind='jump-gap';}
 else if(t>=JUMP.gapEnd&&t<JUMP.landEnd){const u=(t-JUMP.gapEnd)/(JUMP.landEnd-JUMP.gapEnd);y+=.75*(1-u);kind='jump-landing';}
 return{x,y,z,t,kind,bank:clamp(.34*Math.sin(2*t),-.36,.36)};
}

const raw=[];
const ts=[];for(let i=0;i<=BASE_STEPS;i++)ts.push(i/BASE_STEPS*TAU);ts.push(LOOP_T);ts.sort((a,b)=>a-b);
let loopInserted=false;
for(const t of ts){
 if(t>TAU+EPS)continue;
 const p=baseAt(t);raw.push({...p,explicitUp:null});
 if(!loopInserted&&Math.abs(t-LOOP_T)<1e-6){
  loopInserted=true;
  const dt=.001,a=baseAt(t-dt),b=baseAt(t+dt),f=norm({x:b.x-a.x,y:0,z:b.z-a.z}),worldUp={x:0,y:1,z:0};
  const base={x:p.x,y:p.y,z:p.z},center=add(base,mul(worldUp,LOOP_R));
  for(let j=1;j<=LOOP_STEPS;j++){
   const th=-Math.PI/2+j/LOOP_STEPS*TAU,c=Math.cos(th),s=Math.sin(th);
   const pos=add(add(base,mul(f,LOOP_R*c)),mul(worldUp,LOOP_R*(1+s)));
   const tangent=norm(add(mul(f,-s),mul(worldUp,c)));
   const up=norm(sub(center,pos));
   raw.push({x:pos.x,y:pos.y,z:pos.z,t,kind:'loop',bank:0,explicitUp:up,explicitForward:tangent});
  }
 }
}

// Remove accidental duplicate base samples while preserving the loop start/end duplicate,
// then construct a stable forward/up/right frame at every sample.
const points=[];
for(let i=0;i<raw.length;i++){
 const p=raw[i],prev=raw[Math.max(0,i-1)],next=raw[Math.min(raw.length-1,i+1)];
 let forward=p.explicitForward||norm({x:next.x-prev.x,y:next.y-prev.y,z:next.z-prev.z});
 let up;
 if(p.explicitUp) up=p.explicitUp;
 else{
  let right0=norm(cross({x:0,y:1,z:0},forward));
  if(len(right0)<.2)right0={x:1,y:0,z:0};
  const up0=norm(cross(forward,right0));
  up=norm(rotateAround(up0,forward,p.bank||0));
 }
 const right=norm(cross(up,forward));
 points.push({...p,forward,up,right,s:0});
}
let total=0;
for(let i=1;i<points.length;i++){total+=len(sub(points[i],points[i-1]));points[i].s=total;}
export const RACE3D_LENGTH=total;
const wrapS=s=>(s%RACE3D_LENGTH+RACE3D_LENGTH)%RACE3D_LENGTH;

function segmentAtS(s){
 const q=wrapS(s);let lo=0,hi=points.length-1;
 while(lo+1<hi){const mid=(lo+hi)>>1;if(points[mid].s<=q)lo=mid;else hi=mid;}
 const a=points[lo],b=points[Math.min(lo+1,points.length-1)],d=Math.max(EPS,b.s-a.s),u=clamp((q-a.s)/d,0,1);
 return{a,b,u,i:lo};
}
function mixFrame(a,b,u){
 const forward=norm({x:a.forward.x+(b.forward.x-a.forward.x)*u,y:a.forward.y+(b.forward.y-a.forward.y)*u,z:a.forward.z+(b.forward.z-a.forward.z)*u});
 const up=norm({x:a.up.x+(b.up.x-a.up.x)*u,y:a.up.y+(b.up.y-a.up.y)*u,z:a.up.z+(b.up.z-a.up.z)*u});
 const right=norm(cross(up,forward));
 return{forward,up,right};
}
function kindBetween(a,b,u){
 if(a.kind==='loop'||b.kind==='loop')return'loop';
 if(a.kind==='jump-gap'||b.kind==='jump-gap')return'jump-gap';
 if(a.kind==='jump-ramp'||b.kind==='jump-ramp')return'jump-ramp';
 if(a.kind==='jump-landing'||b.kind==='jump-landing')return'jump-landing';
 if(a.kind==='bridge'||b.kind==='bridge')return'bridge';
 return'track';
}
export function racePointAt(s,lane=0){
 const {a,b,u}=segmentAtS(s),f=mixFrame(a,b,u),center={x:a.x+(b.x-a.x)*u,y:a.y+(b.y-a.y)*u,z:a.z+(b.z-a.z)*u};
 const pos=add(center,mul(f.right,lane)),kind=kindBetween(a,b,u),bank=(a.bank||0)+((b.bank||0)-(a.bank||0))*u;
 return{x:pos.x,y:pos.y,z:pos.z,cx:center.x,cy:center.y,cz:center.z,dx:f.forward.x,dy:f.forward.y,dz:f.forward.z,heading:Math.atan2(f.forward.x,f.forward.z),forward:f.forward,up:f.up,right:f.right,bank,kind,s:wrapS(s),lane};
}

const grid=new Map(),segments=[];
function cellKey(ix,iz){return`${ix},${iz}`;}
for(let i=0;i<points.length-1;i++){
 const a=points[i],b=points[i+1],seg={i,a,b};segments.push(seg);
 const minX=Math.min(a.x,b.x)-2,maxX=Math.max(a.x,b.x)+2,minZ=Math.min(a.z,b.z)-2,maxZ=Math.max(a.z,b.z)+2;
 for(let ix=Math.floor(minX/CELL);ix<=Math.floor(maxX/CELL);ix++)for(let iz=Math.floor(minZ/CELL);iz<=Math.floor(maxZ/CELL);iz++){
  const k=cellKey(ix,iz);if(!grid.has(k))grid.set(k,[]);grid.get(k).push(seg);
 }
}
function nearby(x,z){
 const ix=Math.floor(x/CELL),iz=Math.floor(z/CELL),out=[],seen=new Set();
 for(let dx=-1;dx<=1;dx++)for(let dz=-1;dz<=1;dz++)for(const s of grid.get(cellKey(ix+dx,iz+dz))||[])if(!seen.has(s.i)){seen.add(s.i);out.push(s);}
 return out.length?out:segments;
}
function sDelta(a,b){let d=wrapS(a)-wrapS(b);if(d>RACE3D_LENGTH/2)d-=RACE3D_LENGTH;if(d<-RACE3D_LENGTH/2)d+=RACE3D_LENGTH;return d;}
export function projectRacePoint(x,y,z,hintS=null,use3D=true){
 const p={x,y:Number.isFinite(y)?y:0,z};let best=null,bestCost=Infinity;
 for(const seg of nearby(x,z)){
  const a=seg.a,b=seg.b,v=sub(b,a),w=sub(p,a);
  const vv=use3D?dot(v,v):v.x*v.x+v.z*v.z;
  const numer=use3D?dot(w,v):w.x*v.x+w.z*v.z,u=clamp(numer/Math.max(EPS,vv),0,1);
  const center={x:a.x+v.x*u,y:a.y+v.y*u,z:a.z+v.z*u},f=mixFrame(a,b,u),d=sub(p,center);
  const lane=dot(d,f.right),vertical=dot(d,f.up),s=a.s+(b.s-a.s)*u,flat2=(p.x-center.x)**2+(p.z-center.z)**2,dist2=use3D?flat2+(p.y-center.y)**2:flat2;
  const hint=hintS==null?0:Math.pow(Math.abs(sDelta(s,hintS))/14,2)*.06,cost=dist2+hint;
  if(cost<bestCost){bestCost=cost;best={s:wrapS(s),lane,vertical,distance:Math.sqrt(dist2),x:center.x,y:center.y,z:center.z,dx:f.forward.x,dy:f.forward.y,dz:f.forward.z,heading:Math.atan2(f.forward.x,f.forward.z),forward:f.forward,up:f.up,right:f.right,bank:(a.bank||0)+((b.bank||0)-(a.bank||0))*u,kind:kindBetween(a,b,u),segment:seg.i};}
 }
 return best;
}
export function sampleRaceSurface(x,y,z,up={x:0,y:1,z:0},forChassis=false){
 const p=projectRacePoint(x,y,z,null,true);if(!p)return null;
 const allowance=RACE3D_TRACK.halfWidth+(forChassis?2.1:1.35);if(Math.abs(p.lane)>allowance||p.kind==='jump-gap')return null;
 const lane=clamp(p.lane,-RACE3D_TRACK.halfWidth,RACE3D_TRACK.halfWidth),point={x:p.x+p.right.x*lane,y:p.y+p.right.y*lane,z:p.z+p.right.z*lane};
 const d=(x-point.x)*p.up.x+(y-point.y)*p.up.y+(z-point.z)*p.up.z,align=dot(up,p.up);
 return{point,normal:p.up,kind:`race-${p.kind}`,d,align,s:p.s,lane:p.lane};
}

function nearestByKind(kind,highest=false){let pick=null;for(const p of points)if(p.kind===kind&&(!pick||(highest?p.y>pick.y:p.s<pick.s)))pick=p;return pick;}
const loopPts=points.filter(p=>p.kind==='loop'),gapPts=points.filter(p=>p.kind==='jump-gap'),bridge=nearestByKind('bridge',true);
export function race3DFeatureSpec(){
 const loopStart=loopPts[0]?.s||0,loopEnd=loopPts.at(-1)?.s||0,gapStart=gapPts[0]?.s||0,gapEnd=gapPts.at(-1)?.s||0;
 return{id:RACE3D_ID,length:RACE3D_LENGTH,halfWidth:RACE3D_TRACK.halfWidth,loop:{radius:LOOP_R,startS:loopStart,endS:loopEnd,maxY:Math.max(...loopPts.map(p=>p.y))},jump:{startS:gapStart,endS:gapEnd},bridge:{s:bridge?.s||0,y:bridge?.y||0},bankMax:Math.max(...points.map(p=>Math.abs(p.bank||0))),minY:Math.min(...points.map(p=>p.y)),maxY:Math.max(...points.map(p=>p.y))};
}
export function raceCourseSamples(count=320){const out=[];for(let i=0;i<=count;i++)out.push(racePointAt(i/count*RACE3D_LENGTH));return out;}
