"""Keep DOUBLE ORBIT upright through the final post-loop jump.

The existing v7 runoff settles the chassis after either loop but intentionally
stops all assistance as soon as a jump surface begins. Seed 2468 can therefore
reach the final jump with enough residual roll to enter the gap fully inverted
and remain there while still carrying healthy speed.

This v8 patch extends ONLY attitude torque through jump-ramp / jump-gap /
jump-landing after loop two. It does not add tyre traction, downforce, position
correction, quaternion snapping, velocity writes, trackS writes or raceDistance
writes. Geometry and every RAMPAGE path are untouched.
"""
from pathlib import Path


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'DOUBLE ORBIT final jump v8 {label}: expected 1 match, found {n}')
    return text.replace(old, new, 1)


def apply_double_orbit_final_jump_v8(target: Path) -> None:
    physics = target / 'physics3d.js'
    s = physics.read_text()

    # v5 introduced this helper as doubleOrbitExitRunoff; v7 then tunes its
    # behavior in place. Anchor v8 to the current helper name so the patch stays
    # compatible with the actual generated physics pipeline.
    anchor = "function doubleOrbitExitRunoff"
    idx = s.find(anchor)
    if idx < 0:
        raise RuntimeError('DOUBLE ORBIT final jump v8: exit runoff helper not found')

    helper = r"""function doubleOrbitFinalJumpAttitude(w,c,ctx,acc){
 const loops=RAMPAGE_RACE_SPEC.loops;if(activeCourse.id!=='double-orbit'||!loops||loops.length<2)return;
 const b=c.p3,L=RAMPAGE_RACE_SPEC.length,q=((c.trackS??0)%L+L)%L,afterSecond=(q-loops[1].endS+L)%L,road=racePointAt(q);
 if(afterSecond>155||!(road.kind==='jump-ramp'||road.kind==='jump-gap'||road.kind==='jump-landing'))return;
 const bu=bodyUp(b),omega={x:b.wx,y:b.wy,z:b.wz},align=dot(bu,road.up),yawRate=dot(omega,road.up),tiltRate={x:omega.x-road.up.x*yawRate,y:omega.y-road.up.y*yawRate,z:omega.z-road.up.z*yawRate},err=cross(bu,road.up),errMag=Math.hypot(err.x,err.y,err.z);
 // At an exact 180-degree inversion cross(up,upTarget) is near zero. Use the
 // road-forward axis as a deterministic escape direction, choosing the sign
 // from existing roll where possible, so the controller never gets stuck at
 // the antipodal singularity.
 if(align<-.82&&errMag<.35){const rollRate=dot(omega,road.forward),dir=Math.abs(rollRate)>.12?Math.sign(rollRate):(c.id%2?-1:1),kick=.34;err.x+=road.forward.x*dir*kick;err.y+=road.forward.y*dir*kick;err.z+=road.forward.z*dir*kick;}
 const k=align<-.35?17.5:align<.35?13.0:9.0,d=4.4,maxT=(align<-.35?18:14)*b.mass;
 acc.tx+=ctx.clamp((err.x*k-tiltRate.x*d)*b.mass,-maxT,maxT);
 acc.ty+=ctx.clamp((err.y*k-tiltRate.y*d)*b.mass,-maxT,maxT);
 acc.tz+=ctx.clamp((err.z*k-tiltRate.z*d)*b.mass,-maxT,maxT);
}

"""
    s = s[:idx] + helper + s[idx:]

    # v5 calls doubleOrbitExitRunoff(w,c,acc,ctx). Insert the jump-only helper
    # immediately before that unique call so all existing runoff behavior is
    # preserved and only the final-jump attitude moment is added.
    call = "doubleOrbitExitRunoff(w,c,acc,ctx);"
    s = one(s, call, f"doubleOrbitFinalJumpAttitude(w,c,ctx,acc);{call}", 'attitude call')
    physics.write_text(s)


if __name__ == '__main__':
    apply_double_orbit_final_jump_v8(Path('_site'))
