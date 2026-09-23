"""Refresh the isolated comparison page from the approved Temple scene."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'index.html').read_text()
css='''
/* the comparison stays reachable when the portfolio copy is hidden. */
.study-controls{position:fixed;z-index:120;left:20px;bottom:20px;display:flex;align-items:center;gap:10px;padding:10px 14px;background:rgba(8,13,16,.92);border:1px solid rgba(223,231,224,.20);border-radius:16px;color:#dfe7e0;font:12px Onest,sans-serif;backdrop-filter:blur(14px);}
.study-controls strong{font-size:11px;font-weight:500;letter-spacing:.04em;margin-right:4px;}
.study-controls button{font:inherit;color:#c9d3cc;background:none;border:1px solid transparent;border-radius:8px;padding:8px 10px;cursor:pointer;}
.study-controls button[aria-pressed="true"]{background:rgba(223,231,224,.14);color:#fff;}
.study-controls button:focus-visible{outline:2px solid #e94b5a;outline-offset:2px;}
.study-controls button:disabled{opacity:.4;cursor:wait;}
.study-status{font-size:10px;color:#98a59d;max-width:155px;}
@media(max-width:600px){.study-controls{left:10px;right:10px;bottom:66px;padding:7px 10px;gap:2px;flex-wrap:wrap;}.study-status{flex-basis:100%;max-width:none;}.study-controls strong{margin-right:auto;}}
'''
html='''
<aside class="study-controls" aria-label="Temple comparison">
  <strong>Temple study</strong>
  <button id="study-original" type="button" aria-pressed="false">Original</button>
  <button id="study-model" type="button" aria-pressed="true" disabled>Study</button>
  <button id="study-wide" type="button" aria-label="Wide view">Wide</button>
  <button id="study-close" type="button" aria-label="Close view">Close</button>
  <span class="study-status" id="study-status" role="status">Loading detailed model…</span>
</aside>
'''
js='''
/* only the opaque hall changes. its paper, halo and mist keep their approved
   materials so the comparison shares the same weather, camera and exposure. */
const TEMPLE_STUDY = { original: [], model: null, active: true };
function setTempleStudy(active) {
  if (active && !TEMPLE_STUDY.model) return;
  TEMPLE_STUDY.active = active;
  TEMPLE_STUDY.original.forEach(m => { m.visible = !active; });
  if (TEMPLE_STUDY.model) TEMPLE_STUDY.model.visible = active;
  document.getElementById('study-original').setAttribute('aria-pressed', String(!active));
  document.getElementById('study-model').setAttribute('aria-pressed', String(active));
  document.getElementById('study-status').textContent = active ? 'Detailed model · baked lighting' : 'Original model · same camera';
  if (WORLD.key) WORLD.key.shadow.needsUpdate = true;
}
document.getElementById('study-original').addEventListener('click', () => setTempleStudy(false));
document.getElementById('study-model').addEventListener('click', () => setTempleStudy(true));
document.getElementById('study-wide').addEventListener('click', () => scrollTo({ top: 0, behavior: 'smooth' }));
document.getElementById('study-close').addEventListener('click', () => scrollTo({ top: document.getElementById('eternity').offsetTop - 40, behavior: 'smooth' }));
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
    document.getElementById('study-model').disabled = false;
    setTempleStudy(TEMPLE_STUDY.active);
  } catch (error) {
    setTempleStudy(false);
    document.getElementById('study-status').textContent = 'Model unavailable · original shown';
    console.warn('[305 study] Model could not load', error);
  }
}
'''
replacements={
"      type: LOW ? THREE.UnsignedByteType : THREE.HalfFloatType, depthBuffer: true\n": "      type: LOW ? THREE.UnsignedByteType : THREE.HalfFloatType, depthBuffer: true, stencilBuffer: true\n",
"  POST.scene = new THREE.WebGLRenderTarget(w, h, Object.assign({}, O, { depthBuffer: true, samples: LOW ? 0 : 2 }));": """  /* the detailed facade has closely layered paper and timber. r149's default
     offscreen depth is 16 bit; packed depth/stencil gives the view 24 bit. */
  POST.scene = new THREE.WebGLRenderTarget(w, h, Object.assign({}, O, { depthBuffer: true, stencilBuffer: true, samples: LOW ? 0 : 2 }));""",
'every\n        surface below is generated in the browser at load, with no model files and no images behind\n        the scene.':'this Temple study combines a detailed Blender model and baked lighting with a landscape generated in the browser.',
'Every surface in the\n        scene backdrop on this page is generated in browser at load.':'This Temple study combines a detailed Blender model with a live browser landscape.',
'<title>Lova Rakoto — Web developer and designer in Los Angeles</title>':'<title>Temple quality study — ThreeOhFive Studios</title>\n<meta name="robots" content="noindex,nofollow">',
'</style>':css+'\n</style>',
'<script src="assets/three.min.js"></script>':html+'\n<script src="assets/three.min.js"></script>\n<script src="assets/temple-study/GLTFLoader.r149.js"></script>',
"  ['Raising the temple', () => buildTemple()],":"  ['Raising the temple', () => buildTempleStudy()],",
'function buildMaple(seed, x, z, scale) {':js+'\nfunction buildMaple(seed, x, z, scale) {',
"fetch('/__tune/temple/save'":"fetch('/__tune/study/save'",
}
for a,b in replacements.items():
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,b)
(root/'temple-study.html').write_text(s)
print('Created temple-study.html; original page untouched.')
