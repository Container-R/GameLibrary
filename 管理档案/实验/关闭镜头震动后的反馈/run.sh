#!/bin/sh
set -eu
cd "$(dirname "$0")"
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
mkdir -p "$scratch/cache" "$scratch/data" "$scratch/config"
HOME="$scratch" XDG_CACHE_HOME="$scratch/cache" XDG_DATA_HOME="$scratch/data" XDG_CONFIG_HOME="$scratch/config" \
  godot --headless --path . --script probe.gd -- --fixture
