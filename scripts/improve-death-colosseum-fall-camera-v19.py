"""Death Colosseum v1.9 fall-out camera beat.

The live screenshot review showed the result modal appearing on the exact frame
the player fell, hiding the most important payoff of a fall-only mode. Keep
instant elimination, but let the full-3D body/camera show the fall for 1.35s
before revealing the result.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n=text.count(old)
    if n!=1:
        raise RuntimeError(f'Death Colosseum v1.9 {label}: expected 1 match, found {n}')
    return text.replace(old,new,1)


def apply_death_colosseum_fall_camera_v19(target: Path) -> None:
    game_path=target/'game.js'
    game=game_path.read_text()

    game=one(
        game,
        "let previousMode='race';function togglePause()",
        "let previousMode='race',deathFinishAt=0;function togglePause()",
        'fall camera timer state',
    )
    if "function start(){resetInput();resetWorld();" in game:
        game=game.replace(
            "function start(){resetInput();resetWorld();",
            "function start(){resetInput();resetWorld();deathFinishAt=0;",
            1,
        )
    else:
        probe=game.find("function start")
        context=game[max(0,probe-300):probe+1800] if probe>=0 else game[:1800]
        raise RuntimeError(f'Death Colosseum v1.9 start layout context={context!r}')
    old="if((world.mode!=='racing'&&world.cars[0].dead)||world.done){finish();break;}"
    new="""if(world.mode==='death-colosseum'&&world.cars[0].dead){
 if(!deathFinishAt){deathFinishAt=now+1350;resetInput();$('driving').classList.add('hidden');toast('FALLEN — RING OUT',1.15);}
 if(now>=deathFinishAt){finish();break;}
}else if((world.mode!=='racing'&&world.cars[0].dead)||world.done){finish();break;}"""
    game=one(game,old,new,'delayed Death Colosseum result')

    game_path.write_text(game)


if __name__=='__main__':
    apply_death_colosseum_fall_camera_v19(Path('_site'))
