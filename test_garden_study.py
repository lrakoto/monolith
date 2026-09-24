"""Exercise the complete garden with the actual geometry builders, without a GPU."""
import shutil
import subprocess
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent

class GardenStudyTests(unittest.TestCase):
    @unittest.skipIf(shutil.which('node') is None, 'node unavailable')
    def test_geometry_budget_water_and_reversible_scene_modes(self):
        code=r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),THREE=require('./assets/three.min.js');
const page=fs.readFileSync('temple-study.html','utf8'),garden=fs.readFileSync('tools/temple_landscape.js','utf8')+'\n'+fs.readFileSync('tools/woodland_studies.js','utf8')+'\n'+fs.readFileSync('tools/pond_study.js','utf8')+'\n'+fs.readFileSync('tools/garden_details.js','utf8')+'\n'+fs.readFileSync('tools/pond_animal.js','utf8');
const redwoods=fs.readFileSync('redwoods.html','utf8');
const native= ['redwoodTrunkGeo','redwoodSprayGeo'].map(name=>redwoods.match(new RegExp('function '+name+'\\([^\\n]*\\) \\{[\\s\\S]*?\\n\\}'))[0]).join('\n');
const helpers=page.slice(page.indexOf('const clamp  ='),page.indexOf('/* ------------------------------------------------------- 0b'));
function fn(name){return page.match(new RegExp('function '+name+'\\([^\\n]*\\) \\{[\\s\\S]*?\\n\\}'))[0];}
const budgets=[];
for(const kind of ['temple','redwoods','forest'])for(const LOW of [false,true]){
 const scene=new THREE.Scene();scene.fog=new THREE.FogExp2(0x070e13,.0154);
 const key=new THREE.DirectionalLight(0xffffff,1.22),rim=new THREE.DirectionalLight(0xffffff,.34);scene.add(key,rim);
 const water=new THREE.MeshPhysicalMaterial();water.defines.POND_REFLECTION=1;
 water.onBeforeCompile=sh=>{sh.fragmentShader+='normal=normalize((viewMatrix*vec4(pondN,0.)).xyz);';};
 const WORLD={key,pond:new THREE.Mesh(new THREE.PlaneGeometry(),water),fg:[new THREE.Group()],haze:[],embers:new THREE.Group()};
 WORLD.fg[0].name='rockNear';
 for(const name of ['grassFar','grassMid','grassNear']){const grass=new THREE.Group();grass.name=name;WORLD.fg.push(grass);scene.add(grass);}
 const stone=new THREE.MeshStandardMaterial({roughness:.44});
 const stair=new THREE.Mesh(new THREE.BoxGeometry(),stone);scene.add(stair);WORLD.studyStairMat=stone;
 const gateMat=new THREE.MeshStandardMaterial({roughness:.87});
 const gate=new THREE.Mesh(new THREE.BoxGeometry(),gateMat);WORLD.torii=new THREE.Group();WORLD.torii.add(gate);scene.add(WORLD.torii);
 const clock={value:0};
 const POST={comp:{uniforms:{uBloom:{value:0}}},bright:{uniforms:{uThr:{value:.86},uKnee:{value:.50}}}};
 const ctx={THREE,scene,WORLD,POST,LOW,GARDEN_KIND:kind,PODIUM:7,lib:()=>({}),texRedwoodBark:()=>({}),surface:()=>new THREE.MeshStandardMaterial(),WET_TIME:clock,SKY:{moonAzimuth:.2,moonElevation:.305},TEMPLE_STUDY:{landscape:true},aspectFix:()=>.5,tx:()=>new THREE.Texture(),texGlow:()=>null,
 buildMaple(){const t=new THREE.Group();scene.add(t);return t;},buildRocks(){scene.add(new THREE.Mesh(new THREE.SphereGeometry(),new THREE.MeshStandardMaterial()));}};
 vm.createContext(ctx);vm.runInContext(helpers+'\n'+fn('mergeGeos')+'\n'+fn('erodedRockGeo')+'\n'+native+'\n'+garden,ctx);
 vm.runInContext(`
 [[71,12.6,-13,1.05],[72,-11.8,-9.4,.95],[73,9.2,-19,.82],[74,-14.5,-17.5,1],[75,16.5,-6,.88]].forEach(a=>rememberStudyMaple(...a));
 rememberStudyRocks();buildLandscapeStudy();`,ctx);
 const g=scene.getObjectByName('complete garden study');assert(g.visible);
 if(kind==='forest'){assert(g.getObjectByName('pond deer'));for(let t=0;t<120;t+=.05){clock.value=t;ctx.updatePondAnimal();}const deer=g.getObjectByName('pond deer');assert(Number.isFinite(deer.position.x));assert(deer.position.y>.06);assert(deer.position.x>-15 && deer.position.x<-10);
 ctx.camera=new THREE.PerspectiveCamera(48,1.7,.1,200);ctx.camera.position.set(-6,4,10);ctx.camera.lookAt(-12.8,1,-11);ctx.camera.updateMatrixWorld();ctx.RIG={pointer:1,tmx:.1,tmy:-.15};ctx.COARSE=false;
 for(let t=120;t<150;t+=.05){clock.value=t;ctx.updatePondAnimal();}
 assert(deer.position.y>.06);assert(deer.position.x>-15 && deer.position.x<-10);
 const held=deer.position.clone();ctx.updatePondAnimal();assert(deer.position.equals(held));
 }
 assert.notEqual(stair.material,stone);
 if(kind==='temple')assert.notEqual(gate.material,gateMat);else assert.equal(gate.material,gateMat);
 if(kind==='forest'){assert(g.getObjectByName('quiet water lilies').count<=7);assert(g.getObjectByName('shoreline pebble transition').count>0);}
 if(kind==='forest'){assert(!g.getObjectByName('pond terrace tree'));assert(!g.getObjectByName('pond backdrop tree'));assert(g.getObjectByName('pond bank shrub branches'));const trees=g.children.filter(o=>o.name==='woodland tree');assert.equal(trees.length,5);assert.equal(g.children.filter(o=>o.name==='distant woodland tree').length,4);assert.deepEqual(trees.map(o=>o.position.x),[-12.6,11.8,-9.2,14.5,-16.5]);assert(g.getObjectByName('emergent pond reeds').count>0);const pads=g.getObjectByName('pond lily pads');assert(pads.count>0);for(let i=0;i<pads.count;i++){const m=new THREE.Matrix4();pads.getMatrixAt(i,m);assert(Math.abs(m.elements[12])>=6.2);}}
 if(kind==='redwoods')assert(g.getObjectByName('detailed redwood grove'));
 const canopy=g.getObjectByName(kind==='redwoods'?'redwood-needle-sprays':(kind==='forest'?'pond shrub leaves':'garden maple'));
 const leafMaterial=kind!=='temple'?canopy.material:canopy.children.find(o=>o.isInstancedMesh).material;
 const leafShader={uniforms:{},vertexShader:'#include <begin_vertex>\n#include <project_vertex>',fragmentShader:'#include <color_fragment>'};
 leafMaterial.onBeforeCompile(leafShader);
 assert.equal(leafShader.uniforms[kind==='redwoods'?'uBreeze':'uGardenTime'],clock);assert.equal(leafShader.uniforms.uGardenSway,clock);

 const old=scene.getObjectByName('original garden');assert.equal(old.visible,false);WORLD.fg[0].visible=true;assert.equal(WORLD.fg[0].parent.visible,false);
 let triangles=0,meshes=0;
 g.traverse(o=>{if(!o.isMesh)return;meshes++;
  for(const name of ['position','normal'])for(const n of o.geometry.attributes[name].array)assert(Number.isFinite(n));
  const count=o.isInstancedMesh?o.count:1;triangles+=(o.geometry.index?o.geometry.index.count:o.geometry.attributes.position.count)/3*count;
  if(o.isInstancedMesh)for(const n of o.instanceMatrix.array)assert(Number.isFinite(n));
 });
 assert(triangles<500000,kind+triangles);assert(meshes<(kind==='forest'?76:48),kind+meshes);budgets.push(triangles);
 assert.equal(WORLD.pond.material.defines.POND_REFLECTION,1);
 const shader={uniforms:{},vertexShader:'',fragmentShader:''};WORLD.pond.material.onBeforeCompile(shader);
 assert.equal(shader.uniforms.uGardenTime,clock);assert(shader.fragmentShader.includes('float calm='));
 const assertGrass=()=>WORLD.fg.slice(1).forEach(grass=>{assert.equal(grass.parent,scene);assert.equal(grass.visible,true);});assertGrass();
 const studyWater=WORLD.pond.material;
 assert(POST.comp.uniforms.uBloom.value>0);assert(POST.bright.uniforms.uThr.value<.86);
 ctx.setGardenStudy(false);assertGrass();assert.equal(gate.material,gateMat);assert.equal(stair.material,stone);assert.equal(g.visible,false);assert.equal(WORLD.fg[0].visible,true);assert.equal(WORLD.pond.material,water);assert.equal(key.intensity,1.22);assert.equal(scene.fog.density,.0154);
 assert.equal(POST.comp.uniforms.uBloom.value,0);assert.equal(POST.bright.uniforms.uThr.value,.86);
 ctx.setGardenStudy(true);assertGrass();assert.equal(g.visible,true);assert.equal(WORLD.fg[0].visible,false);assert.equal(WORLD.pond.material,studyWater);assert(key.intensity<1.22);assert.equal(key.shadow.needsUpdate,true);
 // The approach stays open and banks taper below water instead of ending at a vertical edge.
 vm.runInContext(`for(const z of [-7,-1,5,10]){if(gardenGround(0,z)>-.4)throw Error('reflection corridor blocked');}
 for(const b of GARDEN_BANKS){if(gardenBankHeight(b,b[0]+b[2]*1.1,b[1])>-.9)throw Error('bank does not taper');}`,ctx);
}
for(let i=0;i<budgets.length;i+=2)assert(budgets[i+1]<budgets[i]*.65,JSON.stringify(budgets));console.log(JSON.stringify({triangles:budgets}));
"""
        result=subprocess.run(['node','-e',code],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)

    @unittest.skipIf(shutil.which('node') is None, 'node unavailable')
    def test_bloom_chain_binds_textures_at_every_pass(self):
        code=r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),THREE=require('./assets/three.min.js');
const source=fs.readFileSync('temple-study.html','utf8');
const code=source.match(/function pass\(mat, target, additive\) \{[\s\S]*?\n\}/)[0]+'\n'+source.match(/function renderPost\(\) \{[\s\S]*?\n\}/)[0];
const mat=(...keys)=>({uniforms:Object.fromEntries(keys.map(k=>[k,{value:k==='uDir'?new THREE.Vector2():null}]))});
const POST={scene:new THREE.WebGLRenderTarget(32,32),levels:Array.from({length:4},(_,i)=>({a:new THREE.WebGLRenderTarget(16>>i,16>>i),b:new THREE.WebGLRenderTarget(16>>i,16>>i),w:16>>i,h:16>>i})),bright:mat('tS'),blur:mat('tS','uDir'),up:mat('tS','uAmt'),comp:mat('tS','tB')};
let passes=0,clears=0;POST.quad={};
const renderer={autoClear:true,setRenderTarget(){},clear(){clears++;},render(){
 assert.equal(this.autoClear,false,'do not clear accumulated bloom');const m=POST.quad.material;
 for(const key of ['tS','tB'])if(m.uniforms[key])assert.equal(m.uniforms[key].value.isTexture,true,key+' must sample a Texture');passes++;
}};
const ctx={THREE,POST,renderer};
vm.createContext(ctx);vm.runInContext(code+'\nrenderPost();',ctx);assert.equal(passes,16);assert.equal(clears,13);assert.equal(renderer.autoClear,true);
"""
        result=subprocess.run(['node','-e',code],cwd=ROOT,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()
