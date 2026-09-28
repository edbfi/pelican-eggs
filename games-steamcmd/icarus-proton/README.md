# Icarus (Proton)


## [Documentation](https://github.com/RocketWerkz/IcarusDedicatedServer)


Icarus is a PvE survival game with dedicated servers. This egg runs the Windows dedicated server under GE-Proton instead of Wine.

## Differences from the upstream Wine egg

This egg is built from the upstream `pelican-eggs/games-steamcmd` Icarus egg. The install script, variables and `config` are unchanged. Only the runtime differs:

| | Upstream (Wine) | This egg (Proton) |
|---|---|---|
| Docker image | `ghcr.io/pelican-eggs/yolks:wine_latest` | `ghcr.io/pelican-eggs/steamcmd:proton` |
| Launcher | `wine` | `xvfb-run -a proton run`, with `SteamAppId`/`SteamGameId` set to `1149460` (the Icarus game app) |
| Save location | default | `-UserDir="Z:/home/container/Icarus"`, so saves, config and logs stay under `/home/container/Icarus/Saved` |
| Process handling | `tail` on the log | `tail` on the log, then `wait` on the server PID |
| `update_url` | upstream egg | `null`, so a panel update check cannot replace this egg with the Wine one |

## Server Ports

| Port         | default |
|--------------|---------|
| Game Port    | 17777   |
| Query Port   | 27015   |

### Notes

The game port is the server's primary allocation. The query port is set by the `QUERY_PORT` variable.

The server config is `Icarus/Saved/Config/ServerSettings.ini`. The installer fetches the upstream template from RocketWerkz only if the file does not already exist.
