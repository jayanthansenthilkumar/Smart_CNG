// Utility functions for SweetAlert2 notifications

const showSuccess = (title, message) => {
    Swal.fire({
        title: title,
        text: message,
        icon: 'success',
        confirmButtonText: 'OK',
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup',
            confirmButton: 'swal-button'
        }
    });
};

const showError = (title, message) => {
    Swal.fire({
        title: title,
        text: message,
        icon: 'error',
        confirmButtonText: 'OK',
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup',
            confirmButton: 'swal-button'
        }
    });
};

const showLoading = (message = 'Please wait...') => {
    Swal.fire({
        title: message,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        },
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup'
        }
    });
};

const closeLoading = () => {
    Swal.close();
};

const showConfirmation = async (title, message) => {
    const result = await Swal.fire({
        title: title,
        text: message,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup',
            confirmButton: 'swal-button',
            cancelButton: 'swal-button'
        }
    });
    return result.isConfirmed;
};
// Analytics Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all charts
    initializeCharts();
    
    // Load real-time station data
    loadStationStatistics();
    
    // Set up refresh interval for real-time data
    setInterval(loadStationStatistics, 300000); // Refresh every 5 minutes
});

function initializeCharts() {
    // Usage Patterns Chart
    const usageCtx = document.getElementById('usagePatternsChart').getContext('2d');
    const usageChart = new Chart(usageCtx, {
        type: 'line',
        data: {
            labels: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
            datasets: [{
                label: 'Average Wait Time (minutes)',
                data: [5, 3, 8, 15, 12, 10, 18, 7],
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Station Usage Patterns (24h)'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Wait Time (minutes)'
                    }
                }
            }
        }
    });

    // Environmental Impact Chart
    const envCtx = document.getElementById('environmentalImpactChart').getContext('2d');
    const envChart = new Chart(envCtx, {
        type: 'bar',
        data: {
            labels: ['CO2 Reduction', 'Trees Saved', 'Fuel Saved'],
            datasets: [{
                label: 'Monthly Impact',
                data: [1200, 45, 850],
                backgroundColor: [
                    'rgba(76, 175, 80, 0.7)',
                    'rgba(156, 204, 101, 0.7)',
                    'rgba(129, 199, 132, 0.7)'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Environmental Impact Metrics'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Station Activity Map
    initializeHeatmap();
}

function initializeHeatmap() {
    // Initialize the map centered on Delhi
    const map = L.map('stationActivityMap').setView([28.6139, 77.2090], 11);
    
    // Add the base map layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Â© OpenStreetMap contributors'
    }).addTo(map);
    
    // Add heatmap layer (using sample data)
    const points = [
        [28.6139, 77.2090, 0.8],
        [28.6229, 77.2100, 0.6],
        [28.6339, 77.2290, 0.4],
        // Add more points based on station activity
    ];
    
    const heatLayer = L.heatLayer(points, {
        radius: 25,
        blur: 15,
        maxZoom: 10,
        gradient: {
            0.4: 'blue',
            0.6: 'lime',
            0.8: 'red'
        }
    }).addTo(map);
}

async function loadStationStatistics() {
    try {
        showLoading('Loading statistics...');
        
        const response = await fetch('/api/station-statistics');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        updateStatistics(data);
        closeLoading();
        
    } catch (error) {
        console.error('Error loading statistics:', error);
        showError('Loading Error', 'Failed to load station statistics. Please try again later.');
    }
}

function updateStatistics(data) {
    // Update summary cards
    document.getElementById('totalUsers').textContent = data.totalUsers;
    document.getElementById('activeCNGVehicles').textContent = data.activeCNGVehicles;
    document.getElementById('totalStations').textContent = data.totalStations;
    document.getElementById('avgWaitTime').textContent = data.averageWaitTime + ' min';
    
    // Update cost savings
    document.getElementById('monthlySavings').textContent = 
        'â‚¹' + data.monthlySavings.toLocaleString();
    document.getElementById('annualSavings').textContent = 
        'â‚¹' + data.annualSavings.toLocaleString();
    
    // Update environmental impact
    document.getElementById('co2Reduced').textContent = 
        data.co2Reduced.toLocaleString() + ' kg';
    document.getElementById('treesEquivalent').textContent = 
        data.treesEquivalent.toLocaleString();
}
// CNG Calculator JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('cngCalculatorForm');
    const resultsSection = document.getElementById('resultsSection');
    let savingsChart = null;
    let fuelComparisonChart = null;

    // Initialize form with any saved vehicle data
    initializeForm();

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        showLoading('Calculating savings...');
        
        // Gather form data
        const formData = {
            vehicleType: document.getElementById('vehicleType').value,
            currentFuel: document.getElementById('currentFuel').value,
            monthlyDistance: parseFloat(document.getElementById('monthlyDistance').value),
            currentMileage: parseFloat(document.getElementById('currentMileage').value),
            kitType: document.getElementById('kitType').value
        };

        try {
            // Make API call to backend
            const response = await fetch('/api/calculate-cng-savings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Failed to calculate savings');
            }

            const data = await response.json();
            
            // Close loading indicator
            closeLoading();
            
            // Show success message
            showSuccess('Calculation Complete', 'Your CNG conversion analysis is ready!');
            
            // Display results
            displayResults(data);
            
            // Save form data for future use
            saveFormData(formData);
            
        } catch (error) {
            console.error('Error:', error);
            closeLoading();
            showError('Calculation Error', 'Failed to calculate savings. Please try again.');
        }
    });

    function displayResults(data) {
        // Show results section
        resultsSection.classList.remove('hidden');
        
        // Update financial summary
        document.getElementById('monthlySavings').textContent = 
            `â‚¹${data.monthly.savings.toLocaleString(undefined, {maximumFractionDigits: 0})}`;
        document.getElementById('conversionCost').textContent = 
            `â‚¹${data.conversion.cost.toLocaleString(undefined, {maximumFractionDigits: 0})}`;
        document.getElementById('breakEvenPeriod').textContent = 
            `${data.roi.months_to_breakeven} months`;
        
        // Update environmental impact
        document.getElementById('co2Reduction').textContent = 
            `${data.environmental.annual_co2_reduction.toFixed(1)} kg`;
        document.getElementById('treesEquivalent').textContent = 
            `${Math.round(data.environmental.trees_equivalent)} trees`;
        
        // Update charts
        updateSavingsChart(data);
        updateFuelComparisonChart(data);
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    function updateSavingsChart(data) {
        const ctx = document.getElementById('savingsChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (savingsChart) {
            savingsChart.destroy();
        }
        
        // Calculate cumulative savings over 5 years
        const labels = [];
        const savingsData = [];
        let cumulativeSavings = -data.conversion.cost;
        
        for (let month = 0; month <= 60; month += 12) {
            labels.push(`Year ${month/12}`);
            savingsData.push(cumulativeSavings + (data.monthly.savings * month));
        }
        
        savingsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Cumulative Savings',
                    data: savingsData,
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '5-Year Savings Projection'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: value => 'â‚¹' + value.toLocaleString()
                        }
                    }
                }
            }
        });
    }

    function updateFuelComparisonChart(data) {
        const ctx = document.getElementById('fuelComparisonChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (fuelComparisonChart) {
            fuelComparisonChart.destroy();
        }
        
        fuelComparisonChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Current Fuel', 'CNG'],
                datasets: [{
                    label: 'Monthly Fuel Cost',
                    data: [
                        data.monthly.current_fuel_cost,
                        data.monthly.cng_fuel_cost
                    ],
                    backgroundColor: [
                        '#ff7043',
                        '#4CAF50'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Fuel Cost Comparison'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: value => 'â‚¹' + value.toLocaleString()
                        }
                    }
                }
            }
        });
    }

    function saveFormData(formData) {
        localStorage.setItem('cngCalculatorData', JSON.stringify(formData));
    }

    function initializeForm() {
        const savedData = localStorage.getItem('cngCalculatorData');
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const element = document.getElementById(key);
                if (element) {
                    element.value = data[key];
                }
            });
        }
    }
});

function printResults() {
    const printWindow = window.open('', '_blank');
    const resultsSection = document.getElementById('resultsSection');
    
    printWindow.document.write(`
        <html>
            <head>
                <title>CNG Conversion Analysis Report</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    .header { text-align: center; margin-bottom: 30px; }
                    .results-grid { display: grid; gap: 20px; }
                    .result-card { border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; }
                    .summary-item { margin: 10px 0; }
                    canvas { max-width: 100%; height: auto; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>CNG Conversion Analysis Report</h1>
                    <p>Generated on ${new Date().toLocaleDateString()}</p>
                </div>
                ${resultsSection.innerHTML}
                <script>window.print();</script>
            </body>
        </html>
    `);
    
    printWindow.document.close();
}
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
        attribution: 'Â© OpenStreetMap contributors'
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
// Location Optimizer JavaScript
class LocationOptimizer {
    constructor() {
        this.map = null;
        this.markers = [];
        this.resultsMarkers = [];
        this.existingStationsMarkers = [];
        this.currentLocationMarker = null;
        this.currentLocation = null;
        this.results = [];
        this.analysis = null;
        
        this.init();
    }
    
    init() {
        console.log('Initializing Location Optimizer...');
        this.initializeMap();
        this.bindEvents();
        this.loadExistingStations();
        this.initializeSlider();
    }
    
    initializeSlider() {
        const radiusSlider = document.getElementById('radius');
        const radiusValue = document.getElementById('radius-value');
        
        if (radiusSlider && radiusValue) {
            // Set initial value
            radiusValue.textContent = radiusSlider.value;
            console.log('Slider initialized with value:', radiusSlider.value);
            
            // Add visual feedback
            radiusSlider.addEventListener('mousedown', () => {
                radiusSlider.style.transform = 'scale(1.02)';
            });
            
            radiusSlider.addEventListener('mouseup', () => {
                radiusSlider.style.transform = 'scale(1)';
            });
            
            radiusSlider.addEventListener('mouseleave', () => {
                radiusSlider.style.transform = 'scale(1)';
            });
        } else {
            console.error('Slider elements not found');
        }
    }
    
    initializeMap() {
        try {
            // Initialize map centered on Delhi
            this.map = L.map('map', {
                center: [28.6139, 77.2090],
                zoom: 11,
                zoomControl: true,
                attributionControl: true
            });
            
            // Add tile layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: 'Â© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(this.map);
            
            // Add click event to map
            this.map.on('click', (e) => {
                this.handleMapClick(e);
            });
            
            console.log('Map initialized successfully');
            
            // Ensure map is properly sized
            setTimeout(() => {
                this.map.invalidateSize();
            }, 100);
        } catch (error) {
            console.error('Error initializing map:', error);
            this.showMessage('Error initializing map. Please refresh the page.', 'error');
        }
    }
    
    bindEvents() {
        // Find locations button (in sidebar)
        document.getElementById('find-locations-btn').addEventListener('click', () => {
            this.findOptimalLocations();
        });
        
        // Find locations button (in map controls)
        document.getElementById('find-locations').addEventListener('click', () => {
            this.findOptimalLocations();
        });
        
        // Use My Location button
        document.getElementById('use-my-location').addEventListener('click', () => {
            this.useMyLocation();
        });
        
        // Select on Map button
        document.getElementById('select-on-map').addEventListener('click', () => {
            this.showMessage('Click anywhere on the map to select your area', 'info');
        });
        
        // Center map button
        document.getElementById('center-map').addEventListener('click', () => {
            if (this.currentLocation) {
                this.map.setView([this.currentLocation.lat, this.currentLocation.lng], 13);
            } else {
                this.map.setView([28.6139, 77.2090], 11);
            }
        });
        
        // Toggle layers button
        document.getElementById('toggle-layers').addEventListener('click', () => {
            this.showMessage('Layer toggle functionality coming soon', 'info');
        });
        
        // Radius slider update
        const radiusSlider = document.getElementById('radius');
        const radiusValue = document.getElementById('radius-value');
        
        if (radiusSlider && radiusValue) {
            radiusSlider.addEventListener('input', (e) => {
                const value = e.target.value;
                radiusValue.textContent = value;
                console.log('Slider value changed to:', value);
            });
            
            radiusSlider.addEventListener('change', (e) => {
                const value = e.target.value;
                radiusValue.textContent = value;
                console.log('Slider value finalized to:', value);
            });
        } else {
            console.error('Slider elements not found for event binding');
        }
        
        // Add enter key support for inputs
        ['center-lat', 'center-lng'].forEach(id => {
            document.getElementById(id).addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.findOptimalLocations();
                }
            });
        });
        
        // Handle window resize to fix map sizing
        window.addEventListener('resize', () => {
            if (this.map) {
                setTimeout(() => {
                    this.map.invalidateSize();
                }, 100);
            }
        });
    }
    
    async loadExistingStations() {
        try {
            console.log('Loading existing stations...');
            const response = await fetch('/api/stations-from-file');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Stations response:', data);
            
            if (data.stations && Array.isArray(data.stations)) {
                this.addExistingStationsToMap(data.stations);
                console.log(`Loaded ${data.stations.length} existing stations`);
            } else {
                console.warn('No stations data found in response');
            }
        } catch (error) {
            console.error('Error loading existing stations:', error);
            this.showMessage('Warning: Could not load existing stations data', 'error');
        }
    }
    
    addExistingStationsToMap(stations) {
        stations.forEach(station => {
            const marker = L.circleMarker([station.position.lat, station.position.lng], {
                radius: 6,
                fillColor: '#6c757d',
                color: 'white',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(this.map);
            
            marker.bindPopup(`
                <div>
                    <h4>${station.name}</h4>
                    <p>Lat: ${station.position.lat.toFixed(6)}</p>
                    <p>Lng: ${station.position.lng.toFixed(6)}</p>
                </div>
            `);
        });
    }
    
    async findOptimalLocations() {
        const latInput = document.getElementById('center-lat');
        const lngInput = document.getElementById('center-lng');
        const radiusInput = document.getElementById('radius');
        const numStationsInput = document.getElementById('num-stations');
        
        if (!latInput || !lngInput || !radiusInput || !numStationsInput) {
            this.showMessage('Required form elements not found', 'error');
            return;
        }
        
        const lat = parseFloat(latInput.value);
        const lng = parseFloat(lngInput.value);
        const radius = parseFloat(radiusInput.value);
        const numStations = parseInt(numStationsInput.value);
        
        console.log('Finding optimal locations with params:', { lat, lng, radius, numStations });
        
        if (isNaN(lat) || isNaN(lng)) {
            this.showMessage('Please enter valid latitude and longitude values', 'error');
            return;
        }
        
        if (isNaN(radius) || radius <= 0) {
            this.showMessage('Please set a valid search radius', 'error');
            return;
        }
        
        if (isNaN(numStations) || numStations <= 0) {
            this.showMessage('Please select a valid number of stations', 'error');
            return;
        }
        
        this.showLoading(true);
        
        try {
            const url = `/api/optimize-locations/${lat}/${lng}?radius=${radius}&num_stations=${numStations}`;
            console.log('Making request to:', url);
            
            const response = await fetch(url);
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
            }
            
            const data = await response.json();
            console.log('API Response:', data);
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Ensure candidates is an array and handle different response formats
            let candidates = [];
            if (data.candidates && Array.isArray(data.candidates)) {
                candidates = data.candidates;
                console.log('Found candidates:', candidates.length);
            } else if (Array.isArray(data)) {
                candidates = data;
                console.log('Data is array:', candidates.length);
            } else {
                console.warn('Unexpected API response format:', data);
                candidates = [];
            }
            
            this.results = candidates;
            this.displayResults(candidates);
            this.addResultsToMap(candidates, lat, lng);
            
            // Update map center
            this.map.setView([lat, lng], 12);
            
            // Show success message
            if (candidates.length > 0) {
                this.showMessage(`Found ${candidates.length} optimal location${candidates.length !== 1 ? 's' : ''}`, 'info');
            } else {
                this.showMessage('No optimal locations found. Try adjusting the search parameters.', 'info');
            }
            
        } catch (error) {
            console.error('Error finding optimal locations:', error);
            this.showMessage('Error finding optimal locations: ' + error.message, 'error');
            this.displayResults([]);
        } finally {
            this.showLoading(false);
        }
    }
    
    async useMyLocation() {
        if (!navigator.geolocation) {
            this.showMessage('Geolocation is not supported by this browser', 'error');
            return;
        }
        
        this.showMessage('Getting your location...', 'info');
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                // Update input fields
                document.getElementById('center-lat').value = lat.toFixed(6);
                document.getElementById('center-lng').value = lng.toFixed(6);
                
                // Update map center
                this.map.setView([lat, lng], 13);
                
                // Add marker for current location
                this.clearCurrentLocationMarker();
                this.currentLocationMarker = L.marker([lat, lng], {
                    icon: L.divIcon({
                        className: 'custom-marker',
                        html: '<div style="background: #667eea; border: 3px solid white; border-radius: 50%; width: 20px; height: 20px;"></div>',
                        iconSize: [20, 20]
                    })
                }).addTo(this.map);
                
                this.currentLocation = { lat, lng };
                this.showMessage('Location found! Click "Find Optimal Locations" to analyze', 'info');
            },
            (error) => {
                let errorMessage = 'Unable to get your location';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = 'Location access denied. Please allow location access.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = 'Location information unavailable.';
                        break;
                    case error.TIMEOUT:
                        errorMessage = 'Location request timed out.';
                        break;
                }
                this.showMessage(errorMessage, 'error');
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000
            }
        );
    }

    clearCurrentLocationMarker() {
        if (this.currentLocationMarker) {
            this.map.removeLayer(this.currentLocationMarker);
            this.currentLocationMarker = null;
        }
    }

    showMessage(message, type = 'info') {
        // Create a temporary message element
        const messageEl = document.createElement('div');
        messageEl.className = `message message-${type}`;
        messageEl.textContent = message;
        messageEl.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'info' ? '#667eea' : '#dc3545'};
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-size: 0.9em;
            font-weight: 500;
        `;
        
        document.body.appendChild(messageEl);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 3000);
    }
    
    handleMapClick(e) {
        this.currentLocation = {
            lat: e.latlng.lat,
            lng: e.latlng.lng
        };
        
        // Update input fields
        document.getElementById('center-lat').value = e.latlng.lat.toFixed(6);
        document.getElementById('center-lng').value = e.latlng.lng.toFixed(6);
        
        // Add marker for current location
        this.clearCurrentLocationMarker();
        this.currentLocationMarker = L.marker([e.latlng.lat, e.latlng.lng], {
            icon: L.divIcon({
                className: 'custom-marker',
                html: '<div style="background: #667eea; border: 3px solid white; border-radius: 50%; width: 20px; height: 20px;"></div>',
                iconSize: [20, 20]
            })
        }).addTo(this.map);
        
        // Show a brief message
        this.showMessage('Area selected! Click "Find Optimal Locations" to analyze.', 'info');
    }
    
    clearCurrentLocationMarker() {
        if (this.currentLocationMarker) {
            this.map.removeLayer(this.currentLocationMarker);
        }
    }
    
    clearResultsMarkers() {
        this.resultsMarkers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.resultsMarkers = [];
    }
    
    addResultsToMap(candidates, centerLat, centerLng) {
        this.clearResultsMarkers();
        this.resultsMarkers = [];
        
        if (!candidates || !Array.isArray(candidates)) {
            console.warn('No candidates to display on map');
            return;
        }
        
        // Add center marker
        const centerMarker = L.marker([centerLat, centerLng], {
            icon: L.divIcon({
                className: 'custom-marker',
                html: '<div style="background: #ff6b6b; border: 3px solid white; border-radius: 50%; width: 20px; height: 20px;"></div>',
                iconSize: [20, 20]
            })
        }).addTo(this.map);
        
        centerMarker.bindPopup('<strong>Search Center</strong>');
        this.resultsMarkers.push(centerMarker);
        
        // Add candidate markers
        candidates.forEach((candidate, index) => {
            if (candidate && candidate.position && candidate.position.lat && candidate.position.lng) {
                const marker = L.marker([candidate.position.lat, candidate.position.lng], {
                    icon: L.divIcon({
                        className: 'recommended-marker',
                        html: `<div style="background: #28a745; border: 3px solid white; border-radius: 50%; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 12px;">${index + 1}</div>`,
                        iconSize: [25, 25]
                    })
                }).addTo(this.map);
                
                marker.bindPopup(`
                    <div>
                        <h4>${candidate.name || 'Recommended Station'}</h4>
                        <p><strong>Score:</strong> ${candidate.total_score || 'N/A'}</p>
                        <p><strong>Area Type:</strong> ${candidate.area_type || 'N/A'}</p>
                        <p><strong>Distance:</strong> ${candidate.distance_from_center || 'N/A'} km</p>
                        <p><strong>Reason:</strong> ${candidate.recommendation_reason || 'Good location for CNG station'}</p>
                    </div>
                `);
                
                this.resultsMarkers.push(marker);
            }
        });
    }
    
    displayResults(candidates) {
        const container = document.getElementById('results-list');
        
        console.log('Displaying results:', candidates);
        
        // Handle undefined or null candidates
        if (!candidates || !Array.isArray(candidates)) {
            console.log('No candidates to display');
            container.innerHTML = `
                <div class="results-fallback">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>No optimal locations found</p>
                    <small>Try adjusting the search parameters or selecting a different area</small>
                </div>
            `;
            return;
        }
        
        if (candidates.length === 0) {
            console.log('Empty candidates array');
            container.innerHTML = `
                <div class="results-fallback">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>No optimal locations found</p>
                    <small>Try adjusting the search parameters or selecting a different area</small>
                </div>
            `;
            return;
        }
        
        console.log(`Displaying ${candidates.length} location cards`);
        
        container.innerHTML = candidates.map((candidate, index) => `
            <div class="location-card compact" data-index="${index}">
                <div class="location-line-1">
                    <div class="location-name">${candidate.name || 'Recommended Station'}</div>
                    <div class="location-distance-chip">${candidate.distance_from_center || 'N/A'} km</div>
                </div>
                <div class="location-line-2">
                    <div class="meta">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${candidate.area_type || 'N/A'}</span>
                    </div>
                    <div class="meta">
                        <i class="fas fa-star"></i>
                        <span>Score: ${candidate.total_score || 'N/A'}</span>
                    </div>
                </div>
                <div class="location-details">
                    <div class="detail-item">
                        <i class="fas fa-chart-line"></i>
                        <span>Demand: ${candidate.demand_score || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-road"></i>
                        <span>Access: ${candidate.accessibility_score || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-dollar-sign"></i>
                        <span>Economic: ${candidate.economic_score || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-users"></i>
                        <span>Competition: ${candidate.competition_score || 'N/A'}</span>
                    </div>
                </div>
                <div class="location-actions">
                    <button class="action-btn primary-btn" onclick="navigator.clipboard.writeText('${candidate.position.lat}, ${candidate.position.lng}')">
                        <i class="fas fa-copy"></i> Copy Coordinates
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }
}

// Initialize the location optimizer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new LocationOptimizer();
});
let map;
let userMarker = null;
let stationMarkers = [];
let allStationMarkers = [];
let routingControl = null;
let accuracyCircle = null;
let isMapInitialized = false;
let searchRadius = 5; // Default radius in km
let radiusCircle = null;
const AVG_SPEED_KMPH = 30; // Average driving speed for ETA in km/h

// Replace with your Google Maps API key
const GOOGLE_MAPS_API_KEY = 'YOUR_API_KEY';

// Initialize map when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if the map container exists
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
        
        // Update radius circle if user location exists
        if (userMarker) {
            updateRadiusCircle(userMarker.getLatLng());
        }
        
        // Refetch stations with new radius if we have a location
        if (userMarker) {
            const pos = userMarker.getLatLng();
            fetchNearbyStations(pos.lat, pos.lng);
        }
    });

    isMapInitialized = true;

    // Load all stations from CSV on initial page load
    loadAllStationsFromFile();
}

function getCurrentLocation() {
    const button = document.getElementById('location-button');
    button.disabled = true;
    showLoading('Getting your location...');

    const done = () => {
        closeLoading();
        button.disabled = false;
    };

    if (!navigator.geolocation) {
        showError("Location Error", "Geolocation is not supported by your browser");
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
            showError('Location Error', 'Unable to determine your location. Click on the map to choose a point.');
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
                showError('Location Permission Denied', 'Location permission denied. You can click on the map to select a point.');
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
                    showWarning('Location Access Blocked', 'Location access is blocked for this site. Enable it in your browser settings, or click on the map to choose a point.');
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

    // Update radius circle
    updateRadiusCircle([lat, lng]);

    // Update API call to include radius
    fetchNearbyStations(lat, lng);
}

function fetchNearbyStations(lat, lng) {
    // Show loading state
    const stationList = document.getElementById('station-list');
    stationList.innerHTML = '<div class="loading">Finding CNG stations...</div>';

    // Prefer server-side filtered endpoint with wait-time predictions
    fetch(`/api/stations-with-wait/${lat}/${lng}?radius=${searchRadius}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            const stations = (data.stations || []).map(s => ({
                name: s.name,
                position: s.position,
                _dist: s.distance_km,
                predicted_wait: typeof s.predicted_wait === 'number' ? s.predicted_wait : null,
                prediction_confidence: s.prediction_confidence
            }));
            if (stations.length === 0) {
                stationList.innerHTML = '<div class="no-stations">No CNG stations found within ' + searchRadius + 'km radius</div>';
                showInfo('No Stations Found', 'No CNG stations found within ' + searchRadius + 'km radius. Try increasing the search radius.');
            } else {
                displayStations(stations);
                showSuccess('Stations Found', `Found ${stations.length} CNG stations near you!`);
            }
        })
        .catch(error => {
            console.error('Error fetching stations:', error);
            // Fallback to client-side from file
            fetch('/api/stations-from-file')
                .then(r => r.json())
                .then(data => {
                    if (data.error) throw new Error(data.error);
                    const all = (data.stations || []).map(s => ({ name: s.name, position: s.position }));
                    const within = all
                        .map(s => ({...s, _dist: calculateDistance(lat, lng, s.position.lat, s.position.lng)}))
                        .filter(s => s._dist <= searchRadius)
                        .sort((a,b) => a._dist - b._dist);
                    if (within.length === 0) {
                        stationList.innerHTML = '<div class="no-stations">No CNG stations found within ' + searchRadius + 'km radius</div>';
                    } else {
                        displayStations(within);
                    }
                })
                .catch(err => {
                    stationList.innerHTML = '<div class="no-stations">Unable to load stations data.</div>';
                    showError('Data Loading Error', 'Unable to load stations data. Please try again later.');
                });
        });
}

// Load and render ALL stations from CSV on the map
function loadAllStationsFromFile() {
    // Clear existing full markers
    allStationMarkers.forEach(m => map.removeLayer(m));
    allStationMarkers = [];

    fetch('/api/stations-from-file')
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                console.error('Stations file error:', data.error);
                showError('Data Loading Error', 'Unable to load stations data: ' + data.error);
                return;
            }
            const stations = data.stations || [];
            if (!stations.length) return;

            const bounds = L.latLngBounds();
            stations.forEach(s => {
                const pos = s.position || {};
                if (typeof pos.lat !== 'number' || typeof pos.lng !== 'number') return;
                const marker = L.marker([pos.lat, pos.lng]).addTo(map);
                marker.bindPopup(`<div class="station-popup"><h3>${s.name || 'CNG Station'}</h3><div class="station-details"><p><i class=\"fas fa-map-marker-alt\"></i> ${pos.lat.toFixed(5)}, ${pos.lng.toFixed(5)}</p></div></div>`);
                allStationMarkers.push(marker);
                bounds.extend([pos.lat, pos.lng]);
            });

            if (allStationMarkers.length) {
                map.fitBounds(bounds, { padding: [40, 40] });
            }
        })
        .catch(err => {
            console.error('Failed to load stations file:', err);
            showError('Data Loading Error', 'Failed to load stations data. Please check your connection and try again.');
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

    // Update station list
    const stationList = document.getElementById('station-list');
    stationList.innerHTML = '';

    // Create bounds to fit all markers
    const bounds = L.latLngBounds();

    // Sort stations by provided distance if available
    const userPos = userMarker.getLatLng();
    stations.sort((a, b) => {
        const ad = typeof a._dist === 'number' ? a._dist : calculateDistance(userPos.lat, userPos.lng, a.position.lat, a.position.lng);
        const bd = typeof b._dist === 'number' ? b._dist : calculateDistance(userPos.lat, userPos.lng, b.position.lat, b.position.lng);
        return ad - bd;
    });

    stations.forEach((station, index) => {
        const position = station.position || { lat: station.lat, lng: station.lng };
        const distanceKm = (typeof station._dist === 'number')
            ? station._dist
            : calculateDistance(userPos.lat, userPos.lng, position.lat, position.lng);
        const distance = distanceKm.toFixed(1);
        const travelTimeMin = Math.round((distanceKm / AVG_SPEED_KMPH) * 60);
        const waitMin = station.predicted_wait != null ? Math.round(station.predicted_wait) : null;
        const totalTimeMin = waitMin != null ? (travelTimeMin + waitMin) : travelTimeMin;

        // Add marker to map
        const marker = L.marker([position.lat, position.lng]).addTo(map);

        // Create popup content with distance
        const popupContent = `
            <div class="station-popup">
                <h3>${station.name}</h3>
                <div class="station-details">
                    <p><i class="fas fa-map-marker-alt"></i> ${distance} km away</p>
                    <p><i class="fas fa-road"></i> ~${travelTimeMin} mins travel</p>
                    ${waitMin != null ? `<p><i class="fas fa-clock"></i> ~${waitMin} mins predicted wait</p>` : ''}
                    <p><i class="fas fa-stopwatch"></i> ~${totalTimeMin} mins total</p>
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
                <p><i class="fas fa-road"></i> ~${travelTimeMin} mins travel</p>
                ${waitMin != null ? `<p><i class=\"fas fa-clock\"></i> ~${waitMin} mins predicted wait</p>` : ''}
                <p><i class="fas fa-stopwatch"></i> ~${totalTimeMin} mins total</p>
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

function getCustomIcon(type, isAvailable) {
    const colors = {
        market: '#4CAF50',    // Green
        office: '#2196F3',    // Blue
        hospital: '#F44336',  // Red
        school: '#FF9800',    // Orange
        mall: '#9C27B0',      // Purple
        parking: '#FDD835',   // Yellow
        default: '#2196F3'    // Default Blue
    };

    const color = colors[type.toLowerCase()] || colors.default;
    const opacity = isAvailable ? '1' : '0.5';

    return L.divIcon({
        className: 'custom-marker',
        html: `
            <div class="marker-pin" style="background-color: ${color}; opacity: ${opacity};">
                <i class="fas fa-gas-pump"></i>
            </div>
        `,
        iconSize: [30, 42],
        iconAnchor: [15, 42],
        popupAnchor: [0, -42]
    });
}

function getDirections(destLat, destLng) {
    if (!userMarker) {
        alert("Please set your location first!");
        return;
    }
    
    const userPos = userMarker.getLatLng();
    const url = `https://www.google.com/maps/dir/?api=1&origin=${userPos.lat},${userPos.lng}&destination=${destLat},${destLng}&travelmode=driving`;
    window.open(url, '_blank');
}

function updateRadiusCircle(latLng) {
    // Remove existing circle if it exists
    if (radiusCircle) {
        map.removeLayer(radiusCircle);
    }
    
    // Create new circle
    radiusCircle = L.circle(latLng, {
        radius: searchRadius * 1000, // Convert km to meters
        color: '#4CAF50',
        fillColor: '#4CAF50',
        fillOpacity: 0.1,
        weight: 1
    }).addTo(map);
}

// Add some CSS for the location button
const style = document.createElement('style');
style.textContent = `
    .custom-map-control {
        margin: 10px;
    }
    .location-button {
        padding: 8px 12px;
        background: white;
        border: 2px solid rgba(0,0,0,0.2);
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }
    .location-button:hover {
        background: #f4f4f4;
    }
    .location-button:disabled {
        background: #cccccc;
        cursor: wait;
    }
`;
document.head.appendChild(style);

function initSidebarToggle() {
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.toggle-sidebar');
    const toggleIcon = toggleBtn.querySelector('i');
    const fallback = document.querySelector('.station-list-fallback');
    
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        
        // Update icon and add transition
        if (sidebar.classList.contains('collapsed')) {
            toggleIcon.style.transform = 'rotate(180deg)';
            toggleBtn.style.display = 'block';
            toggleBtn.style.position = 'relative';
            toggleBtn.style.zIndex = '1000';
            if (fallback) fallback.style.display = 'none';  // Hide fallback when collapsed
        } else {
            toggleIcon.style.transform = 'rotate(0deg)';
            toggleBtn.style.position = 'static';
            // Only show fallback if no stations are listed
            if (fallback && document.querySelectorAll('.station-card').length === 0) {
                fallback.style.display = 'flex';
            }
        }
        
        // Trigger a resize event to update the map
        if (map) {
            setTimeout(() => {
                map.invalidateSize();
            }, 300);
        }
    });
}

function toggleProfileDropdown() {
    const dropdown = document.getElementById('profileDropdown');
    dropdown.classList.toggle('active');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const profileMenu = document.querySelector('.profile-menu');
    const dropdown = document.getElementById('profileDropdown');
    
    if (profileMenu && dropdown && !profileMenu.contains(event.target)) {
        dropdown.classList.remove('active');
    }
});
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
        attribution: 'Â© OpenStreetMap contributors'
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
