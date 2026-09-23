"""Tuning-save regressions; all writes use a temporary source file."""
import http.client
import json
import socket
import threading
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

    def test_scene_save_cannot_overwrite_the_other_scene(self):
        scenes = {name: self.index.with_name(name + ".html") for name in ("redwoods", "forest")}
        for page in scenes.values():
            page.write_text(SOURCE)
        for name, page in scenes.items():
            serve.write_tune({"first": .75}, name)
            self.assertEqual(self.index.read_text(), SOURCE)
            self.assertEqual(page.read_text(), SOURCE.replace("first: .50", "first: 0.75"))
        serve.write_tune({"second": 2})
        self.assertEqual(self.index.read_text(), SOURCE.replace("second: 1.00", "second: 2.00"))
        for page in scenes.values():
            self.assertEqual(page.read_text(), SOURCE.replace("first: .50", "first: 0.75"))

    def test_scene_names_are_allowlisted(self):
        for name in ("../index", "index.html", "../../forest", None):
            with self.subTest(name=name), self.assertRaises(ValueError):
                serve.write_tune({"first": .25}, name)
        self.assertEqual(self.index.read_text(), SOURCE)

class PreviewConnectionTests(unittest.TestCase):
    def test_scene_save_endpoints_target_their_own_page(self):
        with tempfile.TemporaryDirectory() as directory:
            index = Path(directory, "index.html")
            redwoods = Path(directory, "redwoods.html")
            index.write_text(SOURCE)
            redwoods.write_text(SOURCE)
            forest = Path(directory, "forest.html")
            forest.write_text(SOURCE)
            with patch.object(serve, "HERE", Path(directory)), patch.object(serve, "INDEX", index):
                try:
                    server = serve.PreviewServer(("127.0.0.1", 0), serve.Handler)
                except PermissionError:
                    self.skipTest("local socket binding is unavailable in this sandbox")
                worker = threading.Thread(target=server.serve_forever, daemon=True)
                worker.start()
                request = http.client.HTTPConnection(*server.server_address, timeout=2)
                try:
                    expected = {"index.html": SOURCE, "redwoods.html": SOURCE, "forest.html": SOURCE}
                    for endpoint, filename in (("/__tune/temple/save", "index.html"),
                                               ("/__tune/redwoods/save", "redwoods.html"),
                                               ("/__tune/save", "redwoods.html"),
                                               ("/__tune/forest/save", "forest.html")):
                        request.request("POST", endpoint, json.dumps({"first": .75}),
                                        {"content-type": "application/json"})
                        response = request.getresponse()
                        self.assertEqual(response.status, 200)
                        response.read()
                        expected[filename] = SOURCE.replace("first: .50", "first: 0.75")
                        for name, content in expected.items():
                            self.assertEqual(Path(directory, name).read_text(), content)
                finally:
                    request.close()
                    server.shutdown()
                    worker.join(2)
                    server.server_close()

    def test_idle_browser_connection_does_not_block_page_request(self):
        accepted = threading.Event()

        class RecordingHandler(serve.Handler):
            def setup(self):
                super().setup()
                accepted.set()

        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "index.html").write_text("preview ready")
            with patch.object(serve, "HERE", Path(directory)):
                try:
                    server = serve.PreviewServer(("127.0.0.1", 0), RecordingHandler)
                except PermissionError:
                    self.skipTest("local socket binding is unavailable in this sandbox")
                worker = threading.Thread(target=server.serve_forever, daemon=True)
                worker.start()
                idle = None
                request = http.client.HTTPConnection(*server.server_address, timeout=2)
                try:
                    idle = socket.create_connection(server.server_address, timeout=2)
                    self.assertTrue(accepted.wait(2), "idle connection was not accepted")
                    request.request("GET", "/index.html")
                    response = request.getresponse()
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.read(), b"preview ready")
                    self.assertEqual(response.getheader("cache-control"), "no-store")
                finally:
                    request.close()
                    if idle is not None:
                        idle.close()
                    server.shutdown()
                    worker.join(2)
                    server.server_close()


if __name__ == "__main__":
    unittest.main()
