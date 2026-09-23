"""Structural checks on index.html — the page has no runtime tests, and every
failure it can have here is silent: a syntax error in the inline script leaves
the preloader spinning, and a tuning key that exists in one of its three homes
but not the others just quietly does nothing."""
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

INDEX = Path(__file__).resolve().parent / "index.html"
SOURCE = INDEX.read_text(encoding="utf-8")

SCRIPT_RE = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S)
TUNE_RE = re.compile(r"const TUNE = \{(.*?)\n\};", re.S)
SCHEMA_RE = re.compile(r"const TUNE_SCHEMA = \[(.*?)\n\];", re.S)
HANDLERS_RE = re.compile(r"buildTunePanel\(\{(.*?)\n  \}\);", re.S)
SRC_RE = re.compile(r"const WORK_SRC\s+= \{(.*?)\};", re.S)
INFO_RE = re.compile(r"const WORK_INFO = \{(.*?)\n\};", re.S)
PLATES_RE = re.compile(r"const CARD_PLATES = \[(.*?)\];", re.S)

# published to the domain root from main, so it is simply absent on a branch
LLMS = INDEX.parent / "root" / "llms.txt"


def inline_script(source=SOURCE):
    bodies = SCRIPT_RE.findall(source)
    assert bodies, "index.html has no inline <script>"
    return bodies[-1]


class InlineScriptTests(unittest.TestCase):
    @unittest.skipIf(shutil.which("node") is None, "node is not installed")
    def test_inline_script_parses(self):
        for page in (INDEX, INDEX.with_name("redwoods.html"), INDEX.with_name("forest.html"), INDEX.with_name("temple.html"), INDEX.with_name("monolith.html")):
            with self.subTest(page=page.name), tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as staged:
                staged.write(inline_script(page.read_text()))
                staged.flush()
                result = subprocess.run(["node", "--check", staged.name],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)


class SceneRoutingTests(unittest.TestCase):
    def test_temple_is_home_and_first_scene(self):
        for page, current in ((INDEX, "Temple"), (INDEX.with_name("redwoods.html"), "Redwoods"),
                              (INDEX.with_name("forest.html"), "Forest")):
            source = page.read_text()
            builder = "buildTempleStudy" if page == INDEX else "buildTemple"
            self.assertTrue(f"['Raising the temple', () => {builder}()]" in source, page.name)
            self.assertNotIn("function buildMonolith()", source)
            picker = re.search(r'<nav class="scene-picker".*?</nav>', source, re.S).group(0)
            links = re.findall(r'<a href="([^"]+)"([^>]*)>([^<]+)</a>', picker)
            self.assertEqual([(href, label) for href, _, label in links],
                             [("index.html", "Temple"), ("redwoods.html", "Redwoods"), ("forest.html", "Forest")])
            self.assertEqual([label for _, attrs, label in links if 'aria-current="page"' in attrs], [current])
        self.assertIn("function buildTemple()", SOURCE)
        self.assertIn("fetch('/__tune/temple/save'", SOURCE)
        self.assertIn("fetch('/__tune/redwoods/save'", INDEX.with_name("redwoods.html").read_text())

    @unittest.skipIf(shutil.which("node") is None, "node is not installed")
    def test_old_scene_links_preserve_query_and_section(self):
        for old, new in (("temple.html", "index.html"), ("monolith.html", "redwoods.html")):
            redirect = inline_script(INDEX.with_name(old).read_text())
            harness = "const assert=require('node:assert/strict'); const window={location:{search:'?tune=1',hash:'#experience',replace:url=>assert.equal(url," + json.dumps(new + '?tune=1#experience') + ")}};\n"
            result = subprocess.run(["node", "-e", harness + redirect], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipIf(shutil.which("node") is None, "node is not installed")
    def test_navigation_stays_active_at_arrival_and_between_named_sections(self):
        fn = re.search(r"function navChapterIndex\([^\n]+\) \{.*?\n\}", SOURCE, re.S).group(0)
        harness = "const assert=require('node:assert/strict'); const chapters=[0,2400,9000,12000,15000]; for(const [p,i] of [[0,0],[500,0],[2300,0],[2400,1],[8900,1],[9000,2],[12000,3],[15000,4],[18000,4]]) assert.equal(navChapterIndex(chapters,p),i);"
        result = subprocess.run(["node", "-e", fn + "\n" + harness], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class TuningPanelTests(unittest.TestCase):
    """TUNE, TUNE_SCHEMA and the handlers passed to buildTunePanel are three
    separate lists that have to agree on the same keys. Nothing at runtime says
    otherwise — a schema row with no TUNE entry renders a slider reading
    `undefined`, and a TUNE entry with no schema row is invisible but still
    saved back into the file."""

    source = SOURCE

    def setUp(self):
        self.values = set(re.findall(r"^\s*(\w+)\s*:", TUNE_RE.search(self.source).group(1), re.M))
        self.schema = set(re.findall(r"^\s*\['(\w+)'", SCHEMA_RE.search(self.source).group(1), re.M))
        self.handlers = set(re.findall(r"^\s*(\w+)\s*:", HANDLERS_RE.search(self.source).group(1), re.M))

    def test_every_slider_has_a_value(self):
        self.assertEqual(self.schema - self.values, set())

    def test_every_value_has_a_slider(self):
        self.assertEqual(self.values - self.schema, set())

    def test_every_handler_has_a_value(self):
        self.assertEqual(self.handlers - self.values, set())

    def test_schema_groups_stay_contiguous(self):
        """The panel prints a heading whenever the group changes as it walks the
        schema, so a group split in two prints its heading twice."""
        groups = re.findall(r"^\s*\['\w+',[^\]]*'([^']+)'\]", SCHEMA_RE.search(self.source).group(1), re.M)
        runs = [g for i, g in enumerate(groups) if i == 0 or g != groups[i - 1]]
        self.assertEqual(len(runs), len(set(runs)), f"a group is split: {runs}")


class WorkCardTests(unittest.TestCase):
    """A featured project is spelled out in four places that have to agree on
    the same key — the card's data-work, the capture in WORK_SRC, the panel copy
    in WORK_INFO, and the cloth plate in CARD_PLATES. Nothing at runtime
    complains when they drift: a card whose key is missing from WORK_INFO simply
    does not open, and a plate keyed to nothing falls back to the drawing, which
    looks deliberate."""

    source = SOURCE

    def setUp(self):
        self.cards = set(re.findall(r'data-work="(\w+)"', self.source))
        self.src_keys = set(re.findall(r"^\s*(\w+):\s*'assets/work/",
                                       SRC_RE.search(self.source).group(1), re.M))
        self.info = set(re.findall(r"^  (\w+): \{", INFO_RE.search(self.source).group(1), re.M))
        self.plates = set(re.findall(r"'(\w+)'\]", PLATES_RE.search(self.source).group(1)))
        # the same kind again, inside each WORK_INFO entry, where it picks the
        # drawing the detail panel falls back to when a capture is missing
        self.info_plates = set(re.findall(r"plate: \[[^\]]*'(\w+)'\]",
                                          INFO_RE.search(self.source).group(1)))

    def test_every_card_has_panel_copy(self):
        self.assertEqual(self.cards - self.info, set())

    def test_every_panel_belongs_to_a_card(self):
        self.assertEqual(self.info - self.cards, set())

    def test_every_plate_names_a_card(self):
        self.assertEqual(self.plates - self.cards, set())

    def test_every_capture_names_a_card(self):
        self.assertEqual(self.src_keys - self.cards, set())

    def test_every_panel_plate_names_a_card(self):
        self.assertEqual(self.info_plates - self.cards, set())


class MachineReadableTests(unittest.TestCase):
    """The page states the same work three times over for readers that do not
    run scripts: the JSON-LD in the head, the noscript block, and llms.txt.

    The prose is deliberately different in each — a panel body, a fallback, a
    plain-text mirror — so none of this asserts the wording. What it asserts is
    the part that is silently wrong when it drifts: whether the same projects
    are named, and whether they point at the same places."""

    source = SOURCE

    def setUp(self):
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                            self.source, re.S)
        self.assertTrue(blocks, "the head has no JSON-LD block")
        self.graph = json.loads(blocks[0])["@graph"]
        self.parts = [p for n in self.graph if n["@type"] == "ProfilePage"
                      for p in n.get("hasPart", [])]

    def test_json_ld_parses(self):
        """A malformed block is not an error anywhere — it is simply ignored by
        every reader it was written for, which is indistinguishable from never
        having added it."""
        self.assertTrue(self.parts, "no projects in the JSON-LD")

    def test_json_ld_links_match_the_cards(self):
        hrefs = set(re.findall(r'<a class="card" href="([^"]+)"', self.source))
        for part in self.parts:
            self.assertIn(part["url"], hrefs,
                          f"{part['name']} points somewhere no card does")

    def test_noscript_names_every_featured_project(self):
        noscript = re.search(r"<noscript>(.*?)</noscript>", self.source, re.S)
        self.assertIsNotNone(noscript, "the noscript fallback is gone")
        body = noscript.group(1)
        for title in re.findall(r"title: '([^']+)'", INFO_RE.search(self.source).group(1)):
            self.assertIn(title, body, f"{title} is missing from the noscript block")

    @unittest.skipUnless(LLMS.exists(), "root/llms.txt is published from main")
    def test_llms_txt_names_every_featured_project(self):
        text = LLMS.read_text(encoding="utf-8")
        for title in re.findall(r"title: '([^']+)'", INFO_RE.search(self.source).group(1)):
            self.assertIn(title, text, f"{title} is missing from llms.txt")


class RedwoodsTuningPanelTests(TuningPanelTests):
    source = INDEX.with_name("redwoods.html").read_text()


class RedwoodsWorkCardTests(WorkCardTests):
    source = INDEX.with_name("redwoods.html").read_text()


class RedwoodsMachineReadableTests(MachineReadableTests):
    source = INDEX.with_name("redwoods.html").read_text()


class ForestTuningPanelTests(TuningPanelTests):
    source = INDEX.with_name("forest.html").read_text()


class ForestWorkCardTests(WorkCardTests):
    source = INDEX.with_name("forest.html").read_text()


class ForestMachineReadableTests(MachineReadableTests):
    source = INDEX.with_name("forest.html").read_text()


class TempleMaterialTests(unittest.TestCase):
    @unittest.skipIf(shutil.which("node") is None, "node is not installed")
    def test_depth_shading_preserves_forest_light_and_shader_cache(self):
        for page in (INDEX, INDEX.with_name("redwoods.html"), INDEX.with_name("forest.html")):
            with self.subTest(page=page.name):
                source = inline_script(page.read_text())
                depth = re.search(r"function applyTempleDepth\(mat\) \{.*?\n\}", source, re.S).group(0)
                canopy = re.search(r"function applyForestLight\(mat\) \{.*?\n\}", source, re.S)
                harness = r"""
const assert=require('node:assert/strict'),vm=require('node:vm');
const THREE=require('./assets/three.min.js');
const originalFog=THREE.ShaderChunk.fog_fragment;
const WORLD={canopy:new THREE.Texture(),breeze:{value:1}};
const ctx={THREE,WORLD};vm.createContext(ctx);vm.runInContext(DEPTH+CANOPY,ctx);
const plain=new THREE.MeshStandardMaterial(),mat=new THREE.MeshStandardMaterial();
if(CANOPY) ctx.applyForestLight(mat);
const oldKey=mat.customProgramCacheKey();ctx.applyTempleDepth(mat);
const key=mat.customProgramCacheKey();assert.notEqual(key,oldKey);
assert.notEqual(key,plain.customProgramCacheKey());
for(let i=0;i<2;i++) {
 const shader={uniforms:{},vertexShader:THREE.ShaderLib.standard.vertexShader,
  fragmentShader:THREE.ShaderLib.standard.fragmentShader};
 mat.onBeforeCompile(shader);
 assert(!shader.fragmentShader.includes('#include <fog_fragment>'));
 assert.equal((shader.fragmentShader.match(/float fogFactor = 1.0 - exp/g)||[]).length,1);
 const factor=Number(shader.fragmentShader.match(/fogDensity \* fogDensity \* ([.\d]+)/)[1]);
 assert(factor>0 && factor<1);
 assert(shader.fragmentShader.includes('smoothstep( fogNear, fogFar, vFogDepth )'));
 if(CANOPY) {
  assert.equal(shader.uniforms.uCanopy.value,WORLD.canopy);
  assert.equal(shader.uniforms.uBreeze,WORLD.breeze);
  assert(shader.vertexShader.includes('vGardenWorld=(modelMatrix*gardenP).xyz'));
  assert(shader.fragmentShader.includes('diffuseColor.rgb*=mix(.82,1.42,canopy)'));
 }
 assert.equal(mat.customProgramCacheKey(),key);
}
assert.equal(THREE.ShaderChunk.fog_fragment,originalFog);
"""
                result = subprocess.run(["node", "-e", "const DEPTH=" + json.dumps(depth) +
                                         ";const CANOPY=" + json.dumps(canopy.group(0) if canopy else "") +
                                         ";\n" + harness], cwd=INDEX.parent, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)


class PondTests(unittest.TestCase):
    source = SOURCE

    @unittest.skipIf(shutil.which("node") is None, "node is not installed")
    def test_pond_builds_with_and_without_planar_reflections(self):
        import json
        build = re.search(r"function buildPond\(\) \{.*?\n\}", inline_script(self.source), re.S).group(0)
        harness = r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
const THREE = require('./assets/three.min.js');
for (const reflected of [false, true]) {
  const scene = new THREE.Scene(), WORLD = {}, WET_TIME = {value: 0};
  const MIRROR = {on: reflected, texMat: new THREE.Matrix4(),
    target: reflected ? {texture: new THREE.Texture()} : null};
  const TUNE = {puddleOpacity: 1, puddleRipple: .85, puddleShimmer: .32,
    courtReflect: 1.5, courtFresnel: 0};
  vm.runInNewContext(BUILD + '\nbuildPond();', {THREE, scene, WORLD, WET_TIME, MIRROR, TUNE});
  const pond = WORLD.pond, mat = pond.material;
  assert.equal(scene.children.length, 1);
  assert.equal(pond.layers.mask, 2);
  assert(pond.position.y > 0 && pond.position.y < 7 / 40);
  assert(Object.hasOwn(mat.defines, 'PHYSICAL'));
  assert.equal(Boolean(mat.defines.POND_REFLECTION), reflected);
  const shader = {uniforms: {}, vertexShader: THREE.ShaderLib.physical.vertexShader,
    fragmentShader: THREE.ShaderLib.physical.fragmentShader};
  mat.onBeforeCompile(shader);
  assert.equal(shader.uniforms.uPondTime, WET_TIME);
  assert.equal(shader.uniforms.uPondRipple, WORLD.pondUniforms.uPondRipple);
  assert(shader.fragmentShader.includes('if(pondEdge>1.) discard;'));
  assert(shader.fragmentShader.includes('outgoingLight=mix(outgoingLight,pondReflection'));
  assert(!shader.fragmentShader.includes('pow((vPondWorld.x'));
}
"""
        result = subprocess.run(["node", "-e", "const BUILD = " + json.dumps(build) + ";\n" + harness],
                                cwd=INDEX.parent, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)


    @unittest.skipIf(shutil.which("node") is None, "node is not installed")
    def test_greenery_is_rooted_in_basin_and_stays_submerged(self):
        source = inline_script(self.source)
        functions = "\n".join(re.search(r"function " + name + r"\(\) \{.*?\n\}", source, re.S).group(0)
                              for name in ("buildPondBasin", "buildPondGreenery"))
        helpers = source[source.index("const clamp  ="):source.index("/* ------------------------------------------------------- 0b")]
        harness = r"""
const assert=require('node:assert/strict'),vm=require('node:vm');
const THREE=require('./assets/three.min.js');
for(const LOW of [false,true]) {
 const scene=new THREE.Scene(),WORLD={};
 const ctx={THREE,LOW,scene,WORLD};
 vm.runInNewContext(HELPERS+FUNCTIONS+`
 const floor=new THREE.Mesh(buildPondBasin(),new THREE.MeshBasicMaterial());
 floor.rotation.x=-Math.PI/2;floor.position.set(0,0,-18);floor.updateMatrixWorld();
 WORLD.floor=floor;buildPondGreenery();`,ctx);
 const m=WORLD.pondGreenery,p=m.geometry.attributes.position,matrix=new THREE.Matrix4();
 assert(m.isInstancedMesh && m.count>40 && m.count<300);
 assert.equal(m.layers.mask,2);assert.equal(m.material.transparent,false);
 assert(m.geometry.index.count/3*m.count<=6000);
 const root=new THREE.Vector3(),v=new THREE.Vector3(),down=new THREE.Vector3(0,-1,0);
 const ray=new THREE.Raycaster(undefined,down,0,5);
 for(let i=0;i<m.count;i++) {
  m.getMatrixAt(i,matrix);root.setFromMatrixPosition(matrix);
  ray.ray.origin.set(root.x,2,root.z);
  const hit=ray.intersectObject(WORLD.floor)[0];assert(hit);
  assert(Math.abs(root.y-(hit.point.y-.012))<.0001,'root detached from basin');
  for(let j=0;j<p.count;j++) {
   v.fromBufferAttribute(p,j).applyMatrix4(matrix);
   assert(Number.isFinite(v.x+v.y+v.z));assert(v.y<-.10,'blade breaks water');
  }
 }
}
"""
        result = subprocess.run(["node", "-e", "const HELPERS=" + json.dumps(helpers) + ";const FUNCTIONS=" + json.dumps(functions) + ";\n" + harness],
                                cwd=INDEX.parent, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)


class ForestPondTests(PondTests):
    source = INDEX.with_name("forest.html").read_text()


class RedwoodsPondTests(PondTests):
    source = INDEX.with_name("redwoods.html").read_text()


class BootTests(unittest.TestCase):
    @unittest.skipIf(shutil.which("node") is None, "node is not installed")
    def test_critical_failures_fall_back_regardless_of_job_position(self):
        """Run the real boot function with both throws and rejected promises.
        Optional assets may fail, but no scene jobs may run after setup fails."""
        boot = re.search(r"function boot\(\) \{.*?\n\}", inline_script(), re.S).group(0)
        harness = r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const page = fs.readFileSync('index.html', 'utf8');
const jobs = page.match(/const JOBS = \[([\s\S]*?)\n\];/)[1];
assert.match(jobs, /\['Pouring the ground',[^\n]+, true\]/);
async function run(position, rejected, critical) {
  let later = 0;
  const outcome = await new Promise(resolve => {
    const noop = () => {};
    const context = {
      document: {body: {classList: {add: noop}}}, TUNE: {grainOverlay: 0},
      preFill: {style: {}}, prePct: {}, console: {error: noop},
      setTimeout: fn => fn(), start: () => resolve('started'),
      fallback: () => resolve('fallback')
    };
    for (const name of ['applyGrainOverlay', 'buildGames', 'buildArchive', 'buildXpAnchors',
      'wireWorkModal', 'wireCardSheen', 'wireReveals', 'wireNav',
      'wireHeroExit', 'wireFocus', 'wireCursor']) context[name] = noop;
    context.JOBS = Array.from({length: position}, () => ['asset', noop]);
    context.JOBS.push(['setup', () => {
      if (rejected) return Promise.reject(new Error('unavailable'));
      throw new Error('unavailable');
    }, critical], ['later', () => later++]);
    vm.runInNewContext(BOOT + '\nboot();', context);
  });
  assert.equal(outcome, critical ? 'fallback' : 'started');
  assert.equal(later, critical ? 0 : 1);
}
(async () => {
  for (const position of [0, 2, 4])
    for (const rejected of [false, true])
      for (const critical of [false, true]) await run(position, rejected, critical);
})().catch(err => { console.error(err); process.exitCode = 1; });
"""
        import json
        result = subprocess.run(["node", "-e", "const BOOT = " + json.dumps(boot) + ";\n" + harness],
                                cwd=INDEX.parent, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
