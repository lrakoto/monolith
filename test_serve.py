"""Tuning-save regressions; all writes use a temporary source file."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import serve

SOURCE = """<!doctype html>
<script>
const TUNE = {
  first: .50, // keep this note
  second: 1.00,
  steps: 4
};
const untouched = 'portfolio';
</script>
"""

class TuneSaveTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.index = Path(directory.name) / "index.html"
        self.index.write_text(SOURCE)
        patcher = patch.object(serve, "INDEX", self.index)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_partial_save_preserves_other_values_and_source(self):
        self.assertEqual(serve.write_tune({"first": .25}), 1)
        self.assertEqual(self.index.read_text(), SOURCE.replace("first: .50", "first: 0.25"))

    def test_full_save_preserves_decimal_precision(self):
        self.assertEqual(serve.write_tune({"first": .2, "second": 1, "steps": 6}), 3)
        expected = SOURCE.replace("first: .50", "first: 0.20").replace("steps: 4", "steps: 6")
        self.assertEqual(self.index.read_text(), expected)

    def test_unknown_keys_do_not_enter_source(self):
        serve.write_tune({"second": 2, "obsolete": 42})
        self.assertEqual(self.index.read_text(), SOURCE.replace("second: 1.00", "second: 2.00"))

    def test_empty_or_unrecognized_payload_never_erases_settings(self):
        for values in ({}, {"obsolete": 3}, [], None, "text"):
            with self.subTest(values=values), self.assertRaises(ValueError):
                serve.write_tune(values)
            self.assertEqual(self.index.read_text(), SOURCE)

    def test_invalid_value_rejects_entire_save(self):
        for value in (True, None, "2", [], {}, float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                serve.write_tune({"first": .25, "second": value})
            self.assertEqual(self.index.read_text(), SOURCE)

    def test_failed_replace_keeps_original_and_cleans_temporary_file(self):
        with patch.object(serve.os, "replace", side_effect=OSError("disk failure")):
            with self.assertRaises(OSError):
                serve.write_tune({"first": .25})
        self.assertEqual(self.index.read_text(), SOURCE)
        self.assertEqual(list(self.index.parent.iterdir()), [self.index])

    def test_save_preserves_file_permissions(self):
        self.index.chmod(0o640)
        serve.write_tune({"first": .25})
        self.assertEqual(self.index.stat().st_mode & 0o777, 0o640)

    def test_missing_tune_block_does_not_change_file(self):
        self.index.write_text("portfolio without settings")
        with self.assertRaises(ValueError):
            serve.write_tune({"first": .25})
        self.assertEqual(self.index.read_text(), "portfolio without settings")

if __name__ == "__main__":
    unittest.main()
