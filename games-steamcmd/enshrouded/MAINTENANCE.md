# Enshrouded maintenance

See the [README](README.md) for setup, ports and upgrade instructions.

## Configuration lifecycle

The installer downloads the [`enshrouded_server.json`](enshrouded_server.json) seed from this repository's `main` branch when no config exists. It contains the panel-managed keys and four standard groups; the installer assigns random group passwords. The first start applies panel values, and the server fills in other settings with the installed release's defaults.

An existing config with Admin, Friend, Guest and Visitor as its first four groups is left alone. Other layouts are backed up to `enshrouded_server.json.<timestamp>.bak` and rebuilt with the standard groups first. Settings, tags, bans and additional groups are preserved.

Wings writes panel values before every start. The server then rewrites the config with its current layout, adding missing settings at their defaults while retaining existing values. Unmanaged fields such as custom `gameSettings`, `tags`, additional groups and `bannedAccounts` remain editable. Custom game settings require the `Custom` difficulty preset.

The panel addresses groups by position, so the first four must remain in their standard order. Default permissions are:

| Group | Kick / ban | Access inventories | Edit world | Edit bases | Extend bases | Reserved slots |
|-------|------------|--------------------|------------|------------|--------------|----------------|
| Admin | On | On | On | On | On | 0 |
| Friend | Off | On | On | On | Off | 0 |
| Guest | Off | Off | On | Off | Off | 0 |
| Visitor | Off | Off | Off | Off | Off | 0 |

Extend Bases controls placing, upgrading and removing Flame Altars. Total reserved slots must stay at or below Max Players.

## Authentication and launch

The server uses `userGroups[].password`. The obsolete top-level `password` only supports migration of old configs and does not set the standard groups' passwords. A mismatch can disconnect players immediately after Steam authentication.

The egg uses `proton runinprefix` to launch the executable directly. Earlier testing with GE-Proton11-7 found intermittent startup hangs with `proton run` and confirmed clean shutdown and world saves with the current command.

The installer copies `steamclient.so` into `.steam/sdk64` for Proton's Steam integration. Omitting it can hang startup. The launcher ignores SIGINT so it does not kill Wine prematurely; Wine still receives the container's signal and delivers Ctrl+C to the game for a clean shutdown.

Enshrouded 1.0 requires GE-Proton 11 for `SteamUtils011`. Check the runtime version with `cat /usr/local/bin/version`. The runtime image supplies Proton, so an egg update alone does not update it.

## Pterodactyl compatibility

The JSON export is converted with [Scramble](https://redthirten.github.io/scramble-egg-converter/), with these adaptations:

- Group mappings use Pterodactyl's `userGroups[0].password` syntax.
- Text Chat and Voice Chat toggles are omitted: Wings cannot write JSON booleans for these settings. Edit `enableTextChat` and `enableVoiceChat` in the config instead.
- A startup prefix converts the first four groups' permission values from Wings' `0`/`1` values to JSON booleans. It requires Python 3, included in the runtime image, and stops startup if conversion fails.

The conversion preserves additional groups and unrelated settings. Pelican writes booleans directly and needs no conversion. Passwords must contain a non-digit character to prevent Pterodactyl's Wings from writing them as numbers.

## Checking new game releases

New settings normally need no egg change: the server adds them itself. Changes to the names or types of managed keys require updates to the egg and seed:

- `name`, `queryPort`, `slotCount`, `gameSettingsPreset`
- `enableTextChat`, `enableVoiceChat`, `voiceChatMode`
- Passwords, five permission fields and `reservedSlots` in the first four `userGroups`

From the repository root, run this on an x86_64 Linux host with Docker and about 10 GB free:

```bash
scripts/enshrouded-config-check.sh /tmp/enshrouded_server.json
```

It installs the public build with SteamCMD, starts it without a config in the runtime image without publishing ports, and checks the generated managed keys and types. Output passwords are blanked. Exit code 2 means a key is missing or has the wrong type. Supply a work directory as the second argument to reuse an installation.

CI's `.github/scripts/check-pair.py` also verifies the seed's managed keys, group defaults and export parity, including startup equivalence after stripping the Pterodactyl conversion prefix.
