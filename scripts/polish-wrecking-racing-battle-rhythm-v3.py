"""WRECKING RACING battle rhythm v3.

Turn tactical contact zones into a readable fight cadence without changing
vehicle forces or damage. Real car-to-car impacts are timestamped separately
from wall hits in both the legacy and authoritative full-3D collision paths.
Ordinary contact creates a very short CLASH, then BREAKAWAY and REMATCH. Loop
exits and jump landings additionally force a distance-based BREAKAWAY ->
REMATCH beat, so stunt collisions cannot keep the pack permanently bunched.
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
    rhythm = zone_end + r'''export function racingBattleRhythm(sinceCarContact,tacticType,id,lap=0,tacticPhase=1){
 const t=Number.isFinite(sinceCarContact)?sinceCarContact:99,n=Math.max(0,Math.floor(lap||0)),side=((id+n)&1)?1:-1,phase=clamp(Number.isFinite(tacticPhase)?tacticPhase:1,0,1);
 if(tacticType==='jump-split'||tacticType==='jump-flight')return{phase:'STAGE',lane:null,strength:0,source:'stunt'};
 if(tacticType==='loop-merge'||tacticType==='landing-merge'){
  if(phase<.34)return{phase:'BREAKAWAY',lane:side*4.55,strength:.52,source:'feature'};
  return{phase:'REMATCH',lane:-side*1.65,strength:.30,source:'feature'};
 }
 if(t>=0&&t<.05)return{phase:'CLASH',lane:null,strength:0,source:'contact'};
 if(t>=.05&&t<1.20)return{phase:'BREAKAWAY',lane:side*4.65,strength:.48,source:'contact'};
 if(t>=1.20&&t<2.90)return{phase:'REMATCH',lane:-side*1.65,strength:.26,source:'contact'};
 return{phase:'CHASE',lane:null,strength:0,source:'race'};
}
'''
    s = one(s, zone_end, rhythm, 'battle rhythm model')

    edge = " if(Math.abs(p.lane)>5.9)lane=clamp(lane-p.lane*.44,-4.6,4.6);\n"
    battle = r''' const sinceCarContact=w.time-(c.raceCarContactAt??-99),rhythm=racingBattleRhythm(sinceCarContact,tactic.type,c.id,tacticalLap,tactic.phase??1);c.raceBattlePhase=rhythm.phase;c.raceBattleSinceContact=sinceCarContact;c.raceBattleSource=rhythm.source;
 if(!stunt&&rhythm.lane!==null){
  const safeGoal=clamp(rhythm.lane,-5.2,5.2);lane=clamp(lane+(safeGoal-lane)*rhythm.strength,-5.6,5.6);
  if(rhythm.phase==='BREAKAWAY'){c.battleTarget=-1;attack=false;pack=false;}
 }
''' + edge
    s = one(s, edge, battle, 'AI breakaway/rematch cadence')
    racing.write_text(s)

    # Legacy collision path remains supported for non-3D/fallback execution.
    physics = target / 'physics.js'
    p = physics.read_text()
    impact = " if(!b.dead||b.hitAt===w.time){b.score+=Math.round(da*12);b.contacts++;b.lastContact=w.time;}\n w.events.push({type:'impact',a:a.id,b:b.id,power:closing,x:(a.x+b.x)/2,z:(a.z+b.z)/2});"
    impact_new = " if(!b.dead||b.hitAt===w.time){b.score+=Math.round(da*12);b.contacts++;b.lastContact=w.time;}\n if(w.mode==='racing'){a.raceCarContactAt=w.time;b.raceCarContactAt=w.time;}\n w.events.push({type:'impact',a:a.id,b:b.id,power:closing,x:(a.x+b.x)/2,z:(a.z+b.z)/2});"
    p = one(p, impact, impact_new, 'legacy car-to-car contact timestamp')
    physics.write_text(p)

    # Full 3D is authoritative during the actual game and emits its own impact.
    physics3d = target / 'physics3d.js'
    q = physics3d.read_text()
    impact3d = "  w.events.push({type:'impact',a:a.id,b:b.id,power:peak,x:(A.px+B.px)/2,y:(A.py+B.py)/2,z:(A.pz+B.pz)/2});"
    impact3d_new = "  if (w.mode==='racing') { a.raceCarContactAt=w.time; b.raceCarContactAt=w.time; }\n" + impact3d
    q = one(q, impact3d, impact3d_new, 'full 3D car-to-car contact timestamp')
    physics3d.write_text(q)


if __name__ == '__main__':
    apply_wrecking_racing_battle_rhythm_v3(Path('_site'))
