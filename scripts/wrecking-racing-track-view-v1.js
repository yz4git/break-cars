import * as THREE from './three.module.min.js';
import {activeCourse} from './courses.js';
import {RACE3D_LENGTH,RACE3D_TRACK,racePointAt,race3DFeatureSpec} from './racing3d.js';

export function buildRaceTrack({box,sign}){
 const group=new THREE.Group(),spec=race3DFeatureSpec(),samples=560,W=RACE3D_TRACK.halfWidth;
 group.name=`${spec.name} / MATH REBUILD`;
 const palettes={
  'rampage-3d':{road:0x343d42,edge:0xff7444,rail:0x647178,accent:0xffa15d,land:0x4b514a},
  'sky-forge':{road:0x303d46,edge:0x67d9d2,rail:0x66808a,accent:0xa7fff7,land:0x455157},
  'double-orbit':{road:0x39384a,edge:0xd98bff,rail:0x797187,accent:0xffc0ff,land:0x4c4958}
 },P=palettes[spec.courseId]||palettes['rampage-3d'];
 const material=(color,metal=.05)=>new THREE.MeshStandardMaterial({color,roughness:.88,metalness:metal,side:THREE.DoubleSide});
 const offset=(p,h)=>new THREE.Vector3(p.x+p.up.x*h,p.y+p.up.y*h,p.z+p.up.z*h);
 const align=(mesh,p)=>{const m=new THREE.Matrix4().makeBasis(new THREE.Vector3(p.right.x,p.right.y,p.right.z),new THREE.Vector3(p.up.x,p.up.y,p.up.z),new THREE.Vector3(p.forward.x,p.forward.y,p.forward.z));mesh.quaternion.setFromRotationMatrix(m);};
 function ribbon(a,b,color,height=.015){
  const vertices=[];
  for(let i=0;i<samples;i++){
   const p0a=racePointAt(i/samples*RACE3D_LENGTH,a),p0b=racePointAt(i/samples*RACE3D_LENGTH,b),p1a=racePointAt((i+1)/samples*RACE3D_LENGTH,a),p1b=racePointAt((i+1)/samples*RACE3D_LENGTH,b);
   if([p0a,p0b,p1a,p1b].some(p=>p.kind==='jump-gap'))continue;
   const q=[offset(p0a,height),offset(p1a,height),offset(p0b,height),offset(p1a,height),offset(p1b,height),offset(p0b,height)];for(const p of q)vertices.push(p.x,p.y,p.z);
  }
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geo.computeVertexNormals();const mesh=new THREE.Mesh(geo,material(color));mesh.receiveShadow=true;group.add(mesh);return mesh;
 }
 function edgeTube(lane,color,radius=.10,lift=.40){let chunk=[];const flush=()=>{if(chunk.length<4){chunk=[];return;}const geo=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(chunk,false,'centripetal'),Math.max(16,chunk.length*2),radius,6,false),mesh=new THREE.Mesh(geo,material(color,.18));mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);chunk=[];};for(let i=0;i<=samples;i++){const p=racePointAt(i/samples*RACE3D_LENGTH,lane);if(p.kind==='jump-gap'){flush();continue;}chunk.push(offset(p,lift));}flush();}
 const samples3d=[];for(let i=0;i<240;i++)samples3d.push(racePointAt(i/240*RACE3D_LENGTH));
 const minX=Math.min(...samples3d.map(p=>p.x))-24,maxX=Math.max(...samples3d.map(p=>p.x))+24,minZ=Math.min(...samples3d.map(p=>p.z))-24,maxZ=Math.max(...samples3d.map(p=>p.z))+24;
 const land=box(group,(minX+maxX)/2,-3.1,(minZ+maxZ)/2,maxX-minX,.55,maxZ-minZ,P.land);land.receiveShadow=true;
 ribbon(-W,W,P.road,.01);ribbon(-W,-W+.48,0xe5e1d1,.035);ribbon(W-.48,W,0xe5e1d1,.035);ribbon(-W+.48,-W+.84,P.edge,.043);ribbon(W-.84,W-.48,P.edge,.043);edgeTube(-W-.42,P.rail);edgeTube(W+.42,P.rail);
 // Curvature-derived banking is visible through road-normal-aligned lane marks.
 for(let i=0;i<116;i++){const p=racePointAt(i/116*RACE3D_LENGTH);if(p.kind==='loop'||p.kind==='jump-gap')continue;const d=box(group,p.x,p.y,p.z,.14,.018,1.9,0xd2d1c8);align(d,p);d.position.addScaledVector(new THREE.Vector3(p.up.x,p.up.y,p.up.z),.05);}
 // One physical ring visualization for every mathematically inserted loop.
 for(const [index,loop] of spec.loops.entries())for(let i=0;i<34;i++){const p=racePointAt(loop.startS+(loop.endS-loop.startS)*i/33),rib=box(group,p.x,p.y,p.z,W*2+.30,.055,.20,i%6===0?P.accent:0x73797b,true);align(rib,p);rib.position.addScaledVector(new THREE.Vector3(p.up.x,p.up.y,p.up.z),.055);if(i===17){const b=sign(`${spec.name} / LOOP ${index+1}`,18,1.8);b.position.set(p.x,p.y+2.8,p.z);b.rotation.y=p.heading+Math.PI/2;group.add(b);}}
 // Ballistic jump: take-off and landing markers are placed from the actual gap S range.
 for(const side of [-1,1])for(let k=0;k<4;k++){const p=racePointAt(spec.jump.startS-6+k*1.35,side*4.5);if(p.kind==='jump-gap')continue;const m=box(group,p.x,p.y,p.z,.9,.022,.70,k%2?P.accent:0xf1ead9);align(m,p);m.position.addScaledVector(new THREE.Vector3(p.up.x,p.up.y,p.up.z),.065);}
 for(const s of [spec.jump.startS-2,spec.jump.endS+2])for(const side of [-1,1]){const p=racePointAt(s,side*(W+1.2)),h=Math.max(1.2,p.y+3.0);box(group,p.x,p.y-h/2-.3,p.z,.22,h,.22,0x3d4a51,true);}
 // Elevated sections get sparse supports; they communicate height without hiding collisions.
 for(let i=0;i<24;i++){const p=racePointAt(i/24*RACE3D_LENGTH);if(p.y<4.8||p.kind==='loop')continue;for(const side of [-1,1]){const q=racePointAt(p.s,side*(W-.7)),h=Math.max(1,p.y+2.6);box(group,q.x,q.y-h/2-.45,q.z,.25,h,.25,0x43505a,true);}}
 const start=racePointAt(0);for(const side of [-1,1]){const p=racePointAt(0,side*(W+1.2));box(group,p.x,3.3,p.z,.42,6.6,.42,0x8a938e,true);}const beam=box(group,start.x,start.y+6.2,start.z,W*2+4.6,.46,.50,P.edge,true);beam.rotation.y=start.heading;const banner=sign(spec.name,22,2.0);banner.position.set(start.x,start.y+5.25,start.z);banner.rotation.y=start.heading+Math.PI/2;group.add(banner);
 // Outer spectator frame is intentionally low and distant so the whole calculated silhouette reads on iPhone landscape.
 for(const side of [-1,1]){const z=side*(Math.max(Math.abs(minZ),Math.abs(maxZ))+12),b=sign('BREAK CARS / WRECKING RACING',31,2.1);b.position.set(0,8.5,z);b.rotation.y=side>0?Math.PI:0;group.add(b);}
 group.userData.mathCourse={courseId:spec.courseId,designSpeed:spec.designSpeed,maxGrade:spec.maxGrade,bankMax:spec.bankMax,jumpSafety:spec.jump.designRange/Math.max(.1,spec.jump.gapLength)};
 return group;
}
