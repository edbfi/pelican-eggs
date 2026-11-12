<p align="center">
  <img src="assets/pelican-eggs.svg" alt="pelican-eggs logo" width="160" height="160">
</p>

<h1 align="center">pelican-eggs</h1>

<p align="center"><strong>Game-server eggs for Pelican and Pterodactyl.</strong></p>

<p align="center">
  <a href="https://github.com/edbfi/pelican-eggs/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL--3.0--or--later-blue?style=flat" alt="License: AGPL-3.0-or-later"></a>
  <a href="https://github.com/pelican/panel"><img src="https://img.shields.io/badge/Pelican-0F766E?style=flat" alt="Pelican"></a>
  <a href="https://github.com/pterodactyl/panel"><img src="https://img.shields.io/badge/Pterodactyl-10529F?style=flat" alt="Pterodactyl"></a>
</p>

My personal collection of game-server eggs for [Pelican](https://pelican.dev) and Pterodactyl.

## Eggs

| Game | Setup and downloads |
|------|---------------------|
| Enshrouded (Proton) | [README](games-steamcmd/enshrouded/README.md) |
| HumanitZ | [README](games-steamcmd/humanitz/README.md) |
| Icarus (Proton) | [README](games-steamcmd/icarus-proton/README.md) |

## Installation

1. Download the Pelican `.yaml` or Pterodactyl `.json` egg linked in the game's README.
2. Import it into your panel, then create a server using that egg.
3. Assign the ports and configure the panel variables described in the game's README.

## Egg updates

Pelican exports include an `update_url` pointing to their YAML file on this repository's `main` branch. Pelican checks daily and offers an **Update** button when the egg changes. Updates overwrite panel-side edits to the egg.

In your source panel, set **Admin → Eggs → [egg] → Update URL** to the export's `meta.update_url`, so later exports retain it. Pterodactyl users can download and import the updated JSON export.

Follow any game-specific upgrade notes before starting existing servers. Back up configs and saves before reinstalling.

## README format

Keep each egg README around 150–250 words: title and one-sentence description, download links, then **Ports**, **Configuration**, **Notes**, and **Documentation**. Include only setup details and essential caveats; link to separate maintenance notes for implementation details.

## License

Original code by edbfi is licensed under the [GNU Affero General Public License](LICENSE), version 3 or (at your option) any later version (`AGPL-3.0-or-later`).

Inherited eggs and third-party components retain their original licenses and author notices, including the MIT-licensed Icarus installer.
