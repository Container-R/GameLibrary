"""Keep nearest warp and geometry fixed; vary only input overview policy."""
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

def run(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout

with TemporaryDirectory() as folder:
    d = Path(folder)
    asc, src = d/"ridge.asc", d/"ridge.tif"
    asc.write_text("ncols 10\nnrows 4\nxllcorner 0\nyllcorner 0\ncellsize 1\nNODATA_value -9999\n"
                   + "0 0 0 0 1 0 0 0 0 0\n"*4, encoding="ascii")
    run("gdal_translate", "-q", "-ot", "Float32", str(asc), str(src))
    run("gdaladdo", "-q", "-r", "average", str(src), "2")
    out = {}
    for policy in ("AUTO", "NONE"):
        tif, xyz = d/f"{policy}.tif", d/f"{policy}.xyz"
        run("gdalwarp", "-q", "-r", "near", "-ovr", policy,
            "-te", "1.25", "0", "9.25", "4", "-tr", "2", "2",
            "-ot", "Float32", str(src), str(tif))
        run("gdal_translate", "-q", "-of", "XYZ", str(tif), str(xyz))
        points = [list(map(float, line.split())) for line in xyz.read_text().splitlines()]
        out[policy] = [p[2] for p in points if p[1] == 3]
    assert out == {"AUTO":[0.0, 0.5, 0.0, 0.0], "NONE":[0.0, 1.0, 0.0, 0.0]}
    print(json.dumps(out, indent=2))
