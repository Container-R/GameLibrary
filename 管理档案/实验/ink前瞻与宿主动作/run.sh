#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
# Pass absolute paths to an extracted .NET 8.0.428 SDK and inklecate v1.2.1 release.
sdk=$1
ink=$2
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT
for f in permission glue tagged; do
  "$ink/inklecate" -o "$tmp/$f.json" "$f.ink"
done
refs=( "$sdk"/packs/Microsoft.NETCore.App.Ref/*/ref/net8.0/*.dll )
args=()
for p in "${refs[@]}"; do args+=("-r:$p"); done
cp "$ink/ink-engine-runtime.dll" "$tmp/"
"$sdk/dotnet" "$sdk/sdk/8.0.428/Roslyn/bincore/csc.dll" \
  -nologo -noconfig -nostdlib -target:exe "-out:$tmp/InkProbe.dll" \
  "${args[@]}" "-r:$tmp/ink-engine-runtime.dll" Program.cs
printf '%s\n' '{"runtimeOptions":{"tfm":"net8.0","framework":{"name":"Microsoft.NETCore.App","version":"8.0.0"}}}' >"$tmp/InkProbe.runtimeconfig.json"
(cd -- "$tmp" && "$sdk/dotnet" InkProbe.dll)
