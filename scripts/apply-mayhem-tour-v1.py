"""MAYHEM TOUR v1: a three-event run layered over the existing game modes.

Event order: CRATER CROWN -> WRECK HUNT -> DOUBLE ORBIT.
The run survives course reloads through sessionStorage, keeps the selected car,
carries hull condition, and offers one pit choice between events. Existing
single-event modes stay unchanged when the `tour=1` URL flag is absent.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v1 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_tour_v1(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    world_anchor = "let world=makeWorld(),mode='menu',selection=0,gameMode='colosseum',view=0,count=3.5,toastTime=0,shake=0,camHeading=Math.PI,accumulator=0,last=performance.now(),menuTime=0,muted=false,resultShown=false,seed=Date.now()>>>0;"
    tour_core = world_anchor + r'''
const MAYHEM_KEY='break-cars-mayhem-tour-v1',MAYHEM_EVENTS=[
 {course:'crater-crown',mode:'colosseum',name:'CRATER CROWN',goal:'SURVIVE THE CROWN'},
 {course:'hunt-classic',mode:'wreck-hunt',name:'WRECK HUNT',goal:'CHAIN THE WRECKS'},
 {course:'double-orbit',mode:'racing',name:'DOUBLE ORBIT',goal:'CONQUER BOTH LOOPS'}
];
const mayhemParams=new URLSearchParams(location.search),mayhemRequested=mayhemParams.get('tour')==='1';
function mayhemDefault(){return{active:true,event:0,car:selection,hull:1,power:0,armor:0,handling:0,total:0,results:[]};}
function mayhemLoad(){if(!mayhemRequested)return null;try{const x=JSON.parse(sessionStorage.getItem(MAYHEM_KEY)||'null');if(x&&x.active)return x;}catch{}const x=mayhemDefault();try{sessionStorage.setItem(MAYHEM_KEY,JSON.stringify(x));}catch{}return x;}
let mayhemState=mayhemLoad();
function mayhemActive(){return !!(mayhemRequested&&mayhemState?.active);}
function mayhemSave(){if(!mayhemState)return;try{sessionStorage.setItem(MAYHEM_KEY,JSON.stringify(mayhemState));}catch{}}
function mayhemRoute(index){const e=MAYHEM_EVENTS[index];return`?course=${encodeURIComponent(e.course)}&tour=1&event=${index}`;}
function applyMayhemLoadout(){if(!mayhemActive()||!world?.cars?.[0])return;const p=world.cars[0],h=clamp(Number(mayhemState.hull)||1,.18,1);p.tourPower=1+Math.min(3,mayhemState.power||0)*.08;p.tourGrip=1+Math.min(3,mayhemState.handling||0)*.07;p.tourTurn=1+Math.min(3,mayhemState.handling||0)*.08;p.tourArmor=Math.max(.72,1-Math.min(3,mayhemState.armor||0)*.08);p.hp=Math.max(1,Math.round(p.maxHP*h));for(const k of Object.keys(p.parts||{}))p.parts[k]=Math.max(42,Math.round(55+h*45));}
function mayhemScore(){const p=world.cars[0];return world.mode==='racing'?racingPoints(p).total:p.score;}
function mayhemBadgeText(){if(!mayhemActive())return'';return`TOUR ${mayhemState.event+1}/3 · P${mayhemState.power||0} A${mayhemState.armor||0} H${mayhemState.handling||0}`;}
function mayhemEndRun(){try{sessionStorage.removeItem(MAYHEM_KEY);}catch{}location.search='?course=classic';}
function mayhemRestart(){mayhemState=mayhemDefault();mayhemState.car=selection;mayhemSave();location.search=mayhemRoute(0);}
function mayhemChoose(kind){if(!mayhemActive())return;if(kind==='repair')mayhemState.hull=Math.min(1,(mayhemState.hull||.18)+.28);else if(kind==='power')mayhemState.power=Math.min(3,(mayhemState.power||0)+1);else if(kind==='armor')mayhemState.armor=Math.min(3,(mayhemState.armor||0)+1);else if(kind==='handling')mayhemState.handling=Math.min(3,(mayhemState.handling||0)+1);mayhemState.event=Math.min(MAYHEM_EVENTS.length-1,(mayhemState.event||0)+1);mayhemSave();location.search=mayhemRoute(mayhemState.event);}
function mayhemAfterEvent(){if(!mayhemActive())return;const p=world.cars[0],score=mayhemScore(),event=Math.max(0,Math.min(2,mayhemState.event||0)),hull=p.dead?.18:clamp(p.hp/p.maxHP,.18,1);mayhemState.hull=hull;mayhemState.total=(mayhemState.total||0)+score;mayhemState.results=Array.isArray(mayhemState.results)?mayhemState.results:[];mayhemState.results[event]={course:MAYHEM_EVENTS[event].course,score,hull};mayhemSave();$('retry').classList.add('hidden');$('home').classList.add('hidden');$('race-results').classList.add('hidden');let box=$('tour-intermission');if(!box){box=document.createElement('div');box.id='tour-intermission';$('result-stats').after(box);}if(event>=MAYHEM_EVENTS.length-1){box.innerHTML=`<div class="tour-final"><small>MAYHEM TOUR COMPLETE</small><b>${mayhemState.total.toLocaleString()} PTS</b><span>FINAL HULL ${Math.round(hull*100)}%</span><div><button data-tour-final="again">NEW TOUR</button><button data-tour-final="garage">GARAGE</button></div></div>`;box.querySelector('[data-tour-final="again"]').onclick=mayhemRestart;box.querySelector('[data-tour-final="garage"]').onclick=mayhemEndRun;$('result-kicker').textContent='MAYHEM TOUR / COMPLETE';return;}box.innerHTML=`<div class="tour-pit"><small>PIT CHOICE · EVENT ${event+1}/3 COMPLETE</small><b>${MAYHEM_EVENTS[event+1].name} NEXT</b><span>HULL ${Math.round(hull*100)}% · TOTAL ${mayhemState.total.toLocaleString()}</span><div class="tour-pit-grid"><button data-tour-up="repair"><b>REPAIR</b><small>HULL +28%</small></button><button data-tour-up="power" ${mayhemState.power>=3?'disabled':''}><b>POWER</b><small>LV ${mayhemState.power||0} → ${Math.min(3,(mayhemState.power||0)+1)}</small></button><button data-tour-up="armor" ${mayhemState.armor>=3?'disabled':''}><b>ARMOR</b><small>LV ${mayhemState.armor||0} → ${Math.min(3,(mayhemState.armor||0)+1)}</small></button><button data-tour-up="handling" ${mayhemState.handling>=3?'disabled':''}><b>HANDLING</b><small>LV ${mayhemState.handling||0} → ${Math.min(3,(mayhemState.handling||0)+1)}</small></button></div></div>`;box.querySelectorAll('[data-tour-up]').forEach(b=>b.onclick=()=>mayhemChoose(b.dataset.tourUp));$('result-kicker').textContent=`MAYHEM TOUR / EVENT ${event+1} CLEAR`;}
function setupMayhemMenu(){let entry=$('mayhem-tour-entry');if(!entry){entry=document.createElement('button');entry.id='mayhem-tour-entry';entry.type='button';entry.innerHTML='<b>MAYHEM TOUR</b><small>3 EVENT RUN · DAMAGE CARRIES</small>';document.querySelector('.mode-select').appendChild(entry);}entry.onclick=()=>{mayhemState=mayhemDefault();mayhemState.car=selection;mayhemSave();location.search=mayhemRoute(0);};if(!mayhemActive())return;const requestedEvent=Number(mayhemParams.get('event'));if(Number.isInteger(requestedEvent)&&requestedEvent>=0&&requestedEvent<3)mayhemState.event=requestedEvent;const def=MAYHEM_EVENTS[mayhemState.event]||MAYHEM_EVENTS[0];if(activeCourse.id!==def.course){location.replace(mayhemRoute(mayhemState.event));return;}selection=Math.max(0,Math.min(2,mayhemState.car||0));document.querySelectorAll('[data-car]').forEach(b=>b.classList.toggle('selected',Number(b.dataset.car)===selection));document.body.classList.add('mayhem-tour');entry.classList.add('selected');entry.setAttribute('aria-pressed','true');$('mode-tag').textContent=`MAYHEM TOUR · EVENT ${mayhemState.event+1}/3`;$('mode-subtitle').textContent=def.name;$('mode-lead').textContent=def.goal;$('arena-caption').innerHTML=`MAYHEM TOUR<span>${def.name} · ${mayhemState.event+1}/3</span>`;$('start').innerHTML=`EVENT ${mayhemState.event+1} START <span>↗</span>`;const hint=document.querySelector('.course-hint');if(hint)hint.textContent=`HULL ${Math.round((mayhemState.hull||1)*100)}% · POWER ${mayhemState.power||0} · ARMOR ${mayhemState.armor||0} · HANDLING ${mayhemState.handling||0} · TOTAL ${(mayhemState.total||0).toLocaleString()} PTS`;resetWorld();}
window.__breakCarsMayhemTour=()=>mayhemActive()?{...mayhemState,eventDef:MAYHEM_EVENTS[mayhemState.event],worldMode:world?.mode,hp:world?.cars?.[0]?.hp,maxHP:world?.cars?.[0]?.maxHP}:null;
if(mayhemParams.get('tourAudit')==='1')window.__breakCarsMayhemAuditFinish=()=>{if(mode==='countdown'){mode='race';count=0;}finish();};
'''
    s = one(s, world_anchor, tour_core, 'tour core')

    reset_tail = "for(const c of world.cars)carMeshes.push(buildCar(c));resultShown=false;clearParticles();clearBlasts();skidCount=0;skidMesh.count=0;}"
    s = one(s, reset_tail, "for(const c of world.cars)carMeshes.push(buildCar(c));applyMayhemLoadout();resultShown=false;clearParticles();clearBlasts();skidCount=0;skidMesh.count=0;}", 'loadout after reset')

    result_tail = "$('resume').classList.add('hidden');$('modal').classList.remove('hidden');}"
    if s.count(result_tail) != 3:
        raise RuntimeError(f'MAYHEM TOUR v1 result hooks: expected 3 matches, found {s.count(result_tail)}')
    s = s.replace(result_tail, "$('resume').classList.add('hidden');$('modal').classList.remove('hidden');mayhemAfterEvent();}")

    start_tail = "$('time-label').textContent='TIME LEFT';document.body.classList.add('playing');$('toast').textContent='';toastTime=0;accumulator=0;initAudio();}"
    s = one(s, start_tail, "$('time-label').textContent='TIME LEFT';document.body.classList.add('playing');$('toast').textContent='';toastTime=0;accumulator=0;if(mayhemActive()){const badge=document.createElement('div');badge.id='tour-run-badge';badge.textContent=mayhemBadgeText();document.body.appendChild(badge);}$('retry').classList.remove('hidden');$('home').classList.remove('hidden');const oldPit=$('tour-intermission');if(oldPit)oldPit.remove();initAudio();}", 'start badge')

    home = "$('pause').onclick=togglePause;$('resume').onclick=togglePause;$('home').onclick=()=>{mode='menu';resetInput();"
    s = one(s, home, "$('pause').onclick=togglePause;$('resume').onclick=togglePause;$('home').onclick=()=>{if(mayhemActive()){mayhemEndRun();return;}mode='menu';resetInput();", 'home exits tour')

    final_init = "selectMode(activeCourse.mode);"
    if s.count(final_init) != 1:
        raise RuntimeError(f'MAYHEM TOUR v1 menu init: expected 1 match, found {s.count(final_init)}')
    s = s.replace(final_init, final_init + "setupMayhemMenu();", 1)
    game.write_text(s)

    physics = target / 'physics.js'
    s = physics.read_text()
    armor = "const playerArmor=c.id===0?(w.mode==='wreck-hunt'?.62:.82):1;"
    s = one(s, armor, "const playerArmor=c.id===0?(w.mode==='wreck-hunt'?.62:.82)*(c.tourArmor||1):1;", 'armor upgrade')
    drive = "const huntRush=player&&w.mode==='wreck-hunt'&&w.hunt?.rushUntil>w.time;const power=t.power*(player?(huntRush?1.52+Math.min(w.hunt?.combo||0,4)*.06:1.22):1),grip=t.grip*(player?(huntRush?1.22:1.08):1),topSpeed=(player?(huntRush?38+Math.min(w.hunt?.combo||0,4)*1.4:33.5):29)*damageFactor;"
    drive_new = "const huntRush=player&&w.mode==='wreck-hunt'&&w.hunt?.rushUntil>w.time,tourPower=player?(c.tourPower||1):1,tourGrip=player?(c.tourGrip||1):1;const power=t.power*tourPower*(player?(huntRush?1.52+Math.min(w.hunt?.combo||0,4)*.06:1.22):1),grip=t.grip*tourGrip*(player?(huntRush?1.22:1.08):1),topSpeed=(player?(huntRush?38+Math.min(w.hunt?.combo||0,4)*1.4:33.5):29)*(player?1+(tourPower-1)*.42:1)*damageFactor;"
    s = one(s, drive, drive_new, 'power handling upgrades')
    yaw = "const yaw=steering*t.turn*(player?1.09:1)*wallSteerBoost*(u.hand?2.02:1.5)*clamp(Math.abs(forward)/4.6+huntEdge*.48,0,1)*motionSign;"
    s = one(s, yaw, "const yaw=steering*t.turn*(player?(c.tourTurn||1):1)*(player?1.09:1)*wallSteerBoost*(u.hand?2.02:1.5)*clamp(Math.abs(forward)/4.6+huntEdge*.48,0,1)*motionSign;", 'handling turn upgrade')
    physics.write_text(s)

    index = target / 'index.html'
    html = index.read_text()
    html = one(html, '</head>', '<link rel="stylesheet" href="mayhem-tour.css"></head>', 'tour css link')
    index.write_text(html)

    css = target / 'mayhem-tour.css'
    css.write_text(r'''#mayhem-tour-entry{border-color:#ff7f4f55;background:linear-gradient(135deg,#2a1714,#17202a);position:relative;overflow:hidden}#mayhem-tour-entry:before{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 35%,#ff7c4630 50%,transparent 65%);transform:translateX(-100%);animation:tourSweep 3.8s linear infinite}#mayhem-tour-entry b,#mayhem-tour-entry small{position:relative;z-index:1}#mayhem-tour-entry.selected{border-color:#ff885f;box-shadow:0 0 0 1px #ff885f44,0 0 28px #ff63252f}.mayhem-tour .mode-select>[data-mode],.mayhem-tour #course-picker{display:none}.mayhem-tour #mayhem-tour-entry{display:flex;flex:1}.mayhem-tour .course-hint{border-left:3px solid #ff7d50;padding-left:10px;color:#ffd9c9}#tour-run-badge{position:fixed;z-index:19;top:max(62px,calc(env(safe-area-inset-top) + 54px));left:50%;transform:translateX(-50%);padding:5px 10px;border:1px solid #ff875d66;border-radius:999px;background:#15191ee6;color:#ffd5c5;font:800 11px/1.1 system-ui;letter-spacing:.08em;pointer-events:none;white-space:nowrap}.tour-pit,.tour-final{margin-top:10px;padding:12px;border:1px solid #ff825e55;border-radius:14px;background:linear-gradient(150deg,#221815e8,#111a22ed);display:grid;gap:7px}.tour-pit>small,.tour-final>small{font:800 10px/1.1 system-ui;letter-spacing:.13em;color:#ff9a74}.tour-pit>b,.tour-final>b{font:900 18px/1.05 system-ui;color:#fff}.tour-pit>span,.tour-final>span{font:700 11px/1.2 system-ui;color:#c9d3da}.tour-pit-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin-top:3px}.tour-pit-grid button,.tour-final button{min-height:44px;border:1px solid #ffffff2a;border-radius:10px;background:#1c2934;color:#fff}.tour-pit-grid button b{display:block;font:900 12px/1 system-ui}.tour-pit-grid button small{display:block;margin-top:4px;color:#ffae8f;font:700 9px/1 system-ui}.tour-pit-grid button:disabled{opacity:.35}.tour-final>div{display:flex;gap:8px}.tour-final button{flex:1;font:900 11px/1 system-ui}@keyframes tourSweep{to{transform:translateX(100%)}}@media(orientation:landscape) and (max-height:430px){#tour-run-badge{top:max(55px,calc(env(safe-area-inset-top) + 48px));font-size:9px;padding:4px 8px}.tour-pit,.tour-final{padding:9px;gap:5px;margin-top:6px}.tour-pit-grid{grid-template-columns:repeat(4,minmax(0,1fr));gap:5px}.tour-pit-grid button{min-height:40px;padding:5px 3px}.tour-pit>b,.tour-final>b{font-size:15px}.tour-pit>span,.tour-final>span{font-size:9px}}
''')


if __name__ == '__main__':
    apply_mayhem_tour_v1(Path('_site'))
