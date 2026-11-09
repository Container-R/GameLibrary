#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
g++ -std=c++11 -O2 -Wall -Wextra -Ivendor ordering.cpp vendor/vcacheoptimizer.cpp vendor/vfetchoptimizer.cpp vendor/allocator.cpp -o ordering
./ordering > structure.json
python3 raster.py > raster.json
sha256sum ordering.cpp raster.py run.sh README.md structure.json raster.json *.rgba *.png vendor/* > checksums.sha256
