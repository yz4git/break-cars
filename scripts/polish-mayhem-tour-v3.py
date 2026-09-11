"""MAYHEM TOUR v3: give the Tour entry the full menu width on iPhone landscape.

The ordinary menu uses a multi-column mode selector. During a Tour only the
Tour entry is visible, so collapse that selector to one full-width row and keep
its title/subtitle readable without changing the three normal mode cards.
"""
from pathlib import Path


def apply_mayhem_tour_v3(target: Path) -> None:
    css = target / 'mayhem-tour.css'
    s = css.read_text()
    s += r'''
body.mayhem-tour .mode-select{display:block!important;width:100%!important;margin:8px 0 9px!important;grid-template-columns:none!important}
body.mayhem-tour #mayhem-tour-entry{display:flex!important;width:100%!important;min-width:0!important;min-height:48px!important;align-items:center!important;justify-content:space-between!important;gap:14px!important;padding:10px 14px!important;text-align:left!important}
body.mayhem-tour #mayhem-tour-entry b{display:block!important;flex:0 0 auto!important;white-space:nowrap!important;font-size:12px!important;line-height:1.05!important;letter-spacing:.04em!important}
body.mayhem-tour #mayhem-tour-entry small{display:block!important;flex:1 1 auto!important;min-width:0!important;text-align:right!important;white-space:nowrap!important;font-size:9px!important;line-height:1.15!important;letter-spacing:.04em!important;color:#c8d1d8!important}
@media(orientation:landscape) and (max-height:430px){body.mayhem-tour .mode-select{margin:6px 0 7px!important}body.mayhem-tour #mayhem-tour-entry{min-height:42px!important;padding:8px 12px!important}body.mayhem-tour #mayhem-tour-entry b{font-size:11px!important}body.mayhem-tour #mayhem-tour-entry small{font-size:8px!important}}
'''
    css.write_text(s)


if __name__ == '__main__':
    apply_mayhem_tour_v3(Path('_site'))
