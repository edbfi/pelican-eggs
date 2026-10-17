# Enshrouded (Proton)


## [Documentation](https://enshrouded.zendesk.com/hc/en-us/articles/16055441447709-Dedicated-Server-Configuration)


Enshrouded is a game of survival, crafting and Action RPG combat on a voxel-based continent. Its dedicated server (Steam app `2278520`) is Windows-only; this egg runs it under GE-Proton.

The authoritative reference for every setting is `enshrouded_server_readme.txt`, which SteamCMD installs next to `enshrouded_server.exe`.

## Differences from the upstream egg

This egg is written from scratch; only the SteamCMD bootstrap of the install script is the usual steamcmd egg block. Compared with the upstream `pelican-eggs/games-steamcmd` Enshrouded egg:

| | Upstream | This egg |
|---|---|---|
| Password | Writes a top-level `password`, which the server has ignored since update 2 (2024-06-05) | Sets `userGroups[].password` of the Admin, Friend, Guest and Visitor groups |
| Config template | Pre-1.0 file without `userGroups` | The file the current server generates itself ([below](#config-template)) |
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
| Access | Admin, Friend, Guest and Visitor Password | `userGroups[0..3].password` |
| Chat | Text Chat, Voice Chat, Voice Chat Mode | `enableTextChat`, `enableVoiceChat`, `voiceChatMode` |
| Steam | Auto Update, Validate Files | – (SteamCMD on start) |

The passwords are required and have no default, so every server gets its own. A password must not consist of digits only: Pterodactyl's Wings would write it as a JSON number.

Give players the Friend password for the usual permissions (build and use containers). The group permissions are documented in the readme that ships with the server.

## Config

`enshrouded_server.json` lives in the server root. Wings writes the panel values into it before every start, and the server then rewrites the file with its full current layout. Everything the panel does not manage stays editable and is kept: `gameSettings` (used when the preset is `Custom`), `tags`, the group permissions and reserved slots, further groups after the first four, and `bannedAccounts`. Edit the file while the server is stopped; the server rewrites it on start and when a player is banned.

The panel sets the group passwords by position, so the first four `userGroups` must stay Admin, Friend, Guest and Visitor in that order.

### Install and reinstall

The installer creates the file from the [template](#config-template) when it is missing, with random group passwords until the first start applies the panel's. An existing file whose first four groups are the standard ones is left alone.

Any other existing file, for example one from the upstream egg with a single `Default` group, is backed up to `enshrouded_server.json.<timestamp>.bak` and rebuilt. Its settings, tags and bans are kept, the standard groups come first, and its other groups follow them. Upgrading from the upstream egg therefore takes one reinstall. Back up `savegame/` first anyway.

## Config template

`enshrouded_server.json` in this directory is the file the dedicated server writes on its first start without a config. The only change is that the four group passwords are blanked. The current copy comes from server build `25988414` (public branch, 2026-10-16) under GE-Proton11-7. It matches the "DEFAULT enshrouded_server.json / VERSION 1.0.0.0" section of the shipped readme, except that the server writes `randomSpawnerAmount: "Automatic"`, which the readme lists as the 1.0 default elsewhere.

SteamCMD does not supply this file: the depot contains `enshrouded_server_readme.txt` but no `enshrouded_server.json`. The server generates the file only when it starts, so refreshing the template means running the server once.

### Refreshing it

On an x86_64 Linux host with Docker and about 10 GB free:

```bash
scripts/enshrouded-template.sh games-steamcmd/enshrouded/enshrouded_server.json
```

The script installs the public build with SteamCMD into a work directory, starts it once without a config in the egg's runtime image (no ports published), stops it after `HostOnline`, and writes the generated file with blanked passwords. It prints the build ID and Proton version to record above. Review the diff before committing. A new key needs nothing else, but a renamed or removed key that the egg manages also needs an egg change. Passing a work directory as the second argument reuses an earlier install.

Refresh the template after game updates that add settings. An outdated template only affects new installs, because the server adds missing keys to existing files itself.

### Automating it (not implemented)

A daily workflow like [icarus-bevy's release watch](https://github.com/edbfi/icarus-bevy/blob/main/.github/workflows/release-watch.yml) could compare the public build ID with the one recorded here. Reading it with `steamcmd +app_info_print 2278520` is anonymous and cheap. On a change, the workflow would open an issue. Regenerating the template in CI is feasible: a GitHub-hosted runner has Docker, and the script needs only anonymous SteamCMD. It is heavy, though: an 8 GB depot download plus the Proton image on every run. So it fits a manually dispatched job that opens a pull request better than the daily check.

## Proton

`ghcr.io/pelican-eggs/steamcmd:proton` ([Dockerfile](https://github.com/pelican-eggs/yolks/blob/master/steamcmd/proton/Dockerfile)) downloads the latest GE-Proton release when the image is built. The [steamcmd workflow](https://github.com/pelican-eggs/yolks/blob/master/.github/workflows/steamcmd.yml) is scheduled to rebuild it every Monday, but the schedule does not always run. On 2026-10-18 the image contained GE-Proton11-7, built 2026-10-04, while the newest release was GE-Proton11-9. Wings pulls the image again when a server starts, so a rebuilt image reaches servers without changing the egg. Check the version inside a server with `cat /usr/local/bin/version`.

Enshrouded 1.0 needs GE-Proton 11 for Steamworks (`SteamUtils011`); with GE-Proton 10 the server fails with `No SteamUtils011`.

## Pterodactyl

`egg-pterodactyl-enshrouded.json` is this egg converted with [Scramble](https://redthirten.github.io/scramble-egg-converter/), plus two changes for Pterodactyl's Wings:

- Array elements use its `userGroups[0].password` syntax.
- The Text Chat and Voice Chat toggles are left out. Pterodactyl's Wings can only write a variable as a string or a number, and the server resets a non-boolean chat setting to `false`. Set `enableTextChat` and `enableVoiceChat` in the file instead.

## Egg updates

The Pelican export's `update_url` points at `egg-enshrouded.yaml` on `main`. Pelican checks it daily and shows an **Update** button when the file differs from the egg in your panel. Updating overwrites any panel-side edits to the egg. Set the same URL under **Admin → Eggs → Enshrouded (Proton) → Update URL**, otherwise the next export from your panel writes `null` back.
