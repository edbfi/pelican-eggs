# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Game-server eggs for the Pelican panel, each with a Pterodactyl variant. There is no build or package manifest. The content is panel export data plus one shipped helper, `games-steamcmd/humanitz/ini-merge.sh`.

## Local commands

```bash
python3 -m unittest discover -s tests -v                                                                 # ini-merge.sh tests
python3 -m unittest tests.test_ini_merge.IniMergeTests.test_seeds_missing_live_file -v                   # one test case
```

## The two exports are one egg: change both

A behavioural change (startup command, `config.files`/`startup`/`logs`/`stop`, install script, variable default/rules/visibility, `file_denylist`) must go into both `egg-<slug>.yaml` (Pelican, `PLCN_v3`) and `egg-pterodactyl-<slug>.json` (`PTDL_v2`). The two formats differ, so translate between them rather than copying:

| Concern | `egg-*.yaml` (Pelican) | `egg-pterodactyl-*.json` |
|---|---|---|
| Env interpolation in `config.files` | `{{server.environment.VAR}}` | `{{server.build.env.VAR}}` |
| Startup command | `startup_commands.Default` | `startup` (plain string) |
| `config.files` / `startup` / `logs` | native YAML mappings | JSON-encoded strings (escaped, `\/` slashes) |
| Variable `rules` | YAML list | pipe string (`"required\|numeric"`) |
| Per-variable extras | `sort:` | `field_type: "text"`, no `sort` |

The `scripts` blocks must be identical in both files. Display names, variable order, `exported_at` and `uuid`/`tags`/`icon` may differ between the two.

Both files start with `DO NOT EDIT: FILE GENERATED AUTOMATICALLY BY PANEL`. Hand edits are fine here, but the next panel export overwrites them unless the same change is made in the source panel. Say so in your summary whenever you hand-edit an export.

## `ini-merge.sh` is fetched live from `main`

Both HumanitZ install scripts download it with `curl` from `https://raw.githubusercontent.com/edbfi/pelican-eggs/refs/heads/main/games-steamcmd/humanitz/ini-merge.sh`.

- If you rename or move it, update that URL in both exports in the same commit. Otherwise installs break as soon as the change reaches `main`.
- Merging to `main` changes what new installs and reinstalls get. Servers that are already running keep booting their own `/mnt/server/ini-merge.sh` copy until they are reinstalled.
- It must never block boot or clobber player edits. Keep its contract: `set -u` without `set -e`, every failure path logs and exits 0, writes go through `mktemp` plus `.bak` plus atomic `mv`, and it only ever adds missing keys. To change behaviour, keep those failure paths and add a case to `tests/test_ini_merge.py`.
- A helper shipped with an egg must appear in `file_denylist` in both exports.

## Adding an egg

1. Create `games-steamcmd/<slug>/` containing `README.md`, `egg-<slug>.yaml` and `egg-pterodactyl-<slug>.json` (see `games-steamcmd/humanitz/`).
2. Add a row to the `## Eggs` table in the root `README.md`.
3. List any shipped helper in `file_denylist` in both exports.

## Commits

Use Conventional Commits, scoped to the egg slug for egg changes (`feat(humanitz): ...`). PR commits carry a `Signed-off-by` matching the author (`git commit -s`).

## Reference docs

- `games-steamcmd/humanitz/README.md`: ports, which `GameServerSettings.ini` keys are deliberately left out of the panel variables, and the one-time reinstall existing servers need. Read before changing HumanitZ variables, `config.files` mappings or merge behaviour.
