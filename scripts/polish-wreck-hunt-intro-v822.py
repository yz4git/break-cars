"""BREAK CARS v8.22: keep transient HUD messaging on real time.

Rendered 852x393 audits run through a software WebGL path and can deliver frames
far below the target iPhone frame rate. The base toast timer subtracts the
frame-clamped simulation dt, so a two-second HUNT START callout can remain over
the road for many seconds of real time. Gameplay timing is intentionally left
alone; only transient UI uses performance.now() as its expiry clock.

WRECK HUNT's opening callout is also shortened to a compact ~1 second beat and
is suppressed inside MAYHEM TOUR, where the Director already owns the intro.

This is currently the final generated build hook in prepare-pages, so it also
invokes the WRECKING RACING math compiler after every legacy racing patch. That
keeps Pages and every visual/physics diagnostic on the same final course source.
"""
from pathlib import Path
import importlib.util


def apply_wreck_hunt_intro_v822(target: Path) -> None:
    game = target / 'game.js'
    s = game.read_text()
    s += r'''

/* BREAK CARS v8.22 — wall-clock transient HUD + compact WRECK HUNT opening */
const toastV822Base=toast;
let toastWallDeadlineV822=0;
const toastClockTelemetryV822=window.__breakCarsToastClockV822={version:'8.22',wallClock:true,huntOpeningSeconds:.95,mayhemSuppress:true,lastText:'',lastDuration:0};
function toastClearV822(){const el=$('toast');if(el){el.textContent='';el.classList.remove('hunt-opening-v822');}toastTime=0;toastWallDeadlineV822=0;}
toast=function(text,duration=1.4){
 const huntOpening=text==='HUNT START — WRECK TARGETS';
 if(huntOpening&&typeof mayhemActive==='function'&&mayhemActive())return;
 const actual=huntOpening?Math.min(duration,.95):duration;
 toastV822Base(text,actual);toastWallDeadlineV822=performance.now()+Math.max(0,actual)*1000;
 const el=$('toast');if(el)el.classList.toggle('hunt-opening-v822',huntOpening);
 toastClockTelemetryV822.lastText=text;toastClockTelemetryV822.lastDuration=actual;
};
function toastWallClockTickV822(now){
 const el=$('toast');
 if(toastWallDeadlineV822>0&&now>=toastWallDeadlineV822)toastClearV822();
 else if(toastTime<=0&&el&&!el.textContent)el.classList.remove('hunt-opening-v822');
 requestAnimationFrame(toastWallClockTickV822);
}
requestAnimationFrame(toastWallClockTickV822);
'''
    game.write_text(s)

    css = target / 'style.css'
    c = css.read_text()
    c += r'''

/* v8.22: WRECK HUNT opening is a brief cue, not a gameplay-covering title card. */
#toast.hunt-opening-v822{top:27%;font-size:18px;letter-spacing:.14em;padding:5px 14px;border-top:1px solid #ffb45a55;border-bottom:1px solid #ffb45a55;background:linear-gradient(90deg,transparent,#111820b8 16%,#111820b8 84%,transparent);text-shadow:0 2px 10px #000,0 0 16px #ff8a3b44}
@media(orientation:landscape) and (max-height:430px){#toast.hunt-opening-v822{top:26%;font-size:16px;padding:4px 12px;letter-spacing:.12em}}
'''
    css.write_text(c)

    compiler_path = Path(__file__).with_name('rebuild-wrecking-racing-math-v1.py')
    spec = importlib.util.spec_from_file_location('break_cars_wrecking_racing_math_v1', compiler_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_wrecking_racing_math_v1(target)


if __name__ == '__main__':
    apply_wreck_hunt_intro_v822(Path('_site'))
