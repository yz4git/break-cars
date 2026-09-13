'''WRECKING RACING Rival Feud v5.

Extend Rival Duel v4 into a race-long feud without changing physics, damage,
score, input, or course geometry. Real impacts, passes, counters and wrecks build
per-opponent heat. A hot opponent becomes an ARCH RIVAL, hard counters create a
short REVENGE target, and the highest-value surviving rival is locked for the
FINAL LAP duel. Presentation adds only compact heat/finale cues on the existing
RIVAL HUD and event toasts.
'''
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'WRECKING RACING rival feud v5 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_wrecking_racing_rival_feud_v5(target: Path) -> None:
    racing = target / 'racing.js'
    r = racing.read_text()
    marker = 'WRECKING_RACING_RIVAL_FEUD_V5'
    if marker in r:
        raise RuntimeError('WRECKING RACING rival feud v5 already applied')

    r += r'''

// WRECKING_RACING_RIVAL_FEUD_V5
const feudClampV5=(v,a,b)=>Math.max(a,Math.min(b,v));
const feudRecordV5=(feud,id)=>feud.history[id]||(feud.history[id]={id,heat:0,contacts:0,playerPasses:0,rivalCounters:0,defeated:0,playerWrecked:0,revengeMarks:0,lastContactAt:-99,lastEventAt:-99});
const feudAliveV5=(w,id)=>Number.isInteger(id)&&id>0&&id<w.cars.length&&!w.cars[id].dead&&!w.cars[id].finished;
const feudMetricsV5=(w,p,id)=>{const o=w.cars[id];if(!o)return null;return{o,gap:(o.raceDistance??0)-(p.raceDistance??0),distance:dist3(o,p)};};
export function racingRivalFeudDirector(w,dt=1/60){
 if(!w||w.mode!=='racing'||!Array.isArray(w.cars)||!w.cars.length)return racingRivalDirector(w,dt);
 const p=w.cars[0],now=Number.isFinite(w.time)?w.time:0;
 const feud=w.raceRivalFeud||(w.raceRivalFeud={version:'5.0',history:{},archId:-1,revengeId:-1,revengeUntil:-1,finalDuelId:-1,finalDuelAnnounced:false,finalDuelResolved:false,lastDefeatedId:-1,lastEvent:'',lastEventAt:-99});
 const extra=[];
 const setRevenge=(id,seconds,reason)=>{if(!feudAliveV5(w,id))return;const fresh=feud.revengeId!==id||now>=(feud.revengeUntil??-1);feud.revengeId=id;feud.revengeUntil=Math.max(feud.revengeUntil??-1,now+seconds);const rec=feudRecordV5(feud,id);if(fresh){rec.revengeMarks++;feud.lastEvent='REVENGE';feud.lastEventAt=now;extra.push({type:'rival-revenge-v5',car:0,rival:id,reason});}};
 const processEvents=()=>{
  for(const e of [...(w.events||[])]){
   if(!e||e._rivalFeudV5)continue;e._rivalFeudV5=true;
   if(e.type==='impact'&&(e.a===0||e.b===0)){
    const id=e.a===0?e.b:e.a;if(!feudAliveV5(w,id))continue;
    const rec=feudRecordV5(feud,id),power=Math.max(0,Number(e.power)||0),m=feudMetricsV5(w,p,id);rec.contacts++;rec.lastContactAt=now;rec.lastEventAt=now;rec.heat=feudClampV5(rec.heat+.35+power*.115,0,12);
    const o=w.cars[id];if(power>=12&&(o.battleTarget===0||(m&&m.gap<1.5)))setRevenge(id,8,'HARD HIT');
   }else if(e.type==='rival-pass'&&Number.isInteger(e.rival)){
    const rec=feudRecordV5(feud,e.rival);rec.playerPasses++;rec.lastEventAt=now;rec.heat=feudClampV5(rec.heat+1.15,0,12);
   }else if(e.type==='rival-counter'&&Number.isInteger(e.rival)){
    const rec=feudRecordV5(feud,e.rival);rec.rivalCounters++;rec.lastEventAt=now;rec.heat=feudClampV5(rec.heat+1.35,0,12);setRevenge(e.rival,6.5,'COUNTER');
   }else if(e.type==='wreck'){
    if(Number.isInteger(e.car)&&e.car>0&&e.by===0){
     const rec=feudRecordV5(feud,e.car);rec.defeated++;rec.lastEventAt=now;rec.heat=feudClampV5(rec.heat+2.2,0,12);feud.lastDefeatedId=e.car;
     if(e.car===w.raceRivalId||e.car===feud.archId||e.car===feud.finalDuelId){feud.lastEvent='RIVAL WRECKED';feud.lastEventAt=now;extra.push({type:'rival-wrecked-v5',car:0,rival:e.car,x:e.x,z:e.z});}
     if(e.car===feud.finalDuelId)feud.finalDuelResolved=true;
    }else if(e.car===0&&Number.isInteger(e.by)&&e.by>0){
     const rec=feudRecordV5(feud,e.by);rec.playerWrecked++;rec.lastEventAt=now;rec.heat=feudClampV5(rec.heat+3,0,12);setRevenge(e.by,10,'WRECK');
    }
   }
  }
 };
 processEvents();
 let base=racingRivalDirector(w,dt);
 // Rival Duel may append PASS/COUNTER after the physics events were scanned.
 processEvents();
 if(!p||p.dead||p.finished){if(extra.length)w.events.push(...extra);return base;}
 let bestId=-1,bestScore=-Infinity;
 for(const [key,rec] of Object.entries(feud.history)){
  const id=Number(key);if(!feudAliveV5(w,id))continue;const m=feudMetricsV5(w,p,id);if(!m)continue;
  const recent=Math.max(0,5-(now-(rec.lastContactAt??-99))),score=rec.heat+Math.min(rec.contacts,8)*.08+recent*.08-Math.abs(m.gap)*.004;
  if(score>bestScore){bestScore=score;bestId=id;}
 }
 if(bestId>0&&bestScore>=2.05)feud.archId=bestId;
 const finalLap=(p.lap??0)>=TRACK.laps-1||(p.raceDistance??0)>=LENGTH*(TRACK.laps-1);
 if(finalLap&&!feud.finalDuelAnnounced){
  let id=feudAliveV5(w,feud.archId)?feud.archId:(base&&feudAliveV5(w,base.id)?base.id:-1);
  if(id<0){let nearest=Infinity;for(const o of w.cars){if(o===p||o.dead||o.finished)continue;const gap=Math.abs((o.raceDistance??0)-(p.raceDistance??0));if(gap<nearest){nearest=gap;id=o.id;}}}
  if(id>0){feud.finalDuelId=id;feud.finalDuelAnnounced=true;feud.lastEvent='FINAL DUEL';feud.lastEventAt=now;extra.push({type:'rival-final-duel-v5',car:0,rival:id});}
 }
 const revengeActive=now<(feud.revengeUntil??-1)&&feudAliveV5(w,feud.revengeId);
 let targetId=base?.id??-1;
 if(finalLap&&feud.finalDuelAnnounced&&!feud.finalDuelResolved&&feudAliveV5(w,feud.finalDuelId))targetId=feud.finalDuelId;
 else if(revengeActive){const m=feudMetricsV5(w,p,feud.revengeId);if(m&&(Math.abs(m.gap)<105||m.distance<70))targetId=feud.revengeId;}
 else if(feudAliveV5(w,feud.archId)){
  const a=feudRecordV5(feud,feud.archId),b=targetId>0?feudRecordV5(feud,targetId):null,m=feudMetricsV5(w,p,feud.archId);
  if(m&&(Math.abs(m.gap)<92||m.distance<62)&&(!b||a.heat>b.heat+1.05))targetId=feud.archId;
 }
 if(targetId>0&&feudAliveV5=(w,targetId)){
  const m=feudMetricsV5(w,p,targetId),changed=targetId!==w.raceRivalId;
  if(changed){w.raceRivalId=targetId;w.raceRivalLockUntil=Math.max(w.raceRivalLockUntil??0,now+(finalLap?8:4));w.raceRivalSide=rivalGapSideV4(m.gap,0);w.raceRivalSelectedAt=now;}
 const rec=feudRecordV5(feud,targetId),phase=p.raceBattlePhase||m.o.raceBattlePhase||'CHASE';
 let state=racingRivalState(m.gap,m.distance,phase);
 const finalTarget=finalLap&&feud.finalDuelAnnounced&&!feud.finalDuelResolved&&targetId===feud.finalDuelId;
 const revengeTarget=revengeActive&&targetId===feud.revengeId;
 if(finalTarget)state='FINAL DUEL';else if(revengeTarget)state='REVENGE';
 base={...(base||{}),version:'5.0',id:targetId,state,gap:m.gap,distance:m.distance,contactAge:Math.max(0,now-(rec.lastContactAt??-99)),lockedUntil:w.raceRivalLockUntil??now,passes:w.raceRivalPasses||0,counters:w.raceRivalCounters||0,lastEvent:feud.lastEvent||base?.lastEvent||'LOCK',lastEventAt:feud.lastEventAt??base?.lastEventAt??now,feudHeat:rec.heat,feudContacts:rec.contacts,archRival:targetId===feud.archId,revenge:revengeTarget,revengeUntil:feud.revengeUntil,finalDuel:finalTarget,finalDuelId:feud.finalDuelId,defeated:rec.defeated};
 w.raceRival=base;
 }
 if(extra.length)w.events.push(...extra);
 w.raceRivalFeudSnapshot={version:'5.0',archId:feud.archId,revengeId:revengeActive?feud.revengeId:-1,revengeUntil:feud.revengeUntil,finalDuelId:feud.finalDuelId,finalDuel:!!(base?.finalDuel),finalDuelResolved:!!feud.finalDuelResolved,lastDefeatedId:feud.lastDefeatedId,history:feud.history};
 return base;
}
'''
    racing.write_text(r)

    game = target / 'game.js'
    g = game.read_text()
    g = one(
        g,
        'racingPoints,racingRanking,recoverRaceCar,racingRivalDirector}',
        'racingPoints,racingRanking,recoverRaceCar,racingRivalDirector,racingRivalFeudDirector}',
        'game feud import',
    )
    g = one(
        g,
        "if(world.mode==='racing')racingRivalDirector(world,1/60);events();",
        "if(world.mode==='racing')racingRivalFeudDirector(world,1/60);events();",
        'fixed-step feud director',
    )
    g += r'''

/* WRECKING RACING Rival Feud v5 - history/revenge/final-duel presentation only. */
const rivalHeatV5=document.createElement('span');rivalHeatV5.className='rr-heat-v5';rivalHeatV5.textContent='◇';rivalHudV4.appendChild(rivalHeatV5);
const rivalFeudTelemetryV5=window.__breakCarsRivalFeudV5={version:'5.0',active:false,rivalId:-1,heat:0,contacts:0,archId:-1,revengeId:-1,finalDuelId:-1,finalDuel:false,defeated:0,physicsChanged:false,damageChanged:false,scoringChanged:false};
const rivalFeudHudV5Base=updateRivalHudV4;
updateRivalHudV4=function(){
 rivalFeudHudV5Base();const r=world.raceRival,f=world.raceRivalFeudSnapshot,active=world.mode==='racing'&&r&&(mode==='race'||mode==='countdown')&&!world.cars[0].dead&&!world.cars[0].finished;
 if(!active){rivalHeatV5.textContent='◇';rivalHudV4.classList.remove('revenge-v5','final-duel-v5','arch-v5');rivalFeudTelemetryV5.active=false;return;}
 const heat=Math.max(0,Number(r.feudHeat)||0),pips=Math.min(5,Math.max(1,Math.ceil(heat/2.25)));rivalHeatV5.textContent='◆'.repeat(pips);
 rivalHudV4.classList.toggle('revenge-v5',!!r.revenge);rivalHudV4.classList.toggle('final-duel-v5',!!r.finalDuel);rivalHudV4.classList.toggle('arch-v5',!!r.archRival);
 Object.assign(rivalFeudTelemetryV5,{active:true,rivalId:r.id,heat,contacts:r.feudContacts||0,archId:f?.archId??-1,revengeId:f?.revengeId??-1,finalDuelId:f?.finalDuelId??-1,finalDuel:!!r.finalDuel,defeated:r.defeated||0});
};
const rivalFeudEventsV5Base=events;
events=function(){
 let special=null;for(const e of world.events||[]){if(e.type==='rival-wrecked-v5')special={text:`RIVAL #${String(e.rival+1).padStart(2,'0')} WRECKED - FEUD WON`,duration:1.8};else if(e.type==='rival-final-duel-v5'&&!special)special={text:`FINAL LAP - RIVAL DUEL #${String(e.rival+1).padStart(2,'0')}`,duration:1.8};else if(e.type==='rival-revenge-v5'&&!special)special={text:`REVENGE TARGET #${String(e.rival+1).padStart(2,'0')}`,duration:1.15};}
 rivalFeudEventsV5Base();if(special){rivalHudEventUntilV4=performance.now()+950;toast(special.text,special.duration);}
};
'''
    game.write_text(g)

    css = target / 'racing.css'
    c = css.read_text()
    c += r'''

/* WRECKING RACING Rival Feud v5: heat + revenge + final-lap duel. */
#race-rival-v4{min-width:214px}
#race-rival-v4 .rr-heat-v5{min-width:35px;text-align:left;color:#ff9c58;font-size:8px;letter-spacing:-.03em;text-shadow:0 0 8px #ff6b3255}
#race-rival-v4.arch-v5{border-color:#ff9d656b}
#race-rival-v4.revenge-v5{border-color:#ff654a9e;box-shadow:0 6px 18px #0007,0 0 20px #ff49282e,inset 0 1px #ffffff12}
#race-rival-v4.revenge-v5 .rr-state{color:#ff9d88}
#race-rival-v4.final-duel-v5{border-color:#ffd37dbf;background:linear-gradient(90deg,#201313e8,#342018f0,#201313e8);box-shadow:0 6px 22px #0008,0 0 24px #ff9c4538,inset 0 1px #ffffff18}
#race-rival-v4.final-duel-v5 .rr-kicker,#race-rival-v4.final-duel-v5 .rr-state{color:#ffd37d}
@media(orientation:landscape) and (max-height:430px){#race-rival-v4{min-width:202px}#race-rival-v4 .rr-heat-v5{min-width:30px;font-size:7px}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_wrecking_racing_rival_feud_v5(Path('_site'))
