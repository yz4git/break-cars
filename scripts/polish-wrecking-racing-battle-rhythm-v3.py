"""WRECKING RACING battle rhythm v3.

Turn the tactical contact zones into a readable fight cadence without changing
vehicle forces or damage. Real car-to-car impacts are timestamped separately
from wall hits. AI then performs a short BREAKAWAY and crosses back through a
narrow REMATCH lane before returning to normal CHASE behavior. Jump staging
always wins over battle rhythm so stunts stay raceable.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'WRECKING RACING battle rhythm v3 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_wrecking_racing_battle_rhythm_v3(target: Path) -> None:
    racing = target / 'racing.js'
    s = racing.read_text()

    zone_end = """ return{type:'neutral',phase:0,width:0,turn};
}
"""
    rhythm = zone_end + r'''export function racingBattleRhythm(sinceCarContact,tacticType,id,lap=0){
 const t=Number.isFinite(sinceCarContact)?sinceCarContact:99,n=Math.max(0,Math.floor(lap||0)),side=((id+n)&1)?1:-1;
 if(tacticType==='jump-split'||tacticType==='jump-flight')return{phase:'STAGE',lane:null,strength:0};
 if(t>=0&&t<.22)return{phase:'CLASH',lane:null,strength:0};
 if(t>=.22&&t<1.35)return{phase:'BREAKAWAY',lane:side*4.65,strength:.48};
 if(t>=1.35&&t<3.15)return{phase:'REMATCH',lane:-side*1.65,strength:.26};
 if(tacticType==='landing-merge'||tacticType==='loop-merge')return{phase:'REMATCH',lane:-side*1.65,strength:.20};
 return{phase:'CHASE',lane:null,strength:0};
}
'''
    s = one(s, zone_end, rhythm, 'battle rhythm model')

    edge = " if(Math.abs(p.lane)>5.9)lane=clamp(lane-p.lane*.44,-4.6,4.6);\n"
    battle = r''' const sinceCarContact=w.time-(c.raceCarContactAt??-99),rhythm=racingBattleRhythm(sinceCarContact,tactic.type,c.id,tacticalLap);c.raceBattlePhase=rhythm.phase;c.raceBattleSinceContact=sinceCarContact;
 if(!stunt&&rhythm.lane!==null){
  const safeGoal=clamp(rhythm.lane,-5.2,5.2);lane=clamp(lane+(safeGoal-lane)*rhythm.strength,-5.6,5.6);
  if(rhythm.phase==='BREAKAWAY'){c.battleTarget=-1;attack=false;pack=false;}
 }
''' + edge
    s = one(s, edge, battle, 'AI breakaway/rematch cadence')
    racing.write_text(s)

    physics = target / 'physics.js'
    p = physics.read_text()
    impact = " if(!b.dead||b.hitAt===w.time){b.score+=Math.round(da*12);b.contacts++;b.lastContact=w.time;}\n w.events.push({type:'impact',a:a.id,b:b.id,power:closing,x:(a.x+b.x)/2,z:(a.z+b.z)/2});"
    impact_new = " if(!b.dead||b.hitAt===w.time){b.score+=Math.round(da*12);b.contacts++;b.lastContact=w.time;}\n if(w.mode==='racing'){a.raceCarContactAt=w.time;b.raceCarContactAt=w.time;}\n w.events.push({type:'impact',a:a.id,b:b.id,power:closing,x:(a.x+b.x)/2,z:(a.z+b.z)/2});"
    p = one(p, impact, impact_new, 'car-to-car contact timestamp')
    physics.write_text(p)


if __name__ == '__main__':
    apply_wrecking_racing_battle_rhythm_v3(Path('_site'))
