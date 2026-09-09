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


def inline_script():
    bodies = SCRIPT_RE.findall(SOURCE)
    assert bodies, "index.html has no inline <script>"
    return bodies[-1]


class InlineScriptTests(unittest.TestCase):
    @unittest.skipIf(shutil.which("node") is None, "node is not installed")
    def test_inline_script_parses(self):
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as staged:
            staged.write(inline_script())
            staged.flush()
            result = subprocess.run(["node", "--check", staged.name],
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class TuningPanelTests(unittest.TestCase):
    """TUNE, TUNE_SCHEMA and the handlers passed to buildTunePanel are three
    separate lists that have to agree on the same keys. Nothing at runtime says
    otherwise — a schema row with no TUNE entry renders a slider reading
    `undefined`, and a TUNE entry with no schema row is invisible but still
    saved back into the file."""

    def setUp(self):
        self.values = set(re.findall(r"^\s*(\w+)\s*:", TUNE_RE.search(SOURCE).group(1), re.M))
        self.schema = set(re.findall(r"^\s*\['(\w+)'", SCHEMA_RE.search(SOURCE).group(1), re.M))
        self.handlers = set(re.findall(r"^\s*(\w+)\s*:", HANDLERS_RE.search(SOURCE).group(1), re.M))

    def test_every_slider_has_a_value(self):
        self.assertEqual(self.schema - self.values, set())

    def test_every_value_has_a_slider(self):
        self.assertEqual(self.values - self.schema, set())

    def test_every_handler_has_a_value(self):
        self.assertEqual(self.handlers - self.values, set())

    def test_schema_groups_stay_contiguous(self):
        """The panel prints a heading whenever the group changes as it walks the
        schema, so a group split in two prints its heading twice."""
        groups = re.findall(r"^\s*\['\w+',[^\]]*'([^']+)'\]", SCHEMA_RE.search(SOURCE).group(1), re.M)
        runs = [g for i, g in enumerate(groups) if i == 0 or g != groups[i - 1]]
        self.assertEqual(len(runs), len(set(runs)), f"a group is split: {runs}")


class WorkCardTests(unittest.TestCase):
    """A featured project is spelled out in four places that have to agree on
    the same key — the card's data-work, the capture in WORK_SRC, the panel copy
    in WORK_INFO, and the cloth plate in CARD_PLATES. Nothing at runtime
    complains when they drift: a card whose key is missing from WORK_INFO simply
    does not open, and a plate keyed to nothing falls back to the drawing, which
    looks deliberate."""

    def setUp(self):
        self.cards = set(re.findall(r'data-work="(\w+)"', SOURCE))
        self.src_keys = set(re.findall(r"^\s*(\w+):\s*'assets/work/",
                                       SRC_RE.search(SOURCE).group(1), re.M))
        self.info = set(re.findall(r"^  (\w+): \{", INFO_RE.search(SOURCE).group(1), re.M))
        self.plates = set(re.findall(r"'(\w+)'\]", PLATES_RE.search(SOURCE).group(1)))
        # the same kind again, inside each WORK_INFO entry, where it picks the
        # drawing the detail panel falls back to when a capture is missing
        self.info_plates = set(re.findall(r"plate: \[[^\]]*'(\w+)'\]",
                                          INFO_RE.search(SOURCE).group(1)))

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

    def setUp(self):
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                            SOURCE, re.S)
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
        hrefs = set(re.findall(r'<a class="card" href="([^"]+)"', SOURCE))
        for part in self.parts:
            self.assertIn(part["url"], hrefs,
                          f"{part['name']} points somewhere no card does")

    def test_noscript_names_every_featured_project(self):
        noscript = re.search(r"<noscript>(.*?)</noscript>", SOURCE, re.S)
        self.assertIsNotNone(noscript, "the noscript fallback is gone")
        body = noscript.group(1)
        for title in re.findall(r"title: '([^']+)'", INFO_RE.search(SOURCE).group(1)):
            self.assertIn(title, body, f"{title} is missing from the noscript block")

    @unittest.skipUnless(LLMS.exists(), "root/llms.txt is published from main")
    def test_llms_txt_names_every_featured_project(self):
        text = LLMS.read_text(encoding="utf-8")
        for title in re.findall(r"title: '([^']+)'", INFO_RE.search(SOURCE).group(1)):
            self.assertIn(title, text, f"{title} is missing from llms.txt")


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
    for (const name of ['applyGrainOverlay', 'buildArchive', 'buildXpAnchors',
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
