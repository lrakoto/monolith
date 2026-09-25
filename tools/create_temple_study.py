"""Refresh a study; --production explicitly promotes an approved scene."""
import argparse
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--production",action="store_true",help="also replace the approved live scene")
parser.add_argument("--scene",choices=("temple","redwoods","forest","pond"),default="temple")
args=parser.parse_args()
if args.production and args.scene not in ('temple','redwoods'):
 parser.error('Pond remains a study until approved for production')
kind="forest" if args.scene=="pond" else args.scene
output="pond" if kind=="forest" else kind
label="Pond" if kind=="forest" else kind.title()
root=Path(__file__).resolve().parents[1]
s=(root/('tools/templates/'+kind+'-original.html' if kind in ('temple','redwoods') else kind+'.html')).read_text()
css='''
/* the comparison stays reachable when the portfolio copy is hidden. */
.study-controls{position:fixed;z-index:120;left:20px;bottom:20px;display:flex;align-items:center;gap:10px;padding:10px 14px;background:rgba(8,13,16,.92);border:1px solid rgba(223,231,224,.20);border-radius:16px;color:#dfe7e0;font:12px Onest,sans-serif;backdrop-filter:blur(14px);}
.study-controls strong{font-size:11px;font-weight:500;letter-spacing:.04em;margin-right:4px;}
.study-controls button{font:inherit;color:#c9d3cc;background:none;border:1px solid transparent;border-radius:8px;padding:8px 10px;cursor:pointer;}
.study-controls button[aria-pressed="true"]{background:rgba(223,231,224,.14);color:#fff;}
.study-controls button:focus-visible{outline:2px solid #e94b5a;outline-offset:2px;}
.study-controls button:disabled{opacity:.4;cursor:wait;}
.study-status{font-size:10px;color:#98a59d;max-width:155px;}
.study-modes,.study-views{display:flex;align-items:center;}
@media(max-width:600px){.study-controls{left:10px;right:10px;bottom:66px;padding:7px 10px;display:grid;grid-template-columns:1fr auto;gap:3px;}.study-controls button{padding:7px 8px;}.study-status{max-width:155px;justify-self:end;font-size:9px;}.study-controls strong{font-size:10px;}}
'''
html='''
<aside class="study-controls" aria-label="Garden comparison">
  <strong>Garden study</strong>
  <div class="study-modes">
  <button id="study-original" type="button" aria-pressed="false">Original</button>
  <button id="study-temple" type="button" aria-pressed="false" disabled>Temple</button>
  <button id="study-model" type="button" aria-pressed="true" disabled>Study</button>
  </div>
  <div class="study-views">
  <button id="study-wide" type="button" aria-label="Wide view">Wide</button>
  <button id="study-pond" type="button" aria-label="Pond view">Pond</button>
  <button id="study-close" type="button" aria-label="Close view">Close</button>
  </div>
  <span class="study-status" id="study-status" role="status">Loading detailed model…</span>
</aside>
'''
js='''
/* the three comparisons share the camera and keep the approved architecture
   available beneath the model and the complete garden. */
const TEMPLE_STUDY = { original: [], model: null, active: true, landscape: true };
function setTempleStudy(active, landscape = active) {
  if (active && !TEMPLE_STUDY.model) return;
  TEMPLE_STUDY.active = active;
  TEMPLE_STUDY.landscape = active && landscape;
  setGardenStudy(TEMPLE_STUDY.landscape);
  TEMPLE_STUDY.original.forEach(m => { m.visible = !active; });
  if (TEMPLE_STUDY.model) TEMPLE_STUDY.model.visible = active;
  document.getElementById('study-original')?.setAttribute('aria-pressed', String(!active));
  document.getElementById('study-model')?.setAttribute('aria-pressed', String(active && landscape));
  document.getElementById('study-temple')?.setAttribute('aria-pressed', String(active && !landscape));
  if (document.getElementById('study-status')) document.getElementById('study-status').textContent = active ? (landscape ? 'Full garden · moonlit landscape' : 'Temple model · original garden') : 'Original scene · same camera';
  if (WORLD.key) WORLD.key.shadow.needsUpdate = true;
}
document.getElementById('study-original')?.addEventListener('click', () => setTempleStudy(false));
document.getElementById('study-temple')?.addEventListener('click', () => setTempleStudy(true, false));
document.getElementById('study-model')?.addEventListener('click', () => setTempleStudy(true));
document.getElementById('study-wide')?.addEventListener('click', () => scrollTo({ top: 0, behavior: 'smooth' }));
document.getElementById('study-pond')?.addEventListener('click', () => scrollTo({ top: anchors[1] || 0, behavior: 'smooth' }));
document.getElementById('study-close')?.addEventListener('click', () => scrollTo({ top: document.getElementById('eternity').offsetTop - 40, behavior: 'smooth' }));
async function buildTempleStudy() {
  buildTemple();
  WORLD.temple.traverse(m => { if (m.isMesh && m.material.isMeshStandardMaterial) TEMPLE_STUDY.original.push(m); });
  try {
    const [gltf, bounce] = await Promise.all([
      new THREE.GLTFLoader().loadAsync('assets/temple-study/temple-quality.glb'),
      new THREE.TextureLoader().loadAsync('assets/temple-study/temple-bounce.png')
    ]);
    bounce.flipY = false; bounce.encoding = THREE.LinearEncoding;
    const materials = new Set();
    gltf.scene.traverse(m => {
      if (!m.isMesh) return;
      m.castShadow = true; m.receiveShadow = true;
      m.geometry.setAttribute('uv2', m.geometry.attributes.uv.clone());
      const group = Array.isArray(m.material) ? m.material : [m.material];
      group.forEach(mat => materials.add(mat));
    });
    materials.forEach(mat => {
      mat.lightMap = bounce; mat.lightMapIntensity = .75;
      mat.aoMapIntensity = .65; mat.envMapIntensity = .70;
      if (mat.map) mat.map.anisotropy = Math.min(8, maxAniso);
      if (mat.normalMap) mat.normalMap.anisotropy = Math.min(8, maxAniso);
      applyTempleDepth(mat);
    });
    TEMPLE_STUDY.model = gltf.scene; scene.add(gltf.scene);
    if (document.getElementById('study-model')) document.getElementById('study-model').disabled = false;
    if (document.getElementById('study-temple')) document.getElementById('study-temple').disabled = false;
    setTempleStudy(TEMPLE_STUDY.active);
  } catch (error) {
    setTempleStudy(false);
    if (document.getElementById('study-status')) document.getElementById('study-status').textContent = 'Model unavailable · original shown';
    console.warn('[305 study] Model could not load', error);
  }
}
'''
js = "const GARDEN_KIND = '"+kind+"';\n"+js
js += (root/'tools/temple_landscape.js').read_text()
js += (root/'tools/woodland_studies.js').read_text()
js += (root/'tools/pond_study.js').read_text()
js += (root/'tools/pond_animal.js').read_text()
js += (root/'tools/garden_details.js').read_text()
replacements={
'in a portfolio whose every surface is generated in the browser at load.':'in a live moonlit garden with a detailed timber temple.',
'function pass(mat, target, additive) {\n  POST.quad.material = mat;\n  renderer.setRenderTarget(target || null);\n  if (!additive) renderer.clear(true, false, false);\n  renderer.render(POST.qScene, POST.cam);\n}': 'function pass(mat, target, additive) {\n  POST.quad.material = mat;\n  renderer.setRenderTarget(target || null);\n  /* additive upsampling must retain the sharper bloom already in the target. */\n  const autoClear = renderer.autoClear;\n  renderer.autoClear = false;\n  if (!additive) renderer.clear(true, false, false);\n  renderer.render(POST.qScene, POST.cam);\n  renderer.autoClear = autoClear;\n}',
'uBloom: { value: .34 }': 'uBloom: { value: 0 }',
'POST.up.uniforms.tS.value = L[i - 1].a;': 'POST.up.uniforms.tS.value = L[i - 1].a.texture;',
'POST.blur.uniforms.tS.value = L[i].a;': 'POST.blur.uniforms.tS.value = L[i].a.texture;',
'POST.blur.uniforms.tS.value = L[i].b;': 'POST.blur.uniforms.tS.value = L[i].b.texture;',
'POST.up.uniforms.tS.value = L[i].a;': 'POST.up.uniforms.tS.value = L[i].a.texture;',
'POST.comp.uniforms.tB.value = L[0].a;': 'POST.comp.uniforms.tB.value = L[0].a.texture;',
"function erodedRockGeo(radius, seed) {": "function erodedRockGeo(radius, seed, detail = LOW ? 3 : 6) {",
"  const geo = new THREE.IcosahedronGeometry(radius, LOW ? 3 : 6);": "  const geo = new THREE.IcosahedronGeometry(radius, detail);",
"  if (!PERF.locked && clock > 2.2) {": "  recordGardenFrame(raw);\n  if (!PERF.locked && clock > 2.2) {",
"  const plat = new THREE.Mesh(new THREE.BoxGeometry(42, PODIUM, 24), platMat);": "  WORLD.studyStairMat = platMat;\n  const plat = new THREE.Mesh(new THREE.BoxGeometry(42, PODIUM, 24), platMat);",
"    buildRocks();": "    rememberStudyRocks();",
"    initMirror(); buildPuddles(); initTuning();": "    initMirror(); buildPuddles(); initTuning(); buildLandscapeStudy();",
"      type: LOW ? THREE.UnsignedByteType : THREE.HalfFloatType, depthBuffer: true\n": "      type: LOW ? THREE.UnsignedByteType : THREE.HalfFloatType, depthBuffer: true, stencilBuffer: true\n",
"  POST.scene = new THREE.WebGLRenderTarget(w, h, Object.assign({}, O, { depthBuffer: true, samples: LOW ? 0 : 2 }));": """  /* the detailed facade has closely layered paper and timber. r149's default
     offscreen depth is 16 bit; packed depth/stencil gives the view 24 bit. */
  POST.scene = new THREE.WebGLRenderTarget(w, h, Object.assign({}, O, { depthBuffer: true, stencilBuffer: true, samples: LOW ? 0 : 2 }));""",
'every\n        surface below is generated in the browser at load, with no model files and no images behind\n        the scene.':'this Temple study combines a detailed Blender model and baked lighting with a landscape generated in the browser.',
'<title>Lova Rakoto: Web developer and designer in Los Angeles</title>':'<title>Temple garden study: ThreeOhFive Studios</title>\n<meta name="robots" content="noindex,nofollow">',
'</style>':css+'\n</style>',
'<script src="assets/three.min.js"></script>':html+'\n<script src="assets/three.min.js"></script>\n<script src="assets/temple-study/GLTFLoader.r149.js"></script>',
"  ['Raising the temple', () => buildTemple()],":"  ['Raising the temple', () => buildTempleStudy()],",
'function buildMaple(seed, x, z, scale) {':js+'\nfunction buildMaple(seed, x, z, scale) {',
"fetch('/__tune/temple/save'":"fetch('/__tune/study/save'",
}
if kind=='temple':
 start=s.index("  ['Planting the maples'")
 end=s.index("  ['Painting the near grass'",start)
 s=s[:start]+s[start:end].replace('buildMaple(', 'rememberStudyMaple(')+s[end:]
else:
 title=replacements.pop('<title>Lova Rakoto: Web developer and designer in Los Angeles</title>')
 replacements['<title>'+kind.title()+': Lova Rakoto</title>']=title
 replacements.pop('function buildMaple(seed, x, z, scale) {')
 anchor='function texRedwoodBark() {' if kind=='redwoods' else 'function buildStele(seed, x, z, scale) {'
 replacements[anchor]=js+'\n'+anchor
 replacements.pop("fetch('/__tune/temple/save'")
 replacements["fetch('/__tune/"+kind+"/save'"]="fetch('/__tune/study/save'"
 if kind=='redwoods':
  replacements["  ['Growing the redwood grove', () => buildRedwoods()],"]="  ['Growing the redwood grove', () => rememberStudyGrove()],"
 else:
  replacements.pop('    buildRocks();')
  replacements.pop('function erodedRockGeo(radius, seed) {')
  replacements.pop('  const geo = new THREE.IcosahedronGeometry(radius, LOW ? 3 : 6);')
  import re
  baseline=(root/'tools/templates/temple-original.html').read_text()
  erosion=re.search(r'function erodedRockGeo\(radius, seed\) \{.*?\n\}',baseline,re.S).group()
  erosion=erosion.replace('radius, seed)', 'radius, seed, detail = LOW ? 3 : 6)').replace('radius, LOW ? 3 : 6','radius, detail')
  replacements[anchor]=js+'\n'+erosion+'\n'+anchor
  replacements['    buildPondPlanting();']='    rememberStudyPond();'
  # distant tree cutouts belong to the old Forest comparison, not the water garden.
  a=s.index('  trunkGeos.forEach((list, i) => {')
  b=s.index('  /* floor + podium */',a)
  block=s[a:b]
  assert block.count('    scene.add(m);')==1
  s=s[:a]+block.replace('    scene.add(m);','    scene.add(m); GARDEN.original.push(m);')+s[b:]
  start=s.index("  ['Setting the stones'")
  end=s.index("  ['Painting the near grass'",start)
  s=s[:start]+s[start:end].replace('buildStele(', 'rememberStudyStele(')+s[end:]
for a,b in replacements.items():
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,b)
# the study selector stays inside the three experimental scenes.
for scene in ('temple','redwoods','forest'):
 original='index.html' if scene=='temple' else scene+'.html'
 a='<a href="'+original+'"'
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,'<a href="'+('pond' if scene=='forest' else scene)+'-study.html"')
if kind!='temple':
 s=s.replace('Temple garden study',label+' garden study').replace('this Temple study','this '+label+' study').replace('This Temple study','This '+label+' study')
 s=s.replace('<strong>Garden study</strong>','<strong>'+label+' study</strong>')
s=s.replace('>Forest</a>','>Pond</a>')
(root/(output+'-study.html')).write_text(s)
if kind=='forest':
 (root/'forest-study.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Pond study</title><a href="pond-study.html">Open Pond study</a><script>location.replace('pond-study.html'+location.search+location.hash)</script></html>''')
print('Created '+output+'-study.html; live page unchanged unless --production is supplied.')
if args.production:
 # promotion is explicit so the next study pass cannot silently change the live scene.
 for a,b in {
  css:'',html.replace('<strong>Garden study</strong>','<strong>'+label+' study</strong>') if kind!='temple' else html:'',
  '<title>'+label+' garden study: ThreeOhFive Studios</title>\n<meta name="robots" content="noindex,nofollow">':('<title>Lova Rakoto: Web developer and designer in Los Angeles</title>' if kind=='temple' else '<title>Redwoods: Lova Rakoto</title>'),
  "fetch('/__tune/study/save'":"fetch('/__tune/"+kind+"/save'",
  'this '+label+' study combines':'this scene combines',
  'This '+label+' study combines':'This scene combines',
 }.items():
  assert s.count(a)==1,(a,s.count(a))
  s=s.replace(a,b)
 for scene in ('temple','redwoods','forest'):
  original='index.html' if scene=='temple' else scene+'.html'
  a='<a href="'+('pond' if scene=='forest' else scene)+'-study.html"'
  assert s.count(a)==1,(a,s.count(a))
  s=s.replace(a,'<a href="'+original+'"')
 s=s.replace('>Pond</a>','>Forest</a>')
 # pin the model as well as the page; another Blender bake belongs to the study
 # until the next deliberate promotion, even if both are deployed together.
 assets=('temple-quality.glb','temple-bounce.png','GLTFLoader.r149.js','THREE-LICENSE.txt')
 live_assets='assets/temple' if kind=='temple' else 'assets/redwoods'
 (root/live_assets).mkdir(exist_ok=True)
 for asset in assets:
  (root/live_assets/asset).write_bytes((root/'assets/temple-study'/asset).read_bytes())
 assert s.count('assets/temple-study/')==3
 s=s.replace('assets/temple-study/',live_assets+'/')
 live_page='index.html' if kind=='temple' else kind+'.html'
 (root/live_page).write_text(s)
 print('Promoted the approved study to '+live_page+' without comparison controls.')
