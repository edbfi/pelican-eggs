"""Exercise the shipped additive INI merger using temporary files only."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "games-steamcmd/humanitz/ini-merge.sh"


class IniMergeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.reference = self.root / "reference.ini"
        self.live = self.root / "live.ini"

    def run_merge(self):
        return subprocess.run(["bash", str(SCRIPT), str(self.reference), str(self.live)],
                              capture_output=True, text=True, check=True)

    def test_preserves_values_adds_keys_and_is_idempotent(self):
        self.reference.write_text("[Server]\nName=Default\nPort=7777\n[New]\nEnabled=true\n")
        original = "; player comment\n[Server]\nName=Player choice\nCustom=keep\n"
        self.live.write_text(original)
        self.run_merge()
        merged = self.live.read_text()
        self.assertIn("Name=Player choice\nCustom=keep\nPort=7777", merged)
        self.assertIn("[New]\nEnabled=true", merged)
        self.assertEqual(self.live.with_suffix(".ini.bak").read_text(), original)
        self.run_merge()
        self.assertEqual(self.live.read_text(), merged)
        self.assertEqual(self.live.with_suffix(".ini.bak").read_text(), original)

    def test_seeds_missing_live_file(self):
        self.reference.write_text("[Server]\nName=Default\n")
        self.run_merge()
        self.assertEqual(self.live.read_bytes(), self.reference.read_bytes())

    def test_missing_reference_preserves_live_file(self):
        self.live.write_text("[Server]\nName=Player\n")
        before = self.live.read_bytes()
        self.run_merge()
        self.assertEqual(self.live.read_bytes(), before)

    def test_unwritable_destination_is_nonfatal(self):
        self.reference.write_text("[Server]\nName=Default\n")
        self.live = self.root / "missing-directory/live.ini"
        self.run_merge()
        self.assertFalse(self.live.exists())

    def test_missing_arguments_are_nonfatal(self):
        subprocess.run(["bash", str(SCRIPT)], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
