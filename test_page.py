"""Structural checks on index.html — the page has no runtime tests, and every
failure it can have here is silent: a syntax error in the inline script leaves
the preloader spinning, and a tuning key that exists in one of its three homes
but not the others just quietly does nothing."""
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


if __name__ == "__main__":
    unittest.main()
