#!/bin/sh
set -eu
src=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp "$src/check_loop.gd" "$src/project.godot" "$tmp/"
mkdir "$tmp/cache" "$tmp/config" "$tmp/data"
XDG_CACHE_HOME="$tmp/cache" XDG_CONFIG_HOME="$tmp/config" XDG_DATA_HOME="$tmp/data" GODOT_SILENCE_ROOT_WARNING=1 timeout 20 godot --headless --path "$tmp" -s check_loop.gd -- "$@" >"$tmp/stdout" 2>"$tmp/stderr" || { cat "$tmp/stdout" "$tmp/stderr" >&2; exit 1; }
[ ! -s "$tmp/stderr" ] || { cat "$tmp/stderr" >&2; exit 1; }
[ "$(grep -c '^RESULT=' "$tmp/stdout")" -eq 1 ]
sed -n 's/^RESULT=//p' "$tmp/stdout"
