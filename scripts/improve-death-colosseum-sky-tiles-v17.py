"""Death Colosseum v1.7 SKY TILES opening stability.

Visual playtest after the v1.6 readability pass showed SKY TILES dropping too
many AI cars in the first few seconds. Widen only its tiles/bridges enough to
absorb touch/AI steering noise while preserving the gap-and-bridge topology.

"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n=text.count(old)
    if n!=1:
        raise RuntimeError(f'Death Colosseum v1.7 {label}: expected 1 match, found {n}')
    return text.replace(old,new,1)


def apply_death_colosseum_sky_tiles_v17(target: Path) -> None:
    courses_path=target/'courses.js'
    courses=courses_path.read_text()
    courses=one(
        courses,
        "for(const px of [-22,0,22])for(const pz of [-22,0,22])if(Math.abs(x-px)<=6.2&&Math.abs(z-pz)<=6.2)return H;",
        "for(const px of [-22,0,22])for(const pz of [-22,0,22])if(Math.abs(x-px)<=6.6&&Math.abs(z-pz)<=6.6)return H;",
        'tile collision width',
    )
    courses=one(
        courses,
        "if(Math.abs(x)<=28&&[-22,0,22].some(pz=>Math.abs(z-pz)<=2.2))return H;\n  if(Math.abs(z)<=28&&[-22,0,22].some(px=>Math.abs(x-px)<=2.2))return H;",
        "if(Math.abs(x)<=28&&[-22,0,22].some(pz=>Math.abs(z-pz)<=2.7))return H;\n  if(Math.abs(z)<=28&&[-22,0,22].some(px=>Math.abs(x-px)<=2.7))return H;",
        'bridge collision width',
    )
    courses_path.write_text(courses)

    view_path=target/'course-view.js'
    view=view_path.read_text()
    view=one(
        view,
        "for(const x of [-22,0,22])for(const z of [-22,0,22])addBox(x,z,12.4,12.4);for(const z of [-22,0,22])addBox(0,z,56,4.4);for(const x of [-22,0,22])addBox(x,0,4.4,56);",
        "for(const x of [-22,0,22])for(const z of [-22,0,22])addBox(x,z,13.2,13.2);for(const z of [-22,0,22])addBox(0,z,56,5.4);for(const x of [-22,0,22])addBox(x,0,5.4,56);",
        'rendered tile and bridge width',
    )
    view_path.write_text(view)


if __name__=='__main__':
    apply_death_colosseum_sky_tiles_v17(Path('_site'))
