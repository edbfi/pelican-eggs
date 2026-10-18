# Icarus (Proton)

Runs the Windows dedicated server on Linux using GE-Proton.

[Pelican egg](egg-icarus-proton.yaml) · [Pterodactyl egg](egg-pterodactyl-icarus-proton.json) · [Installation and updates](../../README.md#installation)

## Ports

| Port | Default | Protocol |
|------|---------|----------|
| Game | 17777 | UDP |
| Query | 27015 | UDP |

Use the primary allocation for the game port. Add an allocation matching the `QUERY_PORT` panel variable.

## Configuration

Set the server name, query port and automatic updates in the panel.

For other settings, stop the server and edit `Icarus/Saved/Config/ServerSettings.ini`. The installer downloads the upstream template only when this file is missing, preserving an existing config on reinstall.

Saves, config and logs live under `Icarus/Saved` inside the server's files (`/home/container/Icarus/Saved` in the container).

## Notes

- Uses the `ghcr.io/pelican-eggs/steamcmd:proton` runtime image.
- The launcher sets `SteamAppId` and `SteamGameId` to `1149460` and uses `-UserDir` to keep server data in the location above.
- This is a Proton variant of the upstream Wine egg; its install script and panel variables are unchanged.

## Documentation

[Official dedicated server guide](https://github.com/RocketWerkz/IcarusDedicatedServer)
