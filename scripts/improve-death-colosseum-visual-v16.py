"""Death Colosseum v1.6 visual readability pass.

The final 5-course live screenshot review showed the glowing red lower floor
dominating the frame, especially on SKY TILES and BROKEN ORBIT. Keep the fall
zone readable, but make the authored deck silhouette the strongest visual cue.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'Death Colosseum v1.6 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_death_colosseum_visual_v16(target: Path) -> None:
    view_path = target / 'course-view.js'
    view = view_path.read_text()

    view = one(
        view,
        "const H=9,deck=new THREE.MeshStandardMaterial({color:0x323941,roughness:.82,metalness:.18,side:THREE.DoubleSide}),edge=new THREE.MeshStandardMaterial({color:0xff4b32,emissive:0xa5130b,emissiveIntensity:.72,roughness:.48,metalness:.28,side:THREE.DoubleSide});",
        "const H=9,deck=new THREE.MeshStandardMaterial({color:0x3d4852,roughness:.78,metalness:.22,side:THREE.DoubleSide}),edge=new THREE.MeshStandardMaterial({color:0xff6840,emissive:0xd52a12,emissiveIntensity:1.12,roughness:.42,metalness:.32,side:THREE.DoubleSide}),outline=new THREE.LineBasicMaterial({color:0xff8a58,transparent:true,opacity:.76});",
        'deck and edge contrast',
    )

    view = one(
        view,
        "const kill=new THREE.Mesh(new THREE.CylinderGeometry(43,43,.36,96),new THREE.MeshStandardMaterial({color:0x170307,emissive:0x7d0a12,emissiveIntensity:1.35,roughness:.88}));kill.position.y=-.13;kill.receiveShadow=true;group.add(kill);",
        "const kill=new THREE.Mesh(new THREE.CylinderGeometry(43,43,.36,96),new THREE.MeshStandardMaterial({color:0x07080b,emissive:0x2d0308,emissiveIntensity:.34,roughness:.96}));kill.position.y=-.13;kill.receiveShadow=true;group.add(kill);const hazardLine=new THREE.MeshBasicMaterial({color:0xa71b22,transparent:true,opacity:.34,side:THREE.DoubleSide,depthWrite:false});for(const rr of [[11.8,12.05],[23.8,24.05],[35.8,36.05],[41.5,41.85]]){const h=new THREE.Mesh(new THREE.RingGeometry(rr[0],rr[1],96),hazardLine);h.rotation.x=-Math.PI/2;h.position.y=.09;group.add(h);}",
        'dark abyss with sparse hazard rings',
    )

    view = one(
        view,
        "const addBox=(x,z,w,d,y=H)=>{const m=new THREE.Mesh(new THREE.BoxGeometry(w,.8,d),deck);m.position.set(x,y-.4,z);m.receiveShadow=true;group.add(m);return m;};",
        "const addBox=(x,z,w,d,y=H)=>{const m=new THREE.Mesh(new THREE.BoxGeometry(w,.8,d),deck);m.position.set(x,y-.4,z);m.receiveShadow=true;const l=new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry),outline);l.renderOrder=3;m.add(l);group.add(m);return m;};",
        'box deck outline',
    )

    view_path.write_text(view)


if __name__ == '__main__':
    apply_death_colosseum_visual_v16(Path('_site'))
