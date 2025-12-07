// -------------------------------------------
// 1. Initialize the map
// -------------------------------------------
var map = L.map('map').setView([53.35, -6.26], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);

// Layer to hold markers from API (static markers)
var libraryLayer = L.layerGroup().addTo(map);

// Layer for proximity search results (dynamic markers)
var proximityLayer = L.layerGroup().addTo(map);

// -------------------------------------------
// 2. Load ALL libraries once (your existing API)
// -------------------------------------------
fetch('/api/libraries/')
    .then(response => response.json())
    .then(data => {
        console.log("All libraries:", data);

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

// -------------------------------------------
// 3. Dynamic Proximity Search (NEW CODE)
// -------------------------------------------

// Trigger proximity search every time the map stops moving
map.on("moveend", function () {
    const center = map.getCenter();
    const radius = 3000; // meters (3km)

    console.log("Proximity search:", center);

    fetch(`/proximity/?lng=${center.lng}&lat=${center.lat}&radius=${radius}`)
        .then(res => res.json())
        .then(data => {
            console.log("Nearby libraries:", data);

            // Clear previous proximity markers
            proximityLayer.clearLayers();

            // Add new ones
            data.results.forEach(lib => {
                const [lon, lat] = lib.coordinates;

                L.marker([lat, lon], {icon: L.icon({
                    iconUrl: 'https://cdn-icons-png.flaticon.com/512/854/854878.png',
                    iconSize: [28, 28]
                })})
                .addTo(proximityLayer)
                .bindPopup(`<b>${lib.name}</b><br>${Math.round(lib.distance)} m away`);
            });
        });
});
