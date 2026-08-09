// Interactive US Route 20 map.
//
// Basemap detail is the point here, so the default layer is OSM Standard --
// the same osm-carto rendering as tmap's tm_basemap("OpenStreetMap") -- and the
// route is drawn as a cased line that stays legible without the basemap having
// to be muted. Readers can switch to satellite or topo to explore.

(function () {
  "use strict";

  var CANVAS_ID = "us20-map";

  // Coarse geometry for the national view, full resolution once zoomed in.
  var COARSE_URL = "us20.geojson";
  var DETAIL_URL = "us20-detail.geojson";
  var DETAIL_MIN_ZOOM = 9;

  var OSM_ATTRIB =
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

  function basemaps() {
    return {
      Street: L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: OSM_ATTRIB,
      }),
      Satellite: L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        { maxZoom: 19, attribution: "Imagery &copy; Esri" }
      ),
      Topo: L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
        maxZoom: 17,
        attribution: OSM_ATTRIB + ', SRTM | &copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
      }),
    };
  }

  // A wide light casing under a narrow saturated stroke, so the route reads
  // over dense street tiles and over satellite imagery alike.
  var CASING_STYLE = { color: "#ffffff", weight: 7, opacity: 0.85 };
  var ROUTE_STYLE = { color: "#c1272d", weight: 3.5, opacity: 1 };

  // TODO: vignette markers -- {lat, lng, title, html} -- that flyTo a stretch
  // of road and open a popup. Fill these in as the post's sections get written.
  var VIGNETTES = [];

  function addVignettes(map) {
    VIGNETTES.forEach(function (v) {
      L.marker([v.lat, v.lng]).addTo(map).bindPopup("<h4>" + v.title + "</h4>" + v.html);
    });
  }

  function init() {
    var canvas = document.getElementById(CANVAS_ID);
    if (!canvas || typeof L === "undefined") {
      return;
    }

    var layers = basemaps();
    var map = L.map(canvas, {
      // Let the page scroll normally; readers opt in to zooming.
      scrollWheelZoom: false,
      layers: [layers.Street],
    });
    map.setView([42.5, -98], 4);

    L.control.layers(layers, null, { collapsed: false }).addTo(map);
    L.control.scale({ imperial: true, metric: false }).addTo(map);

    var casing = L.geoJSON(null, { style: CASING_STYLE }).addTo(map);
    var route = L.geoJSON(null, {
      style: ROUTE_STYLE,
      onEachFeature: function (feature, layer) {
        layer.bindTooltip("US 20 in " + feature.properties.state, { sticky: true });
      },
    }).addTo(map);

    function draw(geojson) {
      casing.clearLayers().addData(geojson);
      route.clearLayers().addData(geojson);
      casing.bringToBack();
    }

    // Leaflet derives the fit zoom from the container's measured size, so a fit
    // that runs before layout settles -- a background tab, a collapsed parent,
    // or just an early paint -- opens the map far too tight. Rather than guess
    // at timing, keep re-fitting on every resize until the reader takes over.
    var routeBounds = null;
    var readerTookOver = false;

    ["dragstart", "zoomstart"].forEach(function (evt) {
      map.on(evt, function () {
        readerTookOver = true;
      });
    });

    function fitRoute() {
      if (!routeBounds || readerTookOver) {
        return;
      }
      // maxZoom keeps a bad measurement from opening on a single intersection.
      map.fitBounds(routeBounds, { padding: [20, 20], maxZoom: 7, animate: false });
    }

    // invalidateSize triggers Leaflet's own "resize", which re-runs the fit
    // against the corrected size.
    map.on("resize", fitRoute);

    if (typeof ResizeObserver !== "undefined") {
      new ResizeObserver(function () {
        map.invalidateSize();
      }).observe(canvas);
    } else {
      window.addEventListener("load", function () {
        map.invalidateSize();
      });
    }

    fetch(COARSE_URL)
      .then(function (r) {
        return r.json();
      })
      .then(function (geojson) {
        draw(geojson);
        routeBounds = route.getBounds();
        map.invalidateSize();
        fitRoute();

        // Swap in full-resolution geometry the first time the reader zooms in.
        var detail = null;
        map.on("zoomend", function () {
          if (map.getZoom() < DETAIL_MIN_ZOOM || detail) {
            return;
          }
          detail = fetch(DETAIL_URL)
            .then(function (r) {
              return r.json();
            })
            .then(draw);
        });
      })
      .catch(function (err) {
        canvas.innerHTML = '<p class="map-error">Could not load the route map.</p>';
        console.error("US 20 map:", err);
      });

    addVignettes(map);

    // Handle for the browser console, so a candidate vignette location can be
    // tried out with us20Map.flyTo([lat, lng], zoom) before it goes in VIGNETTES.
    window.us20Map = map;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
