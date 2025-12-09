//csrf helper function
// retrueve cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// initialise the map
var map = L.map('map').setView([53.35, -6.26], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);


// layers
var libraryLayer = L.layerGroup().addTo(map);   // Static markers
var proximityLayer = L.layerGroup().addTo(map); // Dynamic results
var drawnItems = new L.FeatureGroup();          // For polygons/rectangles
map.addLayer(drawnItems);

// Load all libraries (static markers)
fetch('/api/libraries/')
    .then(response => response.json())
    .then(data => {
        data.forEach(lib => {
            if (lib.coordinates) {
                const [lon, lat] = lib.coordinates;
                L.marker([lat, lon])
                    .addTo(libraryLayer)
                    .bindPopup(
                        `<b>${lib.name}</b><br>${lib.postcode || ''}<br>${lib.opening_hours || ''}`
                    );
            }
        });
    })
    .catch(err => console.error('Error loading libraries:', err));

// 4. Mode toggle logic
let searchMode = "proximity"; // default

document.querySelectorAll('input[name="searchMode"]').forEach(input => {
    input.addEventListener('change', function() {
        searchMode = this.value;

        // Clear previous results when switching mode
        proximityLayer.clearLayers();
        drawnItems.clearLayers();
        if (clickMarker) map.removeLayer(clickMarker);
        if (window.searchCircle) map.removeLayer(window.searchCircle);
    });
});


// Click-based proximity search
let clickMarker = null;

map.on("click", function(e) {
    if (searchMode !== "proximity") return; // Only run if proximity mode

    const clickedLat = e.latlng.lat;
    const clickedLng = e.latlng.lng;

    // Remove previous click marker
    if (clickMarker) map.removeLayer(clickMarker);

    clickMarker = L.marker([clickedLat, clickedLng]).addTo(map);

    // Optional radius circle
    const radius = 3000; // 3 km
    if (window.searchCircle) map.removeLayer(window.searchCircle);
    window.searchCircle = L.circle([clickedLat, clickedLng], { radius: radius }).addTo(map);

    // Fetch proximity results from backend
    fetch(`/proximity/?lng=${clickedLng}&lat=${clickedLat}&radius=${radius}`)
        .then(res => res.json())
        .then(data => {
            proximityLayer.clearLayers();
            data.results.forEach(lib => {
                const [lon, lat] = lib.coordinates;
                L.marker([lat, lon], {
                    icon: L.icon({
                        iconUrl: 'https://cdn-icons-png.flaticon.com/512/854/854878.png',
                        iconSize: [28, 28]
                    })
                })
                .addTo(proximityLayer)
                .bindPopup(`<b>${lib.name}</b><br>${Math.round(lib.distance)} m away`);
            });
        });
});

// Polygon / Rectangle Spatial Search
var drawControl = new L.Control.Draw({
    draw: {
        polygon: true,
        rectangle: true,
        polyline: false,
        circle: false,
        marker: false,
        circlemarker: false
    },
    edit: {
        featureGroup: drawnItems
    }
});
map.addControl(drawControl);

map.on(L.Draw.Event.CREATED, function(e) {
    if (searchMode !== "polygon") return; // Only run if polygon mode

    var layer = e.layer;
    drawnItems.addLayer(layer);

    var polygonGeoJSON = layer.toGeoJSON();

    fetch('/polygon-search/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(polygonGeoJSON)
    })
    .then(res => res.json())
    .then(data => {
        // Clear previous dynamic markers
        proximityLayer.clearLayers();

        // Add results as GeoJSON markers
        L.geoJSON(data, {
            pointToLayer: function(feature, latlng) {
                return L.marker(latlng).bindPopup(`<b>${feature.properties.name}</b>`);
            }
        }).addTo(proximityLayer);
    })
    .catch(err => console.error(err));
});
