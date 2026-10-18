# HumanitZ

Runs the native Linux dedicated server for HumanitZ.

[Pelican egg](egg-humanitz.yaml) · [Pterodactyl egg](egg-pterodactyl-humanitz.json) · [Installation and updates](../../README.md#installation)

## Ports

| Port | Default | Protocol |
|------|---------|----------|
| Game | 7777 | UDP |
| Query | 27015 | UDP |
| RCON (optional) | 8888 | TCP |

Use the primary allocation for the game port. Add an allocation matching `QUERY_PORT`, and one matching `RCON_PORT` if RCON is enabled.

## Configuration

Set server identity, passwords, player limits and RCON options in the panel. Keep the default Steam beta branch, `linuxbranch`, for the Linux server.

For advanced settings, stop the server and edit `HumanitZServer/GameServerSettings.ini`. Panel-managed keys are overwritten on startup; other settings are preserved.

The included `REF_GameServerSettings.ini` lists the available settings. The egg's merge helper adds missing keys from that reference on startup and reinstall, preserving existing values and custom keys.

## Notes

- Requires a 64-bit Linux host.
- Upgrading an existing server to this egg: back up configs and saves, update the egg, then reinstall once to install the merge helper. Fresh installs need no extra steps.
- RCON is disabled by default. Set a password before enabling it.

## Documentation

[Private server hosting guide](https://humanitz.wiki.gg/wiki/Private_Server_Hosting_Setup)

The installed `README.txt` describes most server variables.
