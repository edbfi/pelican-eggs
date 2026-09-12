"""Reject behavioral drift between the two HumanitZ panel exports."""
import json
from pathlib import Path
import yaml

root = Path("games-steamcmd/humanitz")
pelican = yaml.safe_load((root / "egg-humanit-z.yaml").read_text())
pterodactyl = json.loads((root / "egg-pterodactyl-humanit-z.json").read_text())


def normalize(value):
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, str):
        return value.replace("server.environment.", "server.build.env.")
    return value


def variables(egg):
    result = {}
    for item in egg["variables"]:
        default = item["default_value"]
        if isinstance(default, bool):
            default = str(default).lower()
        rules = item["rules"]
        result[item["env_variable"]] = {
            "default": str(default),
            "rules": sorted(rules.split("|") if isinstance(rules, str) else rules),
            "viewable": item["user_viewable"],
            "editable": item["user_editable"],
        }
    return result


assert variables(pelican) == variables(pterodactyl), "Variable behavior differs"
assert pelican["scripts"] == pterodactyl["scripts"], "Install scripts differ"
assert pelican["file_denylist"] == pterodactyl["file_denylist"], "File permissions differ"
assert "ini-merge.sh" in pelican["file_denylist"]
assert normalize(pelican["startup_commands"]["Default"]) == pterodactyl["startup"]
for key in ("files", "startup", "logs"):
    assert normalize(pelican["config"][key]) == json.loads(pterodactyl["config"][key]), key
assert pelican["config"]["stop"] == pterodactyl["config"]["stop"]
print("HumanitZ Pelican/Pterodactyl behavioral parity passed")
