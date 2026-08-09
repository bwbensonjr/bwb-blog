# Map technology decision

## Requirement

See the path of US 20 over a high-quality (probably OSM) basemap, legible from
national zoom down to street level, so readers can find their own connections.

## Options

### tmap in view mode (massnumbers.us pattern)

`tmap_mode("view")` + `tm_shape(route) + tm_lines() + tm_basemap("OpenStreetMap")`.

- Familiar; same code shape as the massnumbers precinct maps.
- Requires adding `sf` and `tmap` to this repo's renv. `sf` pulls in GDAL/GEOS/PROJ
  system libraries. This blog's renv.lock currently has none of the three
  (no `sf`, no `tmap`, no `leaflet`) — 118 packages, all pure-R/CRAN-simple.
- tmap view mode is a thin wrapper over the R `leaflet` widget. Everything it
  can render, Leaflet can render; the reverse is not true.
- Weak spot for this post: the interactions I actually want (click a vignette,
  fly to that stretch of road, popup with a photo, toggle state segments) are
  awkward or impossible through `tm_view()`.
- The htmlwidget inlines the whole geometry into the page HTML with no
  zoom-dependent detail control.

tmap is the right tool when the map *is* a statistical graphic — a choropleth
driven by a data join. That is the massnumbers case. This post is one line and a
handful of annotated points, so the data-join convenience buys nothing.

### R `leaflet` package

Middle ground. `leaflet::addGeoJSON()` accepts raw GeoJSON, so this needs only
`leaflet` + `htmlwidgets`, not `sf`. More control than tmap, but still writing
JS configuration through an R API, and still inlining geometry into the HTML.

### Hand-written Leaflet JS (watertown-elections pattern) — RECOMMENDED

- Zero new R dependencies. Post renders as plain markdown.
- Full control over the things that matter here: basemap choice, per-state
  styling, vignette markers that `flyTo` a location, popups with photos,
  scroll-wheel and zoom limits, layer control.
- Route geometry stays a separate static `.geojson` file that the page fetches,
  so the HTML stays small and GitHub Pages serves the geometry gzipped and
  cacheable. Can also serve a coarse file for national zoom and a detailed one
  for close-in zoom.
- Reuses patterns already written in `watertown-elections/docs/app.js`
  (`L.map` / `L.tileLayer` / `L.geoJSON` / `fitBounds`).

Wiring into Quarto: a `<div id="us20-map">` plus `format: html: include-after-body`
(or a raw `<script>` block) in the post, with `us20.geojson`, `us20-map.js`, and
the Leaflet CSS/JS from unpkg — same as watertown-elections.

## Basemap candidates

Priority is the detail and quality of the basemap itself, not making the route
line stand out — the line can carry its own weight with thickness and color.
That rules out CARTO Voyager and the other "muted" styles, which deliberately
thin out POIs, buildings, and labels to stay out of an overlay's way.

Two different axes of "quality" pull in different directions:

- **Information density** — how much is actually drawn. OSM Standard
  (osm-carto) is the winner; it is the reference rendering, with buildings,
  footpaths, POI icons, and landuse at high zoom.
- **Rendering quality** — sharpness and smoothness. Vector tiles win outright:
  crisp labels at every zoom, fractional zoom, retina-sharp. `tile.openstreetmap.org`
  serves no @2x tiles, so osm-carto looks soft on a Retina display.

| Option | Key? | Notes |
|--------|------|-------|
| OSM Standard `tile.openstreetmap.org` | no | Densest detail. Not retina. Community-funded; see policy below. |
| OpenFreeMap (Liberty style) | no | Vector, MapLibre. No registration, no request limits, commercial use OK. |
| OpenTopoMap | no | Contours + hillshading over OSM. Good for Yellowstone, the Cascades, Idaho. Slow tile server. |
| Esri World Imagery | no | Satellite. Free with attribution. Strong complement for exploring. |
| USGS National Map | no | US-only topo and imagery. Authoritative, and the whole route is domestic. |
| Stadia / Thunderforest | yes | Skip — API key not worth it given the above. |

### OSM tile usage policy

Verified at <https://operations.osmfoundation.org/policies/tiles/>. Normal
interactive viewing by humans is permitted. Requirements: visible
"© OpenStreetMap contributors" attribution that is not hidden behind a toggle,
a valid Referer (browsers send this), and no prefetching or offline caching of
tiles. A low-traffic personal blog is fine. Worth remembering that this is
donated infrastructure, and a post on a Globe-adjacent topic could get shared
widely — OpenFreeMap is the hedge, since it states no limits explicitly.

### Decision

Hand-written Leaflet with raster tiles. Default basemap is OSM Standard —
this is the same rendering as tmap's `tm_basemap("OpenStreetMap")`, which is an
alias for the leaflet-providers `OpenStreetMap.Mapnik` entry pointing at
`tile.openstreetmap.org`. Same tiles, no R dependencies.

A layer control lets readers switch while exploring. No API keys anywhere:

```js
Street    https://tile.openstreetmap.org/{z}/{x}/{y}.png          maxZoom 19
Satellite Esri World Imagery (ArcGIS rest/services/World_Imagery)  maxZoom 19
Topo      https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png         maxZoom 17
```

Route line styling: a wide light casing under a narrower saturated stroke, so
it stays readable over both the street and satellite layers without needing the
basemap to be muted.

## Route geometry source

OpenStreetMap route relations, fetched via Overpass. US 20 exists as 12
per-state `type=route` relations with `network=US:US`, `ref=20`:

| State | Relation |
|-------|----------|
| OR | 406017 |
| ID | 406627 (Idaho Medal of Honor Highway) |
| MT | 20002033 |
| WY | 408084 |
| NE | 408085 |
| IA | 408086 |
| IL | 2308560 |
| IN | 2308561 |
| OH | 1017178 |
| PA | 7724881 |
| NY | 67761 |
| MA | 408090 |

Filtering on exactly `ref=20` with no `modifier` excludes the Business,
Alternate, and Truck routes. Fetch script: `_gis/fetch_us20.py`.

### TIGER/Line cross-check

Both sources were built and compared. TIGER extract: `fetch_tiger.sh` then
`merge_tiger.py`. Note that US 20 is mostly MTFCC S1200 (secondary road) in
TIGER, so the national PRIMARYROADS file does not contain it — the per-state
PRISECROADS files are the ones to use.

Geodesic length by state, in miles:

| | OR | ID | MT | WY | NE | IA | IL | IN | OH | PA | NY | MA | total |
|--|--|--|--|--|--|--|--|--|--|--|--|--|--|
| OSM | 457 | 504 | 10 | 478 | 440 | 598 | 292 | 204 | 329 | 53 | 420 | 186 | **3970** |
| TIGER | 452 | 495 | 12 | 513 | 439 | 573 | 277 | 202 | 233 | 59 | 420 | 170 | **3844** |

They agree within a few percent almost everywhere. Ohio is the one real
divergence (329 vs 233); TIGER names a segment for only one route, so where
US 20 runs concurrent with another highway the US 20 mileage can vanish.

Both totals exceed the published ~3,365 miles because both digitize divided
highway as two separate centerlines. Iowa is the clearest case: 573-598 miles
for a state US 20 crosses in about 300, because it is four-lane divided across
most of its width. This is not an error to fix — drawing both carriageways is
what the road actually looks like — but it means these files cannot be used to
measure route length.

Going with OSM as the published source: it is more consistent state to state,
it has no concurrency gaps, and the per-state relations give a natural handle
for highlighting one state at a time. TIGER stays as the cross-check.

### Way fragmentation

OSM splits US 20 into roughly 8,900 short ways. Simplifying each way in
isolation cannot go below two points per way, which put a floor of ~18,500
points (434 KB) on the national-view file. `build_geojson.py` now stitches ways
that share an endpoint into longer runs before simplifying, which drops the
coarse file to 2,114 points (50 KB) with total length falling only 1.8%
(3970 -> 3897 mi), i.e. no meaningful shortcuts.

### Verified in the browser

- Coarse file (50 KB) loads on page view; the 1.9 MB detail file is fetched
  only after the reader crosses zoom 9.
- OSM Standard, Esri imagery, and OpenTopoMap all load with no API key.
- The white casing under the red stroke stays legible over satellite imagery.
- Leaflet's `getBoundsZoom` returns the layer's `maxZoom` when the container
  measures zero, so a map that initialises in a background tab or a collapsed
  container opens zoomed to street level in the middle of Nebraska. The fix is
  a `maxZoom` cap on the initial fit plus a `ResizeObserver` that re-fits until
  the reader interacts.
