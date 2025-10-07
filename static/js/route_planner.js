let routeMap;
let routeLayer;
let markersLayer;
let destinationMarker;
let sourceMarker;
let externalStationsLayer;
let externalStationMarkers = [];
let allowStationPopups = false;

// Initialize map
function initializeMap() {
    routeMap = L.map('route-map').setView([51.505, -0.09], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(routeMap);
    
    markersLayer = L.layerGroup().addTo(routeMap);
    routeLayer = L.layerGroup().addTo(routeMap);
    externalStationsLayer = L.layerGroup().addTo(routeMap);
    // Ensure no popups are open initially
    routeMap.closePopup();

    // Add click event to map
    routeMap.on('click', handleMapClick);
}

// Handle map clicks for destination selection
function handleMapClick(e) {
    const latlng = e.latlng;
    
    // Update destination marker
    if (destinationMarker) {
        routeMap.removeLayer(destinationMarker);
    }
    
    destinationMarker = L.marker([latlng.lat, latlng.lng], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41]
        })
    }).addTo(routeMap);

    // Update destination input field with coordinates
    document.getElementById('end-location').value = `${latlng.lat.toFixed(6)}, ${latlng.lng.toFixed(6)}`;
}

// Handle current location
function getCurrentLocation() {
    const startInput = document.getElementById('start-location');
    const locateBtn = document.querySelector('.location-btn');

    const onLocated = (lat, lng) => {
            if (sourceMarker) {
                routeMap.removeLayer(sourceMarker);
            }
            sourceMarker = L.marker([lat, lng], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41]
                })
            }).addTo(routeMap);
        startInput.value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        routeMap.setView([lat, lng], 13);
    };

    const enableBtn = () => { if (locateBtn) { locateBtn.disabled = false; locateBtn.classList.remove('is-loading'); } };
    const disableBtn = () => { if (locateBtn) { locateBtn.disabled = true; locateBtn.classList.add('is-loading'); } };

    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser. You can manually enter coordinates or allow location access.');
        return;
    }

    disableBtn();

    const geoOptions = { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 };

    navigator.geolocation.getCurrentPosition(
        (position) => {
            enableBtn();
            onLocated(position.coords.latitude, position.coords.longitude);
        },
        async (error) => {
            // Map error codes to friendly messages
            let msg = '';
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    msg = 'Location permission denied. Please allow access in your browser settings.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    msg = 'Location unavailable. Trying a network-based fallback...';
                    break;
                case error.TIMEOUT:
                    msg = 'Location request timed out. Retrying with lower accuracy...';
                    break;
                default:
                    msg = 'Could not get your location. Trying a fallback...';
            }

            // Inform user
            console.warn(msg);

            // If timeout, retry once with lower accuracy
            if (error.code === error.TIMEOUT) {
                try {
                    const retryPos = await new Promise((resolve, reject) =>
                        navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: false, timeout: 8000, maximumAge: 60000 })
                    );
                    enableBtn();
                    return onLocated(retryPos.coords.latitude, retryPos.coords.longitude);
                } catch (_) { /* fall through to IP fallback */ }
            }

            // If permission denied, do not try IP fallback automatically (privacy). Just notify and exit.
            if (error.code === error.PERMISSION_DENIED) {
                enableBtn();
                alert('Location permission denied. Enter coordinates manually or allow location access and try again.');
                return;
            }

            // Fallback: approximate IP-based geolocation
            try {
                const resp = await fetch('https://ipapi.co/json/');
                if (resp.ok) {
                    const data = await resp.json();
                    if (data && data.latitude && data.longitude) {
                        enableBtn();
                        return onLocated(data.latitude, data.longitude);
                    }
                }
                throw new Error('IP geolocation failed');
            } catch (e) {
                enableBtn();
                alert('Unable to determine your location. Please enter the coordinates manually (lat, lng).');
            }
        },
        geoOptions
    );
}

// Load external stations from backend and render on map
async function loadExternalStations() {
    try {
        const resp = await fetch('/api/stations-from-file');
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || 'Failed to load stations');

        externalStationsLayer.clearLayers();
        externalStationMarkers = [];
        const pumpIcon = L.icon({
            iconUrl: 'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-green.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41]
        });

        data.stations.forEach((s) => {
            const lat = s.position?.lat;
            const lng = s.position?.lng;
            if (typeof lat !== 'number' || typeof lng !== 'number') return;
            const marker = L.marker([lat, lng], { icon: pumpIcon })
                .addTo(externalStationsLayer)
                .bindPopup(`<strong>${(s.name || 'CNG Station')}</strong>`);
            // Disable popups before search; enable after search
            marker.on('click', (e) => {
                if (!allowStationPopups) return;
                e.target.openPopup();
            });
            // Hide markers until route is planned
            marker.setOpacity(0);
            externalStationMarkers.push(marker);
        });
    } catch (e) {
        console.error('Station load failed:', e);
    }
}

// CNG Models database aligned with dropdown values and backend expectations
// Units: tankCapacity (kg), range (km), fillingSpeed (kg/min), consumption (kg/km)
const cngModels = {
    maruti_wagonr_cng: {
        name: "Maruti WagonR CNG",
        tankCapacity: 60,
        range: 300,
        fillingSpeed: 10,
        consumption: 0.20
    },
    hyundai_santro_cng: {
        name: "Hyundai Santro CNG",
        tankCapacity: 60,
        range: 320,
        fillingSpeed: 10,
        consumption: 0.19
    },
    tata_tiago_cng: {
        name: "Tata Tiago CNG",
        tankCapacity: 60,
        range: 330,
        fillingSpeed: 11,
        consumption: 0.18
    },
    maruti_ertiga_cng: {
        name: "Maruti Ertiga CNG",
        tankCapacity: 70,
        range: 320,
        fillingSpeed: 11,
        consumption: 0.22
    },
    maruti_dzire_cng: {
        name: "Maruti Dzire S-CNG",
        tankCapacity: 60,
        range: 340,
        fillingSpeed: 10,
        consumption: 0.18
    },
    hyundai_nios_cng: {
        name: "Hyundai Grand i10 Nios CNG",
        tankCapacity: 60,
        range: 330,
        fillingSpeed: 10,
        consumption: 0.18
    },
    tata_tigor_cng: {
        name: "Tata Tigor CNG",
        tankCapacity: 70,
        range: 350,
        fillingSpeed: 11,
        consumption: 0.20
    },
    toyota_glanza_cng: {
        name: "Toyota Glanza CNG",
        tankCapacity: 60,
        range: 350,
        fillingSpeed: 10,
        consumption: 0.17
    }
};

// Add this function to calculate the actual route
async function calculateRoute(startCoords, endCoords) {
    const startStr = `${startCoords[1]},${startCoords[0]}`;
    const endStr = `${endCoords[1]},${endCoords[0]}`;
    
    try {
        const response = await fetch(
            `https://router.project-osrm.org/route/v1/driving/${startStr};${endStr}?overview=full&geometries=geojson`
        );
        
        if (!response.ok) {
            throw new Error('Route calculation failed');
        }
        
        const data = await response.json();
        
        if (data.code !== 'Ok') {
            throw new Error('No route found');
        }
        
        // Calculate segments for battery monitoring
        const coordinates = data.routes[0].geometry.coordinates;
        const segments = [];
        let totalDistance = 0;
        
        for (let i = 0; i < coordinates.length - 1; i++) {
            const distance = calculateSegmentDistance(
                coordinates[i][1], coordinates[i][0],
                coordinates[i + 1][1], coordinates[i + 1][0]
            );
            totalDistance += distance;
            segments.push({
                start: [coordinates[i][1], coordinates[i][0]],
                end: [coordinates[i + 1][1], coordinates[i + 1][0]],
                distance: distance
            });
        }
        
        return {
            coordinates: coordinates.map(coord => [coord[1], coord[0]]),
            distance: totalDistance,
            duration: Math.round(data.routes[0].duration / 60),
            segments: segments
        };
    } catch (error) {
        console.error('Error calculating route:', error);
        throw error;
    }
}

function calculateSegmentDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Update the displayRoute function to handle the new route format
function displayRoute(route, stops) {
    // Clear previous route and markers
    routeLayer.clearLayers();
    markersLayer.clearLayers();
    
    // Draw route line
    const routePath = L.polyline(route.coordinates, {
        color: '#4CAF50',
        weight: 5
    }).addTo(routeLayer);
    
    // Add markers for start and end points
    const startPoint = route.coordinates[0];
    const endPoint = route.coordinates[route.coordinates.length - 1];
    
    // Update stat cards (Distance, Duration, Stops)
    const distEl = document.getElementById('summaryDistance');
    const durEl = document.getElementById('summaryDuration');
    const stopsEl = document.getElementById('summaryStops');
    if (distEl) distEl.textContent = `${route.distance.toFixed(1)} km`;
    if (durEl) durEl.textContent = `${route.duration} mins`;
    if (stopsEl) stopsEl.textContent = `${stops.length}`;
    
    // Start marker
    L.marker(startPoint, {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41]
        })
    }).addTo(markersLayer).bindPopup('Start');
    
    // End marker
    L.marker(endPoint, {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41]
        })
    }).addTo(markersLayer).bindPopup('Destination');
    
    // Add markers for CNG filling stops
    stops.forEach((stop, index) => {
        const marker = L.marker([stop.lat, stop.lng], {
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41]
            })
        }).addTo(markersLayer);
        
        const popupContent = `
            <div class="cng-stop-popup">
                <h3>${stop.name}</h3>
                <p>Arrival Fuel: ${stop.arrivalFuel}%</p>
                <p>Filling Time: ${stop.fillTime} mins</p>
                <p>Departure Fuel: ${stop.departureFuel}%</p>
            </div>
        `;
        
        marker.bindPopup(popupContent);
    });
    
    // Update stops list in sidebar
    displayStopsList(stops);
    
    // Fit map to show entire route
    routeMap.fitBounds(routePath.getBounds(), {
        padding: [50, 50]
    });
}

// Display stops list in sidebar
function displayStopsList(stops) {
    const stopsList = document.getElementById('stops-list');
    if (!stops.length) {
        stopsList.innerHTML = '<p>No CNG filling stops needed</p>';
        return;
    }
    
    const stopsHTML = stops.map((stop, index) => `
        <div class="stop-card">
            <h4>Stop ${index + 1}: ${stop.name}</h4>
            <div class="stop-details">
                <p><i class="fas fa-gas-pump"></i> Arrival: ${stop.arrivalFuel}%</p>
                <p><i class="fas fa-clock"></i> Fill time: ${stop.fillTime} mins</p>
                <p><i class="fas fa-tachometer-alt"></i> Departure: ${stop.departureFuel}%</p>
            </div>
        </div>
    `).join('');
    
    stopsList.innerHTML = stopsHTML;
}

// Add this function to clear previous route data
function clearPreviousRoute() {
    // Clear map layers
    if (routeLayer) routeLayer.clearLayers();
    if (markersLayer) markersLayer.clearLayers();
    
    // Clear route summary if it exists
    const existingSummary = document.querySelector('.route-summary');
    if (existingSummary) {
        existingSummary.remove();
    }
    
    // Clear CNG filling stops list
    const stopsList = document.getElementById('stops-list');
    if (stopsList) {
        stopsList.innerHTML = '';
    }
}

// Update the form submission handler
document.getElementById('route-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    clearPreviousRoute();
    // Hide popups before searching
    allowStationPopups = false;
    routeMap.closePopup();
    
    const startLocation = document.getElementById('start-location').value;
    const endLocation = document.getElementById('end-location').value;
    const cngModel = document.getElementById('cng-model').value;
    const currentFuel = document.getElementById('current-fuel').value;
    
    if (!startLocation || !endLocation || !cngModel || !currentFuel) {
        alert('Please fill in all fields');
        return;
    }
    
    // Show loading state
    const routeResults = document.querySelector('.route-results');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-indicator';
    loadingDiv.innerHTML = `
        <div class="spinner"></div>
        <p>Calculating optimal route...</p>
    `;
    routeResults.prepend(loadingDiv);
    
    try {
        // Resolve inputs: accept either "lat,lng" or place names via Nominatim
        const resolveInput = async (input) => {
            // Try coords first
            const parts = input.split(',');
            if (parts.length === 2) {
                const lat = parseFloat(parts[0].trim());
                const lng = parseFloat(parts[1].trim());
                if (!isNaN(lat) && !isNaN(lng)) return { lat, lng };
            }
            // Fallback to geocoding (Nominatim)
            const q = encodeURIComponent(input);
            const resp = await fetch(`https://nominatim.openstreetmap.org/search?q=${q}&format=json&limit=1`);
            const data = await resp.json();
            if (Array.isArray(data) && data.length) {
                const lat = parseFloat(data[0].lat);
                const lng = parseFloat(data[0].lon);
                if (!isNaN(lat) && !isNaN(lng)) return { lat, lng };
            }
            throw new Error(`Could not resolve location: ${input}`);
        };

        const startResolved = await resolveInput(startLocation);
        const endResolved = await resolveInput(endLocation);
        
        // Calculate route first
        const routeData = await calculateRoute([startResolved.lat, startResolved.lng], [endResolved.lat, endResolved.lng]);
        
        // Clean up CNG model data before sending
        const selectedCngModel = cngModels[cngModel];
        if (!selectedCngModel) {
            throw new Error('Invalid CNG model selected');
        }

        const response = await fetch('/api/route-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                route: routeData,
                cngModel: selectedCngModel,
                currentFuel: parseInt(currentFuel)
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to plan route');
        }
        
        loadingDiv.remove();
        
        if (data.fillingStops) {
            displayRoute(routeData, data.fillingStops);
            // Reveal only nearest 2 stations to the destination and open nearest popup
            const endPoint = routeData.coordinates[routeData.coordinates.length - 1];
            updateNearestStationsVisibility(endPoint[0], endPoint[1], 2);
        } else {
            throw new Error('No CNG filling stops returned');
        }
    } catch (error) {
        loadingDiv.remove();
        console.error('Error planning route:', error);
        alert(error.message || 'Error planning route. Please try again.');
    }
});

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', () => { initializeMap(); loadExternalStations(); });

// Utility: find nearest station marker to a given lat/lng
function updateNearestStationsVisibility(targetLat, targetLng, k = 2) {
    if (!externalStationMarkers.length) return;
    const target = L.latLng(targetLat, targetLng);
    const scored = externalStationMarkers.map(m => ({ marker: m, d: target.distanceTo(m.getLatLng()) }));
    scored.sort((a, b) => a.d - b.d);
    // Hide all
    externalStationMarkers.forEach(m => m.setOpacity(0));
    // Show top k
    const topK = scored.slice(0, k).map(s => s.marker);
    topK.forEach(m => m.setOpacity(1));
    // Enable popups and open nearest
    allowStationPopups = true;
    if (topK[0]) topK[0].openPopup();
}