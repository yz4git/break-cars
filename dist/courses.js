// Course selection is URL-backed: reloading creates one coherent physics/render world.
export const COURSES=[
 {id:'classic',mode:'colosseum',name:'THE COLOSSEUM',hint:'既存のアリーナ'},
 {id:'crater-crown',mode:'colosseum',name:'CRATER CROWN',hint:'中央の王冠丘とリング状の斜面。高所から車体を重ねて押し込め。'},
 {id:'hunt-classic',mode:'wreck-hunt',name:'WRECK HUNT',hint:'既存の連続撃破アリーナ'},
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
 return null;
}
export function courseSurface(x,z){const h=courseHeight(x,z);if(h===null)return null;const e=.06,gx=(courseHeight(x+e,z)-courseHeight(x-e,z))/(2*e),gz=(courseHeight(x,z+e)-courseHeight(x,z-e))/(2*e),n=Math.hypot(gx,1,gz);return{h,n:{x:-gx/n,y:1/n,z:-gz/n}};}
