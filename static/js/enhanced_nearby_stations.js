// Enhanced Nearby Stations JavaScript with Animations and Interactions

let map;
let userMarker = null;
let stationMarkers = [];
let routingControl = null;
let accuracyCircle = null;
let isMapInitialized = false;
let searchRadius = 5;
let radiusCircle = null;
let currentStations = [];
let filteredStations = [];

// Animation and UI state
let isLoading = false;
let currentFilters = {
    status: 'all',
    sortBy: 'distance'
};

document.addEventListener('DOMContentLoaded', function() {
    const mapContainer = document.getElementById('map');
    if (mapContainer && !isMapInitialized) {
        initMap();
    }
    // Removed sidebar toggle feature
    initFilters();
    initMapControls();
    initModal();

    // Add smooth entrance animations
    setTimeout(() => {
        document.querySelector('.sidebar').classList.add('animate__animated', 'animate__slideInRight');
        document.querySelector('.main-content').classList.add('animate__animated', 'animate__slideInLeft');
    }, 100);
});

function initMap() {
    if (isMapInitialized) {
        return;
    }

    // Initialize map with better default view
    map = L.map('map', {
        zoomControl: false,
        attributionControl: false
    }).setView([28.6139, 77.2090], 11);

    // Add custom tile layer with better styling
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add zoom control
    L.control.zoom({
        position: 'bottomright'
    }).addTo(map);

    // Add attribution
    L.control.attribution({
        position: 'bottomleft',
        prefix: false
    }).addTo(map);

    map.on('click', function(e) {
        handleLocationSelect(e.latlng.lat, e.latlng.lng);
    });

    const locationButton = document.getElementById('location-button');
    if (locationButton) {
        locationButton.addEventListener('click', getCurrentLocation);
    }

    // Enhanced radius slider functionality
    const radiusSlider = document.getElementById('radius-slider');
    const radiusValue = document.getElementById('radius-value');
    
    radiusSlider.addEventListener('input', function(e) {
        searchRadius = parseInt(e.target.value);
        radiusValue.textContent = searchRadius;
        
        // Add visual feedback
        radiusValue.style.transform = 'scale(1.2)';
        setTimeout(() => {
            radiusValue.style.transform = 'scale(1)';
        }, 200);
        
        if (userMarker) {
            updateRadiusCircle(userMarker.getLatLng());
            fetchNearbyStations(userMarker.getLatLng().lat, userMarker.getLatLng().lng);
        }
    });

    isMapInitialized = true;
}

function initFilters() {
    const sortFilter = document.getElementById('sort-filter');

    sortFilter.addEventListener('change', function(e) {
        currentFilters.sortBy = e.target.value;
        applyFilters();
    });
}

function initMapControls() {
    const centerMapBtn = document.getElementById('center-map');
    const toggleLayersBtn = document.getElementById('toggle-layers');
    const fullscreenBtn = document.getElementById('fullscreen-map');

    centerMapBtn.addEventListener('click', function() {
        if (userMarker) {
            map.setView(userMarker.getLatLng(), 15);
            addPulseAnimation(userMarker);
        } else {
            showNotification('Please select a location first', 'warning');
        }
    });

    toggleLayersBtn.addEventListener('click', function() {
        // Toggle between different map layers
        showNotification('Layer toggle feature coming soon!', 'info');
    });

    fullscreenBtn.addEventListener('click', function() {
        toggleFullscreen();
    });
}

function initModal() {
    const aboutBtn = document.querySelector('.about-btn');
    const modal = document.getElementById('aboutModal');
    const closeBtn = document.querySelector('.close-modal');

    if (aboutBtn && modal) {
        aboutBtn.addEventListener('click', () => {
            modal.style.display = 'block';
            modal.classList.add('animate__animated', 'animate__fadeIn');
        });

        closeBtn.addEventListener('click', () => {
            modal.classList.add('animate__animated', 'animate__fadeOut');
            setTimeout(() => {
                modal.style.display = 'none';
                modal.classList.remove('animate__animated', 'animate__fadeOut');
            }, 300);
        });

        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.classList.add('animate__animated', 'animate__fadeOut');
                setTimeout(() => {
                    modal.style.display = 'none';
                    modal.classList.remove('animate__animated', 'animate__fadeOut');
                }, 300);
            }
        });
    }
}

function getCurrentLocation() {
    const button = document.getElementById('location-button');
    const originalContent = button.innerHTML;
    
    // Enhanced loading state
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Getting location...';
    button.disabled = true;
    button.classList.add('loading');

    const done = () => {
        button.innerHTML = originalContent;
        button.disabled = false;
        button.classList.remove('loading');
    };

    if (!navigator.geolocation) {
        showNotification("Geolocation is not supported by your browser", 'error');
        return done();
    }

    const optionsHigh = { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 };
    const optionsLow = { enableHighAccuracy: false, timeout: 8000, maximumAge: 60000 };

    const onSuccess = (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        handleLocationSelect(lat, lng);
        map.setView([lat, lng], 14);
        
        // Add success animation
        showNotification('Location found successfully!', 'success');
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
                        showNotification('Location found via IP geolocation', 'info');
                        done();
                        return;
                    }
                } catch {}
            }
            showNotification('Unable to determine your location. Click on the map to choose a point.', 'warning');
            done();
        })();
    };

    const startGeo = () => navigator.geolocation.getCurrentPosition(
        onSuccess,
        (err) => {
            if (err && err.code === err.TIMEOUT) {
                navigator.geolocation.getCurrentPosition(onSuccess, () => tryIpFallback(), optionsLow);
            } else if (err && err.code === err.POSITION_UNAVAILABLE) {
                tryIpFallback();
            } else if (err && err.code === err.PERMISSION_DENIED) {
                showNotification('Location permission denied. You can click on the map to select a point.', 'warning');
                done();
            } else {
                tryIpFallback();
            }
        },
        optionsHigh
    );

    try {
        if (navigator.permissions && navigator.permissions.query) {
            navigator.permissions.query({ name: 'geolocation' }).then((status) => {
                if (status.state === 'denied') {
                    showNotification('Location access is blocked for this site. Enable it in your browser settings, or click on the map to choose a point.', 'warning');
                    return tryIpFallback();
                }
                startGeo();
            }).catch(() => startGeo());
        } else {
            startGeo();
        }
    } catch (_) {
        startGeo();
    }
}

function handleLocationSelect(lat, lng) {
    // Remove existing user marker with animation
    if (userMarker) {
        map.removeLayer(userMarker);
    }
    
    // Create enhanced user marker
    userMarker = L.marker([lat, lng], {
        icon: L.divIcon({
            className: 'custom-user-marker',
            html: '<div class="user-marker-pin"><i class="fas fa-user"></i></div>',
            iconSize: [30, 30],
            iconAnchor: [15, 30]
        })
    }).addTo(map);

    // Add popup with animation
    userMarker.bindPopup(`
        <div class="user-popup">
            <h4><i class="fas fa-map-marker-alt"></i> Your Location</h4>
            <p>Lat: ${lat.toFixed(6)}<br>Lng: ${lng.toFixed(6)}</p>
        </div>
    `).openPopup();

    updateRadiusCircle([lat, lng]);
    fetchNearbyStations(lat, lng);
}

function updateRadiusCircle(center) {
    if (radiusCircle) {
        map.removeLayer(radiusCircle);
    }
    
    radiusCircle = L.circle(center, {
        color: '#023E8A',
        fillColor: '#023E8A',
        fillOpacity: 0.1,
        radius: searchRadius * 1000
    }).addTo(map);
}

function fetchNearbyStations(lat, lng) {
    if (isLoading) return;
    
    isLoading = true;
    showLoadingState();

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
                .sort((a, b) => a._dist - b._dist);

            currentStations = within;
            applyFilters();
        })
        .catch(err => {
            console.error('Error fetching stations from file:', err);
            showErrorState('Unable to load stations data.');
        })
        .finally(() => {
            isLoading = false;
        });
}

function showLoadingState() {
    const stationList = document.getElementById('station-list');
    stationList.innerHTML = `
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">Finding CNG stations...</div>
        </div>
    `;
}

function showErrorState(message) {
    const stationList = document.getElementById('station-list');
    stationList.innerHTML = `
        <div class="no-stations">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
        </div>
    `;
}

function applyFilters() {
    if (!currentStations.length) return;

    // No status filter
    let filtered = currentStations;

    // Apply sorting
    switch (currentFilters.sortBy) {
        case 'wait-time':
            filtered = filtered.sort((a, b) => (a.waitTime || 0) - (b.waitTime || 0));
            break;
        case 'rating':
            filtered = filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
            break;
        default: // distance
            filtered = filtered.sort((a, b) => a._dist - b._dist);
    }

    filteredStations = filtered;
    displayStations(filtered);
}

function displayStations(stations) {
    // Clear existing markers with animation
    stationMarkers.forEach(marker => {
        map.removeLayer(marker);
    });
    stationMarkers = [];
    
    const stationList = document.getElementById('station-list');
    
    if (stations.length === 0) {
        stationList.innerHTML = `
            <div class="no-stations">
                <i class="fas fa-search"></i>
                <p>No CNG stations found within ${searchRadius}km radius</p>
                <small>Try increasing the search radius or selecting a different location</small>
            </div>
        `;
        return;
    }

    // Clear and prepare for new stations
    stationList.innerHTML = '';
    
    const bounds = L.latLngBounds();
    
    stations.forEach((station, index) => {
        const position = station.position || { lat: station.lat, lng: station.lng };
        const distance = (typeof station._dist === 'number')
            ? station._dist.toFixed(2)
            : (userMarker ? calculateDistance(userMarker.getLatLng().lat, userMarker.getLatLng().lng, position.lat, position.lng).toFixed(2) : '?');
        
        // Create enhanced marker
        const marker = L.marker([position.lat, position.lng], {
            icon: L.divIcon({
                className: 'custom-station-marker',
                html: `<div class="station-marker-pin"><i class="fas fa-gas-pump"></i></div>`,
                iconSize: [25, 25],
                iconAnchor: [12, 25]
            })
        }).addTo(map);
        
        // Generate random data for demo
        const waitTime = Math.floor(Math.random() * 30) + 5;
        const rating = (Math.random() * 2 + 3).toFixed(1);
        // Removed station status display
        
        const popupContent = `
            <div class="station-popup">
                <h3>${station.name}</h3>
                <div class="station-details">
                    <p><i class="fas fa-map-marker-alt"></i> ${distance} km away</p>
                    <p><i class="fas fa-clock"></i> ${waitTime} min wait</p>
                    <p><i class="fas fa-star"></i> ${rating}/5 rating</p>
                </div>
                <button onclick="getDirections(${position.lat}, ${position.lng})" class="direction-btn">
                    <i class="fas fa-directions"></i> Get Directions
                </button>
            </div>
        `;
        
        marker.bindPopup(popupContent);
        stationMarkers.push(marker);
        bounds.extend([position.lat, position.lng]);

        // Create compact two-line station card for sidebar
        const stationCard = document.createElement('div');
        stationCard.className = 'station-card compact fade-in';
        stationCard.style.animationDelay = `${index * 0.05}s`;
        
        stationCard.innerHTML = `
            <div class="station-line-1">
                <span class="station-name" title="${station.name}">${station.name}</span>
                <span class="station-distance-chip">${distance} km</span>
            </div>
            <div class="station-line-2">
                <span class="meta"><i class="fas fa-clock"></i> ${waitTime} min</span>
                <span class="meta"><i class="fas fa-star"></i> ${rating}</span>
            </div>
        `;

        stationCard.addEventListener('click', () => {
            map.setView([position.lat, position.lng], 15);
            marker.openPopup();
            addPulseAnimation(marker);
        });

        stationList.appendChild(stationCard);
    });

    // Fit map to show all markers with animation
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

function addPulseAnimation(marker) {
    const element = marker.getElement();
    if (element) {
        element.classList.add('pulse-animation');
        setTimeout(() => {
            element.classList.remove('pulse-animation');
        }, 1000);
    }
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const d = R * c;
    return d;
}

function deg2rad(deg) {
    return deg * (Math.PI/180);
}

function getDirections(lat, lng) {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
    window.open(url, '_blank');
    showNotification('Opening directions in Google Maps...', 'info');
}

function saveStation(name, lat, lng) {
    // In a real app, this would save to localStorage or send to server
    showNotification(`Saved ${name} to your favorites!`, 'success');
}

function toggleFullscreen() {
    const mapContainer = document.querySelector('.map-container');
    if (!document.fullscreenElement) {
        mapContainer.requestFullscreen().then(() => {
            showNotification('Entered fullscreen mode', 'info');
            setTimeout(() => map.invalidateSize(), 100);
        });
    } else {
        document.exitFullscreen().then(() => {
            showNotification('Exited fullscreen mode', 'info');
            setTimeout(() => map.invalidateSize(), 100);
        });
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Remove after delay
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

// Sidebar toggle removed

// Add CSS for custom markers and animations
const style = document.createElement('style');
style.textContent = `
    .custom-user-marker {
        background: none !important;
        border: none !important;
    }
    
    .user-marker-pin {
        width: 30px;
        height: 30px;
        background: linear-gradient(135deg, #dc3545, #ff6b7a);
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 10px rgba(220, 53, 69, 0.3);
        animation: userMarkerPulse 2s ease-in-out infinite;
    }
    
    .user-marker-pin i {
        transform: rotate(45deg);
        color: white;
        font-size: 12px;
    }
    
    .custom-station-marker {
        background: none !important;
        border: none !important;
    }
    
    .station-marker-pin {
        width: 25px;
        height: 25px;
        background: linear-gradient(135deg, #023E8A, #6BB6FF);
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(2, 62, 138, 0.3);
        transition: all 0.3s ease;
    }
    
    .station-marker-pin i {
        transform: rotate(45deg);
        color: white;
        font-size: 10px;
    }
    
    .station-marker-pin:hover {
        transform: rotate(-45deg) scale(1.2);
        box-shadow: 0 4px 12px rgba(2, 62, 138, 0.4);
    }
    
    @keyframes userMarkerPulse {
        0%, 100% { transform: rotate(-45deg) scale(1); }
        50% { transform: rotate(-45deg) scale(1.1); }
    }
    
    .pulse-animation {
        animation: pulse 1s ease-in-out;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 10000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        border-left: 4px solid #023E8A;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        border-left-color: #28a745;
    }
    
    .notification-error {
        border-left-color: #dc3545;
    }
    
    .notification-warning {
        border-left-color: #ffc107;
    }
    
    .notification i {
        font-size: 18px;
    }
    
    .notification-success i {
        color: #28a745;
    }
    
    .notification-error i {
        color: #dc3545;
    }
    
    .notification-warning i {
        color: #ffc107;
    }
    
    .user-popup {
        text-align: center;
        padding: 10px;
    }
    
    .user-popup h4 {
        margin: 0 0 10px 0;
        color: #023E8A;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .user-popup p {
        margin: 0;
        font-size: 12px;
        color: #666;
    }
`;
document.head.appendChild(style);
