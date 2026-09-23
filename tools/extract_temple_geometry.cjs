/* keep the study's footprint tied to the approved scene, not a second set of measurements. */
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..'),THREE=require(path.join(root,'assets/three.min.js'));
const src=fs.readFileSync(path.join(root,'index.html'),'utf8');
function fn(name){const m=src.match(new RegExp('function '+name+'\\([^\\n]*\\) \\{[\\s\\S]*?\\n\\}'));if(!m)throw Error(name);return m[0];}
const WORLD={},scene=new THREE.Scene();
const texture=()=>new THREE.Texture();
const ctx={THREE,WORLD,scene,PODIUM:7,TEMPLE_Z:-44,TUNE:{slotBright:.85},SLOT_RGB:[1,.82,.60],
 wallWood:()=>({tag:'timber'}),postWood:()=>({tag:'post'}),texRoof:()=>({tag:'roof'}),texTemplePlaque:()=>({tag:'plaque'}),
 texWindowPaper:texture,texShoji:texture,texGlow:texture,tx:texture,lib:(k,f)=>f(),hdr:(r,g,b)=>new THREE.Color(r,g,b),
 smooth:(a,b,x)=>{let t=Math.min(1,Math.max(0,(x-a)/(b-a)));return t*t*(3-2*t)},weatherRoofEdges:g=>g,applyTempleDepth:()=>{},
 surface:(t,rep,o)=>{const m=new THREE.MeshStandardMaterial({color:o.color,roughness:o.roughness,metalness:o.metalness});m.name=t.tag;return m;}};
vm.runInNewContext(['mergeGeos','roofGeo','buildTemple'].map(fn).join('\n')+'\nbuildTemple();',ctx);
WORLD.temple.updateMatrixWorld(true);
const meshes=[];
WORLD.temple.traverse(m=>{if(!m.isMesh||!m.material.isMeshStandardMaterial)return;
 const g=m.geometry.clone().applyMatrix4(m.matrixWorld);meshes.push({name:m.material.name||'brass',
 positions:Array.from(g.attributes.position.array),indices:Array.from(g.index.array),uv:Array.from(g.attributes.uv.array)});});
const output=path.join(root,'artifacts/temple-study/source-geometry.json');
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,JSON.stringify({coordinateSystem:'three-y-up-world',meshes}));
console.log(`${meshes.length} meshes → ${output}`);
