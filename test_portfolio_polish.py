from pathlib import Path
import subprocess
import unittest

class CursorIdleTests(unittest.TestCase):
    def test_cursor_stops_at_rest_and_resumes(self):
        subprocess.run(['node','tools/test_cursor_idle.mjs'], cwd=Path(__file__).resolve().parent, check=True)
