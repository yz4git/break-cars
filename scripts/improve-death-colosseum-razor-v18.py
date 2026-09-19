"""Death Colosseum v1.8 RAZOR CROSS center battle hub.

Live visual audit showed the four narrow arms funneling all cars into a 6.6m
intersection, producing random mass ring-outs. Preserve the knife-edge arms but
give the exact center a compact square battle hub.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n=text.count(old)
    if n!=1:
        raise RuntimeError(f'Death Colosseum v1.8 {label}: expected 1 match, found {n}')
    return text.replace(old,new,1)


def apply_death_colosseum_razor_v18(target: Path) -> None:
    courses_path=target/'courses.js'
    courses=courses_path.read_text()
    courses=one(
        courses,
        "if(id==='razor-cross'){\n  if((Math.abs(x)<=3.3&&Math.abs(z)<=36)||(Math.abs(z)<=3.3&&Math.abs(x)<=36))return H;",
        "if(id==='razor-cross'){\n  if(Math.abs(x)<=6.5&&Math.abs(z)<=6.5)return H;\n  if((Math.abs(x)<=3.3&&Math.abs(z)<=36)||(Math.abs(z)<=3.3&&Math.abs(x)<=36))return H;",
        'center hub collision',
    )
    courses_path.write_text(courses)

    view_path=target/'course-view.js'
    view=view_path.read_text()
    view=one(
        view,
        "addBox(0,0,6.6,72);addBox(0,0,72,6.6);for(const [x,z] of [[0,29],[29,0],[0,-29],[-29,0]])",
        "addBox(0,0,6.6,72);addBox(0,0,72,6.6);addBox(0,0,13,13);for(const [x,z] of [[0,29],[29,0],[0,-29],[-29,0]])",
        'rendered center hub',
    )
    view_path.write_text(view)


if __name__=='__main__':
    apply_death_colosseum_razor_v18(Path('_site'))
