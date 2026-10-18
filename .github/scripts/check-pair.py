"""Reject behavioral drift between the Pelican and Pterodactyl export of each egg,
and between the Enshrouded egg and the config seed its installer downloads."""
import json
from pathlib import Path
import re
import shlex
import yaml

# Directory -> (Pelican export, Pterodactyl export, deliberate Pterodactyl differences).
PAIRS = {
    "humanitz": ("egg-humanitz.yaml", "egg-pterodactyl-humanitz.json", {}),
    "icarus-proton": ("egg-icarus-proton.yaml", "egg-pterodactyl-icarus-proton.json", {}),
    # Pterodactyl's Wings indexes arrays as key[N] and cannot write a variable as a JSON
    # boolean, so its export omits the chat toggles and converts group permissions at startup
    # (games-steamcmd/enshrouded/README.md).
    "enshrouded": ("egg-enshrouded.yaml", "egg-pterodactyl-enshrouded.json", {
        "find": {"enableTextChat", "enableVoiceChat"},
        "variables": {"ENABLE_TEXT_CHAT", "ENABLE_VOICE_CHAT"},
        "array_index": True,
        "permission_conversion": True,
    }),
}


def normalize(value, array_index=False):
    if isinstance(value, dict):
        return {normalize(key, array_index): normalize(item, array_index) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize(item, array_index) for item in value]
    if isinstance(value, str):
        value = value.replace("server.environment.", "server.build.env.")
        value = value.replace("server.allocations.default.port", "server.build.default.port")
        if array_index:
            value = re.sub(r"^(\w+)\.(\d+)\.", r"\1[\2].", value)
    return value


def variables(egg, omit=frozenset()):
    result = {}
    for item in egg["variables"]:
        if item["env_variable"] in omit:
            continue
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


def config(value):
    return json.loads(value) if isinstance(value, str) else value


def check(directory, pelican_name, pterodactyl_name, differences):
    root = Path("games-steamcmd") / directory
    pelican = yaml.safe_load((root / pelican_name).read_text())
    pterodactyl = json.loads((root / pterodactyl_name).read_text())
    array_index = differences.get("array_index", False)

    expected = variables(pelican, differences.get("variables", set()))
    assert expected == variables(pterodactyl), f"{directory}: variable behavior differs"
    assert pelican["scripts"] == pterodactyl["scripts"], f"{directory}: install scripts differ"
    assert (pelican["file_denylist"] or []) == pterodactyl["file_denylist"], f"{directory}: file permissions differ"
    startup = pterodactyl["startup"]
    if differences.get("permission_conversion"):
        conversion, separator, startup = startup.partition(" || exit 1; ")
        command = shlex.split(conversion)
        assert separator and len(command) == 3 and command[:2] == ["python3", "-c"], f"{directory}: missing permission conversion"
    assert normalize(next(iter(pelican["startup_commands"].values()))) == startup, f"{directory}: startup differs"
    files = normalize(config(pelican["config"]["files"]), array_index)
    for parser in files.values():
        for key in differences.get("find", ()):
            parser["find"].pop(key, None)
    assert files == config(pterodactyl["config"]["files"]), f"{directory}: config files differ"
    for key in ("startup", "logs"):
        assert normalize(config(pelican["config"][key])) == config(pterodactyl["config"][key]), f"{directory}: {key}"
    assert pelican["config"]["stop"] == pterodactyl["config"]["stop"], f"{directory}: stop"


def check_enshrouded_seed():
    """Every key the egg writes must exist in the seed, so Wings keeps its JSON type."""
    root = Path("games-steamcmd/enshrouded")
    egg = yaml.safe_load((root / "egg-enshrouded.yaml").read_text())
    seed = json.loads((root / "enshrouded_server.json").read_text())
    assert [group["name"] for group in seed["userGroups"]] == ["Admin", "Friend", "Guest", "Visitor"]
    assert all(group["password"] == "" for group in seed["userGroups"]), "seed passwords must be blank"
    find = config(egg["config"]["files"])["enshrouded_server.json"]["find"]
    options = {variable["env_variable"]: variable for variable in egg["variables"]}
    for index, group in enumerate(seed["userGroups"]):
        for field, default in group.items():
            if field in {"name", "password"}:
                continue
            key = f"userGroups.{index}.{field}"
            reference = re.fullmatch(r"\{\{server.environment.(\w+)\}\}", find[key])
            assert reference, f"enshrouded: {key} must reference a panel variable"
            variable = options[reference[1]]
            assert str(variable["default_value"]) == str(int(default)), f"enshrouded: {key} default differs from seed"
            expected_rule = "boolean" if isinstance(default, bool) else "integer"
            assert expected_rule in variable["rules"], f"enshrouded: {key} has the wrong validation type"
    for key in find:
        value = seed
        for part in key.split("."):
            value = value[int(part)] if isinstance(value, list) else value.get(part)
            assert value is not None, f"enshrouded: seed lacks {key}"


for directory, (pelican_name, pterodactyl_name, differences) in PAIRS.items():
    check(directory, pelican_name, pterodactyl_name, differences)
assert "ini-merge.sh" in yaml.safe_load(
    Path("games-steamcmd/humanitz/egg-humanitz.yaml").read_text())["file_denylist"]
check_enshrouded_seed()
print(f"Pelican/Pterodactyl behavioral parity passed for {len(PAIRS)} eggs; Enshrouded seed matches")
