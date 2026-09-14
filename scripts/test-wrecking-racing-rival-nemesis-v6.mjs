import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';

const selected=process.env.WRECK_NEMESIS_COURSE;
if(!selected){
  for(const id of ['rampage-3d','sky-forge','double-orbit']){
    const r=spawnSync(process.execPath,[import.meta.filename],{env:{...process.env,WRECK_NEMESIS_COURSE:id},encoding:'utf8'});
    process.stdout.write(r.stdout||'');process.stderr.write(r.stderr||'');assert.equal(r.status,0,`${id}: rival nemesis v6 regression failed`);
  }
  console.log('WRECKING RACING rival nemesis v6: all 3 courses passed');
  process.exit(0);
}

globalThis.location={search:`?course=${selected}`};
const stamp=`${selected}-${Date.now()}`;
const racing=await import(`../_site/racing.js?nemesis=${stamp}`);
const {racingRivalPersonality,racingNemesisShouldPursue,racingNemesisLaneIntent,racingRivalNemesisResult,racingAI}=racing;
for(const fn of [racingRivalPersonality,racingNemesisShouldPursue,racingNemesisLaneIntent,racingRivalNemesisResult,racingAI])assert.equal(typeof fn,'function');

const roles=new Set(Array.from({length:8},(_,i)=>racingRivalPersonality(i+1,selected).key));
assert.deepEqual([...roles].sort(),['BLOCKER','BRAWLER','DAREDEVIL','HUNTER'],`${selected}: deterministic personality coverage incomplete`);
const persona=racingRivalPersonality(1,selected);
assert.equal(racingNemesisShouldPursue(persona,90,'neutral',true),true,'FINAL DUEL must force pursuit intent');
assert.equal(racingNemesisShouldPursue(persona,0,'jump-flight',false),false,'jump flight must suppress pursuit');
const jump=racingNemesisLaneIntent(persona,3,1.5,-1,'jump-flight',true,true);
assert.equal(jump.active,false,'jump flight must disable nemesis lane pressure');
assert.equal(jump.strength,0,'jump flight must have zero personality pressure');
const normal=racingNemesisLaneIntent(persona,3,1.5,-1,'neutral',false,true);
const finale=racingNemesisLaneIntent(persona,3,1.5,-1,'neutral',true,true);
assert(normal.active&&finale.active,'safe-road personality pressure should be active');
assert(finale.strength>normal.strength,`${selected}: FINAL DUEL should strengthen safe-road pressure`);
assert(Math.abs(finale.laneGoal)<=5.05,`${selected}: final lane goal escaped safety envelope`);

const mk=(id,extra={})=>({id,dead:false,finished:false,finishOrder:0,score:100+id,hp:80+id,maxHP:100,...extra});
const mock={mode:'racing',time:88,events:[],cars:[mk(0,{finished:true,finishOrder:1}),mk(1,{finished:true,finishOrder:2})],raceRivalId:1,raceRivalFeud:{history:{},archId:1,finalDuelId:1,finalDuelResolved:false}};
const before=mock.cars.map(c=>({score:c.score,hp:c.hp}));
const won=racingRivalNemesisResult(mock);
assert.equal(won.result,'WON','finish-order feud win did not resolve');
assert.equal(won.rivalId,1);
assert(mock.events.some(e=>e.type==='rival-feud-result-v6'&&e.result==='WON'),'feud verdict event missing');
assert.deepEqual(mock.cars.map(c=>({score:c.score,hp:c.hp})),before,'nemesis resolver must not change score or damage');
const eventCount=mock.events.length;racingRivalNemesisResult(mock);assert.equal(mock.events.length,eventCount,'resolved feud emitted duplicate verdict');

const crushed={mode:'racing',time:42,events:[],cars:[mk(0),mk(1,{dead:true})],raceRivalId:1,raceRivalFeud:{history:{},archId:1,finalDuelId:1,finalDuelResolved:true}};
assert.equal(racingRivalNemesisResult(crushed).result,'CRUSHED','wrecked nemesis should resolve as CRUSHED');

const gameSource=await readFile(new URL('../_site/game.js',import.meta.url),'utf8');
const racingSource=await readFile(new URL('../_site/racing.js',import.meta.url),'utf8');
const racingCss=await readFile(new URL('../_site/racing.css',import.meta.url),'utf8');
assert.match(racingSource,/WRECKING_RACING_RIVAL_NEMESIS_V6/,'v6 runtime marker missing');
assert.match(racingSource,/p\.kind!==['"]loop['"]/,'loop safety gate missing');
assert.match(racingSource,/tactic\.type!==['"]jump-split['"]&&tactic\.type!==['"]jump-flight['"]/,'jump tactical safety gate missing');
assert.match(gameSource,/__breakCarsRivalNemesisV6/,'nemesis telemetry missing');
assert.match(gameSource,/rival-feud-result-v6/,'feud verdict presentation missing');
assert.match(racingCss,/#race-feud-result-v6/,'feud verdict styling missing');

const {makeWorld,step}=await import(`../_site/physics.js?nemesis=${stamp}`);
const w=makeWorld(0,9261,'racing');w.endAt=999;w.limit=999;w.done=false;
w.raceRivalId=1;w.raceRivalFeud={version:'5.0',history:{},archId:1,revengeId:-1,revengeUntil:-1,finalDuelId:-1,finalDuelAnnounced:false,finalDuelResolved:false,lastDefeatedId:-1,lastEvent:'',lastEventAt:-99};
let personaFrames=0,activeFrames=0,safeViolations=0,maxStrength=0;
for(let frame=0;frame<360&&!w.done;frame++){
  const u=racingAI(w,w.cars[0],1/60);step(w,u,1/60,true);
  for(const c of w.cars.slice(1)){
    if(c.raceRivalPersonality)personaFrames++;
    const n=c.raceNemesisIntent;if(n){if(n.active)activeFrames++;if(n.active&&!n.safe)safeViolations++;maxStrength=Math.max(maxStrength,n.strength||0);}
  }
}
assert(personaFrames>500,`${selected}: CPU personality telemetry did not run (${personaFrames})`);
assert(activeFrames>20,`${selected}: ARCH RIVAL never applied safe-road personality pressure (${activeFrames})`);
assert.equal(safeViolations,0,`${selected}: active nemesis intent bypassed safety gate`);
assert(maxStrength<=.92+1e-9,`${selected}: personality steering strength escaped cap (${maxStrength})`);

w.raceRivalId=1;Object.assign(w.raceRivalFeud,{archId:1,finalDuelId:1,finalDuelAnnounced:true,finalDuelResolved:false});
let finalFrames=0;
for(let frame=0;frame<120&&!w.done;frame++){
  const u=racingAI(w,w.cars[0],1/60);step(w,u,1/60,true);
  if(w.cars[1].raceNemesisIntent?.finalDuel)finalFrames++;
}
assert(finalFrames>0,`${selected}: FINAL DUEL personality behavior never activated`);
console.log(`${selected}: roles=${[...roles].join('/')} personaFrames=${personaFrames} active=${activeFrames} final=${finalFrames} maxStrength=${maxStrength.toFixed(2)}`);
