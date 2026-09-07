import * as THREE from './three.module.min.js';
import {activeCourse,courseHeight} from './courses.js';
export function buildCourseTerrain(){
 const group=new THREE.Group();if(courseHeight(0,0)===null)return group;
 const n=112,size=87,verts=[],colors=[],indices=[];
 for(let j=0;j<=n;j++)for(let i=0;i<=n;i++){const x=(i/n-.5)*size,z=(j/n-.5)*size,y=courseHeight(x,z);verts.push(x,y+.015,z);const stripe=Math.floor((activeCourse.id==='crater-crown'?Math.hypot(x,z):z+45)/3)%2,c=new THREE.Color(activeCourse.id==='crater-crown'?(stripe?0x807461:0x696457):(stripe?0x55767b:0x344f59));c.multiplyScalar(.8+y*.07);colors.push(c.r,c.g,c.b);}
 for(let j=0;j<n;j++)for(let i=0;i<n;i++){if(Math.hypot(((i+.5)/n-.5)*size,((j+.5)/n-.5)*size)>42.5)continue;const a=j*(n+1)+i,b=a+1,c=a+n+1,d=c+1;indices.push(a,c,b,b,c,d);}
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));geometry.setIndex(indices);geometry.computeVertexNormals();const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.95}));mesh.receiveShadow=true;group.add(mesh);return group;
}
