#!/usr/bin/env bash
# Extract US Route 20 from Census TIGER/Line as a cross-check on the OSM
# route relations fetched by fetch_us20.py.
#
# Note: US 20 is mostly MTFCC S1200 (secondary road) in TIGER, not S1100, so the
# national PRIMARYROADS file does not contain it. The per-state PRISECROADS
# files carry both classes.
set -euo pipefail

YEAR=2025
WORK="tiger"
mkdir -p "$WORK"

# state FIPS:postal, west to east along the route
STATES=(41:OR 16:ID 30:MT 56:WY 31:NE 19:IA 17:IL 18:IN 39:OH 42:PA 36:NY 25:MA)

for entry in "${STATES[@]}"; do
    fips="${entry%%:*}"
    post="${entry##*:}"
    base="tl_${YEAR}_${fips}_prisecroads"

    if [ ! -f "$WORK/$base.zip" ]; then
        curl -sS -A "bwb-blog-us20/1.0 (+https://brentwbenson.org)" \
            -o "$WORK/$base.zip" \
            "https://www2.census.gov/geo/tiger/TIGER${YEAR}/PRISECROADS/$base.zip"
    fi

    # RTTYP='U' is a US route; the regex keeps "US Hwy 20" while rejecting the
    # Business/Alternate/Bypass/Spur variants and other routes such as US 201.
    ogr2ogr -f GeoJSON "$WORK/us20_$post.geojson" \
        "/vsizip/$WORK/$base.zip/$base.shp" \
        -where "RTTYP='U' AND FULLNAME LIKE 'US Hwy 20'" \
        -nln us20 -overwrite -lco COORDINATE_PRECISION=6 2>/dev/null

    n=$(ogrinfo -so -al "$WORK/us20_$post.geojson" 2>/dev/null \
        | awk '/Feature Count/ {print $3}')
    echo "$post: $n features"
done

echo "wrote per-state GeoJSON under $WORK/"
