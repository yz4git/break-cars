// Course selection is URL-backed: reloading creates one coherent physics/render world.
export const COURSES=[
 {id:'classic',mode:'colosseum',name:'THE COLOSSEUM',hint:'既存のアリーナ'},
 {id:'crater-crown',mode:'colosseum',name:'CRATER CROWN',hint:'中央の王冠丘とリング状の斜面。高所から車体を重ねて押し込め。'},
 {id:'tidal-foundry',mode:'wreck-hunt',name:'TIDAL FOUNDRY',hint:'波状路面と斜めの土手。浮いた敵の着地に追撃しCHAINをつなげ。'},
 {id:'hunt-classic',mode:'wreck-hunt',name:'WRECK HUNT',hint:'既存の連続撃破アリーナ'},
 {id:'sky-forge',mode:'racing',name:'SKY FORGE',hint:'非対称の立体8字。大ループ、連続うねり、天空交差橋を4周。'},
 {id:'rampage-3d',mode:'racing',name:'RAMPAGE 3D',hint:'既存のBOOST LOOPコース'}
];
const requested=new URLSearchParams(globalThis.location?.search||'').get('course');
export const activeCourse=COURSES.find(c=>c.id===requested)||COURSES[0];
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
export function courseHeight(x,z){
 if(activeCourse.id==='crater-crown'){
  const r=Math.hypot(x,z),a=Math.atan2(z,x);
  const crown=3.8*(1-smooth((r-5)/12));
  const ring=2.4*Math.exp(-(((r-28)/6)**2))*(0.78+.22*Math.cos(a*4));
  return crown+ring;
 }
 if(activeCourse.id==='tidal-foundry'){
  const edge=1-smooth((Math.hypot(x,z)-30)/10);
  const waves=(.5+.5*Math.cos(z*.43))*1.8*Math.exp(-(((x+13)/10)**2));
  const diagonal=2.8*Math.exp(-(((z-x*.55-5)/6)**2))*(1-smooth((Math.abs(x)-20)/12));
  const east=1.6*Math.exp(-(((x-20)/7)**2))*(.6+.4*Math.cos(z*.28));
  return edge*(waves+diagonal+east);
 }
 return null;
}
export function courseSurface(x,z){const h=courseHeight(x,z);if(h===null)return null;const e=.06,gx=(courseHeight(x+e,z)-courseHeight(x-e,z))/(2*e),gz=(courseHeight(x,z+e)-courseHeight(x,z-e))/(2*e),n=Math.hypot(gx,1,gz);return{h,n:{x:-gx/n,y:1/n,z:-gz/n}};}
