"""Check Pterodactyl's permission conversion without launching the game."""
import copy
import json
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1] / "games-steamcmd/enshrouded"
PERMISSIONS = ("canKickBan", "canAccessInventories", "canEditWorld", "canEditBase", "canExtendBase")


class EnshroudedStartupTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.config = self.root / "enshrouded_server.json"
        self.egg = json.loads((ROOT / "egg-pterodactyl-enshrouded.json").read_text())
        # Execute the conversion from the actual export, without Proton or the log tail.
        self.command, separator, _ = self.egg["startup"].partition(" || exit 1; ")
        self.assertTrue(separator, "conversion failure must stop startup")
        self.seed = json.loads((ROOT / "enshrouded_server.json").read_text())

    def convert(self):
        return subprocess.run(shlex.split(self.command), cwd=self.root,
                              text=True, capture_output=True)

    def test_permission_toggles_keep_json_types_and_unmanaged_settings(self):
        original = copy.deepcopy(self.seed)
        original["tags"] = ["keep me"]
        original["gameSettings"] = {"playerHealthFactor": 1.5}
        original["userGroups"].append({"name": "Custom", "canEditWorld": 0})
        for group in original["userGroups"][:4]:
            group["password"] = "quotes\" and unicode æ"
            group["reservedSlots"] = 2
        for representation in (bool, int, lambda value: str(int(value))):
            with self.subTest(representation=representation):
                config = copy.deepcopy(original)
                # Flip every default to prove both enabling and disabling work per group.
                for group in config["userGroups"][:4]:
                    for key in PERMISSIONS:
                        group[key] = representation(not group[key])
                expected = copy.deepcopy(original)
                for group in expected["userGroups"][:4]:
                    for key in PERMISSIONS:
                        group[key] = not group[key]
                self.config.write_text(json.dumps(config))
                result = self.convert()
                self.assertEqual(result.returncode, 0, result.stderr)
                actual = json.loads(self.config.read_text())
                self.assertEqual(actual, expected)
                self.assertTrue(all(type(group[key]) is bool
                                    for group in actual["userGroups"][:4] for key in PERMISSIONS))
                before = self.config.read_bytes()
                self.assertEqual(self.convert().returncode, 0)
                self.assertEqual(self.config.read_bytes(), before)

    def test_invalid_permission_does_not_rewrite_config(self):
        self.seed["userGroups"][3]["canEditBase"] = "invalid"
        self.config.write_text(json.dumps(self.seed))
        before = self.config.read_bytes()
        self.assertNotEqual(self.convert().returncode, 0)
        self.assertEqual(self.config.read_bytes(), before)

    def test_startup_has_valid_shell_syntax(self):
        result = subprocess.run(["bash", "-n", "-c", self.egg["startup"]],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
