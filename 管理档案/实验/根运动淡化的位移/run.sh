#!/bin/bash
set -e -o pipefail
cd "$(dirname "$0")"
t=$(mktemp -d)
trap 'rm -rf -- "$t"' EXIT
mkdir "$t"/{config,data,cache}
XDG_CONFIG_HOME="$t/config" XDG_DATA_HOME="$t/data" XDG_CACHE_HOME="$t/cache" GODOT_SILENCE_ROOT_WARNING=1 godot --headless --path . --script probe.gd | sed -n '/^{/,$p'
