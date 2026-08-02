# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A collection of game-server "eggs" for the [Pelican](https://pelican.dev) panel, with Pterodactyl
compatibility variants. There is **no build system, no package manifest, no test suite, no linter,
and no CI** — do not go looking for one. The only executable code is `games-steamcmd/humanitz/ini-merge.sh`.
Everything else is panel export data and prose documentation.

## Layout

```
games-steamcmd/<game-slug>/
  README.md                       # ports, install notes, panel-admin guidance
  egg-<game>.yaml                 # Pelican export      (meta.version: PLCN_v3)
  egg-pterodactyl-<game>.json     # Pterodactyl export  (meta.version: PTDL_v2)
  ini-merge.sh                    # optional per-egg helper, fetched at install time
```

`games-steamcmd/` groups eggs whose install script uses SteamCMD. The root `README.md` carries an
`## Eggs` table that must gain one row per egg directory.

## The Two Exports Must Stay in Sync

Both egg files describe the same server. Every behavioural change — startup command, `config.files`
mappings, install script, variable defaults, `file_denylist` — must land in **both**. The panels use
different schemas, so this is a translation, not a copy:

| Concern | `egg-*.yaml` (Pelican) | `egg-pterodactyl-*.json` (Pterodactyl) |
|---|---|---|
| Env var interpolation | `{{server.environment.VAR}}` | `{{server.build.env.VAR}}` |
| Startup command | `startup_commands.Default` | `startup` (plain string) |
| `config.files` / `startup` / `logs` | native YAML mappings | **JSON-encoded strings** inside the JSON |
| Variable rules | YAML list (`- required`, `- numeric`) | pipe string (`"required\|numeric"`) |
| Variable ordering / naming | `sort:` key, `[Server]`/`[RCON]` name prefixes | no `sort`; plain names, `field_type: "text"` |

`env_variable` names, `default_value`s, and rule semantics are identical across the pair; only display
names and ordering legitimately differ. `exported_at` timestamps also differ — that is expected, not drift.

Both files open with a `DO NOT EDIT: FILE GENERATED AUTOMATICALLY BY PANEL` comment and are committed
as panel exports (see commit `4efe1c1`, "sync current panel exports"). Hand-editing is workable for
small changes, but any change made only in the file and not in the panel will be lost on the next export.

## Common Change Workflows

**Changing an existing egg's behaviour**
1. Apply the change to `egg-<game>.yaml`.
2. Apply the equivalent change to `egg-pterodactyl-<game>.json`, translating per the table above.
3. Update `games-steamcmd/<game>/README.md` if the change affects ports, exposed variables, or the
   upgrade path for existing servers.
4. Confirm the YAML and JSON still parse before committing.

**Adding a new egg**
1. Create `games-steamcmd/<slug>/` with the four-file layout above.
2. Add a row to the `## Eggs` table in the root `README.md`.
3. If the egg ships a helper script, add its filename to `file_denylist` in both exports so panel users
   cannot edit or delete it.

**Changing `ini-merge.sh`** — see the constraints below; this file is not just a repo artifact.

## `ini-merge.sh` Is Fetched Over the Network

The HumanitZ install script downloads the helper by absolute URL:

```
https://raw.githubusercontent.com/engels74/pelican-eggs/refs/heads/main/games-steamcmd/humanitz/ini-merge.sh
```

Consequences that are easy to get wrong:

- **Moving or renaming the file breaks installs on the live `main` branch immediately.** If the path must
  change, update the URL in the install script of *both* exports in the same commit.
- Pushing a change to `main` reaches existing servers only on install/reinstall; boot runs the local copy
  written to `/mnt/server/ini-merge.sh`.
- The script is invoked on every boot from the startup command, guarded by
  `[ -f ./ini-merge.sh ] && bash ./ini-merge.sh ... || true`.

Its safety contract is deliberate and must be preserved: it uses `set -u` **without** `set -e`, logs
problems, and **always exits 0** so it can never block server boot. It only ever *adds* keys missing from
the live INI, writes via `mktemp` + atomic `mv`, keeps a `.bak`, and bails out if the merge produced empty
output. Do not add `set -e`, non-zero exits, or any path that rewrites or reorders existing keys — user
edits to `GameServerSettings.ini` are guaranteed to survive.

## HumanitZ-Specific Facts

- `SRCDS_BETAID` must remain `linuxbranch`: app `2728330` has no public-branch depot, so the Linux server
  files exist only on that beta. Both exports pin this with `in:linuxbranch` and mark it non-editable.
- Only a curated subset of `GameServerSettings.ini` is exposed as panel variables. The rest is left to the
  reference file plus the merge helper — do not widen `config.files` `find:` mappings without also updating
  `games-steamcmd/humanitz/README.md`, which documents this boundary to panel admins.

## Conventions

- Conventional Commits with the egg slug as scope: `feat(humanitz): ...`, `chore(renovate): ...`.
- `renovate.json` is a shared fleet policy (`config:recommended`, `group:allNonMajor`); change it only when
  deliberately diverging from that policy.

## Additional Documentation

- `games-steamcmd/humanitz/README.md` — read before changing HumanitZ variables, ports, the INI merge
  behaviour, or anything affecting how existing servers upgrade.
- Root `README.md` — read/update when adding, removing, or renaming an egg directory.
