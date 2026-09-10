"""RAMPAGE v14: exact live-WebGL audit start just before the Omega.

Normal gameplay is untouched. Only URLs carrying the existing ``visualAudit``
query parameter move the player to a deterministic point 30 m before the first
RAMPAGE loop, centered on the road and aligned with its tangent. This prevents
the visual audit from spending its short capture window driving the unrelated
opening curve and colliding with scenery before the Omega is reached.

The audit starts with a modest 18 m/s forward speed. Audit URLs also expose a
read-only telemetry snapshot for the Playwright visual audit so transient crash
slowdowns can be distinguished from a genuine loop stall. Physics, controls,
loop geometry, camera logic and all non-audit URLs remain unchanged.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'RAMPAGE live audit v14 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_rampage_live_audit_start_v14(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()

    old = "function start(){resetInput();resetWorld();mode='countdown';count=3.5;camHeading=world.cars[0].heading;"
    new = """const rampageLiveVisualAudit=new URLSearchParams(location.search).has('visualAudit');
function placeRampageLiveVisualAudit(){
 if(!rampageLiveVisualAudit||gameMode!=='racing')return;
 const c=world.cars[0],loop=raceLoopAt(0),startS=loop.startS-30,p=trackPoint(startS,0),launch=18;
 Object.assign(c,{trackS:startS,raceDistance:startS,lane:0,x:p.x,z:p.z,heading:p.heading,vx:p.forward.x*launch,vz:p.forward.z*launch,omega:0,wrongWay:0,stallTime:0,recoveryAt:-10});
 c.nextGate=Math.max(0,Math.floor(Math.max(0,startS)/(LENGTH/4))+1);
}
function rampageLiveAuditState(){
 if(!rampageLiveVisualAudit||gameMode!=='racing')return null;
 const c=world?.cars?.[0];if(!c)return null;
 const b=c.p3,loop=raceLoopAt(0),s0=c.trackS??0,q=((s0%LENGTH)+LENGTH)%LENGTH,span=Math.max(1,loop.endS-loop.startS),road=trackPoint(s0,0);
 const vx=b?.vx??c.vx??0,vy=b?.vy??0,vz=b?.vz??c.vz??0;
 return {mode,trackS:s0,raceDistance:c.raceDistance??0,roadKind:road?.kind??'',loopT:road?.kind==='loop'?Math.max(0,Math.min(1,(q-loop.startS)/span)):null,speedMps:Math.hypot(vx,vy,vz),forwardSpeed:road?.forward?vx*road.forward.x+vy*road.forward.y+vz*road.forward.z:null,upY:b?1-2*(b.qx*b.qx+b.qz*b.qz):1,groundedWheels:b?.groundedWheels??null,rampageBoost:!!c.rampageBoost,boostTarget:c.rampageBoostTarget??0,dead:!!c.dead,finished:!!c.finished,position:{x:b?.px??c.x??0,y:b?.py??0,z:b?.pz??c.z??0}};
}
if(rampageLiveVisualAudit)window.__breakCarsAuditState=rampageLiveAuditState;
function start(){resetInput();resetWorld();placeRampageLiveVisualAudit();mode='countdown';count=3.5;camHeading=world.cars[0].heading;"""
    s = one(s, old, new, 'audit-only race start')
    game.write_text(s)


if __name__ == '__main__':
    apply_rampage_live_audit_start_v14(Path('_site'))
