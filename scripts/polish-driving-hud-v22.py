"""BREAK CARS v22: improve compact driving HUD legibility on iPhone landscape.

This is presentation-only.  Camera switching, radar rendering, input, physics,
scoring and mode rules are untouched.  The Japanese camera label is forced to
one horizontal line with a slightly wider tap target, while the radar receives
a modest size/contrast lift so it remains readable over the 3D scene.
"""
from pathlib import Path


def apply_driving_hud_v22(target: Path) -> None:
    racing = target / 'racing.css'
    css = racing.read_text()
    marker = '/* BREAK CARS driving HUD v22 */'
    if marker in css:
        raise RuntimeError('driving HUD v22 already applied')

    polish = r'''

/* BREAK CARS driving HUD v22 */
body.playing #camera{
  width:56px;
  min-width:56px;
  height:38px;
  padding:0 8px;
  white-space:nowrap;
  writing-mode:horizontal-tb;
  line-height:1;
  font-size:13px;
  font-weight:800;
  letter-spacing:.04em;
}
body.playing #radar{
  width:92px;
  height:92px;
  opacity:.94;
  background:#101b28a6;
  border:1px solid #ffffff26;
  border-radius:16px;
  box-shadow:0 8px 24px #0005,inset 0 1px #ffffff14;
}
@media (orientation:landscape) and (max-height:430px){
  body.playing #camera{
    width:54px;
    min-width:54px;
    height:38px;
    font-size:13px;
  }
  body.playing #radar{
    width:86px;
    height:86px;
    top:max(54px,calc(env(safe-area-inset-top) + 46px));
  }
}
'''
    racing.write_text(css.rstrip() + polish + '\n')


if __name__ == '__main__':
    apply_driving_hud_v22(Path('_site'))
