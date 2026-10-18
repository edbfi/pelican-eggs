# Enshrouded (Proton)

Runs the Windows dedicated server on Linux using GE-Proton.

[Pelican egg](egg-enshrouded.yaml) · [Pterodactyl egg](egg-pterodactyl-enshrouded.json) · [Installation and updates](../../README.md#installation)

## Ports

| Port | Default | Protocol |
|------|---------|----------|
| Query | 15637 | UDP |

Use the primary allocation for the query port. No additional ports are needed.

## Configuration

Set the server name, player limit, difficulty, group passwords and permissions in the panel. Passwords are required and must include a non-digit character.

Edit other settings in `enshrouded_server.json` while the server is stopped. Panel-managed values are overwritten on startup; other settings are preserved.

Keep the first four groups in this order: Admin, Friend, Guest, Visitor. Give players the Friend password for the default building permissions. Keep total reserved slots at or below Max Players.

## Notes

- Requires GE-Proton 11 or newer.
- Pterodactyl: set `enableTextChat` and `enableVoiceChat` directly in the config file.
- Migrating from the upstream egg: back up `savegame/`, update the egg, then reinstall once.
- When updating an existing egg, copy customized group permissions and reserved slots into the panel before the next start.

## Documentation

[Server configuration](https://enshrouded.zendesk.com/hc/en-us/articles/16055441447709-Dedicated-Server-Configuration) · [Server roles](https://enshrouded.zendesk.com/hc/en-us/articles/19191581489309-Server-Roles-Configuration) · [Maintenance notes](MAINTENANCE.md)

The installed `enshrouded_server_readme.txt` documents every server setting.
