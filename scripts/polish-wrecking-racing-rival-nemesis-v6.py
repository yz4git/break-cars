"""WRECKING RACING Rival Nemesis v6.

Give the existing Rival Feud a deterministic driving personality without
changing vehicle forces, damage, score, course geometry, loop handling, or jump
handling. Nemesis pressure is lane/target intent only and is disabled inside
vertical loops and jump flight/ramp/landing sections. FINAL DUEL strengthens
that safe-road intent, while finish order resolves the feud.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'WRECKING RACING rival nemesis v6 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_wrecking_racing_rival_nemesis_v6(target: Path) -> None:
    racing = target / 'racing.js'
    r = racing.read_text()
    marker = 'WRECKING_RACING_RIVAL_NEMESIS_V6'
    if marker in r:
        raise RuntimeError('WRECKING RACING rival nemesis v6 already applied')

    ai_head = """let lane=c.lane,pack=false,attack=false,sideBySide=false,attackGap=99;const tactic=racingTacticalZone(p.s),tacticalLap=Math.max(0,Math.floor(Math.max(0,c.raceDistance)/LENGTH));c.raceTacticalZone=tactic.type;const rival=w.cars[c.battleTarget],turnSoon=Math.abs(angle(trackPoint(p.s+20).heading-trackPoint(p.s).heading));"""
    ai_head_v6 = """let lane=c.lane,pack=false,attack=false,sideBySide=false,attackGap=99;const tactic=racingTacticalZone(p.s),tacticalLap=Math.max(0,Math.floor(Math.max(0,c.raceDistance)/LENGTH));c.raceTacticalZone=tactic.type;
 const personaV6=racingRivalPersonality(c.id),feudV6=w.raceRivalFeud,playerV6=w.cars[0],playerGapV6=playerV6?(playerV6.raceDistance??0)-(c.raceDistance??0):99;
 const activeNemesisV6=c.id>0&&playerV6&&!playerV6.dead&&!playerV6.finished&&(c.id===w.raceRivalId||c.id===feudV6?.archId||c.id===feudV6?.revengeId||c.id===feudV6?.finalDuelId);
 const finalDuelV6=!!(activeNemesisV6&&feudV6?.finalDuelAnnounced&&!feudV6?.finalDuelResolved&&c.id===feudV6?.finalDuelId);
 const safeNemesisV6=!stunt&&p.kind!=='loop'&&tactic.type!=='jump-split'&&tactic.type!=='jump-flight';
 if(activeNemesisV6&&safeNemesisV6&&racingNemesisShouldPursue(personaV6,playerGapV6,tactic.type,finalDuelV6)){c.battleTarget=0;c.battleTimer=Math.max(c.battleTimer??0,finalDuelV6 ? .72 : .34);}
 const rival=w.cars[c.battleTarget],turnSoon=Math.abs(angle(trackPoint(p.s+20).heading-trackPoint(p.s).heading));"""
    r = one(r, ai_head, ai_head_v6, 'AI personality target lock')

    rhythm_block = """ if(!stunt&&rhythm.lane!==null){
  const safeGoal=clamp(rhythm.lane,-5.2,5.2);lane=clamp(lane+(safeGoal-lane)*rhythm.strength,-5.6,5.6);
  if(rhythm.phase==='BREAKAWAY'){c.battleTarget=-1;attack=false;pack=false;}
 }
 if(Math.abs(p.lane)>5.9)lane=clamp(lane-p.lane*.44,-4.6,4.6);
"""
    rhythm_v6 = """ if(!stunt&&rhythm.lane!==null){
  const safeGoal=clamp(rhythm.lane,-5.2,5.2);lane=clamp(lane+(safeGoal-lane)*rhythm.strength,-5.6,5.6);
  if(rhythm.phase==='BREAKAWAY'){c.battleTarget=-1;attack=false;pack=false;}
 }
 const playerProjV6=activeNemesisV6&&playerV6?projectCar(playerV6):null;
 const intentV6=racingNemesisLaneIntent(personaV6,playerGapV6,playerProjV6?.lane??0,p.lane,tactic.type,finalDuelV6,activeNemesisV6&&safeNemesisV6);
 if(intentV6.active){lane=clamp(lane+(intentV6.laneGoal-lane)*intentV6.strength,-5.2,5.2);if(finalDuelV6){c.battleTarget=0;c.battleTimer=Math.max(c.battleTimer??0,.72);}}
 c.raceRivalPersonality=personaV6.key;c.raceNemesisIntent={version:'6.0',persona:personaV6.key,active:intentV6.active,safe:intentV6.safe,finalDuel:finalDuelV6,laneGoal:intentV6.laneGoal,strength:intentV6.strength,playerGap:playerGapV6};
 if(Math.abs(p.lane)>5.9)lane=clamp(lane-p.lane*.44,-4.6,4.6);
"""
    r = one(r, rhythm_block, rhythm_v6, 'AI safe-road nemesis lane pressure')

    early = "if(!p||p.dead||p.finished){if(extra.length)w.events.push(...extra);return base;}"
    early_v6 = "if(!p||p.dead||p.finished){if(extra.length)w.events.push(...extra);racingRivalNemesisResult(w);return base;}"
    r = one(r, early, early_v6, 'finished/dead feud resolution')

    final = """ w.raceRivalFeudSnapshot={version:'5.0',archId:feud.archId,revengeId:revengeActive?feud.revengeId:-1,revengeUntil:feud.revengeUntil,finalDuelId:feud.finalDuelId,finalDuel:!!(base?.finalDuel),finalDuelResolved:!!feud.finalDuelResolved,lastDefeatedId:feud.lastDefeatedId,history:feud.history};
 return base;
}
"""
    final_v6 = """ w.raceRivalFeudSnapshot={version:'5.0',archId:feud.archId,revengeId:revengeActive?feud.revengeId:-1,revengeUntil:feud.revengeUntil,finalDuelId:feud.finalDuelId,finalDuel:!!(base?.finalDuel),finalDuelResolved:!!feud.finalDuelResolved,lastDefeatedId:feud.lastDefeatedId,history:feud.history};
 racingRivalNemesisResult(w);
 return base;
}
"""
    r = one(r, final, final_v6, 'live feud resolution')

    r += r'''

// WRECKING_RACING_RIVAL_NEMESIS_V6
const NEMESIS_PERSONAS_V6=[
 {key:'BRAWLER',pursuit:.88,pressure:.78,finale:.96,offset:.16},
 {key:'HUNTER',pursuit:.96,pressure:.57,finale:.86,offset:.42},
 {key:'BLOCKER',pursuit:.72,pressure:.47,finale:.82,offset:.08},
 {key:'DAREDEVIL',pursuit:.84,pressure:.63,finale:.93,offset:1.18},
];
const NEMESIS_COURSE_SALT_V6={'rampage-3d':0,'sky-forge':1,'double-orbit':2};
export function racingRivalPersonality(id,courseId=COURSE_SPEC.courseId){
 const n=Math.max(1,Math.floor(Number(id)||1)),salt=NEMESIS_COURSE_SALT_V6[courseId]??0,base=NEMESIS_PERSONAS_V6[(n-1+salt)%NEMESIS_PERSONAS_V6.length];
 return{...base,index:(n-1+salt)%NEMESIS_PERSONAS_V6.length,side:((n+salt)&1)?1:-1};
}
export function racingNemesisShouldPursue(persona,playerGap,tacticType='neutral',finalDuel=false){
 if(finalDuel)return true;
 const gap=Number.isFinite(playerGap)?playerGap:99,kind=persona?.key||'HUNTER';
 if(tacticType==='jump-split'||tacticType==='jump-flight')return false;
 if(kind==='BRAWLER')return Math.abs(gap)<27;
 if(kind==='HUNTER')return gap>-20&&gap<42;
 if(kind==='BLOCKER')return gap<0&&gap>-25;
 if(kind==='DAREDEVIL')return Math.abs(gap)<34&&(tacticType==='overtake'||tacticType==='neutral'||tacticType==='loop-merge'||tacticType==='landing-merge');
 return false;
}
export function racingNemesisLaneIntent(persona,playerGap,playerLane,ownLane,tacticType='neutral',finalDuel=false,active=true){
 const safe=active&&tacticType!=='jump-split'&&tacticType!=='jump-flight',p=persona||NEMESIS_PERSONAS_V6[1],gap=Number.isFinite(playerGap)?playerGap:99;
 if(!safe)return{active:false,safe:false,laneGoal:ownLane,strength:0,finalDuel:!!finalDuel};
 let goal=playerLane,strength=p.pressure??.5;
 if(p.key==='BRAWLER')goal=playerLane+p.side*(gap>=0?.12:.28);
 else if(p.key==='HUNTER')goal=playerLane+p.side*(gap>=0?.34:.16);
 else if(p.key==='BLOCKER')goal=gap<0?playerLane+p.side*.06:playerLane+p.side*.72;
 else if(p.key==='DAREDEVIL')goal=playerLane+p.side*(gap>=0?p.offset:.58);
 if(finalDuel){strength=Math.min(.92,strength+(p.finale??.85)*.17);goal=playerLane+(goal-playerLane)*.72;}
 return{active:true,safe:true,laneGoal:feudClampV5(goal,-5.05,5.05),strength:feudClampV5(strength,.18,.92),finalDuel:!!finalDuel};
}
export function racingRivalNemesisResult(w){
 if(!w||w.mode!=='racing'||!Array.isArray(w.cars)||!w.cars.length)return null;
 const feud=w.raceRivalFeud,p=w.cars[0],state=w.raceRivalNemesis||(w.raceRivalNemesis={version:'6.0',resolved:false,result:'',rivalId:-1,resolvedAt:-1,persona:''});
 if(state.resolved)return state;
 const candidate=Number.isInteger(feud?.finalDuelId)&&feud.finalDuelId>0?feud.finalDuelId:Number.isInteger(feud?.archId)&&feud.archId>0?feud.archId:Number.isInteger(w.raceRivalId)&&w.raceRivalId>0?w.raceRivalId:-1;
 if(candidate<1||candidate>=w.cars.length)return state;
 const rival=w.cars[candidate],persona=racingRivalPersonality(candidate);let result='';
 if(rival.dead||feud?.finalDuelResolved)result='CRUSHED';
 else if(p.dead&&!rival.dead)result='LOST';
 else if(p.finished){
  if(!rival.finished)result='WON';
  else if((p.finishOrder||99)<(rival.finishOrder||99))result='WON';
  else if((p.finishOrder||99)>(rival.finishOrder||99))result='LOST';
  else result='DRAW';
 }else if(rival.finished&&!p.finished)result='LOST';
 if(!result){state.rivalId=candidate;state.persona=persona.key;return state;}
 Object.assign(state,{resolved:true,result,rivalId:candidate,resolvedAt:Number.isFinite(w.time)?w.time:0,persona:persona.key});
 w.events?.push({type:'rival-feud-result-v6',car:0,rival:candidate,result,persona:persona.key});
 return state;
}
'''
    racing.write_text(r)

    game = target / 'game.js'
    g = game.read_text()
    g += r'''

/* WRECKING RACING Rival Nemesis v6 - personality/finale presentation only. */
const rivalPersonaV6=document.createElement('span');rivalPersonaV6.className='rr-persona-v6';rivalHudV4.appendChild(rivalPersonaV6);
const feudResultV6=document.createElement('div');feudResultV6.id='race-feud-result-v6';document.body.appendChild(feudResultV6);
const nemesisTelemetryV6=window.__breakCarsRivalNemesisV6={version:'6.0',active:false,rivalId:-1,persona:'',finalDuel:false,result:'',laneGoal:0,strength:0,physicsChanged:false,damageChanged:false,scoringChanged:false};
const nemesisHudV6Base=updateRivalHudV4;
updateRivalHudV4=function(){
 nemesisHudV6Base();const r=world.raceRival,c=r?world.cars[r.id]:null,n=world.raceRivalNemesis;
 const active=world.mode==='racing'&&r&&c&&(mode==='race'||mode==='countdown')&&!world.cars[0].dead&&!world.cars[0].finished;
 rivalPersonaV6.textContent=active?(c.raceRivalPersonality||n?.persona||''):'';
 const showResult=!!(n?.resolved&&(world.cars[0].finished||world.cars[0].dead||world.done));
 feudResultV6.classList.toggle('active',showResult);
 if(showResult)feudResultV6.textContent=`FEUD ${n.result} · RIVAL #${String(n.rivalId+1).padStart(2,'0')} · ${n.persona}`;
 const intent=c?.raceNemesisIntent;Object.assign(nemesisTelemetryV6,{active:!!active,rivalId:r?.id??-1,persona:c?.raceRivalPersonality||n?.persona||'',finalDuel:!!r?.finalDuel,result:n?.result||'',laneGoal:intent?.laneGoal??0,strength:intent?.strength??0});
};
const nemesisEventsV6Base=events;
events=function(){
 let verdict=null;for(const e of world.events||[]){if(e.type==='rival-feud-result-v6')verdict=e;}
 nemesisEventsV6Base();
 if(verdict){rivalHudEventUntilV4=performance.now()+1200;const lead=verdict.result==='CRUSHED'?'NEMESIS CRUSHED':`FEUD ${verdict.result}`;toast(`${lead} - #${String(verdict.rival+1).padStart(2,'0')} ${verdict.persona}`,2.0);}
};
'''
    game.write_text(g)

    css = target / 'racing.css'
    c = css.read_text()
    c += r'''

/* WRECKING RACING Rival Nemesis v6: personality tag + final feud verdict. */
#race-rival-v4 .rr-persona-v6{min-width:48px;text-align:center;font-size:7px;letter-spacing:.08em;color:#b9c7d1;opacity:.92}
#race-rival-v4.final-duel-v5 .rr-persona-v6{color:#ffd37d}
#race-feud-result-v6{display:none;position:fixed;z-index:15;pointer-events:none;left:50%;top:max(91px,calc(env(safe-area-inset-top) + 84px));transform:translateX(-50%);padding:8px 15px;border:1px solid #ffd37dbf;border-radius:9px;background:#171315ed;box-shadow:0 8px 24px #000a,0 0 24px #ff9c4538;color:#ffe0a4;font:900 11px/1 Arial,sans-serif;letter-spacing:.11em;white-space:nowrap}
#race-feud-result-v6.active{display:block}
@media(orientation:landscape) and (max-height:430px){#race-rival-v4 .rr-persona-v6{min-width:42px;font-size:6px}#race-feud-result-v6{top:max(82px,calc(env(safe-area-inset-top) + 75px));padding:7px 12px;font-size:10px}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_wrecking_racing_rival_nemesis_v6(Path('_site'))
