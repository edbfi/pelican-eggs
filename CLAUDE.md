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
| Startup command | `startup_commands.<name>` (`Default`, or e.g. `Proton`) | `startup` (plain string) |
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

## Naming

One slug per egg: lowercase, hyphen-separated, and identical in the folder name and both file names.

```
games-steamcmd/<slug>/
├── README.md
├── egg-<slug>.yaml                # Pelican
└── egg-pterodactyl-<slug>.json    # Pterodactyl
```

A variant gets its own slug with the variant as a suffix (`icarus-proton`). Panel exports are named after the egg's display name (`HumanitZ` exports as `egg-humanit-z.yaml`), so rename a fresh export to the repo slug before committing it.

Do not rename an existing egg folder that a published install script fetches from, such as `humanitz/` for `ini-merge.sh`. Eggs already imported into panels keep the old URL.

## `update_url`

In each Pelican export, `meta.update_url` points at that same file on `main`: `https://raw.githubusercontent.com/edbfi/pelican-eggs/refs/heads/main/games-steamcmd/<slug>/egg-<slug>.yaml`. Pelican fetches it daily, compares it with the whole egg, and offers an Update that replaces the egg with the file, including its `update_url`. A URL that doesn't point at the file itself either turns updates off after one update (`null` in the file) or leaves the egg flagged "update available" forever. Renaming or moving an export means updating its `update_url` in the same commit.

Keep `update_url: null` in the Pterodactyl exports. Pterodactyl never fetches it, and a Pelican panel that imported the JSON would compare its own export format with `PTDL_v2` and never match.

## Refreshing exports

The Pelican panel is the source and the files are its output. Prefer this flow to hand edits:

1. Make the change in the panel. To load the repo version first, use **Admin → Eggs → Import → URL** with the YAML's raw URL. The import matches on `uuid` and updates the existing egg in place.
2. Export the egg from Pelican as `.yaml`. The Export button opens `/api/application/eggs/<id>/export?format=yaml`.
3. Convert that YAML with [Scramble](https://redthirten.github.io/scramble-egg-converter/) → **Convert to Pterodactyl**. It runs in the browser and writes `update_url: null`.
4. Rename the results to the repo slug. Scramble names its output `pterodactyl-egg-<slug>.json`, which becomes `egg-pterodactyl-<slug>.json`.
5. Confirm both files still have identical `scripts` blocks before committing.

## Adding an egg

1. Create `games-steamcmd/<slug>/` containing `README.md`, `egg-<slug>.yaml` and `egg-pterodactyl-<slug>.json` (see `games-steamcmd/humanitz/` and [Naming](#naming)).
2. Add a row to the `## Eggs` table in the root `README.md`.
3. List any shipped helper in `file_denylist` in both exports.

## Commits

Use Conventional Commits, scoped to the egg slug for egg changes (`feat(humanitz): ...`). PR commits carry a `Signed-off-by` matching the author (`git commit -s`).

## Reference docs

- `games-steamcmd/humanitz/README.md`: ports, which `GameServerSettings.ini` keys are deliberately left out of the panel variables, and the one-time reinstall existing servers need. Read before changing HumanitZ variables, `config.files` mappings or merge behaviour.
- `games-steamcmd/icarus-proton/README.md`: how this egg differs from the upstream Wine Icarus egg, and its ports.
