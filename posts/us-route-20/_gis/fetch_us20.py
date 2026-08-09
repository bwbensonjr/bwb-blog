"""Fetch US Route 20 geometry from OpenStreetMap via Overpass, one state relation
at a time, and write a GeoJSON FeatureCollection of MultiLineStrings (one per state)."""

import json
import time
import urllib.parse
import urllib.request

RELATIONS = [
    (406017, "OR"), (406627, "ID"), (20002033, "MT"), (408084, "WY"),
    (408085, "NE"), (408086, "IA"), (2308560, "IL"), (2308561, "IN"),
    (1017178, "OH"), (7724881, "PA"), (67761, "NY"), (408090, "MA"),
]

ENDPOINT = "https://overpass-api.de/api/interpreter"
OUT = "us20_raw.json"

# Overpass rejects generic library User-Agents with HTTP 406, matching the OSM
# policy that clients identify themselves and provide a contact URL.
USER_AGENT = "bwb-blog-us20/1.0 (+https://brentwbenson.org)"


def fetch(rel_id):
    query = f"[out:json][timeout:300];rel({rel_id});way(r);out geom;"
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(ENDPOINT, data=data, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.load(resp)


def load_existing():
    """Resume support: keep states already fetched so a rate-limited run can be
    re-run without refetching what succeeded."""
    try:
        with open(OUT) as f:
            return {f_["properties"]["state"]: f_ for f_ in json.load(f)["features"]}
    except (FileNotFoundError, ValueError, KeyError):
        return {}


def save(by_state):
    ordered = [by_state[s] for _, s in RELATIONS if s in by_state]
    with open(OUT, "w") as f:
        json.dump({"type": "FeatureCollection", "features": ordered}, f)


def main():
    by_state = load_existing()
    if by_state:
        print(f"resuming, already have: {', '.join(sorted(by_state))}")

    for rel_id, state in RELATIONS:
        if state in by_state:
            continue

        for attempt in range(5):
            try:
                result = fetch(rel_id)
                break
            except Exception as exc:  # noqa: BLE001
                # Overpass allows 2 concurrent slots and returns 429 when the
                # quota is exhausted; it needs a real pause, not a quick retry.
                wait = 60 if "429" in str(exc) else 20
                print(f"  {state} attempt {attempt + 1} failed: {exc} (waiting {wait}s)")
                time.sleep(wait)
        else:
            print(f"  {state} FAILED")
            continue

        lines = [
            [[round(p["lon"], 6), round(p["lat"], 6)] for p in w["geometry"]]
            for w in result["elements"]
            if w.get("type") == "way" and w.get("geometry")
        ]
        pts = sum(len(line) for line in lines)
        print(f"{state}: {len(lines)} ways, {pts} points")
        by_state[state] = {
            "type": "Feature",
            "properties": {"state": state, "relation_id": rel_id, "ref": "US 20"},
            "geometry": {"type": "MultiLineString", "coordinates": lines},
        }
        save(by_state)
        time.sleep(12)

    save(by_state)
    missing = [s for _, s in RELATIONS if s not in by_state]
    print(f"wrote {OUT} with {len(by_state)}/{len(RELATIONS)} states")
    if missing:
        print(f"MISSING (re-run to resume): {', '.join(missing)}")


if __name__ == "__main__":
    main()
