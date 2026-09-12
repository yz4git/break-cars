"""MAYHEM TOUR v8.14: give every recap chapter a distinct visual identity.

V8.13 made the nine-event recap readable and course-coded, but the successful
852x393 visual audit still read as one frozen DOUBLE ORBIT frame with different
text on top. This pass stays presentation-only: it does not fake historical 3D
replays. Instead it turns the existing course key into a stronger editorial
visual language so each event visibly cuts to a new chapter.

Families:
- Colosseum: concentric arena rings.
- Wreck Hunt: target/crosshair + hazard bands.
- Racing: perspective lane ribbons.
Opening/finale get separate tour-wide compositions. Physics, AI, progression,
real replay recording and result data remain unchanged.
"""
from pathlib import Path


def apply_mayhem_recap_v814(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += r'''

/* MAYHEM TOUR v8.14 — distinct visual identity per recap chapter */
const MAYHEM_RECAP_V814_IDENTITY={
 opening:{family:'tour',label:'THE COMPLETE RUN',x:'-2%',y:'1%',angle:'-2deg',scale:1.08},
 classic:{family:'colosseum',label:'THE COLOSSEUM',x:'-8%',y:'3%',angle:'-7deg',scale:1.09},
 'crater-crown':{family:'colosseum',label:'CRATER CROWN',x:'7%',y:'-3%',angle:'8deg',scale:1.14},
 'maelstrom-pit':{family:'colosseum',label:'MAELSTROM PIT',x:'10%',y:'4%',angle:'-13deg',scale:1.18},
 'hunt-classic':{family:'hunt',label:'WRECK HUNT',x:'-8%',y:'-1%',angle:'5deg',scale:1.08},
 'cross-fire':{family:'hunt',label:'CROSS FIRE',x:'8%',y:'3%',angle:'-7deg',scale:1.12},
 'tidal-foundry':{family:'hunt',label:'TIDAL FOUNDRY',x:'-1%',y:'-4%',angle:'10deg',scale:1.16},
 'rampage-3d':{family:'racing',label:'RAMPAGE 3D',x:'-7%',y:'4%',angle:'-5deg',scale:1.08},
 'sky-forge':{family:'racing',label:'SKY FORGE',x:'6%',y:'-4%',angle:'6deg',scale:1.13},
 'double-orbit':{family:'racing',label:'DOUBLE ORBIT',x:'2%',y:'2%',angle:'-10deg',scale:1.18},
 finale:{family:'finale',label:'FINAL RECORD',x:'0%',y:'0%',angle:'0deg',scale:1.1}
};
const mayhemRecapV814SceneBase=mayhemRecapV813Scene;
mayhemRecapV813Scene=function(el,scene,course=''){
 mayhemRecapV814SceneBase(el,scene,course);if(!el)return;
 const key=course||scene,meta=MAYHEM_RECAP_V814_IDENTITY[key]||{family:'tour',label:String(key||'MAYHEM TOUR').toUpperCase(),x:'0%',y:'0%',angle:'0deg',scale:1.08};
 el.dataset.family=meta.family;el.dataset.visual='v814';
 const backdrop=el.querySelector('.mayhem-recap-backdrop');
 if(backdrop){backdrop.dataset.label=meta.label;backdrop.style.setProperty('--recap-x',meta.x);backdrop.style.setProperty('--recap-y',meta.y);backdrop.style.setProperty('--recap-angle',meta.angle);backdrop.style.setProperty('--recap-scale',String(meta.scale));backdrop.style.setProperty('--recap-scale-in',String(meta.scale+.07));}
 window.__breakCarsMayhemRecapIdentity={scene,course:key,family:meta.family,label:meta.label,visual:'v814'};
};
window.__breakCarsMayhemV814=true;
'''
    game.write_text(s)

    css = target / 'mayhem-tour.css'
    c = css.read_text()
    c += r'''
/* v8.14: stronger course/family identity without pretending the frozen 3D view is historical footage. */
#mayhem-tour-recap:before,#mayhem-tour-recap:after{height:11%}
.mayhem-recap-backdrop{inset:11% -5% 12%;opacity:.5;overflow:hidden;filter:saturate(1.12) contrast(1.04);transform-origin:50% 50%;--recap-x:0%;--recap-y:0%;--recap-angle:0deg;--recap-scale:1.08;--recap-scale-in:1.15}
.mayhem-recap-backdrop:before{content:"";position:absolute;inset:-18% -8%;opacity:.72;transform-origin:center;animation:mayhemRecapMotifDrift 4.8s ease-in-out infinite alternate}
.mayhem-recap-backdrop:after{content:attr(data-label);position:absolute;right:3%;bottom:-2%;width:auto;height:auto;background:none!important;transform:none!important;animation:none!important;color:rgba(255,255,255,.075);font:1000 italic clamp(38px,8vw,74px)/.82 system-ui;letter-spacing:.04em;white-space:nowrap;text-shadow:0 0 24px rgba(var(--recap-a),.14);pointer-events:none}
#mayhem-tour-recap[data-family="colosseum"] .mayhem-recap-backdrop:before{background:repeating-radial-gradient(ellipse at 48% 54%,transparent 0 38px,rgba(var(--recap-a),.24) 39px 41px,transparent 42px 67px),conic-gradient(from 18deg at 48% 54%,transparent 0 10%,rgba(var(--recap-b),.11) 10% 13%,transparent 13% 28%,rgba(var(--recap-a),.08) 28% 31%,transparent 31% 100%)}
#mayhem-tour-recap[data-family="hunt"] .mayhem-recap-backdrop:before{background:linear-gradient(90deg,transparent 49.4%,rgba(var(--recap-a),.28) 49.4% 50.6%,transparent 50.6%),linear-gradient(0deg,transparent 49.1%,rgba(var(--recap-b),.22) 49.1% 50.9%,transparent 50.9%),radial-gradient(circle at 50% 50%,transparent 0 52px,rgba(var(--recap-a),.25) 53px 56px,transparent 57px 86px,rgba(var(--recap-b),.14) 87px 90px,transparent 91px),repeating-linear-gradient(132deg,transparent 0 42px,rgba(var(--recap-a),.08) 43px 51px,transparent 52px 92px)}
#mayhem-tour-recap[data-family="racing"] .mayhem-recap-backdrop:before{inset:-45% -10% -18%;background:repeating-linear-gradient(90deg,transparent 0 8%,rgba(var(--recap-a),.18) 8.2% 8.9%,transparent 9.1% 18%),linear-gradient(180deg,transparent 0 42%,rgba(var(--recap-b),.16) 43% 45%,transparent 46% 100%);transform:perspective(460px) rotateX(58deg) translateY(18%);animation:mayhemRecapRaceFlow 2.6s linear infinite}
#mayhem-tour-recap[data-family="tour"] .mayhem-recap-backdrop:before{background:conic-gradient(from -18deg at 50% 52%,transparent 0 8%,rgba(var(--recap-a),.16) 8% 10%,transparent 10% 22%,rgba(var(--recap-b),.08) 22% 24%,transparent 24% 38%,rgba(var(--recap-a),.12) 38% 40%,transparent 40% 100%),radial-gradient(circle at 50% 52%,rgba(var(--recap-a),.16),transparent 38%)}
#mayhem-tour-recap[data-family="finale"] .mayhem-recap-backdrop:before{background:linear-gradient(118deg,rgba(var(--recap-a),.18) 0 27%,transparent 27% 48%,rgba(var(--recap-b),.12) 48% 51%,transparent 51% 70%,rgba(var(--recap-a),.12) 70% 100%),radial-gradient(circle at 50% 50%,rgba(var(--recap-b),.14),transparent 44%)}
.mayhem-recap-backdrop.cut{animation:mayhemRecapCutV814 .56s cubic-bezier(.16,.8,.2,1) both}
@keyframes mayhemRecapCutV814{0%{opacity:.06;filter:saturate(1.25) contrast(1.12) blur(7px);transform:translate(var(--recap-x),var(--recap-y)) rotate(var(--recap-angle)) scale(var(--recap-scale-in))}38%{opacity:.56}100%{opacity:.5;filter:saturate(1.12) contrast(1.04) blur(0);transform:translate(var(--recap-x),var(--recap-y)) rotate(var(--recap-angle)) scale(var(--recap-scale))}}
@keyframes mayhemRecapMotifDrift{from{translate:-1.5% 0}to{translate:1.5% 0}}
@keyframes mayhemRecapRaceFlow{from{background-position:0 0,0 0}to{background-position:88px 0,0 0}}
@media(prefers-reduced-motion:reduce){.mayhem-recap-backdrop:before{animation:none!important}}
'''
    css.write_text(c)


if __name__ == '__main__':
    apply_mayhem_recap_v814(Path('_site'))
