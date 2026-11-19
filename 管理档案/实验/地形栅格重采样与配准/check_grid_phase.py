"""Synthetic 1 m height raster -> 2 m GDAL targets. No Mars assets needed."""
import json
import subprocess
from tempfile import TemporaryDirectory
from pathlib import Path

def run(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout

with TemporaryDirectory() as t:
    d = Path(t)
    src = d / "ridge.asc"
    src.write_text("ncols 10\nnrows 4\nxllcorner 0\nyllcorner 0\ncellsize 1\nNODATA_value -9999\n"
                   + ("0 0 0 0 1 0 0 0 0 0\n"*4), encoding="ascii")
    results = {}
    for phase in (0, 1, 0.25, 1.25):
        for method in ("near", "average"):
            tif = d / f"offset-{phase}-{method}.tif"
            xyz = d / "output.xyz"
            # Source Z is clipped to identical interior rows; require all centers valid.
            run("gdalwarp", "-q", "-r", method, "-te", str(phase), "0", str(phase+8), "4",
                "-tr", "2", "2", "-ot", "Float32", str(src), str(tif))
            run("gdal_translate", "-q", "-of", "XYZ", str(tif), str(xyz))
            centers, heights = [], []
            for line in xyz.read_text().splitlines():
                x, y, z = map(float, line.split())
                if y == 3:
                    centers.append(x)
                    heights.append(z)
            assert len(centers) == 4 and all(z >= 0 for z in heights)
            results[f"origin_{phase}_{method}"] = {"centers_x_m": centers, "height_m": heights}
    assert results["origin_0_near"]["height_m"] == [0, 0, 0, 0]
    assert results["origin_1_near"]["height_m"] == [0, 1, 0, 0]
    assert results["origin_0_average"]["height_m"] == [0, 0, 0.5, 0]
    assert results["origin_1_average"]["height_m"] == [0, 0.5, 0, 0]
    assert results["origin_0.25_near"]["height_m"] == [0, 0, 0, 0]
    assert results["origin_1.25_near"]["height_m"] == [0, 1, 0, 0]
    assert results["origin_0.25_average"]["height_m"] == [0, 0.125, 0.375, 0]
    assert results["origin_1.25_average"]["height_m"] == [0, 0.5, 0, 0]
    print(json.dumps({"gdal":run("gdalwarp","--version").strip(),"profile":results},indent=2))
