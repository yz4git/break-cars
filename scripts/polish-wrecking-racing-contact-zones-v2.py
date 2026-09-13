"""WRECKING RACING tactical contact zones v2.

Keep the math-built geometry and vehicle physics unchanged, but make the race
shape create deliberate battle beats. AI spreads into fast overtake lanes on
low-curvature road, forms three lanes before/through jumps, and converges into
two close channels after jumps and loops. The zones are derived from the final
math feature spec so all three WRECKING RACING courses share the same rules.
"""
from pathlib import Path
import importlib.util


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'WRECKING RACING contact v2 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_wrecking_racing_contact_v2(target: Path) -> None:
    racing = target / 'racing.js'
    s = racing.read_text()

    anchor = "const forwardGap=(target,current)=>{let d=target-current;if(d<0)d+=LENGTH;return d;};\n"
    tactical = anchor + r'''const CONTACT_ZONE_CONFIGS={
 'rampage-3d':{mergeWidth:1.85,overtakeWidth:4.75,jumpWidth:3.65,mergeLen:34,jumpLead:44,landingLen:30,straightTurn:.17},
 'sky-forge':{mergeWidth:2.05,overtakeWidth:4.95,jumpWidth:3.95,mergeLen:31,jumpLead:46,landingLen:32,straightTurn:.15},
 'double-orbit':{mergeWidth:1.80,overtakeWidth:5.10,jumpWidth:4.05,mergeLen:36,jumpLead:48,landingLen:34,straightTurn:.17},
};
const CONTACT_ZONE=CONTACT_ZONE_CONFIGS[COURSE_SPEC.courseId]||CONTACT_ZONE_CONFIGS['rampage-3d'];
export function racingTacticalLane(id,lap,zone){
 const n=Math.max(0,Math.floor(lap||0));
 if(zone?.type==='jump-split'||zone?.type==='jump-flight')return[-zone.width,0,zone.width][(id+n)%3];
 if(zone?.type==='loop-merge'||zone?.type==='landing-merge'||zone?.type==='overtake')return((id+n)&1?1:-1)*zone.width;
 return 0;
}
export function racingTacticalZone(s){
 const q=wrap(s),cfg=CONTACT_ZONE,loops=COURSE_SPEC.loops||[COURSE_SPEC.loop].filter(Boolean);
 for(let i=0;i<loops.length;i++){
  const after=forwardGap(q,loops[i].endS);
  if(after<cfg.mergeLen)return{type:'loop-merge',feature:i,phase:after/cfg.mergeLen,width:cfg.mergeWidth};
 }
 const j=COURSE_SPEC.jump;
 if(j){
  const span=forwardGap(j.endS,j.startS),along=forwardGap(q,j.startS);
  if(along<=span)return{type:'jump-flight',phase:span?along/span:0,width:cfg.jumpWidth};
  const toJump=forwardGap(j.startS,q);
  if(toJump<cfg.jumpLead)return{type:'jump-split',phase:1-toJump/cfg.jumpLead,width:cfg.jumpWidth};
  const afterJump=forwardGap(q,j.endS);
  if(afterJump<cfg.landingLen)return{type:'landing-merge',phase:afterJump/cfg.landingLen,width:cfg.mergeWidth};
 }
 const turn=Math.abs(angle(trackPoint(q+28).heading-trackPoint(q).heading));
 if(turn<cfg.straightTurn)return{type:'overtake',phase:1,width:cfg.overtakeWidth,turn};
 return{type:'neutral',phase:0,width:0,turn};
}
'''
    s = one(s, anchor, tactical, 'tactical zone model')

    old_lane = "let lane=c.lane,pack=false,attack=false,sideBySide=false,attackGap=99;const rival=w.cars[c.battleTarget],turnSoon=Math.abs(angle(trackPoint(p.s+20).heading-trackPoint(p.s).heading));"
    new_lane = "let lane=c.lane,pack=false,attack=false,sideBySide=false,attackGap=99;const tactic=racingTacticalZone(p.s),tacticalLap=Math.max(0,Math.floor(Math.max(0,c.raceDistance)/LENGTH));c.raceTacticalZone=tactic.type;const rival=w.cars[c.battleTarget],turnSoon=Math.abs(angle(trackPoint(p.s+20).heading-trackPoint(p.s).heading));"
    s = one(s, old_lane, new_lane, 'AI tactical zone lookup')

    avoid = "for(const o of w.cars){if(o===c||o.finished)continue;const op=projectCar(o),gap=o.raceDistance-c.raceDistance;if(op&&o.dead&&gap>-2&&gap<16&&Math.abs(op.lane-lane)<3.5&&Math.abs((o.p3?.py??op.y)-(c.p3?.py??p.y))<3){lane=op.lane>0?-5:5;c.battleTarget=-1;attack=false;pack=false;}}\n"
    tactical_ai = avoid + r''' const tacticalGoal=racingTacticalLane(c.id,tacticalLap,tactic);c.raceTacticalLaneGoal=tacticalGoal;
 if(tactic.type==='jump-split'||tactic.type==='jump-flight'){
  const strength=tactic.type==='jump-flight'?.72:.46;lane=clamp(lane+(tacticalGoal-lane)*strength,-5.8,5.8);c.battleTarget=-1;attack=false;pack=false;
 }else if(tactic.type==='loop-merge'){
  lane=clamp(lane+(tacticalGoal-lane)*(.60-.20*tactic.phase),-5.6,5.6);
 }else if(tactic.type==='landing-merge'){
  lane=clamp(lane+(tacticalGoal-lane)*(.56-.18*tactic.phase),-5.6,5.6);
 }else if(tactic.type==='overtake'&&!attack&&!pack){
  lane=clamp(lane+(tacticalGoal-lane)*.16,-5.6,5.6);
 }
'''
    s = one(s, avoid, tactical_ai, 'AI lane staging')
    racing.write_text(s)

    rhythm_path = Path(__file__).with_name('polish-wrecking-racing-battle-rhythm-v3.py')
    spec = importlib.util.spec_from_file_location('break_cars_wrecking_racing_battle_rhythm_v3', rhythm_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_wrecking_racing_battle_rhythm_v3(target)


if __name__ == '__main__':
    apply_wrecking_racing_contact_v2(Path('_site'))
