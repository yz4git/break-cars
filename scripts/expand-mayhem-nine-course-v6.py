"""MAYHEM TOUR v6: expand the run from three events to the complete nine-course tour.

All authored courses are used exactly once. Player hull/upgrades and the v5 persistent
RIVAL/Director state continue across every course. The three-event prototype's generic
routing/result code already supports arbitrary event counts; this pass removes the few
hard-coded `3` bounds/labels and replaces the route with the full escalation ladder.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'MAYHEM TOUR v6 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_mayhem_nine_course_v6(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    events_old = """const MAYHEM_KEY='break-cars-mayhem-tour-v1',MAYHEM_EVENTS=[
 {course:'crater-crown',mode:'colosseum',name:'CRATER CROWN',goal:'SURVIVE THE CROWN'},
 {course:'hunt-classic',mode:'wreck-hunt',name:'WRECK HUNT',goal:'CHAIN THE WRECKS'},
 {course:'double-orbit',mode:'racing',name:'DOUBLE ORBIT',goal:'CONQUER BOTH LOOPS'}
];"""
    events_new = """const MAYHEM_KEY='break-cars-mayhem-tour-v2',MAYHEM_EVENTS=[
 {course:'classic',mode:'colosseum',name:'THE COLOSSEUM',goal:'SURVIVE THE OPENING BRAWL'},
 {course:'crater-crown',mode:'colosseum',name:'CRATER CROWN',goal:'SURVIVE THE CROWN'},
 {course:'maelstrom-pit',mode:'colosseum',name:'MAELSTROM PIT',goal:'BREAK THE SPIRAL'},
 {course:'hunt-classic',mode:'wreck-hunt',name:'WRECK HUNT',goal:'CHAIN THE WRECKS'},
 {course:'cross-fire',mode:'wreck-hunt',name:'CROSS FIRE',goal:'HUNT THROUGH THE CROSSING'},
 {course:'tidal-foundry',mode:'wreck-hunt',name:'TIDAL FOUNDRY',goal:'SURVIVE THE CRUSH ZONE'},
 {course:'rampage-3d',mode:'racing',name:'RAMPAGE 3D',goal:'BREAK THE OMEGA'},
 {course:'sky-forge',mode:'racing',name:'SKY FORGE',goal:'MASTER THE SKY CROSSING'},
 {course:'double-orbit',mode:'racing',name:'DOUBLE ORBIT',goal:'CONQUER BOTH LOOPS'}
];"""
    s = one(s, events_old, events_new, 'nine-course route')

    s = one(
        s,
        "event=Math.max(0,Math.min(2,mayhemState.event||0))",
        "event=Math.max(0,Math.min(MAYHEM_EVENTS.length-1,mayhemState.event||0))",
        'result event bound',
    )
    s = one(
        s,
        "if(Number.isInteger(requestedEvent)&&requestedEvent>=0&&requestedEvent<3)mayhemState.event=requestedEvent;",
        "if(Number.isInteger(requestedEvent)&&requestedEvent>=0&&requestedEvent<MAYHEM_EVENTS.length)mayhemState.event=requestedEvent;",
        'requested event bound',
    )

    badge_old = "function mayhemBadgeText(){if(!mayhemActive())return'';return`TOUR ${mayhemState.event+1}/3 · P${mayhemState.power||0} A${mayhemState.armor||0} H${mayhemState.handling||0} · R${mayhemRivalId()+1}`;}"
    badge_new = "function mayhemBadgeText(){if(!mayhemActive())return'';return`TOUR ${mayhemState.event+1}/${MAYHEM_EVENTS.length} · P${mayhemState.power||0} A${mayhemState.armor||0} H${mayhemState.handling||0} · R${mayhemRivalId()+1}`;}"
    s = one(s, badge_old, badge_new, 'tour badge count')

    s = one(
        s,
        "entry.innerHTML='<b>MAYHEM TOUR</b><small>3 EVENT RUN · RIVAL · LIVE DIRECTOR</small>';",
        "entry.innerHTML='<b>MAYHEM TOUR</b><small>9 COURSE RUN · RIVAL · LIVE DIRECTOR</small>';",
        'menu course count',
    )
    s = one(
        s,
        "<small>PIT CHOICE · EVENT ${event+1}/3 COMPLETE</small>",
        "<small>PIT CHOICE · EVENT ${event+1}/${MAYHEM_EVENTS.length} COMPLETE</small>",
        'pit course count',
    )
    s = one(
        s,
        "$('mode-tag').textContent=`MAYHEM TOUR · EVENT ${mayhemState.event+1}/3`;",
        "$('mode-tag').textContent=`MAYHEM TOUR · EVENT ${mayhemState.event+1}/${MAYHEM_EVENTS.length}`;",
        'mode tag count',
    )
    s = one(
        s,
        "$('arena-caption').innerHTML=`MAYHEM TOUR<span>${def.name} · ${mayhemState.event+1}/3</span>`;",
        "$('arena-caption').innerHTML=`MAYHEM TOUR<span>${def.name} · ${mayhemState.event+1}/${MAYHEM_EVENTS.length}</span>`;",
        'arena caption count',
    )

    expose_old = "window.__breakCarsMayhemTour=()=>mayhemActive()?{...mayhemState,eventDef:MAYHEM_EVENTS[mayhemState.event],worldMode:world?.mode,hp:world?.cars?.[0]?.hp,maxHP:world?.cars?.[0]?.maxHP,rival:{id:mayhemRivalId(),name:mayhemRivalName(),hp:mayhemRivalLive()?.hp??0,maxHP:mayhemRivalLive()?.maxHP??0},director:window.__breakCarsMayhemDirector||{state:mayhemDirectorState,intensity:mayhemDirectorIntensity}}:null;"
    expose_new = "window.__breakCarsMayhemTour=()=>mayhemActive()?{...mayhemState,tourLength:MAYHEM_EVENTS.length,eventDef:MAYHEM_EVENTS[mayhemState.event],worldMode:world?.mode,hp:world?.cars?.[0]?.hp,maxHP:world?.cars?.[0]?.maxHP,rival:{id:mayhemRivalId(),name:mayhemRivalName(),hp:mayhemRivalLive()?.hp??0,maxHP:mayhemRivalLive()?.maxHP??0},director:window.__breakCarsMayhemDirector||{state:mayhemDirectorState,intensity:mayhemDirectorIntensity}}:null;"
    s = one(s, expose_old, expose_new, 'tour length telemetry')

    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += "\n/* v6: complete nine-course run */\nbody.mayhem-tour #mayhem-tour-entry small{letter-spacing:.04em}\n"
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_nine_course_v6(Path('_site'))
