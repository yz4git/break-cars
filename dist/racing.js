// Capsule-shaped oval. Shared exact geometry for physics, lap tracking and rendering.
export const TRACK={straight:48,radius:27,halfWidth:9,laps:4,limit:150,grace:22};
export const LENGTH=TRACK.straight*4+Math.PI*2*TRACK.radius;
const wrap=s=>(s%LENGTH+LENGTH)%LENGTH;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const angle=v=>Math.atan2(Math.sin(v),Math.cos(v));
export function trackPoint(s,lane=0){let q=wrap(s+48),x,z,dx,dz;const r=27;if(q<96){x=-48+q;z=-r;dx=1;dz=0;}else if((q-=96)<Math.PI*r){const a=q/r;x=48+r*Math.sin(a);z=-r*Math.cos(a);dx=Math.cos(a);dz=Math.sin(a);}else if((q-=Math.PI*r)<96){x=48-q;z=r;dx=-1;dz=0;}else{q-=96;const a=Math.PI+q/r;x=-48+r*Math.sin(a);z=-r*Math.cos(a);dx=Math.cos(a);dz=Math.sin(a);}return{x:x+dz*lane,z:z-dx*lane,heading:Math.atan2(dx,dz),dx,dz};}
export function projectTrack(x,z){const centerX=clamp(x,-48,48),nx=x-centerX,nz=z,radial=Math.hypot(nx,nz);let q;if(x>48){q=96+clamp(Math.atan2(x-48,-z),0,Math.PI)*27;}else if(x< -48){let a=Math.atan2(x+48,-z);if(a<0)a+=Math.PI*2;q=192+Math.PI*27+(clamp(a,Math.PI,2*Math.PI)-Math.PI)*27;}else q=z<=0?x+48:96+Math.PI*27+48-x;return{s:wrap(q-48),lane:radial-27,nx:radial>0?nx/radial:0,nz:radial>0?nz/radial:1,radial};}
export function setupRace(w){w.mode='racing';w.limit=TRACK.limit;w.finishCount=0;w.endAt=TRACK.limit;for(const c of w.cars){const slot=c.id===0?11:c.id-1,grid=-8-Math.floor(slot/2)*6.2,lane=(slot%2?1:-1)*3;const p=trackPoint(grid,lane);Object.assign(c,{x:p.x,z:p.z,heading:p.heading,hp:c.hp*1.75,maxHP:c.maxHP*1.75,raceDistance:grid,trackS:wrap(grid),nextGate:0,lap:0,finished:false,finishTime:null,finishOrder:0,lane:lane+(w.rand()-.5)*1.4,wrongWay:0,gateDistance:0,aiReverse:0,stallTime:0,recoveryAt:-10});}return w;}
export function trackPosition(w){return [...w.cars].sort((a,b)=>Number(b.finished)-Number(a.finished)||(a.finished?a.finishOrder-b.finishOrder:0)||Number(a.dead)-Number(b.dead)||b.raceDistance-a.raceDistance||a.id-b.id);}
const PLACE_POINTS=[3500,2900,2400,2000,1700,1400,1150,900,700,500,350,200];
export function racingPoints(c){const lapPoints=Math.min(c.lap,TRACK.laps)*400,finishPoints=c.finished?PLACE_POINTS[c.finishOrder-1]||0:0;return{lapPoints,finishPoints,total:c.score+lapPoints+finishPoints};}
export function racingRanking(w){return [...w.cars].sort((a,b)=>racingPoints(b).total-racingPoints(a).total||Number(b.finished)-Number(a.finished)||b.raceDistance-a.raceDistance);}
export function advanceRace(w,c,dt){if(c.finished||c.dead)return;const p=projectTrack(c.x,c.z);let delta=p.s-c.trackS;if(delta>LENGTH/2)delta-=LENGTH;if(delta< -LENGTH/2)delta+=LENGTH;c.trackS=p.s;
 // Reject teleports; signed progress and ordered quarter-lap gates prevent shortcuts and reverse farming.
 if(Math.abs(delta)>4||Math.abs(p.lane)>TRACK.halfWidth+1)return;
 const previous=c.raceDistance;c.raceDistance+=delta;c.wrongWay=delta<-.015?Math.min(c.wrongWay+dt,5):Math.max(0,c.wrongWay-dt*2);
 const gate=c.nextGate*LENGTH/4;if(previous<gate&&c.raceDistance>=gate){c.nextGate++;c.gateDistance=gate;if(c.nextGate>1&&(c.nextGate-1)%4===0){c.lap++;w.events.push({type:'lap',car:c.id,lap:c.lap});if(c.lap>=TRACK.laps){c.finished=true;c.finishTime=w.time;c.finishOrder=++w.finishCount;w.endAt=Math.min(w.endAt,w.time+TRACK.grace);w.events.push({type:'finish',car:c.id,place:c.finishOrder});}}}
}
export function racingAI(w,c,dt){if(c.finished)return{gas:0,brake:1,steer:0};const p=projectTrack(c.x,c.z),speed=Math.hypot(c.vx,c.vz);c.stallTime=speed<2?c.stallTime+dt:Math.max(0,c.stallTime-dt);if(c.stallTime>1.6){c.aiReverse=1.0;c.stallTime=0;}
 let lane=c.lane;const lookAhead=clamp(8+speed*.44,9,21);for(const o of w.cars){if(o===c||o.finished)continue;let gap=projectTrack(o.x,o.z).s-p.s;if(gap<0)gap+=LENGTH;if(gap>18)continue;const otherLane=projectTrack(o.x,o.z).lane;if(o.dead&&gap<16){if(Math.abs(otherLane-lane)<3.2)lane=otherLane>0?-4.8:4.8;}else if(gap>3&&gap<12&&Math.abs(otherLane-lane)<4&&c.id%3===0){lane=clamp(otherLane+(c.id%2?.9:-.9),-4.8,4.8);}}
 const target=trackPoint(p.s+lookAhead,lane),delta=angle(Math.atan2(target.x-c.x,target.z-c.z)-c.heading);
 if(c.aiReverse>0){c.aiReverse-=dt;return{gas:0,brake:1,steer:-Math.sign(delta),hand:0};}
 const turn=angle(trackPoint(p.s+25).heading-trackPoint(p.s).heading),targetSpeed=Math.abs(turn)>.3?18.5+(c.id%3):25+(c.id%3);return{gas:speed<targetSpeed?1:.25,brake:speed>targetSpeed+3?1:0,steer:clamp(delta*1.8,-1,1),hand:Math.abs(delta)>1.1&&speed>12?1:0};
}
export function constrainTrack(c){const p=projectTrack(c.x,c.z),outer=27+9-2.45,inner=27-9+2.45;let nx=0,nz=0;if(p.radial>outer){const excess=p.radial-outer;c.x-=p.nx*excess;c.z-=p.nz*excess;nx=p.nx;nz=p.nz;}else if(p.radial<inner){const excess=inner-p.radial;c.x+=p.nx*excess;c.z+=p.nz*excess;nx=-p.nx;nz=-p.nz;}else return null;return{nx,nz,speed:Math.max(0,c.vx*nx+c.vz*nz)};}
export function recoverRaceCar(w,c){if(c.dead||c.finished||w.time-c.recoveryAt<5)return false;const p=trackPoint(c.trackS,c.lane);Object.assign(c,{x:p.x,z:p.z,heading:p.heading,vx:0,vz:0,omega:0,wrongWay:0,recoveryAt:w.time});c.score=Math.max(0,c.score-200);w.events.push({type:'recover',car:c.id});return true;}
