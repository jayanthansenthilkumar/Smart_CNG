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
        attribution: '© OpenStreetMap contributors'
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
        '₹' + data.monthlySavings.toLocaleString();
    document.getElementById('annualSavings').textContent = 
        '₹' + data.annualSavings.toLocaleString();
    
    // Update environmental impact
    document.getElementById('co2Reduced').textContent = 
        data.co2Reduced.toLocaleString() + ' kg';
    document.getElementById('treesEquivalent').textContent = 
        data.treesEquivalent.toLocaleString();
}