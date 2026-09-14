"""WRECKING RACING Rival Showdown v7.

Make the v6 rival personalities readable as driving behavior without changing
vehicle forces, damage, scoring, grip, speed, course geometry, loop handling,
or jump handling. Each persona gets a deterministic safe-road signature lane
intent. Protected loop/jump regions still win, FINAL DUEL tightens only the
intent layer, and the UI adds compact arrival/signature/result presentation.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'WRECKING RACING rival showdown v7 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_wrecking_racing_rival_showdown_v7(target: Path) -> None:
    racing = target / 'racing.js'
    r = racing.read_text()
    marker = 'WRECKING_RACING_RIVAL_SHOWDOWN_V7'
    if marker in r:
        raise RuntimeError('WRECKING RACING rival showdown v7 already applied')

    old_ai = """ const intentV6=racingNemesisLaneIntent(personaV6,playerGapV6,playerProjV6?.lane??0,p.lane,tactic.type,finalDuelV6,activeNemesisV6&&safeNemesisV6);
 if(intentV6.active){lane=clamp(lane+(intentV6.laneGoal-lane)*intentV6.strength,-5.2,5.2);if(finalDuelV6){c.battleTarget=0;c.battleTimer=Math.max(c.battleTimer??0,.72);}}
 c.raceRivalPersonality=personaV6.key;c.raceNemesisIntent={version:'6.0',persona:personaV6.key,active:intentV6.active,safe:intentV6.safe,finalDuel:finalDuelV6,laneGoal:intentV6.laneGoal,strength:intentV6.strength,playerGap:playerGapV6};
"""
    new_ai = """ const intentV6=racingNemesisLaneIntent(personaV6,playerGapV6,playerProjV6?.lane??0,p.lane,tactic.type,finalDuelV6,activeNemesisV6&&safeNemesisV6);
 const signatureV7=racingRivalSignature(personaV6,playerGapV6,playerProjV6?.lane??0,p.lane,tactic.type,finalDuelV6,activeNemesisV6&&safeNemesisV6,w.time,c.id);
 if(intentV6.active){lane=clamp(lane+(intentV6.laneGoal-lane)*intentV6.strength,-5.2,5.2);if(finalDuelV6){c.battleTarget=0;c.battleTimer=Math.max(c.battleTimer??0,.72);}}
 if(signatureV7.active){lane=clamp(lane+(signatureV7.laneGoal-lane)*signatureV7.strength,-5.2,5.2);if(signatureV7.lock){c.battleTarget=0;c.battleTimer=Math.max(c.battleTimer??0,finalDuelV6?.80:.42);}}
 c.raceRivalPersonality=personaV6.key;c.raceNemesisIntent={version:'6.0',persona:personaV6.key,active:intentV6.active,safe:intentV6.safe,finalDuel:finalDuelV6,laneGoal:intentV6.laneGoal,strength:intentV6.strength,playerGap:playerGapV6};
 c.raceRivalSignature={version:'7.0',persona:personaV6.key,key:signatureV7.key,label:signatureV7.label,short:signatureV7.short,cue:signatureV7.cue,active:signatureV7.active,safe:signatureV7.safe,finalDuel:finalDuelV6,laneGoal:signatureV7.laneGoal,strength:signatureV7.strength,phase:signatureV7.phase,playerGap:playerGapV6};
"""
    r = one(r, old_ai, new_ai, 'AI signature intent wiring')

    r += r'''

// WRECKING_RACING_RIVAL_SHOWDOWN_V7
const RIVAL_SIGNATURES_V7={
 BRAWLER:{key:'BODY_CHECK',label:'BODY CHECK',short:'RAM',cue:'CLOSE THE GAP'},
 HUNTER:{key:'SHADOW_LINE',label:'LOCK ON',short:'LOCK',cue:'STAYS ON YOUR BUMPER'},
 BLOCKER:{key:'SHUT_DOOR',label:'SHUT DOOR',short:'BLOCK',cue:'OWNS YOUR RACING LINE'},
 DAREDEVIL:{key:'CROSS_CUT',label:'CROSS CUT',short:'CUT',cue:'CROSSES THE FAST LINE'},
};
export function racingRivalSignature(persona,playerGap,playerLane,ownLane,tacticType='neutral',finalDuel=false,active=true,time=0,id=1){
 const p=persona||racingRivalPersonality(id),spec=RIVAL_SIGNATURES_V7[p.key]||RIVAL_SIGNATURES_V7.HUNTER;
 const gap=Number.isFinite(playerGap)?playerGap:99,clock=Number.isFinite(time)?time:0,cycle=((clock*.37+Math.max(0,id)*.173)%1+1)%1;
 const safe=!!active&&tacticType!=='jump-split'&&tacticType!=='jump-flight';
 if(!safe)return{...spec,active:false,safe:false,finalDuel:!!finalDuel,laneGoal:ownLane,strength:0,phase:cycle,lock:false};
 let engaged=false,goal=playerLane,strength=.18;
 if(p.key==='BRAWLER'){
  engaged=Math.abs(gap)<20&&cycle<.66;goal=playerLane-p.side*(gap>=0?.14:.06);strength=.24;
 }else if(p.key==='HUNTER'){
  engaged=gap>-18&&gap<36&&cycle<.84;goal=playerLane+p.side*.24;strength=.18;
 }else if(p.key==='BLOCKER'){
  engaged=gap<0&&gap>-28&&cycle<.76;goal=playerLane+p.side*.05;strength=.21;
 }else if(p.key==='DAREDEVIL'){
  engaged=Math.abs(gap)<30&&(tacticType==='overtake'||tacticType==='neutral')&&cycle<.72;goal=playerLane+p.side*(cycle<.36?1.35:-1.02);strength=.23;
 }
 if(finalDuel){engaged=true;strength=Math.min(.36,strength+.09);goal=playerLane+(goal-playerLane)*.82;}
 return{...spec,active:!!engaged,safe:true,finalDuel:!!finalDuel,laneGoal:feudClampV5(goal,-5.05,5.05),strength:engaged?feudClampV5(strength,.12,.36):0,phase:cycle,lock:!!engaged};
}
'''
    racing.write_text(r)

    game = target / 'game.js'
    g = game.read_text()
    g += r'''

/* WRECKING RACING Rival Showdown v7 - compact signature/arrival/finale presentation only. */
const rivalSignatureV7=document.createElement('span');rivalSignatureV7.className='rr-signature-v7';rivalHudV4.appendChild(rivalSignatureV7);
const showdownV7=document.createElement('div');showdownV7.id='race-showdown-v7';showdownV7.innerHTML='<b></b><span></span>';document.body.appendChild(showdownV7);
const showdownTitleV7=showdownV7.querySelector('b'),showdownSubV7=showdownV7.querySelector('span');
let showdownUntilV7=0,lastRivalV7=-1,lastFinalDuelV7=false,lastSignatureV7='',signaturePulseUntilV7=0;
const rivalShowdownTelemetryV7=window.__breakCarsRivalShowdownV7={version:'7.0',active:false,rivalId:-1,persona:'',signature:'',signatureActive:false,finalDuel:false,laneGoal:0,strength:0,physicsChanged:false,damageChanged:false,scoringChanged:false,speedChanged:false,gripChanged:false};
function showRivalShowdownV7(title,sub='',duration=1200,finale=false){showdownTitleV7.textContent=title;showdownSubV7.textContent=sub;showdownUntilV7=performance.now()+duration;showdownV7.classList.toggle('finale',!!finale);}
const rivalShowdownHudV7Base=updateRivalHudV4;
updateRivalHudV4=function(){
 rivalShowdownHudV7Base();
 const r=world.raceRival,c=r?world.cars[r.id]:null,sig=c?.raceRivalSignature,n=world.raceRivalNemesis;
 const active=world.mode==='racing'&&r&&c&&(mode==='race'||mode==='countdown')&&!world.cars[0].dead&&!world.cars[0].finished;
 const persona=c?.raceRivalPersonality||n?.persona||'';
 rivalSignatureV7.textContent=active&&sig?.active?sig.label:'';rivalSignatureV7.classList.toggle('active',!!(active&&sig?.active));
 if(active){rivalHudV4.dataset.personaV7=persona;}else{delete rivalHudV4.dataset.personaV7;}
 if(mode==='race'&&active&&r.id!==lastRivalV7){const lockTitle=r.revenge?'REVENGE RIVAL':r.archRival?'ARCH RIVAL':'RIVAL LOCK';showRivalShowdownV7(`${lockTitle} #${String(r.id+1).padStart(2,'0')} · ${persona}`,sig?.cue||'',1250,false);lastRivalV7=r.id;}
 if(active&&r.finalDuel&&!lastFinalDuelV7){showRivalShowdownV7(`FINAL DUEL · ${persona}`,`RIVAL #${String(r.id+1).padStart(2,'0')} · ${sig?.label||'LOCK ON'}`,1650,true);}
 lastFinalDuelV7=!!(active&&r.finalDuel);
 if(active&&sig?.active&&sig.label!==lastSignatureV7){signaturePulseUntilV7=performance.now()+420;lastSignatureV7=sig.label;}else if(!sig?.active)lastSignatureV7='';
 rivalHudV4.classList.toggle('signature-v7',performance.now()<signaturePulseUntilV7);
 showdownV7.classList.toggle('active',performance.now()<showdownUntilV7&&mode==='race'&&!world.cars[0].dead&&!world.cars[0].finished);
 const resolved=!!(n?.resolved&&(world.cars[0].finished||world.cars[0].dead||world.done));
 if(resolved){const phrase=n.result==='CRUSHED'?'NEMESIS CRUSHED':n.result==='WON'?'RIVAL DEFEATED':n.result==='LOST'?'RIVAL ESCAPED':'UNFINISHED BUSINESS';feudResultV6.textContent=`${phrase} · #${String(n.rivalId+1).padStart(2,'0')} ${n.persona}`;feudResultV6.classList.add('showdown-v7-result');}else feudResultV6.classList.remove('showdown-v7-result');
 Object.assign(rivalShowdownTelemetryV7,{active:!!active,rivalId:r?.id??-1,persona,signature:sig?.label||'',signatureActive:!!sig?.active,finalDuel:!!r?.finalDuel,laneGoal:sig?.laneGoal??0,strength:sig?.strength??0});
};
'''
    game.write_text(g)

    css = target / 'racing.css'
    c = css.read_text()
    c += r'''

/* WRECKING RACING Rival Showdown v7: readable signature attacks without center-screen clutter. */
#race-rival-v4 .rr-signature-v7{display:none;min-width:56px;text-align:center;font-size:7px;letter-spacing:.055em;color:#ffe1a6;opacity:.96}
#race-rival-v4 .rr-signature-v7.active{display:inline-block}
#race-rival-v4.signature-v7{filter:brightness(1.18);border-color:#ffd28ca8}
#race-rival-v4[data-persona-v7='HUNTER'] .rr-signature-v7{color:#9eeadd}
#race-rival-v4[data-persona-v7='BLOCKER'] .rr-signature-v7{color:#ffe0a0}
#race-rival-v4[data-persona-v7='DAREDEVIL'] .rr-signature-v7{color:#ffc2ef}
#race-showdown-v7{display:none;position:fixed;z-index:14;pointer-events:none;left:50%;top:max(84px,calc(env(safe-area-inset-top) + 77px));transform:translateX(-50%);min-width:216px;max-width:calc(100vw - 250px);padding:6px 12px 5px;box-sizing:border-box;border:1px solid #ffbd6373;border-radius:8px;background:#111820e8;box-shadow:0 8px 22px #0009,0 0 18px #ff9c4528;text-align:center;white-space:nowrap}
#race-showdown-v7.active{display:block}
#race-showdown-v7 b{display:block;color:#ffd18b;font:900 10px/1.05 Arial,sans-serif;letter-spacing:.11em}
#race-showdown-v7 span{display:block;margin-top:4px;color:#b9c8d1;font:800 7px/1 Arial,sans-serif;letter-spacing:.10em}
#race-showdown-v7.finale{border-color:#ffd37dc2;background:#241817ed;box-shadow:0 8px 24px #0009,0 0 22px #ff9c4542}
#race-feud-result-v6.showdown-v7-result{border-width:2px;box-shadow:0 9px 28px #000b,0 0 30px #ff9c4552;font-size:12px}
@media(orientation:landscape) and (max-height:430px){#race-rival-v4 .rr-signature-v7{min-width:48px;font-size:6px}#race-showdown-v7{top:max(76px,calc(env(safe-area-inset-top) + 69px));min-width:196px;max-width:calc(100vw - 220px);padding:5px 10px 4px}#race-showdown-v7 b{font-size:9px}#race-showdown-v7 span{font-size:6px;margin-top:3px}#race-feud-result-v6.showdown-v7-result{font-size:10px}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_wrecking_racing_rival_showdown_v7(Path('_site'))
