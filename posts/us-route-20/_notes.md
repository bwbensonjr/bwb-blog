# US Route 20

I was inspired by the Boston Globe piece about Boston area homes on
the U.S. Route 20, the longest road in the country, which featured on
condo on Watertown's North Beacon Street. This condo is less than a
mile from our house in Watertown and is on my commuting route to work.

I looked up the Wikipedia article and was struck by my connections
with different parts of the road across multiple states. My initial
idea for the blog post is to provide an overview of U.S. Route 20 and
its history, describe a few vignettes about some of my connections,
and provide a high-quality interactive map allowing people to explore
their own connections with U.S. Route 20.

## References 

- [Boston-area condos for sale along Route 20, the longest road in the country](https://www.bostonglobe.com/2026/08/07/magazine/homes-route-20-kenmore-watertown/)
- [US Route 20 - The longest road in the United States](https://en.wikipedia.org/wiki/U.S._Route_20)

## Tasks 

- [x] Create blog post page and verify ability to preview.
- [x] Get machine-readable representation of U.S. Route 20 for use in map.
  - OSM route relations (12 per-state) is the published source; Census
    TIGER/Line built as a cross-check. See `_map-notes.md`.
- [x] Decide on map technology (first ideas are `tmap` (massnumbers.us) and `leaflet` (watertown-elections)).
  - Hand-written Leaflet with OSM Standard tiles, the same rendering as
    tmap's `tm_basemap("OpenStreetMap")`. No new R dependencies.
  - The key requirement is the ability to see the path of the route on
    a really nice (probably OpenStreetMap) layer to see everything
    around it (roads, towns, landmarks, buildings, etc.) at various
    levels of zoom.

## Still to do

- [ ] Write the overview and history sections.
- [ ] Pick the vignette locations and add them to `VIGNETTES` in
      `us20-map.js`. `us20Map.flyTo([lat, lng], zoom)` in the browser console
      is handy for trying a location out.
- [ ] Hero image.
- [ ] Remove `draft: true` when ready to publish.




