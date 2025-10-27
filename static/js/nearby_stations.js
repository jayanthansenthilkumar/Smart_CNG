let map;
let userMarker = null;
let stationMarkers = [];
let routingControl = null;
let accuracyCircle = null;
let isMapInitialized = false;
let searchRadius = 5;
let radiusCircle = null;

document.addEventListener('DOMContentLoaded', function() {
    const mapContainer = document.getElementById('map');
    if (mapContainer && !isMapInitialized) {
        initMap();
    }
    initSidebarToggle();

    // Add modal functionality
    const aboutBtn = document.querySelector('.about-btn');
    const modal = document.getElementById('aboutModal');
    const closeBtn = document.querySelector('.close-modal');

    aboutBtn.addEventListener('click', () => {
        modal.style.display = 'block';
    });

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

function initMap() {
    if (isMapInitialized) {
        return;
    }

    map = L.map('map').setView([28.6139, 77.2090], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    map.on('click', function(e) {
        handleLocationSelect(e.latlng.lat, e.latlng.lng);
    });

    const locationButton = document.getElementById('location-button');
    if (locationButton) {
        locationButton.addEventListener('click', getCurrentLocation);
    }

    // Add radius slider functionality
    const radiusSlider = document.getElementById('radius-slider');
    const radiusValue = document.getElementById('radius-value');
    
    radiusSlider.addEventListener('input', function(e) {
        searchRadius = parseInt(e.target.value);
        radiusValue.textContent = searchRadius;
        
        if (userMarker) {
            updateRadiusCircle(userMarker.getLatLng());
        }
        
        if (userMarker) {
            const pos = userMarker.getLatLng();
            fetchNearbyStations(pos.lat, pos.lng);
        }
    });

    isMapInitialized = true;
}

function getCurrentLocation() {
    const button = document.getElementById('location-button');
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Getting location...';
    button.disabled = true;

    const done = () => resetLocationButton(button);

    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser");
        return done();
    }

    const optionsHigh = { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 };
    const optionsLow = { enableHighAccuracy: false, timeout: 8000, maximumAge: 60000 };

    const onSuccess = (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        handleLocationSelect(lat, lng);
        map.setView([lat, lng], 14);
        done();
    };

    const tryIpFallback = () => {
        const withTimeout = (p, ms=4000) => Promise.race([
            p,
            new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), ms))
        ]);
        const providers = [
            () => withTimeout(fetch('https://ipapi.co/json/').then(r => r.json())),
            () => withTimeout(fetch('https://ipwho.is/').then(r => r.json()).then(d => ({ latitude: d.latitude, longitude: d.longitude }))),
            () => withTimeout(fetch('https://geolocation-db.com/json/').then(r => r.json()).then(d => ({ latitude: parseFloat(d.latitude), longitude: parseFloat(d.longitude) }))),
        ];
        (async () => {
            for (const p of providers) {
                try {
                    const data = await p();
                    const lat = typeof data.latitude === 'number' ? data.latitude : parseFloat(data.latitude);
                    const lng = typeof data.longitude === 'number' ? data.longitude : parseFloat(data.longitude);
                    if (isFinite(lat) && isFinite(lng)) {
                        handleLocationSelect(lat, lng);
                        map.setView([lat, lng], 12);
                        done();
                        return;
                    }
                } catch {}
            }
            alert('Unable to determine your location. Click on the map to choose a point.');
            done();
        })();
    };

    const startGeo = () => navigator.geolocation.getCurrentPosition(
        onSuccess,
        (err) => {
            if (err && err.code === err.TIMEOUT) {
                // Retry with lower accuracy
                navigator.geolocation.getCurrentPosition(onSuccess, () => tryIpFallback(), optionsLow);
            } else if (err && err.code === err.POSITION_UNAVAILABLE) {
                // Go straight to IP-based fallback
                tryIpFallback();
            } else if (err && err.code === err.PERMISSION_DENIED) {
                alert('Location permission denied. You can click on the map to select a point.');
                done();
            } else {
                // Unavailable or unknown
                tryIpFallback();
            }
        },
        optionsHigh
    );

    // If Permissions API is available, check first to avoid silent failures
    try {
        if (navigator.permissions && navigator.permissions.query) {
            navigator.permissions.query({ name: 'geolocation' }).then((status) => {
                if (status.state === 'denied') {
                    alert('Location access is blocked for this site. Enable it in your browser settings, or click on the map to choose a point.');
                    return tryIpFallback();
                }
                // 'granted' or 'prompt' -> attempt geolocation
                startGeo();
            }).catch(() => startGeo());
        } else {
            startGeo();
        }
    } catch (_) {
        startGeo();
    }
}

function resetLocationButton(button) {
    button.innerHTML = '<i class="fas fa-location-arrow"></i> Use My Location';
    button.disabled = false;
}

function handleLocationSelect(lat, lng) {
    if (userMarker) {
        map.removeLayer(userMarker);
    }
    
    userMarker = L.marker([lat, lng], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34]
        })
    }).addTo(map);
    userMarker.bindPopup("Your Location").openPopup();

    updateRadiusCircle([lat, lng]);
    fetchNearbyStations(lat, lng);
}

function fetchNearbyStations(lat, lng) {
    // Show loading state
    const stationList = document.getElementById('station-list');
    stationList.innerHTML = '<div class="loading">Finding CNG stations...</div>';

    // Use stations from file, compute distances client-side
    fetch('/api/stations-from-file')
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            const all = (data.stations || []).map(s => ({
                name: s.name || 'CNG Station',
                position: { lat: s.position.lat, lng: s.position.lng }
            }));
            // Filter within radius and sort by distance
            const within = all
                .map(s => ({...s, _dist: calculateDistance(lat, lng, s.position.lat, s.position.lng)}))
                .filter(s => s._dist <= searchRadius)
                .sort((a, b) => a._dist - b._dist)
                .slice(0, 3); // nearest 3

            if (within.length === 0) {
                stationList.innerHTML = '<div class="no-stations">No CNG stations found within ' + searchRadius + 'km radius</div>';
            } else {
                displayStations(within);
            }
        })
        .catch(err => {
            console.error('Error fetching stations from file:', err);
            stationList.innerHTML = '<div class="no-stations">Unable to load stations data.</div>';
        });
}

function filterStationsWithinRadius(stations, center) {
    return stations.filter(station => {
        const stationPos = station.position || { lat: station.lat, lng: station.lng };
        const distance = calculateDistance(
            center.lat,
            center.lng,
            stationPos.lat,
            stationPos.lng
        );
        return distance <= searchRadius;
    });
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the earth in km
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const d = R * c; // Distance in km
    return d;
}

function deg2rad(deg) {
    return deg * (Math.PI/180);
}

function displayStations(stations) {
    // Clear existing markers
    stationMarkers.forEach(marker => map.removeLayer(marker));
    stationMarkers = [];
    
    const stationList = document.getElementById('station-list');
    stationList.innerHTML = ''; // Clear existing list
    
    const bounds = L.latLngBounds();
    
    stations.forEach((station, index) => {
        const position = station.position || { lat: station.lat, lng: station.lng };
        const distance = (typeof station._dist === 'number')
            ? station._dist.toFixed(2)
            : (userMarker ? calculateDistance(userMarker.getLatLng().lat, userMarker.getLatLng().lng, position.lat, position.lng).toFixed(2) : '?');
        
        const marker = L.marker([position.lat, position.lng]).addTo(map);
        
        const popupContent = `
            <div class="station-popup">
                <h3>${station.name}</h3>
                <div class="station-details">
                    <p><i class="fas fa-map-marker-alt"></i> ${distance} km away</p>
                </div>
                <button onclick="getDirections(${position.lat}, ${position.lng})" class="direction-btn">
                    <i class="fas fa-directions"></i> Get Directions
                </button>
            </div>
        `;
        
        marker.bindPopup(popupContent);
        stationMarkers.push(marker);
        bounds.extend([position.lat, position.lng]);

        // Create station card with distance
        const stationCard = document.createElement('div');
        stationCard.className = 'station-card';
        stationCard.innerHTML = `
            <h3>${station.name}</h3>
            <div class="station-details">
                <p><i class="fas fa-map-marker-alt"></i> ${distance} km away</p>
            </div>
            <button onclick="getDirections(${position.lat}, ${position.lng})" class="direction-btn">
                <i class="fas fa-directions"></i> Get Directions
            </button>
        `;

        stationCard.addEventListener('click', () => {
            map.setView([position.lat, position.lng], 15);
            marker.openPopup();
        });

        stationList.appendChild(stationCard);
    });

    // Fit map to show all markers and radius circle
    if (stationMarkers.length > 0) {
        if (userMarker) {
            bounds.extend(userMarker.getLatLng());
        }
        map.fitBounds(bounds, {
            padding: [50, 50],
            maxZoom: 15
        });
    }
}

// Reference to fetchNearbyStations function from main.js