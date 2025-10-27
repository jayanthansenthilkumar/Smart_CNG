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
                attribution: '© OpenStreetMap contributors',
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
