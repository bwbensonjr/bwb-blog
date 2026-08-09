"""Turn the raw Overpass output into the GeoJSON the map actually loads.

Writes two files so the national view is not paying for street-level vertices:

  us20.geojson       simplified, one MultiLineString per state, for zoom <= 9
  us20-detail.geojson full resolution, swapped in at higher zoom

Pure stdlib Douglas-Peucker so this needs no GDAL/shapely.
"""

import json
import math

# Source defaults to the OSM route relations; pass us20_tiger.json to build from
# the Census extract instead.
RAW = "us20_raw.json"
COARSE_OUT = "../us20.geojson"
DETAIL_OUT = "../us20-detail.geojson"

# Degrees. ~0.001 deg latitude is roughly 111 m. At the national view a
# tolerance around 200 m is invisible.
COARSE_TOLERANCE = 0.002


def perpendicular_distance(pt, start, end):
    if start == end:
        return math.dist(pt, start)
    x0, y0 = pt
    x1, y1 = start
    x2, y2 = end
    num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    return num / math.dist(start, end)


def douglas_peucker(points, tolerance):
    if len(points) < 3:
        return points
    dmax, index = 0.0, 0
    for i in range(1, len(points) - 1):
        d = perpendicular_distance(points[i], points[0], points[-1])
        if d > dmax:
            dmax, index = d, i
    if dmax <= tolerance:
        return [points[0], points[-1]]
    left = douglas_peucker(points[:index + 1], tolerance)
    right = douglas_peucker(points[index:], tolerance)
    return left[:-1] + right


def stitch(lines):
    """Join lines that share an endpoint into longer runs.

    OSM splits US 20 into roughly 8,900 short ways. Simplifying each way in
    isolation cannot go below two points per way, which puts a hard floor of
    ~18,000 points on the coarse file. Chaining them first lets Douglas-Peucker
    actually work, and drops the national-view file by roughly 10x.
    """
    remaining = {i: [tuple(p) for p in line] for i, line in enumerate(lines) if len(line) > 1}
    by_end = {}
    for i, line in remaining.items():
        by_end.setdefault(line[0], []).append(i)
        by_end.setdefault(line[-1], []).append(i)

    def take(endpoint):
        """Pop an unused line that starts or ends at this point."""
        for i in by_end.get(endpoint, []):
            if i in remaining:
                line = remaining.pop(i)
                return line if line[0] == endpoint else line[::-1]
        return None

    runs = []
    while remaining:
        i = next(iter(remaining))
        run = remaining.pop(i)
        # Extend forward, then backward, following shared endpoints.
        while True:
            nxt = take(run[-1])
            if nxt is None:
                break
            run.extend(nxt[1:])
        while True:
            prv = take(run[0])
            if prv is None:
                break
            run[:0] = prv[::-1][:-1]
        runs.append(run)
    return runs


def simplify_feature(feature, tolerance):
    lines = [
        douglas_peucker(line, tolerance)
        for line in stitch(feature["geometry"]["coordinates"])
    ]
    return {
        "type": "Feature",
        "properties": feature["properties"],
        "geometry": {
            "type": "MultiLineString",
            "coordinates": [[list(p) for p in line] for line in lines if len(line) > 1],
        },
    }


def count_points(fc):
    return sum(
        len(line)
        for f in fc["features"]
        for line in f["geometry"]["coordinates"]
    )


def main(raw=RAW):
    with open(raw) as f:
        detail = json.load(f)

    coarse = {
        "type": "FeatureCollection",
        "features": [simplify_feature(f, COARSE_TOLERANCE) for f in detail["features"]],
    }

    for path, fc in ((DETAIL_OUT, detail), (COARSE_OUT, coarse)):
        with open(path, "w") as f:
            json.dump(fc, f, separators=(",", ":"))
        print(f"{path}: {len(fc['features'])} states, {count_points(fc)} points")


if __name__ == "__main__":
    import sys

    sys.setrecursionlimit(100000)
    main(sys.argv[1] if len(sys.argv) > 1 else RAW)
