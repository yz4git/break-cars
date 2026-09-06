import * as THREE from './three.module.min.js?v=wr110-20260906';
import {trackPoint,LENGTH,TRACK} from './racing.js?v=wr110-20260906';
export function buildRaceTrack({box,sign}){
 const group=new THREE.Group();group.name='Iron Loop Raceway';
 function strip(a,b,color,height=.01){const vertices=[],uv=[];for(let i=0;i<180;i++){const s=i/180*LENGTH,t=(i+1)/180*LENGTH;const p=[trackPoint(s,a),trackPoint(s,b),trackPoint(t,a),trackPoint(t,a),trackPoint(s,b),trackPoint(t,b)];for(let j=0;j<6;j++){vertices.push(p[j].x,height,p[j].z);uv.push(p[j].x/35,p[j].z/35);}}const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geo.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));geo.computeVertexNormals();const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color,roughness:1,side:THREE.DoubleSide}));mesh.receiveShadow=true;group.add(mesh);return mesh;}
 const land=box(group,0,-.4,0,210,.6,145,0x55594c);land.receiveShadow=true;strip(-9,9,0x3c4348,.015);strip(-9,-8.5,0xdfded0,.023);strip(8.5,9,0xdfded0,.023);
 // Curbs, outer concrete barrier and lower inner barrier share the physics boundaries.
 for(let i=0;i<144;i++){const s=(i+.5)/144*LENGTH;for(const lane of [-9,9]){const p=trackPoint(s,lane+.5*Math.sign(lane));const segment=box(group,p.x,.62,p.z,.7,1.25,LENGTH/144*1.08,i%4<2?0xbfc4be:0x48535a,true);segment.rotation.y=p.heading;const curbP=trackPoint(s,lane*.9);const curb=box(group,curbP.x,.07,curbP.z,.7,.1,LENGTH/144*1.03,i%2?0xff6d3b:0xdad8c9);curb.rotation.y=p.heading;}}
 for(let i=0;i<48;i++){const p=trackPoint(i/48*LENGTH,0),dash=box(group,p.x,.032,p.z,.12,.014,2.7,0xbabcb5);dash.rotation.y=p.heading;}
 for(let i=0;i<12;i++){const p=trackPoint(i/12*LENGTH,5.8),shape=new THREE.Shape();shape.moveTo(-.9,-1);shape.lineTo(0,1.1);shape.lineTo(.9,-1);shape.lineTo(0,-.2);shape.closePath();const m=new THREE.Mesh(new THREE.ShapeGeometry(shape),new THREE.MeshBasicMaterial({color:0xffa55f,side:THREE.DoubleSide}));m.rotation.order='YXZ';m.rotation.set(-Math.PI/2,p.heading+Math.PI,0);m.position.set(p.x,.045,p.z);group.add(m);}
 for(let x=-1.4;x<1.5;x+=.7)for(let z=-35.4;z< -18.4;z+=.7)box(group,x,.04,z,.69,.025,.69,(Math.round(x/.7)+Math.round(z/.7))%2?0xe7e5d8:0x161f27);
 for(const z of [-38.5,-15.5])box(group,0,3,z,.4,6,.4,0x89938e,true);box(group,0,6,-27,.6,.5,24,0xff7040,true);const banner=sign('WRECKING RACING',20,2);banner.position.set(-.1,5.1,-27);banner.rotation.y=-Math.PI/2;group.add(banner);
 const infield=sign('IRON LOOP',26,3.8);infield.rotation.x=-Math.PI/2;infield.position.set(0,.04,0);group.add(infield);
 for(const side of [-1,1]){for(let row=0;row<5;row++)box(group,0,1.5+row*1.3,side*(43+row*2.1),102,1.5,2.2,row%2?0x344653:0x475862);for(let i=0;i<60;i++){const x=-49+(i%20)*5.1,row=Math.floor(i/20);box(group,x,3.7+row*1.3,side*(44+row*2.1),.38,.8,.38,[0xc89c73,0x687d8c,0x9ca3a0][i%3]);}const b=sign('BREAK CARS / FULL CONTACT',35,2.4);b.position.set(0,9,side*53);b.rotation.y=side>0?Math.PI:0;group.add(b);}
 for(const x of [-90,90])for(const z of [-46,46]){box(group,x,12,z,.4,24,.4,0x344451);box(group,x,24,z,6,1.6,.8,0xeff1e4);}
 return group;
}
