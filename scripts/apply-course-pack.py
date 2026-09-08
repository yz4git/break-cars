"""Integrate selectable courses after the existing physics/tuning pipeline."""
from pathlib import Path

def apply_course_pack(target):
 p=target/'physics3d.js';s=p.read_text();s="import {courseSurface} from './courses.js';\n"+s
 s=s.replace('function baseHeight(x,z) {','function baseHeight(x,z) {\n  const custom=courseSurface(x,z);if(custom)return custom;')
 s=s.replace('const ramp=rampSurface(x,z);','const ramp=courseSurface(x,z)?null:rampSurface(x,z);').replace('const loop=loopSurface(x,y,z);','const loop=courseSurface(x,z)?null:loopSurface(x,y,z);');p.write_text(s)
 p=target/'game.js';s=p.read_text();s="import {COURSES,activeCourse,courseHeight} from './courses.js';\nimport {buildCourseTerrain} from './course-view.js';\n"+s
 s=s.replace('const fullPhysicsSpec=fullPhysicsFeatureSpec();','const customTerrain=buildCourseTerrain();arena.add(customTerrain);\nconst fullPhysicsSpec=fullPhysicsFeatureSpec();')
 # The legacy arena stunt group contains its own closed torus loop.  Never let
 # that decorative/physics course coexist with a racing course: the race ribbon
 # itself is the only loop geometry in racing mode.
 s=s.replace("let world=makeWorld()", "fullPhysicsCourse.visible=activeCourse.mode!=='racing'&&courseHeight(0,0)===null;\nlet world=makeWorld()")
 s=s.replace("arena.visible=gameMode==='colosseum';raceTrack.visible=gameMode==='racing';", "arena.visible=gameMode==='colosseum';fullPhysicsCourse.visible=gameMode!=='racing'&&activeCourse.mode!=='racing'&&courseHeight(0,0)===null;raceTrack.visible=gameMode==='racing';")
 # Mode buttons choose the default of that mode when leaving a selected custom course.
 s=s.replace("function selectMode(next){if(mode!=='menu')return;", "function selectMode(next){if(mode!=='menu')return;if(next!==activeCourse.mode){location.search='?course='+COURSES.find(c=>c.mode===next).id;return;}")
 marker="for(const b of document.querySelectorAll('[data-mode]'))b.onclick=()=>selectMode(b.dataset.mode);"
 assert marker in s
 s=s.replace(marker,marker+"\nconst coursePicker=document.createElement('select');coursePicker.id='course-picker';coursePicker.setAttribute('aria-label','コース選択');for(const c of COURSES.filter(c=>c.mode===activeCourse.mode)){const o=document.createElement('option');o.value=c.id;o.textContent=c.name;coursePicker.appendChild(o);}coursePicker.value=activeCourse.id;coursePicker.onchange=()=>{location.search='?course='+encodeURIComponent(coursePicker.value);};document.querySelector('.mode-select').after(coursePicker);\n")
 s=s.replace("inArenaLoop=gameMode!=='racing'&&","inArenaLoop=courseHeight(0,0)===null&&gameMode!=='racing'&&")
 s += "\nselectMode(activeCourse.mode);$('mode-tag').textContent=activeCourse.name+' / '+activeCourse.mode.toUpperCase();$('arena-caption').textContent=activeCourse.name;const courseHint=document.createElement('p');courseHint.className='course-hint';courseHint.textContent=activeCourse.hint;coursePicker.after(courseHint);\n"
 p.write_text(s)
 p=target/'index.html';s=p.read_text().replace('</head>','<link rel=\"stylesheet\" href=\"courses.css\"></head>');p.write_text(s)

 # An asymmetric elevated ribbon retains the existing branch-aware projection and lap gates.
 p=target/'racing3d.js';s=p.read_text();s="import {activeCourse} from './courses.js';\nconst skyForge=activeCourse.id==='sky-forge';\n"+s
 s=s.replace("loopRadius:6.8", "loopRadius:skyForge?7.5:6.8")
 s=s.replace("const x=62*Math.sin(t),z=40*Math.sin(t)*Math.cos(t);", "const x=(skyForge?70:62)*Math.sin(t)+(skyForge?7*Math.sin(2*t):0),z=(skyForge?47:40)*Math.sin(t)*Math.cos(t);")
 s=s.replace("let y=7.4*gauss(t,Math.PI,.28)+2.4*gauss(t,1.82,.48)+1.6*gauss(t,4.02,.55);", "let y=(skyForge?10.5:7.4)*gauss(t,Math.PI,skyForge?.36:.28)+2.4*gauss(t,1.82,.48)+1.6*gauss(t,4.02,.55);if(skyForge)y+=1.3*gauss(t,1.55,.14)+1.7*gauss(t,2.05,.15)+1.3*gauss(t,2.50,.15);")
 s=s.replace("clamp(.34*Math.sin(2*t),-.36,.36)", "clamp((skyForge?.43:.34)*Math.sin(2*t),-.44,.44)")
 p.write_text(s)
 p=target/'track-view.js';s=p.read_text();s="import {activeCourse} from './courses.js';\n"+s;s=s.replace("sign('RAMPAGE 3D',22,2.2)","sign(activeCourse.mode==='racing'?activeCourse.name:'RAMPAGE 3D',22,2.2)");s=s.replace("0xff7042","(activeCourse.id==='sky-forge'?0x72d8d3:0xff7042)");p.write_text(s)
