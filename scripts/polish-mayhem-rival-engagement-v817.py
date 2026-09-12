"""MAYHEM TOUR v8.17: keep the persistent RIVAL in the fight.

The nine-event series already carries one rival, its hull, and the series score.
This pass improves the *ordinary* first eight events: when the rival drifts out
of the action it gets a small, bounded rejoin force and a stronger preference
for the player. Racing uses race-distance catch-up plus the existing battle AI;
arena modes use a short predicted intercept. RELIEF still wins immediately and
the existing event-nine FINAL DUEL remains the sole pressure layer there.

No teleporting, damage multipliers, geometry changes, or player nerfs are added.
"""
from pathlib import Path


def apply_mayhem_rival_engagement_v817(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += r'''

/* MAYHEM TOUR v8.17 — persistent RIVAL engagement for events 1-8 */
const mayhemDirectorTickV817Base=mayhemDirectorTick;
let mayhemRivalEngagementState='SEARCH',mayhemRivalEngagementDistance=999,mayhemRivalEngagementGap=0,mayhemRivalEngagementContacts=0,mayhemRivalEngagementLastContact=-99;
function mayhemRivalEngagementTelemetryV817(p,r,extra={}){
 const hull=p?clamp(p.hp/Math.max(1,p.maxHP),0,1):0,rivalHull=r?clamp(r.hp/Math.max(1,r.maxHP),0,1):0;
 window.__breakCarsMayhemRivalEngagement={state:mayhemRivalEngagementState,distance:mayhemRivalEngagementDistance,gap:mayhemRivalEngagementGap,contacts:mayhemRivalEngagementContacts,event:mayhemState?.event??-1,playerHull:hull,rivalHull,...extra};
 document.body.dataset.mayhemRivalEngagement=mayhemRivalEngagementState.toLowerCase().replaceAll(' ','-');
}
function mayhemRivalEngagementTickV817(dt){
 if(!mayhemActive()||mode!=='race'||!world?.cars?.[0])return;
 const p=world.cars[0],r=mayhemRivalLive();
 if(!r||r.dead||r.finished){mayhemRivalEngagementState='OUT';mayhemRivalEngagementDistance=999;mayhemRivalEngagementTelemetryV817(p,r);return;}
 const dx=p.x-r.x,dz=p.z-r.z,dist=Math.hypot(dx,dz)||.001,playerHull=clamp(p.hp/Math.max(1,p.maxHP),0,1),pressure=typeof mayhemTourPressure==='function'?mayhemTourPressure():.5;
 mayhemRivalEngagementDistance=dist;
 for(const e of world.events||[])if(e.type==='impact'&&((e.a===0&&e.b===r.id)||(e.b===0&&e.a===r.id))&&world.time-mayhemRivalEngagementLastContact>.24){mayhemRivalEngagementLastContact=world.time;mayhemRivalEngagementContacts++;}
 // Event nine already owns a carefully bounded FINAL DUEL. Never stack another
 // catch-up layer on top of it, and always respect the Director's low-hull relief.
 if(mayhemFinalDuelActive()){mayhemRivalEngagementState='FINAL DUEL';mayhemRivalEngagementGap=(p.raceDistance||0)-(r.raceDistance||0);mayhemRivalEngagementTelemetryV817(p,r,{finalDuel:true});return;}
 if(mayhemDirectorState==='RELIEF'||playerHull<.36){mayhemRivalEngagementState='RELIEF';mayhemRivalEngagementGap=0;mayhemRivalEngagementTelemetryV817(p,r,{relief:true});return;}
 mayhemRivalEngagementState=dist<8?'CONTACT':dist<20?'LOCK':dist<38?'HUNT':'REJOIN';
 if(world.mode==='racing'){
  const gap=(p.raceDistance||0)-(r.raceDistance||0);mayhemRivalEngagementGap=gap;
  // Keep the authored racing battle AI in charge. This only refreshes its player
  // target while the two cars are plausibly in the same fight window.
  if(gap>-7&&gap<24){r.battleTarget=0;r.battleTimer=Math.min(Number(r.battleTimer)||.12,.08);r.raceAggro=Math.max(Number(r.raceAggro)||.8,.90+pressure*.06);}
  // If the rival loses the pack, add at most ~1.35 m/s^2 along its own heading.
  // It cannot teleport, skip track projection, or receive a bonus while ahead.
  if(gap>8&&gap<70){const catchup=Math.min(1.35,.34+(gap-8)*.021)*( .72+pressure*.42)*dt;r.vx+=Math.sin(r.heading)*catchup;r.vz+=Math.cos(r.heading)*catchup;}
 }else{
  mayhemRivalEngagementGap=0;r.target=0;r.aiTimer=Math.max(Number(r.aiTimer)||0,.62);
  if(dist>12&&dist<52){const lead=.22+pressure*.18,tx=p.x+(p.vx||0)*lead,tz=p.z+(p.vz||0)*lead,ix=tx-r.x,iz=tz-r.z,il=Math.hypot(ix,iz)||1,force=Math.min(.92,.28+(dist-12)*.018)*( .72+pressure*.38)*dt;r.vx+=ix/il*force;r.vz+=iz/il*force;}
 }
 mayhemRivalEngagementTelemetryV817(p,r,{pressure,director:mayhemDirectorState});
}
mayhemDirectorTick=function(dt){mayhemDirectorTickV817Base(dt);mayhemRivalEngagementTickV817(dt);};
window.__breakCarsMayhemV817=true;
'''
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.17: make an active rivalry legible without adding another HUD panel. */
body[data-mayhem-rival-engagement="lock"] #mayhem-rival-marker,
body[data-mayhem-rival-engagement="contact"] #mayhem-rival-marker{filter:drop-shadow(0 0 8px #ff496b88)}
body[data-mayhem-rival-engagement="contact"] #mayhem-rival-marker{transform:translate(-50%,-50%) scale(1.08)}
body[data-mayhem-rival-engagement="rejoin"] #mayhem-rival-marker{opacity:.72}
body[data-mayhem-rival-engagement="relief"] #mayhem-rival-marker{opacity:.48;filter:saturate(.55)}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_rival_engagement_v817(Path('_site'))
