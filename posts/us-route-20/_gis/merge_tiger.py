"""Merge the per-state TIGER extracts into one FeatureCollection shaped exactly
like fetch_us20.py's output (one MultiLineString per state), and report the
geodesic length per state so it can be compared against OSM and against the
published ~3,365 mile figure.

Length is the useful diagnostic: TIGER names a segment for only one route, so
where US 20 runs concurrent with an interstate the FULLNAME is the interstate
and the US 20 mileage silently disappears.
"""

import json
import math
import os

STATES = ["OR", "ID", "MT", "WY", "NE", "IA", "IL", "IN", "OH", "PA", "NY", "MA"]
WORK = "tiger"
OUT = "us20_tiger.json"

EARTH_RADIUS_MI = 3958.7613


def haversine(a, b):
    lon1, lat1 = math.radians(a[0]), math.radians(a[1])
    lon2, lat2 = math.radians(b[0]), math.radians(b[1])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_MI * math.asin(math.sqrt(h))


def line_length(coords):
    return sum(haversine(coords[i], coords[i + 1]) for i in range(len(coords) - 1))


def state_lines(state):
    path = os.path.join(WORK, f"us20_{state}.geojson")
    with open(path) as f:
        fc = json.load(f)

    lines = []
    for feat in fc["features"]:
        geom = feat.get("geometry") or {}
        if geom.get("type") == "LineString":
            lines.append(geom["coordinates"])
        elif geom.get("type") == "MultiLineString":
            lines.extend(geom["coordinates"])
    return lines


def main():
    features, total = [], 0.0
    for state in STATES:
        lines = state_lines(state)
        miles = sum(line_length(line) for line in lines)
        total += miles
        pts = sum(len(line) for line in lines)
        print(f"{state}: {len(lines):5d} segments  {pts:6d} points  {miles:7.1f} mi")
        features.append({
            "type": "Feature",
            "properties": {"state": state, "ref": "US 20", "source": "TIGER/Line 2025"},
            "geometry": {"type": "MultiLineString", "coordinates": lines},
        })

    with open(OUT, "w") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f)
    print(f"\ntotal: {total:.1f} mi   (published length is about 3,365 mi)")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
