// Course selection is URL-backed: reloading creates one coherent physics/render world.
export const COURSES=[
 {id:'maelstrom-pit',mode:'colosseum',name:'MAELSTROM PIT',hint:'広い中央ピットと低く長いうねり。全方向から中央へ戻れ、速度を乗せて縁から飛び込める。'},
 {id:'classic',mode:'colosseum',name:'THE COLOSSEUM',hint:'既存のアリーナ'},
 {id:'crater-crown',mode:'colosseum',name:'CRATER CROWN',hint:'中央の王冠丘とリング状の斜面。高所から車体を重ねて押し込め。'},
 {id:'cross-fire',mode:'wreck-hunt',name:'CROSS FIRE',hint:'四方向のワイドランプが中央で交差。壁ではなく走り切れる起伏で空中交差と着地狩りを狙え。'},
 {id:'tidal-foundry',mode:'wreck-hunt',name:'TIDAL FOUNDRY',hint:'波状路面と斜めの土手。浮いた敵の着地に追撃しCHAINをつなげ。'},
 {id:'hunt-classic',mode:'wreck-hunt',name:'WRECK HUNT',hint:'既存の連続撃破アリーナ'},
 {id:'double-orbit',mode:'racing',name:'DOUBLE ORBIT',hint:'2連垂直ループ、約40度バンク、14m高架。空と地面が入れ替わる4周。'},
 {id:'sky-forge',mode:'racing',name:'SKY FORGE',hint:'非対称の立体8字。大ループ、連続うねり、天空交差橋を4周。'},
 {id:'rampage-3d',mode:'racing',name:'RAMPAGE 3D',hint:'既存のBOOST LOOPコース'}
];
const requested=new URLSearchParams(globalThis.location?.search||'').get('course');
export const activeCourse=COURSES.find(c=>c.id===requested)||COURSES.find(c=>c.id==='classic');
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
export function courseHeight(x,z){
 if(activeCourse.id==='maelstrom-pit'){
  // Rebuilt for actual combat: the old 8m closed rim put the spawn ring on
  // 24-32 degree slopes and forced every AI path through a 40+ degree wall.
  // This version keeps the visual pit/maelstrom identity but guarantees broad,
  // continuous approaches to the central fighting area from every spawn angle.
  const r=Math.hypot(x,z),a=Math.atan2(z,x);
  const bowl=1.8*smooth((r-10)/24);
  const rimCenter=21+1.2*Math.sin(3*a);
  const rim=2.0*Math.exp(-(((r-rimCenter)/10.5)**2))*(.84+.16*Math.cos(2*a)**2);
  const center=.35*(1-smooth((r-5)/8));
  return (bowl+rim+center)*(1-smooth((r-39)/4));
 }
 if(activeCourse.id==='crater-crown'){
  const r=Math.hypot(x,z),a=Math.atan2(z,x);
  const crown=3.8*(1-smooth((r-5)/12));
  const ring=2.4*Math.exp(-(((r-28)/6)**2))*(0.78+.22*Math.cos(a*4));
  return crown+ring;
 }
 if(activeCourse.id==='cross-fire'){
  // Rebuilt for WRECK HUNT: the original 7.2m kickers contained 60+ degree
  // faces. Four lower, wider ramps now create jumps without becoming walls;
  // hypot() blends the crossing so diagonal approaches have no hard seam.
  const r=Math.hypot(x,z),edge=1-smooth((r-37)/5);
  const arm=(along,across)=>{
   const d=Math.abs(along),rise=smooth((d-4.5)/10),fall=1-smooth((d-18)/15),lane=1-smooth((Math.abs(across)-5)/9);
   return 2.75*rise*fall*lane;
  };
  const ax=arm(x,z),az=arm(z,x),kick=.82*Math.hypot(ax,az);
  const center=.25*Math.exp(-((r/11)**2));
  return edge*(kick+center);
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
