import * as THREE from './three.module.min.js?v=wr3d-v1';
import {trackPoint,LENGTH,TRACK,race3DFeatureSpec} from './racing.js?v=wr3d-v1';

export function buildRaceTrack({box,sign}){
 const group=new THREE.Group();group.name='Rampage 3D Circuit';
 const spec=race3DFeatureSpec(),samples=420;
 const material=(color,metalness=.05)=>new THREE.MeshStandardMaterial({color,roughness:.9,metalness,side:THREE.DoubleSide});
 const offset=(p,h)=>new THREE.Vector3(p.x+p.up.x*h,p.y+p.up.y*h,p.z+p.up.z*h);
 function ribbon(a,b,color,height=.015){
  const vertices=[];
  for(let i=0;i<samples;i++){
   const s0=i/samples*LENGTH,s1=(i+1)/samples*LENGTH,p0a=trackPoint(s0,a),p0b=trackPoint(s0,b),p1a=trackPoint(s1,a),p1b=trackPoint(s1,b);
   if([p0a,p0b,p1a,p1b].some(p=>p.kind==='jump-gap'))continue;
   // Winding follows forward x right = road up, so the visible front face is
   // the same side used by suspension/tyre physics. The previous right x
   // forward winding pointed at -up and made loop entries read underside-first.
   const q=[offset(p0a,height),offset(p1a,height),offset(p0b,height),offset(p1a,height),offset(p1b,height),offset(p0b,height)];for(const p of q)vertices.push(p.x,p.y,p.z);
  }
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geo.computeVertexNormals();const mesh=new THREE.Mesh(geo,material(color));mesh.receiveShadow=true;mesh.castShadow=false;group.add(mesh);return mesh;
 }
 function edgeTube(lane,color,radius=.11,lift=.44){
  let chunk=[];const flush=()=>{if(chunk.length<4){chunk=[];return;}const curve=new THREE.CatmullRomCurve3(chunk,false,'centripetal'),geo=new THREE.TubeGeometry(curve,Math.max(12,chunk.length*2),radius,6,false),mesh=new THREE.Mesh(geo,material(color,.2));mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);chunk=[];};
  for(let i=0;i<=samples;i++){const p=trackPoint(i/samples*LENGTH,lane);if(p.kind==='jump-gap'){flush();continue;}chunk.push(offset(p,lift));}flush();
 }
 function align(mesh,p){const m=new THREE.Matrix4().makeBasis(new THREE.Vector3(p.right.x,p.right.y,p.right.z),new THREE.Vector3(p.up.x,p.up.y,p.up.z),new THREE.Vector3(p.forward.x,p.forward.y,p.forward.z));mesh.quaternion.setFromRotationMatrix(m);}
 function postAt(s,lane,color=0x5c676d){const p=trackPoint(s,lane),h=Math.max(.8,p.y+.9),m=box(group,p.x/1,p.y*.5-.05,p.z/1,.18,h,.18,color,true);return m;}

 // Infield is lowered so the jump gap and over/under crossing read as real depth.
 const land=box(group,0,-2.7,0,170,.5,118,0x4d5148);land.receiveShadow=true;
 ribbon(-TRACK.halfWidth,TRACK.halfWidth,0x363e43,.01);
 ribbon(-TRACK.halfWidth,-TRACK.halfWidth+.48,0xe4e0cf,.035);ribbon(TRACK.halfWidth-.48,TRACK.halfWidth,0xe4e0cf,.035);
 ribbon(-TRACK.halfWidth+.48,-TRACK.halfWidth+.82,0xff7042,.043);ribbon(TRACK.halfWidth-.82,TRACK.halfWidth-.48,0xff7042,.043);
 edgeTube(-TRACK.halfWidth-.45,0x626d72,.12,.52);edgeTube(TRACK.halfWidth+.45,0x626d72,.12,.52);

 // Banked center dashes follow the actual surface normal, including hills and the loop.
 for(let i=0;i<94;i++){const p=trackPoint(i/94*LENGTH,0);if(p.kind==='jump-gap'||p.kind==='loop')continue;const d=box(group,p.x,p.y,p.z,.13,.018,2.1,0xc7c7bd);align(d,p);d.position.add(new THREE.Vector3(p.up.x*.045,p.up.y*.045,p.up.z*.045));}

 // Explicit loop ribs make the vertical stunt readable without blocking the chase camera.
 for(let i=0;i<30;i++){const s=spec.loop.startS+(spec.loop.endS-spec.loop.startS)*i/29,p=trackPoint(s,0);const rib=box(group,p.x,p.y,p.z,TRACK.halfWidth*2+.35,.055,.22,i%5===0?0xff7545:0x6e7474,true);align(rib,p);rib.position.add(new THREE.Vector3(p.up.x*.055,p.up.y*.055,p.up.z*.055));}

 // Jump take-off/landing chevrons and deep gap supports.
 for(let k=0;k<5;k++)for(const lane of [-5.4,0,5.4]){const s=spec.jump.startS-8+k*1.55,p=trackPoint(s,lane);if(p.kind==='jump-gap')continue;const marker=box(group,p.x,p.y,p.z,1.05,.025,.72,k%2?0xffa45e:0xe8e3d3);align(marker,p);marker.position.add(new THREE.Vector3(p.up.x*.07,p.up.y*.07,p.up.z*.07));}
 const before=trackPoint(spec.jump.startS-4,0),after=trackPoint(spec.jump.endS+4,0);for(const p of [before,after])for(const side of [-1,1]){const q=trackPoint(p.s,side*(TRACK.halfWidth+1.5));box(group,q.x,Math.max(-1.9,q.y*.5-1),q.z,.22,Math.max(1.4,q.y+1.8),.22,0x394750,true);}

 // The elevated branch crosses above the low branch at the arena center.
 const bridge=trackPoint(spec.bridge.s,0);for(const lane of [-7.3,7.3]){const p=trackPoint(spec.bridge.s,lane);box(group,p.x,(p.y-2.25)/2,p.z,.52,Math.max(2,p.y+1.5),.52,0x46545d,true);box(group,p.x,p.y-.65,p.z,2.1,.42,2.1,0x5a666a,true);}const crossSign=sign('OVER / UNDER SMASH',20,2.2);crossSign.position.set(bridge.x,bridge.y+4.3,bridge.z);crossSign.rotation.y=bridge.heading+Math.PI/2;group.add(crossSign);

 // Start/finish gantry sits clear of the chase camera and names the new circuit.
 const start=trackPoint(0,0);for(const side of [-1,1]){const p=trackPoint(0,side*(TRACK.halfWidth+1.3));box(group,p.x,3.4,p.z,.42,6.8,.42,0x89938e,true);}const beam=box(group,start.x,6.6,start.z,TRACK.halfWidth*2+5,.48,.52,0xff7040,true);beam.rotation.y=start.heading;const banner=sign('RAMPAGE 3D',22,2.2);banner.position.set(start.x,start.y+5.5,start.z);banner.rotation.y=start.heading+Math.PI/2;group.add(banner);

 // Spectator terraces and skyline still frame the course without hiding elevation changes.
 for(const side of [-1,1]){for(let row=0;row<4;row++)box(group,0,1+row*1.25,side*(48+row*2.2),128,1.35,2.1,row%2?0x344653:0x475862);const b=sign('BREAK CARS / FULL CONTACT 3D',35,2.4);b.position.set(0,8.5,side*58);b.rotation.y=side>0?Math.PI:0;group.add(b);}
 for(const x of [-82,82])for(const z of [-45,45]){box(group,x,10,z,.4,20,.4,0x344451);box(group,x,20,z,5,1.4,.8,0xeff1e4);}
 const loopBoard=sign('VERTICAL WRECK LOOP',18,2);const loopP=trackPoint((spec.loop.startS+spec.loop.endS)*.5,0);loopBoard.position.set(loopP.x,loopP.y+2.5,loopP.z-5);loopBoard.rotation.y=loopP.heading+Math.PI/2;group.add(loopBoard);
 return group;
}
