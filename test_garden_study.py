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
const page=fs.readFileSync('temple-study.html','utf8'),garden=fs.readFileSync('tools/temple_landscape.js','utf8');
const helpers=page.slice(page.indexOf('const clamp  ='),page.indexOf('/* ------------------------------------------------------- 0b'));
function fn(name){return page.match(new RegExp('function '+name+'\\([^\\n]*\\) \\{[\\s\\S]*?\\n\\}'))[0];}
const budgets=[];
for(const LOW of [false,true]){
 const scene=new THREE.Scene();scene.fog=new THREE.FogExp2(0x070e13,.0154);
 const key=new THREE.DirectionalLight(0xffffff,1.22),rim=new THREE.DirectionalLight(0xffffff,.34);scene.add(key,rim);
 const water=new THREE.MeshPhysicalMaterial();water.defines.POND_REFLECTION=1;
 water.onBeforeCompile=sh=>{sh.fragmentShader+='normal=normalize((viewMatrix*vec4(pondN,0.)).xyz);';};
 const WORLD={key,pond:new THREE.Mesh(new THREE.PlaneGeometry(),water),fg:[new THREE.Group()],haze:[],embers:new THREE.Group()};
 const clock={value:0};
 const POST={comp:{uniforms:{uBloom:{value:0}}},bright:{uniforms:{uThr:{value:.86},uKnee:{value:.50}}}};
 const ctx={THREE,scene,WORLD,POST,LOW,WET_TIME:clock,SKY:{moonAzimuth:.2,moonElevation:.305},TEMPLE_STUDY:{landscape:true},aspectFix:()=>.5,tx:()=>new THREE.Texture(),texGlow:()=>null,
 buildMaple(){const t=new THREE.Group();scene.add(t);return t;},buildRocks(){scene.add(new THREE.Mesh(new THREE.SphereGeometry(),new THREE.MeshStandardMaterial()));}};
 vm.createContext(ctx);vm.runInContext(helpers+'\n'+fn('mergeGeos')+'\n'+fn('erodedRockGeo')+'\n'+garden,ctx);
 vm.runInContext(`
 [[71,12.6,-13,1.05],[72,-11.8,-9.4,.95],[73,9.2,-19,.82],[74,-14.5,-17.5,1],[75,16.5,-6,.88]].forEach(a=>rememberStudyMaple(...a));
 rememberStudyRocks();buildLandscapeStudy();`,ctx);
 const g=scene.getObjectByName('complete garden study');assert(g.visible);
 const old=scene.getObjectByName('original garden');assert.equal(old.visible,false);WORLD.fg[0].visible=true;assert.equal(WORLD.fg[0].parent.visible,false);
 let triangles=0,meshes=0;
 g.traverse(o=>{if(!o.isMesh)return;meshes++;
  for(const name of ['position','normal'])for(const n of o.geometry.attributes[name].array)assert(Number.isFinite(n));
  const count=o.isInstancedMesh?o.count:1;triangles+=(o.geometry.index?o.geometry.index.count:o.geometry.attributes.position.count)/3*count;
  if(o.isInstancedMesh)for(const n of o.instanceMatrix.array)assert(Number.isFinite(n));
 });
 assert(triangles<450000,triangles);assert(meshes<40,meshes);budgets.push(triangles);
 assert.equal(WORLD.pond.material.defines.POND_REFLECTION,1);
 const shader={uniforms:{},vertexShader:'',fragmentShader:''};WORLD.pond.material.onBeforeCompile(shader);
 assert.equal(shader.uniforms.uGardenTime,clock);assert(shader.fragmentShader.includes('float calm='));
 const studyWater=WORLD.pond.material;
 assert(POST.comp.uniforms.uBloom.value>0);assert(POST.bright.uniforms.uThr.value<.86);
 ctx.setGardenStudy(false);assert.equal(g.visible,false);assert.equal(WORLD.fg[0].visible,true);assert.equal(WORLD.pond.material,water);assert.equal(key.intensity,1.22);assert.equal(scene.fog.density,.0154);
 assert.equal(POST.comp.uniforms.uBloom.value,0);assert.equal(POST.bright.uniforms.uThr.value,.86);
 ctx.setGardenStudy(true);assert.equal(g.visible,true);assert.equal(WORLD.fg[0].visible,false);assert.equal(WORLD.pond.material,studyWater);assert(key.intensity<1.22);assert.equal(key.shadow.needsUpdate,true);
 // The approach stays open and banks taper below water instead of ending at a vertical edge.
 vm.runInContext(`for(const z of [-7,-1,5,10]){if(gardenGround(0,z)>-.4)throw Error('reflection corridor blocked');}
 for(const b of GARDEN_BANKS){if(gardenBankHeight(b,b[0]+b[2]*1.1,b[1])>-.9)throw Error('bank does not taper');}`,ctx);
}
assert(budgets[1]<budgets[0]*.65,JSON.stringify(budgets));console.log(JSON.stringify({triangles:budgets}));
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
