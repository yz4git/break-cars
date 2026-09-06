import test from 'node:test';
import assert from 'node:assert/strict';
import {makeWorld,step} from '../dist/physics.js';
import {TRACK,LENGTH,trackPoint,projectTrack,advanceRace,racingPoints,racingRanking,recoverRaceCar} from '../dist/racing.js';

test('track projection agrees with rendering on both straights and both bends',()=>{
 for(let s=0;s<LENGTH;s+=.7)for(const lane of [-6,0,6]){const p=trackPoint(s,lane),q=projectTrack(p.x,p.z);let error=Math.abs(q.s-s);error=Math.min(error,LENGTH-error);assert(error<1e-8);assert(Math.abs(q.lane-lane)<1e-8);}
});
function moveTo(w,c,s){const p=trackPoint(s);c.x=p.x;c.z=p.z;w.time+=1/60;advanceRace(w,c,1/60);}
test('ordered gates award four laps once, then a single finishing bonus',()=>{
 const w=makeWorld(0,3,'racing'),c=w.cars[0];for(let s=c.raceDistance+1;s<=LENGTH*4+2;s+=1)moveTo(w,c,s);
 assert.equal(c.lap,4);assert(c.finished);assert.equal(c.finishOrder,1);assert.equal(w.finishCount,1);assert.equal(racingPoints(c).lapPoints,1600);assert.equal(racingPoints(c).finishPoints,3500);
 for(let i=0;i<100;i++)moveTo(w,c,LENGTH*4+3+i);assert.equal(w.finishCount,1);assert.equal(c.lap,4);
});
test('line oscillation, backwards lap and teleporting across the infield award no laps',()=>{
 const w=makeWorld(0,3,'racing'),c=w.cars[0];for(let s=c.raceDistance+1;s<=3;s++)moveTo(w,c,s);
 for(let loop=0;loop<8;loop++){for(let s=3;s>=-3;s--)moveTo(w,c,s);for(let s=-3;s<=3;s++)moveTo(w,c,s);}assert.equal(c.lap,0);
 for(let s=3;s>=-LENGTH;s--)moveTo(w,c,s);assert.equal(c.lap,0);const before=c.raceDistance;moveTo(w,c,LENGTH/2);assert.equal(c.raceDistance,before);assert.equal(c.lap,0);
});
test('recovery does not grant progress and has score penalty and cooldown',()=>{
 const w=makeWorld(0,2,'racing'),c=w.cars[0];c.score=600;const d=c.raceDistance;assert(recoverRaceCar(w,c));assert.equal(c.score,400);assert.equal(c.raceDistance,d);assert(!recoverRaceCar(w,c));w.time=6;assert(recoverRaceCar(w,c));assert.equal(c.score,200);
});
test('race score combines destruction, completed laps and finishing order',()=>{
 const w=makeWorld(0,1,'racing'),[a,b]=w.cars;Object.assign(a,{finished:true,finishOrder:1,lap:4,score:0});Object.assign(b,{finished:true,finishOrder:2,lap:4,score:1000});assert.equal(racingRanking(w)[0].id,b.id);assert.equal(racingPoints(a).total,5100);assert.equal(racingPoints(b).total,5500);
});
test('all CPU classes can complete seeded races, with finite state inside the course',()=>{
 for(const seed of [1,19,73]){const w=makeWorld(seed%3,seed,'racing');let frames=0;while(!w.done&&frames++<9100){step(w,{},1/60,true);for(const c of w.cars){assert(Number.isFinite(c.x+c.z+c.heading+c.hp+c.raceDistance));assert(Math.abs(projectTrack(c.x,c.z).lane)<11);assert(c.hp>=0&&c.hp<=c.maxHP);}}
  assert(w.done);assert(w.finishCount>=8);assert(w.cars[0].finished);assert(w.time<TRACK.limit);assert(w.cars.some(c=>c.contacts>0));
 }
});
