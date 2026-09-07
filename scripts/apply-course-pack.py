"""Integrate selectable courses after the existing physics/tuning pipeline."""
from pathlib import Path

def apply_course_pack(target):
 p=target/'physics3d.js';s=p.read_text();s="import {courseSurface} from './courses.js';\n"+s
 s=s.replace('function baseHeight(x,z) {','function baseHeight(x,z) {\n  const custom=courseSurface(x,z);if(custom)return custom;')
 s=s.replace('const ramp=rampSurface(x,z);','const ramp=courseSurface(x,z)?null:rampSurface(x,z);').replace('const loop=loopSurface(x,y,z);','const loop=courseSurface(x,z)?null:loopSurface(x,y,z);');p.write_text(s)
 p=target/'game.js';s=p.read_text();s="import {COURSES,activeCourse,courseHeight} from './courses.js';\nimport {buildCourseTerrain} from './course-view.js';\n"+s
 s=s.replace('const fullPhysicsSpec=fullPhysicsFeatureSpec();','const customTerrain=buildCourseTerrain();arena.add(customTerrain);\nconst fullPhysicsSpec=fullPhysicsFeatureSpec();')
 s=s.replace("let world=makeWorld()", "fullPhysicsCourse.visible=courseHeight(0,0)===null;\nlet world=makeWorld()")
 # Mode buttons choose the default of that mode when leaving a selected custom course.
 s=s.replace("function selectMode(next){if(mode!=='menu')return;", "function selectMode(next){if(mode!=='menu')return;if(next!==activeCourse.mode){location.search='?course='+COURSES.find(c=>c.mode===next).id;return;}")
 marker="for(const b of document.querySelectorAll('[data-mode]'))b.onclick=()=>selectMode(b.dataset.mode);"
 assert marker in s
 s=s.replace(marker,marker+"\nconst coursePicker=document.createElement('select');coursePicker.id='course-picker';coursePicker.setAttribute('aria-label','コース選択');for(const c of COURSES.filter(c=>c.mode===activeCourse.mode)){const o=document.createElement('option');o.value=c.id;o.textContent=c.name;coursePicker.appendChild(o);}coursePicker.value=activeCourse.id;coursePicker.onchange=()=>{location.search='?course='+encodeURIComponent(coursePicker.value);};document.querySelector('.mode-select').after(coursePicker);\n")
 s += "\nselectMode(activeCourse.mode);$('mode-tag').textContent=activeCourse.name+' / '+activeCourse.mode.toUpperCase();$('arena-caption').textContent=activeCourse.name;const courseHint=document.createElement('p');courseHint.className='course-hint';courseHint.textContent=activeCourse.hint;coursePicker.after(courseHint);\n"
 p.write_text(s)
 p=target/'index.html';s=p.read_text().replace('</head>','<link rel="stylesheet" href="courses.css"></head>');p.write_text(s)
