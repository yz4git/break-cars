"""Align Wrecking Racing labels/help with the dedicated RAMPAGE 3D course."""
from pathlib import Path


def replace_all(text: str, old: str, new: str, label: str) -> str:
    n=text.count(old)
    if n<1:
        raise RuntimeError(f'Racing3D UI {label}: no matches')
    return text.replace(old,new)


def apply_racing3d_ui(target: Path) -> None:
    path=target/'game.js';s=path.read_text()
    s=replace_all(s,"IRON LOOP / WRECKING RACING","RAMPAGE 3D / WRECKING RACING","mode tag")
    s=replace_all(s,"4 LAPS. FULL CONTACT.","4 LAPS. FULL CONTACT 3D.","subtitle")
    s=replace_all(s,"追い抜け。ぶつけろ。勝ち取れ。","飛べ。傾け。交差で潰せ。ループを抜けろ。","mode lead")
    s=replace_all(s,"4周 ／ 衝突点＋1周400点＋完走順位ボーナス<br>側面スピン +200 ／ 撃破 +500 ／ 逆走は周回に加算されません","4周 ／ 高低差・ジャンプ・バンク・立体交差・垂直ループ<br>衝突点＋1周400点 ／ 側面スピン +250 ／ 撃破 +500 ／ 完走順位ボーナス","mode hint")
    s=replace_all(s,"IRON LOOP<span>WRECKING RACING / 4 LAPS</span>","RAMPAGE 3D<span>JUMP / BANK / CROSS / VERTICAL LOOP</span>","arena caption")
    s=replace_all(s,"4周。衝突点＋1周400点＋完走順位ボーナスで総合順位を決定。1位3500点、2位2900点、3位2400点。側面スピンは200点、撃破は500点。先頭ゴール後22秒で終了。","RAMPAGE 3Dを4周。高低差、ジャンプ、バンク、上下交差、垂直ループを突破しながら、衝突点＋1周400点＋完走順位ボーナスで総合順位を決定。側面スピンは250点、撃破は500点。先頭ゴール後24秒で終了。","pause help")
    s=replace_all(s,"4周！ 追い抜け、ぶつけろ。","RAMPAGE 3D！ 飛べ、ぶつけろ、ループを抜けろ。","opening toast")
    path.write_text(s)

if __name__=='__main__':
    apply_racing3d_ui(Path('_site'))
