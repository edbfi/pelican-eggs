#!/usr/bin/env bash
# Smoke: the shipped ini-merge.sh parses, passes ShellCheck and keeps its merge contract.
# Run from the repo root: uv run --no-project bash scripts/smoke.sh
set -euo pipefail
cd "$(dirname "$0")/.."

helper=games-steamcmd/humanitz/ini-merge.sh
bash -n "$helper"
shellcheck "$helper"
python3 -B -m unittest discover -s tests -v
