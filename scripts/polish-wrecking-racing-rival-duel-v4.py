'''WRECKING RACING Rival Duel v4.

Make the battle rhythm readable as a persistent one-on-one rivalry without
changing vehicle physics, damage, scoring, or input. The player gets one active
rival selected from recent car contacts and nearby race-progress competitors.
Selection uses hysteresis so an overtake does not instantly swap opponents.

The runtime exposes a compact HUD/radar treatment and PASS/COUNTER beats. All
camera/impact presentation remains owned by the existing Impact Cinema layer.
'''
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'WRECKING RACING rival duel v4 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_wrecking_racing_rival_duel_v4(target: Path) -> None:
    racing = target / 'racing.js'
    r = racing.read_text()
    marker = 'WRECKING_RACING_RIVAL_DUEL_V4'
    if marker in r:
        raise RuntimeError('WRECKING RACING rival duel v4 already applied')

    r += r'''

// WRECKING_RACING_RIVAL_DUEL_V4
const rivalGapSideV4=(gap,previous=0)=>gap>2.2?1:gap<-2.2?-1:previous;
export function racingRivalState(gap,worldDistance,battlePhase='CHASE'){
 const phase=String(battlePhase||'CHASE');
 if(phase==='BREAKAWAY')return'BREAKAWAY';
 if(phase==='REMATCH')return'REMATCH';
 if(worldDistance<10&&Math.abs(gap)<5.5)return'SIDE BY SIDE';
 if(gap>8)return'HUNT';
 if(gap<-8)return'DEFEND';
 return'DUEL';
}
export function racingRivalDirector(w,dt=1/60){
 if(!w||w.mode!=='racing'||!Array.isArray(w.cars)||!w.cars.length)return null;
 const p=w.cars[0],now=Number.isFinite(w.time)?w.time:0;
 if(!p||p.dead||p.finished){w.raceRival=null;w.raceRivalId=-1;return null;}
 const previousId=Number.isInteger(w.raceRivalId)?w.raceRivalId:-1,current=w.cars[previousId];
 const contactAge=o=>{
  const a=p.raceCarContactAt,b=o?.raceCarContactAt;
  return Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<.08?Math.max(0,now-Math.max(a,b)):99;
 };
 const metrics=o=>{
  if(!o||o===p||o.dead||o.finished)return null;
  const gap=(o.raceDistance??0)-(p.raceDistance??0),distance=dist3(o,p),recent=contactAge(o);
  if(!((Math.abs(gap)<68&&distance<44)||recent<4.5))return null;
  const targeted=o.battleTarget===0?-1.8:0,currentBias=o.id===previousId?-3.2:0,contactBias=Math.max(0,4.5-recent)*-2.65;
  const score=Math.abs(gap)*.27+distance*.22+targeted+currentBias+contactBias;
  return{o,gap,distance,recent,score};
 };
 let best=null;
 for(const o of w.cars){const m=metrics(o);if(m&&(!best||m.score<best.score))best=m;}
 let chosen=metrics(current);
 if(!chosen||(now>=(w.raceRivalLockUntil??-1)&&best&&best.o.id!==previousId&&best.score<chosen.score-4.2))chosen=best;
 if(!chosen){w.raceRival=null;w.raceRivalId=-1;return null;}
 const changed=chosen.o.id!==previousId;
 if(changed){
  w.raceRivalId=chosen.o.id;w.raceRivalLockUntil=now+2.4;w.raceRivalSide=rivalGapSideV4(chosen.gap,0);
  w.raceRivalSelectedAt=now;w.raceRivalLastEvent='LOCK';w.raceRivalLastEventAt=now;
 }else if(chosen.recent<.12)w.raceRivalLockUntil=Math.max(w.raceRivalLockUntil??0,now+3.2);
 const before=w.raceRivalSide??rivalGapSideV4(chosen.gap,0),after=rivalGapSideV4(chosen.gap,before);
 if(!changed&&before!==0&&after!==before&&now-(w.raceRivalSelectedAt??-99)>.35){
  const type=before===1&&after===-1?'rival-pass':before===-1&&after===1?'rival-counter':null;
  if(type){
   w.raceRivalLastEvent=type==='rival-pass'?'PASS':'COUNTER';w.raceRivalLastEventAt=now;
   w.raceRivalLockUntil=Math.max(w.raceRivalLockUntil??0,now+3.4);
   if(type==='rival-pass')w.raceRivalPasses=(w.raceRivalPasses||0)+1;else w.raceRivalCounters=(w.raceRivalCounters||0)+1;
   w.events?.push({type,car:0,rival:chosen.o.id,gap:chosen.gap,x:(p.x+chosen.o.x)/2,z:(p.z+chosen.o.z)/2});
  }
 }
 w.raceRivalSide=after;
 const phase=p.raceBattlePhase||chosen.o.raceBattlePhase||'CHASE',state=racingRivalState(chosen.gap,chosen.distance,phase);
 const snapshot={version:'4.0',id:chosen.o.id,state,gap:chosen.gap,distance:chosen.distance,contactAge:chosen.recent,
  lockedUntil:w.raceRivalLockUntil??now,passes:w.raceRivalPasses||0,counters:w.raceRivalCounters||0,
  lastEvent:w.raceRivalLastEvent||'LOCK',lastEventAt:w.raceRivalLastEventAt??now};
 w.raceRival=snapshot;return snapshot;
}
'''
    racing.write_text(r)

    game = target / 'game.js'
    g = game.read_text()
    g = one(
        g,
        'racingPoints,racingRanking,recoverRaceCar}',
        'racingPoints,racingRanking,recoverRaceCar,racingRivalDirector}',
        'game racing import',
    )
    g = one(
        g,
        'step(world,input);events();',
        "step(world,input);if(world.mode==='racing')racingRivalDirector(world,1/60);events();",
        'fixed-step rival director',
    )
    g += r'''

/* WRECKING RACING Rival Duel v4 - presentation/telemetry only. */
const rivalHudV4=document.createElement('div');
rivalHudV4.id='race-rival-v4';
rivalHudV4.innerHTML='<span class="rr-kicker">RIVAL</span><b class="rr-car">--</b><span class="rr-state">SEARCH</span><span class="rr-gap">--m</span>';
document.body.appendChild(rivalHudV4);
const rivalTelemetryV4=window.__breakCarsRivalDuelV4={version:'4.0',active:false,rivalId:-1,state:'IDLE',gap:0,distance:0,passes:0,counters:0,lastEvent:'',physicsChanged:false,scoringChanged:false};
let rivalHudEventUntilV4=0;
function updateRivalHudV4(){
 const r=world.raceRival,active=world.mode==='racing'&&r&&(mode==='race'||mode==='countdown')&&!world.cars[0].dead&&!world.cars[0].finished;
 rivalHudV4.classList.toggle('active',!!active);
 if(!active){rivalTelemetryV4.active=false;return;}
 const car=String(r.id+1).padStart(2,'0'),ahead=r.gap>=0,meters=Math.round(Math.abs(r.gap));
 rivalHudV4.querySelector('.rr-car').textContent=`#${car}`;
 rivalHudV4.querySelector('.rr-state').textContent=r.state;
 rivalHudV4.querySelector('.rr-gap').textContent=`${ahead?'▲':'▼'} ${meters}m`;
 rivalHudV4.classList.toggle('ahead',ahead);rivalHudV4.classList.toggle('behind',!ahead);
 rivalHudV4.classList.toggle('event',performance.now()<rivalHudEventUntilV4);
 Object.assign(rivalTelemetryV4,{active:true,rivalId:r.id,state:r.state,gap:r.gap,distance:r.distance,passes:r.passes,counters:r.counters,lastEvent:r.lastEvent});
}
const rivalEventsV4Base=events;
events=function(){
 for(const e of world.events||[]){
  if(e.type==='rival-pass'&&e.car===0){rivalHudEventUntilV4=performance.now()+720;toast('RIVAL PASS - DEFEND',1.05);}
  else if(e.type==='rival-counter'&&e.car===0){rivalHudEventUntilV4=performance.now()+720;toast('RIVAL COUNTER - CHASE',1.05);}
 }
 rivalEventsV4Base();
};
const rivalRadarV4Base=drawRadar;
drawRadar=function(){
 rivalRadarV4Base();
 const r=world.raceRival;if(world.mode!=='racing'||!r)return;
 const c=world.cars[r.id];if(!c||c.dead||c.finished)return;
 const ctx=$('radar').getContext('2d'),scale=.87,x=80+c.x*scale,y=80+c.z*scale;
 ctx.save();ctx.strokeStyle='#ffbd63';ctx.lineWidth=2.2;ctx.beginPath();ctx.arc(x,y,6.2,0,Math.PI*2);ctx.stroke();ctx.restore();
};
const rivalVisualsV4Base=visuals;
visuals=function(dt){rivalVisualsV4Base(dt);updateRivalHudV4();};
'''
    game.write_text(g)

    css = target / 'racing.css'
    c = css.read_text()
    c += r'''

/* WRECKING RACING Rival Duel v4: compact iPhone-landscape rivalry readout. */
#race-rival-v4{
 display:none;position:fixed;z-index:9;pointer-events:none;
 top:max(50px,calc(env(safe-area-inset-top) + 44px));left:50%;transform:translateX(-50%);
 min-width:184px;height:31px;padding:0 10px;box-sizing:border-box;
 align-items:center;justify-content:center;gap:7px;
 border:1px solid #ffbd6352;border-radius:9px;
 background:linear-gradient(90deg,#121923d9,#1e2329e8,#121923d9);
 box-shadow:0 6px 18px #0007,inset 0 1px #ffffff12;
 color:#f3f1e8;font:800 11px/1 Arial,sans-serif;letter-spacing:.06em;
 transition:transform .12s ease,filter .12s ease,border-color .12s ease;
}
body.playing #race-rival-v4.active{display:flex}
#race-rival-v4 .rr-kicker{font-size:9px;letter-spacing:.17em;color:#ffbd63}
#race-rival-v4 .rr-car{font-size:15px;font-style:italic;color:#fff3db}
#race-rival-v4 .rr-state{min-width:72px;text-align:center;font-size:9px;color:#d9e0e5}
#race-rival-v4 .rr-gap{min-width:45px;text-align:right;font-variant-numeric:tabular-nums;color:#ffc977}
#race-rival-v4.behind .rr-gap{color:#84e4cd}
#race-rival-v4.event{transform:translateX(-50%) scale(1.055);filter:brightness(1.28);border-color:#ffd28ca8}
@media(orientation:landscape) and (max-height:430px){
 #race-rival-v4{top:max(44px,calc(env(safe-area-inset-top) + 39px));min-width:174px;height:28px;padding:0 8px;gap:6px}
 #race-rival-v4 .rr-car{font-size:14px}#race-rival-v4 .rr-state{min-width:67px}
}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_wrecking_racing_rival_duel_v4(Path('_site'))
