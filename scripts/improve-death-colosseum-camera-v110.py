"""Death Colosseum v1.10 horizon-stable chase camera.

Visual playtest showed the full-physics chase camera inheriting the car's roll
while balancing on an arena edge. On flat fall-only decks this makes the
horizon rotate exactly when the player most needs to read the ledge. Keep the
vehicle's real 6DoF pose, but keep the Death Colosseum camera world-up.
"""
from pathlib import Path


def apply_death_colosseum_camera_v110(target: Path) -> None:
    game_path=target/'game.js'
    game=game_path.read_text()
    old="camera.up.lerp(physicsCamUp,1-Math.exp(-6*dt));"
    new="camera.up.lerp(world.mode==='death-colosseum'?physicsWorldUp:physicsCamUp,1-Math.exp(-6*dt));"
    n=game.count(old)
    if n!=1:
        raise RuntimeError(f'Death Colosseum v1.10 horizon camera: expected 1 match, found {n}')
    game_path.write_text(game.replace(old,new,1))


if __name__=='__main__':
    apply_death_colosseum_camera_v110(Path('_site'))
