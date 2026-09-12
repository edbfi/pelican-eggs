# AGENTS.md

This file provides guidance to AI coding agents when working with code in this
repository.

## What this is

A personal collection of game-server eggs for the [Pelican](https://pelican.dev) panel, with
Pterodactyl compatibility variants. No build system, no package manifest, no test suite, no
application linter. CI now validates exports, paired behavior and the INI helper;
see `CI.md` and `.github/scripts/`. The only shipped executable code in the repo is
`games-steamcmd/humanitz/ini-merge.sh`; everything else is panel export data and prose.

## Layout

```
games-steamcmd/<slug>/
  README.md                     # ports, install notes, panel-admin guidance
  egg-<slug>.yaml               # Pelican export      (meta.version: PLCN_v3)
  egg-pterodactyl-<slug>.json   # Pterodactyl export  (meta.version: PTDL_v2)
  <helper>.sh                   # optional, fetched at install time (see below)
```

`games-steamcmd/` groups eggs whose install script uses SteamCMD. The root `README.md` carries an
`## Eggs` table that needs one row per egg directory.

## The two exports are one egg — change both

Every behavioural change (startup command, `config.files`, install script, variable defaults,
`file_denylist`) must land in `egg-<slug>.yaml` **and** `egg-pterodactyl-<slug>.json`. The panel
schemas differ, so this is a translation, not a copy:

| Concern | `egg-*.yaml` (Pelican) | `egg-pterodactyl-*.json` |
|---|---|---|
| Env interpolation | `{{server.environment.VAR}}` | `{{server.build.env.VAR}}` |
| Startup command | `startup_commands.Default` | `startup` (plain string) |
| `config.files` / `.startup` / `.logs` | native YAML mappings | **JSON-encoded strings** |
| Variable rules | YAML list (`- required`, `- numeric`) | pipe string (`"required\|numeric"`) |
| Per-variable extras | `sort:` for order, `[Server]`/`[RCON]` name prefixes | `field_type: "text"` on every variable, no `sort:` |

`env_variable`, `default_value`, and rule semantics must match exactly across the pair. Display
names, variable ordering, `exported_at`, and the YAML-only `uuid`/`tags`/`icon` keys legitimately
differ — that is not drift. The install scripts are byte-identical today; keep them that way.

Both files open with `DO NOT EDIT: FILE GENERATED AUTOMATICALLY BY PANEL` and are committed
straight out of the panel. Hand-editing works for small changes, but anything applied only here
and not in the panel is lost on the next export — flag that when you hand-edit.

## `ini-merge.sh` is live infrastructure, not a repo artifact

The HumanitZ install script `curl`s it by absolute URL off `main`:

```
https://raw.githubusercontent.com/edbfi/pelican-eggs/refs/heads/main/games-steamcmd/humanitz/ini-merge.sh
```

- Moving or renaming the file breaks installs on live `main` immediately. If the path must change,
  update the URL in the install script of **both** exports in the same commit.
- A push to `main` reaches existing servers only on install/reinstall. Boot runs the local copy at
  `/mnt/server/ini-merge.sh`, invoked from the startup command as
  `[ -f ./ini-merge.sh ] && bash ./ini-merge.sh <ref.ini> <live.ini> || true`.

Its safety contract is deliberate: `set -u` **without** `set -e`, every failure path logs and
exits 0, writes go through `mktemp` plus an atomic `mv` after a one-shot `.bak`, and it only ever
*adds* keys absent from the live INI. Do not add `set -e`, a non-zero exit, or any path that
rewrites or reorders existing keys — a merge that goes wrong must degrade to "no change", never
block server boot or clobber a player's edited `GameServerSettings.ini`.

## Adding an egg

1. Create `games-steamcmd/<slug>/` with the four files above.
2. Add a row to the `## Eggs` table in the root `README.md`.
3. Add any helper script shipped with the egg to `file_denylist` in **both** exports, so panel
   users cannot edit or delete it.

## Commits

Conventional Commits scoped to the egg slug: `feat(humanitz): ...`, `chore(renovate): ...`.

## Reference docs

- `games-steamcmd/humanitz/README.md` — HumanitZ ports, which `GameServerSettings.ini` keys are
  deliberately *not* exposed as panel variables, and the one-time reinstall existing servers need.
  Read before changing HumanitZ variables, `config.files` mappings, or merge behaviour.
- `README.md` (root) — the `## Eggs` index. Update when adding, renaming, or removing an egg.
