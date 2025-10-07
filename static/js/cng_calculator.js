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
            `₹${data.monthly.savings.toLocaleString(undefined, {maximumFractionDigits: 0})}`;
        document.getElementById('conversionCost').textContent = 
            `₹${data.conversion.cost.toLocaleString(undefined, {maximumFractionDigits: 0})}`;
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
                            callback: value => '₹' + value.toLocaleString()
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
                            callback: value => '₹' + value.toLocaleString()
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