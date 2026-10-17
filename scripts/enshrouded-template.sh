#!/usr/bin/env bash
# Regenerate games-steamcmd/enshrouded/enshrouded_server.json from the current Enshrouded server.
# The depot ships no enshrouded_server.json: the server writes one on its first start. This installs
# the public build with SteamCMD, starts it once under the egg's Proton image without a config, and
# writes the file it generated with the user-group passwords blanked.
# Needs Docker on an x86_64 Linux host and about 10 GB in WORK_DIR. Publishes no ports.
# Usage: scripts/enshrouded-template.sh OUTPUT_JSON [WORK_DIR]
set -euo pipefail

out=${1:?usage: $0 OUTPUT_JSON [WORK_DIR]}
work=${2:-$(mktemp -d)}
installer=ghcr.io/pelican-eggs/installers:debian
runtime=ghcr.io/pelican-eggs/steamcmd:proton
name="enshrouded-template-$$"

mkdir -p "$work"
work=$(cd "$work" && pwd)
trap 'docker rm -f "$name" >/dev/null 2>&1 || true' EXIT
docker pull -q "$installer" >/dev/null
docker pull -q "$runtime" >/dev/null

# Install or update the public build, owned by the runtime image's user (uid 1000).
docker run --rm -v "$work:/mnt/server" "$installer" bash -c '
    set -e
    cd /mnt/server
    if [ ! -x steamcmd/steamcmd.sh ]; then
        mkdir -p steamcmd
        curl -fsSL https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz | tar -xz -C steamcmd
    fi
    mkdir -p steamapps .steam/sdk32 .steam/sdk64
    export HOME=/mnt/server
    for attempt in 1 2 3; do
        steamcmd/steamcmd.sh +@sSteamCmdForcePlatformType windows +force_install_dir /mnt/server \
            +login anonymous +app_update 2278520 validate +quit || true
        [ -f enshrouded_server.exe ] && break
    done
    [ -f enshrouded_server.exe ]
    cp steamcmd/linux32/steamclient.so .steam/sdk32/
    cp steamcmd/linux64/steamclient.so .steam/sdk64/
    chown -R 1000:1000 /mnt/server'

# Start without a config so the server generates one, as the egg's startup command does.
rm -rf "$work/enshrouded_server.json" "$work/logs"
docker run -dit --name "$name" -v "$work:/home/container" -w /home/container "$runtime" bash -c '
    mkdir -p .steam/steam/steamapps/compatdata/2278520
    export STEAM_COMPAT_CLIENT_INSTALL_PATH=/home/container/.steam/steam
    export STEAM_COMPAT_DATA_PATH=/home/container/.steam/steam/steamapps/compatdata/2278520
    exec proton runinprefix ./enshrouded_server.exe' >/dev/null
for _ in $(seq 1 60); do
    grep -qs "'HostOnline' (up)" "$work/logs/enshrouded_server.log" && break
    sleep 5
done
if ! grep -qs "'HostOnline' (up)" "$work/logs/enshrouded_server.log"; then
    echo "The server did not come up; see $work/logs" >&2
    exit 1
fi
docker stop -t 30 "$name" >/dev/null

# Blank the generated (random) group passwords; the installer and the panel set their own.
sed -E 's/^([[:space:]]*"password": )"([^"\\]|\\.)*"/\1""/' "$work/enshrouded_server.json" > "$out"
if [ "$(grep -c '"password": ""' "$out")" -ne 4 ]; then
    echo "Expected four blanked user-group passwords in $out" >&2
    exit 1
fi
[ -z "$(tail -c1 "$out")" ] || echo >> "$out"

build=$(sed -n 's/^[[:space:]]*"buildid"[[:space:]]*"\([0-9]*\)".*/\1/p' "$work/steamapps/appmanifest_2278520.acf")
proton=$(docker run --rm --entrypoint cat "$runtime" /usr/local/bin/version)
echo "Wrote $out from build $build (${proton##* }, $(date -u +%F)). Work dir: $work"
