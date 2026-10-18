# Enshrouded (Proton)


## [Documentation](https://enshrouded.zendesk.com/hc/en-us/articles/16055441447709-Dedicated-Server-Configuration)


Enshrouded is a game of survival, crafting and Action RPG combat on a voxel-based continent. Its dedicated server (Steam app `2278520`) is Windows-only; this egg runs it under GE-Proton.

The authoritative reference for every setting is `enshrouded_server_readme.txt`, which SteamCMD installs next to `enshrouded_server.exe`.

## Differences from the upstream egg

This egg is written from scratch; only the SteamCMD bootstrap of the install script is the usual steamcmd egg block. Compared with the upstream `pelican-eggs/games-steamcmd` Enshrouded egg:

| | Upstream | This egg |
|---|---|---|
| Password | Writes a top-level `password`, which the server has ignored since update 2 (2024-06-05) | Sets `userGroups[].password` of the Admin, Friend, Guest and Visitor groups |
| New config | Pre-1.0 file without `userGroups` | A seed of the managed keys that the server completes with the installed release's defaults |
| `gamePort` | Written, although the server no longer has one | Not used; the primary allocation is `queryPort` |
| Launch | `proton run`, which goes through Proton's `steam.exe` shim | `proton runinprefix`, which starts the exe directly |
| Stop | `^C` kills the server within 2 s, before it saves | `^C` shuts the server down cleanly and saves the world |
| Docker image | `ghcr.io/parkervcp/steamcmd:proton` | `ghcr.io/pelican-eggs/steamcmd:proton` |
| `update_url` (Pelican) | upstream egg | this file on `edbfi/pelican-eggs` `main` |

### Why players were disconnected after Steam authentication

The upstream egg writes the panel password to a top-level `password` key. The shipped readme says the server no longer uses that key, except to migrate an old file that has no `userGroups` into a single `Default` group. The server also drops the key whenever it rewrites the file. The passwords that count are those of the `userGroups`, which the server generates randomly; a config reported from the upstream egg had a single `Default` group with a generated password. Players enter the panel password, it matches no group, and the server drops them right after Steam authentication, as in [mornedhels/enshrouded-server#95](https://github.com/mornedhels/enshrouded-server/issues/95):

```text
[I] [online] Client '7656…' authenticated by steam
[W] [session] Unable to find machine for peer 0(1).
[W] [session] Could not store acknowledge of packet id: 72.
[I] [online] Disconnecting peer 0(1)
```

The `m#0(128) … EstablishingBaseline` line in the periodic session report is the server's own machine and also appears on healthy servers.

### Why the launch changed

Tested on a scratch copy of the server with GE-Proton11-7 (the image's Proton at the time):

| Startup | Started | `^C` |
|---|---|---|
| `proton run ./enshrouded_server.exe` | 3 of 6 starts hung before writing a log | Server killed after about 2 s, no save |
| `trap '' INT; proton runinprefix ./enshrouded_server.exe …; wait` | 6 of 6, `HostOnline` after about 2 s | Clean shutdown, world saved, exit code 0 |

`runinprefix` runs the exe in the prepared prefix without the `steam.exe` shim. Steam still works through Proton's `lsteamclient` (`Server connected to Steam successfully`), which loads the `steamclient.so` the installer copies to `.steam/sdk64`. Without that file the server hangs at start.

On `^C`, Wings sends SIGINT to the whole container process group. Proton's Python launcher would turn it into a KeyboardInterrupt and kill Wine, so the startup command ignores SIGINT for the launcher. Wine still receives it, turns it into a console Ctrl+C, and the server runs its normal shutdown.

## Server Ports

| Port | default | Protocol |
|------|---------|----------|
| Game/Query Port | 15637 | UDP |

### Notes

The server has a single port, `queryPort`. The egg sets it to the server's primary allocation; no other allocation is needed.

## Panel variables

| Category | Variable | `enshrouded_server.json` |
|---|---|---|
| Server | Server Name, Max Players (1–16), Difficulty Preset | `name`, `slotCount`, `gameSettingsPreset` |
| Admin, Friend, Guest, Visitor | Password, Kick / Ban Players, Access Inventories, Edit World, Edit Bases, Extend Bases, Reserved Slots (one section per group) | `userGroups[0..3].password`, `canKickBan`, `canAccessInventories`, `canEditWorld`, `canEditBase`, `canExtendBase`, `reservedSlots` |
| Chat | Text Chat, Voice Chat, Voice Chat Mode | `enableTextChat`, `enableVoiceChat`, `voiceChatMode` |
| Steam | Auto Update, Validate Files | – (SteamCMD on start) |

The passwords are required and have no default, so every server gets its own. A password must not consist of digits only: Pterodactyl's Wings would write it as a JSON number.

Each group has five permission toggles and a reserved-slot count, pre-filled from the shipped [`enshrouded_server.json`](enshrouded_server.json) seed:

| Group | Kick / ban | Access inventories | Edit world | Edit bases | Extend bases | Reserved slots |
|---|---|---|---|---|---|---|
| Admin | On | On | On | On | On | 0 |
| Friend | Off | On | On | On | Off | 0 |
| Guest | Off | Off | On | Off | Off | 0 |
| Visitor | Off | Off | Off | Off | Off | 0 |

Give players the Friend password for the default building and container permissions, or adjust its toggles to suit your server. Extend Bases controls placing, upgrading and removing Flame Altars. Reserved slots keep room for that group when other groups fill the server; keep the total across all groups at or below Max Players. The group permissions are documented in the readme that ships with the server and the [server roles guide](https://enshrouded.zendesk.com/hc/en-us/articles/19191581489309-Server-Roles-Configuration).

## Config

`enshrouded_server.json` lives in the server root. Wings writes the panel values into it before every start, and the server then rewrites the file with its full current layout. Set the first four groups' passwords, permissions and reserved slots in the panel: file edits to those fields are overwritten on start. Everything the panel does not manage stays editable and is kept: `gameSettings` (used when the preset is `Custom`), `tags`, further groups after the first four, and `bannedAccounts`. Edit the file while the server is stopped; the server rewrites it on start and when a player is banned.

The panel sets the group options by position, so the first four `userGroups` must stay Admin, Friend, Guest and Visitor in that order. Updating an existing egg adds the new options at their defaults; copy any customized permissions or reserved slots from your config into the panel before the next start.

### Install and reinstall

When the file is missing, the installer downloads the seed [`enshrouded_server.json`](enshrouded_server.json) from this repository's `main` branch, as the HumanitZ egg does with its helper script, and gives the four groups random passwords. The seed holds only the keys the panel manages, typed as the server expects them, plus the four standard groups. The installer stops if the download fails or the seed lacks the standard groups, and `.github/scripts/check-pair.py` checks in CI that every key the egg writes exists in it. The first start applies the panel's values, and the server fills in everything else with the defaults of the installed release. The result is identical to the file the server generates on its own, apart from the passwords. An existing file whose first four groups are the standard ones is left alone.

Any other existing file, for example one from the upstream egg with a single `Default` group, is backed up to `enshrouded_server.json.<timestamp>.bak` and rebuilt. Its settings, tags and bans are kept, the standard groups come first, and its other groups follow them. Upgrading from the upstream egg therefore takes one reinstall. Back up `savegame/` first anyway.

## New game releases

The egg keeps no full copy of `enshrouded_server.json`, only the seed of the keys it manages. The depot does not supply the file either: it installs `enshrouded_server_readme.txt`, which documents every setting, but the config only comes into existence when the server starts. The server then keeps the file current on every start: it adds settings it is missing, at their defaults, and keeps existing values. With build `25988414` (GE-Proton11-7), removing `tags`, `bannedAccounts` and three 1.0 `gameSettings` keys from a file brought them back on the next start, while a changed `playerHealthFactor` stayed. A release that adds settings therefore needs nothing from the egg, for new and existing servers alike.

A release only needs an egg change if Keen renames or removes a key the egg manages, or changes the types: `name`, `queryPort`, `slotCount`, `gameSettingsPreset`, `enableTextChat`, `enableVoiceChat`, `voiceChatMode` and the first four `userGroups`. Wings would keep writing the old key and the server would drop it, so the panel setting would have no effect. To check a release, run this on an x86_64 Linux host with Docker and about 10 GB free:

```bash
scripts/enshrouded-config-check.sh /tmp/enshrouded_server.json
```

It installs the public build with SteamCMD into a work directory and starts it once without a config in the egg's runtime image, publishing no ports. It writes the generated file with blanked passwords and checks those keys. It exits 2 if any key is missing or has the wrong type. Passing a work directory as the second argument reuses an earlier install.

## Proton

`ghcr.io/pelican-eggs/steamcmd:proton` ([Dockerfile](https://github.com/pelican-eggs/yolks/blob/master/steamcmd/proton/Dockerfile)) downloads the latest GE-Proton release when the image is built. The [steamcmd workflow](https://github.com/pelican-eggs/yolks/blob/master/.github/workflows/steamcmd.yml) is scheduled to rebuild it every Monday, but the schedule does not always run. On 2026-10-18 the image contained GE-Proton11-7, built 2026-10-04, while the newest release was GE-Proton11-9. Wings pulls the image again when a server starts, so a rebuilt image reaches servers without changing the egg. Check the version inside a server with `cat /usr/local/bin/version`.

Enshrouded 1.0 needs GE-Proton 11 for Steamworks (`SteamUtils011`); with GE-Proton 10 the server fails with `No SteamUtils011`.

## Pterodactyl

`egg-pterodactyl-enshrouded.json` is this egg converted with [Scramble](https://redthirten.github.io/scramble-egg-converter/), plus three changes for Pterodactyl's Wings:

- Array elements use its `userGroups[0].password` syntax for all group settings.
- The Text Chat and Voice Chat toggles are left out. Pterodactyl's Wings can only write a variable as a string or a number, and the server resets a non-boolean chat setting to `false`. Set `enableTextChat` and `enableVoiceChat` in the file instead.
- Its startup command converts the first four groups' five permission fields from Wings' `0`/`1` values into JSON booleans before launching the game.

The conversion runs only in the Pterodactyl export and preserves unrelated settings and additional groups. It uses Python 3, which is included in the Proton image; a failed conversion stops startup. Pelican writes JSON booleans directly and retains its original startup command. The parity check requires the Pterodactyl command after conversion to match Pelican's startup.

## Egg updates

The Pelican export's `update_url` points at `egg-enshrouded.yaml` on `main`. Pelican checks it daily and shows an **Update** button when the file differs from the egg in your panel. Updating overwrites any panel-side edits to the egg. Set the same URL under **Admin → Eggs → Enshrouded (Proton) → Update URL**, otherwise the next export from your panel writes `null` back.
