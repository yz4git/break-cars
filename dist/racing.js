import {RACE3D_LENGTH,RACE3D_TRACK,racePointAt,projectRacePoint,race3DFeatureSpec} from './racing3d.js?v=wr3d-v1';

export const TRACK={straight:0,radius:0,halfWidth:RACE3D_TRACK.halfWidth,laps:4,limit:165,grace:24,name:'RAMPAGE 3D'};
export const LENGTH=RACE3D_LENGTH;
const wrap=s=>(s%LENGTH+LENGTH)%LENGTH;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const angle=v=>Math.atan2(Math.sin(v),Math.cos(v));
const carY=c=>c.p3?.py;
const projectCar=c=>projectTrack(c.x,c.z,carY(c),c.trackS);
const dist3=(a,b)=>Math.hypot(a.x-b.x,(a.p3?.py??0)-(b.p3?.py??0),a.z-b.z);

export function trackPoint(s,lane=0){return racePointAt(s,lane);}
export function projectTrack(x,z,y=null,hintS=null){return projectRacePoint(x,y??0,z,hintS,y!=null);}
export {race3DFeatureSpec};

export function setupRace(w){
 w.mode='racing';w.limit=TRACK.limit;w.finishCount=0;w.endAt=TRACK.limit;w.raceCourse='rampage-3d';
 for(const c of w.cars){
  const slot=c.id===0?11:c.id-1,grid=-9-Math.floor(slot/2)*6.5,lane=(slot%2?1:-1)*2.8,p=trackPoint(grid,lane);
  Object.assign(c,{x:p.x,z:p.z,heading:p.heading,hp:c.hp*1.75,maxHP:c.maxHP*1.75,raceDistance:grid,trackS:wrap(grid),nextGate:0,lap:0,finished:false,finishTime:null,finishOrder:0,lane:lane+(w.rand()-.5)*1.25,wrongWay:0,gateDistance:0,aiReverse:0,stallTime:0,recoveryAt:-10,raceAggro:clamp(.72+(c.id%4)*.07+(w.rand()-.5)*.1,.66,.98),battleTarget:-1,battleTimer:.08+w.rand()*.35,battleSide:c.id%2?1:-1,brawlTimer:.6+w.rand()*1.5});
 }
 return w;
}
export function trackPosition(w){return [...w.cars].sort((a,b)=>Number(b.finished)-Number(a.finished)||(a.finished?a.finishOrder-b.finishOrder:0)||Number(a.dead)-Number(b.dead)||b.raceDistance-a.raceDistance||a.id-b.id);}
const PLACE_POINTS=[3500,2900,2400,2000,1700,1400,1150,900,700,500,350,200];
export function racingPoints(c){const lapPoints=Math.min(c.lap,TRACK.laps)*400,finishPoints=c.finished?PLACE_POINTS[c.finishOrder-1]||0:0;return{lapPoints,finishPoints,total:c.score+lapPoints+finishPoints};}
export function racingRanking(w){return [...w.cars].sort((a,b)=>racingPoints(b).total-racingPoints(a).total||Number(b.finished)-Number(a.finished)||b.raceDistance-a.raceDistance);}

export function advanceRace(w,c,dt){
 if(c.finished||c.dead)return;
 const p=projectCar(c);if(!p)return;
 let delta=p.s-c.trackS;if(delta>LENGTH/2)delta-=LENGTH;if(delta<-LENGTH/2)delta+=LENGTH;c.trackS=p.s;
 // Ordered progress remains continuous through the vertical loop and the upper/lower crossover.
 if(Math.abs(delta)>5.5||Math.abs(p.lane)>TRACK.halfWidth+1.5)return;
 const previous=c.raceDistance;c.raceDistance+=delta;c.wrongWay=delta<-.02?Math.min(c.wrongWay+dt,5):Math.max(0,c.wrongWay-dt*2);
 const gate=c.nextGate*LENGTH/4;
 if(previous<gate&&c.raceDistance>=gate){
  c.nextGate++;c.gateDistance=gate;
  if(c.nextGate>1&&(c.nextGate-1)%4===0){
   c.lap++;w.events.push({type:'lap',car:c.id,lap:c.lap});
   if(c.lap>=TRACK.laps){c.finished=true;c.finishTime=w.time;c.finishOrder=++w.finishCount;w.endAt=Math.min(w.endAt,w.time+TRACK.grace);w.events.push({type:'finish',car:c.id,place:c.finishOrder});}
  }
 }
}

export function racingAI(w,c,dt){
 if(c.finished)return{gas:0,brake:1,steer:0};
 const p=projectCar(c),speed=Math.hypot(c.vx,c.vz),aggro=c.raceAggro??.8;if(!p)return{gas:1,brake:0,steer:0,hand:0};
 c.stallTime=speed<2?c.stallTime+dt:Math.max(0,c.stallTime-dt);if(c.stallTime>1.6&&p.kind!=='loop'){c.aiReverse=1.0;c.stallTime=0;}
 // The loop is a precision stunt: stay centered and committed instead of trying to ram halfway up a wall.
 if(p.kind==='loop'){c.battleTarget=-1;return{gas:1,brake:0,steer:clamp(-p.lane*.16,-.42,.42),hand:0};}
 const stunt=p.kind==='jump-ramp'||p.kind==='jump-gap'||p.kind==='jump-landing';
 c.brawlTimer=(c.brawlTimer??0)-dt;if(c.brawlTimer<=0){c.brawlTimer=.7+w.rand()*1.4;if(w.rand()<.6)c.battleSide*=-1;}
 c.battleTimer=(c.battleTimer??0)-dt;const current=w.cars[c.battleTarget],currentGap=current?current.raceDistance-c.raceDistance:99;
 if(stunt)c.battleTarget=-1;
 else if(c.battleTimer<=0||!current||current.dead||current.finished||current===c||currentGap>21||currentGap<-8){
  let best=Infinity,target=-1;
  for(const o of w.cars){
   if(o===c||o.dead||o.finished)continue;const gap=o.raceDistance-c.raceDistance;if(gap<-6.5||gap>19.5)continue;
   const op=projectCar(o),laneGap=Math.abs((op?.lane??99)-p.lane),worldDist=dist3(o,c);if(!op||laneGap>7.2||worldDist>23||Math.abs((o.p3?.py??op.y)-(c.p3?.py??p.y))>4.5)continue;
   const hp=o.hp/Math.max(1,o.maxHP),alongside=Math.abs(gap)<5.2?-1.25:0,finisher=hp<.42?-1.15:hp<.68?-.45:0,ahead=gap>2&&gap<11?-.5:0,behind=gap<0?Math.abs(gap)*.1:0,score=worldDist*.16+laneGap*.24+Math.abs(gap-3.5)*.16+behind+alongside+finisher+ahead-(o.id===0?.08:0)+(o.id%5)*.02;
   if(score<best){best=score;target=o.id;}
  }
  c.battleTarget=target;c.battleTimer=.16+(1-aggro)*.32+w.rand()*.18;
 }
 let lane=c.lane,pack=false,attack=false,sideBySide=false,attackGap=99;const rival=w.cars[c.battleTarget],turnSoon=Math.abs(angle(trackPoint(p.s+20).heading-trackPoint(p.s).heading));
 if(rival&&!rival.dead&&!rival.finished&&!stunt){
  const rp=projectCar(rival),gap=rival.raceDistance-c.raceDistance,laneGap=(rp?.lane??99)-p.lane,worldDist=dist3(rival,c);sideBySide=Math.abs(gap)<5.5&&Math.abs(laneGap)<6.2&&worldDist<10;
  const ahead=gap>=0&&gap<17&&Math.abs(laneGap)<7&&worldDist<20,trailingHit=gap<0&&gap>-5.5&&worldDist<8;pack=sideBySide||ahead||trailingHit;attackGap=gap;attack=pack&&turnSoon<.92;
  if(attack){let desiredLane=rp.lane;if(sideBySide||trailingHit)desiredLane+=c.battleSide*.06;else if(gap>7)desiredLane+=c.battleSide*.14;const strength=clamp(.72+aggro*.28+(rival.hp/rival.maxHP<.5?.08:0),0,1);lane=clamp(lane+(desiredLane-lane)*strength,-5.9,5.9);}else if(ahead){lane=clamp(lane+(rp.lane-lane)*(.36+aggro*.24),-5.7,5.7);}
 }
 for(const o of w.cars){if(o===c||o.finished)continue;const op=projectCar(o),gap=o.raceDistance-c.raceDistance;if(op&&o.dead&&gap>-2&&gap<16&&Math.abs(op.lane-lane)<3.5&&Math.abs((o.p3?.py??op.y)-(c.p3?.py??p.y))<3){lane=op.lane>0?-5:5;c.battleTarget=-1;attack=false;pack=false;}}
 if(Math.abs(p.lane)>5.9)lane=clamp(lane-p.lane*.44,-4.6,4.6);
 const lookAhead=stunt?12:attack?clamp(6+speed*.24,7,13):clamp(8+speed*.44,9,21),target=trackPoint(p.s+lookAhead,lane),delta=angle(Math.atan2(target.x-c.x,target.z-c.z)-c.heading);
 if(c.aiReverse>0){c.aiReverse-=dt;return{gas:0,brake:1,steer:-Math.sign(delta),hand:0};}
 if(stunt)return{gas:1,brake:0,steer:clamp(delta*1.45,-.65,.65),hand:0};
 const turn=angle(trackPoint(p.s+25).heading-trackPoint(p.s).heading),bankHelp=Math.min(Math.abs(target.bank||0)*10,2.5),baseSpeed=Math.abs(turn)>.3?18.5+(c.id%3)+bankHelp:25+(c.id%3),fightBoost=attack?5.2+aggro*3.1:pack?2.4+aggro*1.4:0,targetSpeed=baseSpeed+fightBoost,closingRam=attack&&attackGap>1.5&&attackGap<13,gas=speed<targetSpeed?1:attack?.78:.25,brake=attack?0:speed>targetSpeed+(pack?5.2:3)?1:0;
 return{gas:closingRam?1:gas,brake,steer:clamp(delta*(attack?2.35:1.8),-1,1),hand:Math.abs(delta)>1.22&&speed>14&&!attack?1:0};
}

export function constrainTrack(c){
 const p=projectCar(c);if(!p||p.kind==='jump-gap')return null;
 const limit=TRACK.halfWidth-2.45,over=Math.abs(p.lane)-limit;if(over<=0)return null;
 const sign=Math.sign(p.lane)||1,nx=p.right.x*sign,ny=p.right.y*sign,nz=p.right.z*sign,correction={x:-nx*over,y:-ny*over,z:-nz*over};
 c.x+=correction.x;c.z+=correction.z;
 const vx=c.p3?.vx??c.vx,vy=c.p3?.vy??0,vz=c.p3?.vz??c.vz;
 return{nx,ny,nz,speed:Math.max(0,vx*nx+vy*ny+vz*nz),correction,projection:p};
}
export function recoverRaceCar(w,c){
 if(c.dead||c.finished||w.time-c.recoveryAt<5)return false;
 const p=trackPoint(c.trackS,clamp(c.lane,-4.8,4.8));Object.assign(c,{x:p.x,z:p.z,heading:p.heading,vx:0,vz:0,omega:0,wrongWay:0,recoveryAt:w.time});c.score=Math.max(0,c.score-200);w.events.push({type:'recover',car:c.id});return true;
}
