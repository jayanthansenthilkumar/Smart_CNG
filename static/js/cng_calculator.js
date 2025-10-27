/**
 * CNG Switch Calculator - Frontend Logic
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('cngCalculatorForm');
    const resultsSection = document.getElementById('resultsSection');

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            vehicleType: document.getElementById('vehicleType').value,
            currentFuel: document.getElementById('currentFuel').value,
            dailyKm: document.getElementById('dailyKm').value,
            currentMileage: document.getElementById('currentMileage').value || null
        };

        // Validate
        if (!formData.vehicleType || !formData.currentFuel || !formData.dailyKm) {
            alert('Please fill in all required fields');
            return;
        }

        try {
            // Show loading state
            const button = form.querySelector('button[type="submit"]');
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculating...';
            button.disabled = true;

            // Call API
            const response = await fetch('/api/cng-calculator/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Calculation failed');
            }

            const results = await response.json();
            
            // Display results
            displayResults(results);
            
            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } catch (error) {
            console.error('Error:', error);
            alert('Error calculating savings. Please try again.');
        } finally {
            // Reset button
            const button = form.querySelector('button[type="submit"]');
            button.innerHTML = originalText;
            button.disabled = false;
        }
    });
});

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'block';

    // Recommendation
    displayRecommendation(data.recommendation);

    // Stats
    document.getElementById('annualSavings').textContent = `₹${formatNumber(data.savings.total_annual)}`;
    document.getElementById('paybackPeriod').textContent = data.roi.payback_months < 100 
        ? `${data.roi.payback_months} months (${data.roi.payback_years} years)` 
        : 'Not viable';
    document.getElementById('co2Reduction').textContent = `${formatNumber(data.environmental.annual_reduction_kg)} kg/year`;
    document.getElementById('fiveYearROI').textContent = `₹${formatNumber(data.savings.five_year)}`;

    // Cost comparison
    document.getElementById('currentFuelCost').textContent = `₹${formatNumber(data.current_costs.total)}/year`;
    document.getElementById('cngFuelCost').textContent = `₹${formatNumber(data.cng_costs.total)}/year`;
    document.getElementById('conversionCost').textContent = `₹${formatNumber(data.cng_costs.conversion)}`;
    document.getElementById('netSavings').textContent = `₹${formatNumber(data.savings.total_annual)}/year`;

    // Environmental impact
    document.getElementById('treesEquivalent').textContent = formatNumber(data.environmental.trees_equivalent);
    document.getElementById('emissionReduction').textContent = `${formatNumber(data.environmental.reduction_percentage)}%`;
    
    // Calculate petrol saved over 5 years
    const annualKm = parseFloat(document.getElementById('dailyKm').value) * 365;
    const fuelType = document.getElementById('currentFuel').value;
    const mileage = fuelType === 'petrol' ? 15 : 20;
    const petrolSaved = (annualKm / mileage) * 5;
    document.getElementById('petrolSaved').textContent = `${formatNumber(petrolSaved)} L`;

    // Savings chart
    displaySavingsChart(data.monthly_breakdown);
}

function displayRecommendation(recommendation) {
    const ratingDiv = document.getElementById('rating');
    const messageDiv = document.getElementById('recommendationMessage');
    const reasonsList = document.getElementById('recommendationReasons');

    // Rating stars
    const stars = '★'.repeat(recommendation.rating) + '☆'.repeat(5 - recommendation.rating);
    ratingDiv.innerHTML = `<span class="stars">${stars}</span>`;
    ratingDiv.className = 'rating rating-' + recommendation.rating;

    // Message
    messageDiv.textContent = recommendation.message;

    // Reasons
    reasonsList.innerHTML = '';
    recommendation.reasons.forEach(reason => {
        const li = document.createElement('li');
        li.innerHTML = `<i class="fas fa-check-circle"></i> ${reason}`;
        reasonsList.appendChild(li);
    });
}

function displaySavingsChart(monthlyData) {
    const chartDiv = document.getElementById('savingsChart');
    
    if (!monthlyData || monthlyData.length === 0) {
        chartDiv.innerHTML = '<p>No data available</p>';
        return;
    }

    // Create simple bar chart
    const maxValue = Math.max(...monthlyData.map(d => Math.abs(d.cumulative_saving)));
    const minValue = Math.min(...monthlyData.map(d => d.cumulative_saving));
    
    let chartHTML = '<div class="chart-bars">';
    
    // Show every 6 months for first 5 years
    const displayMonths = [6, 12, 18, 24, 30, 36, 42, 48, 54, 60];
    
    displayMonths.forEach(month => {
        if (month <= monthlyData.length) {
            const data = monthlyData[month - 1];
            const value = data.cumulative_saving;
            const isPositive = value >= 0;
            const percentage = Math.abs(value) / maxValue * 100;
            
            chartHTML += `
                <div class="chart-bar-container">
                    <div class="chart-bar ${isPositive ? 'positive' : 'negative'}" 
                         style="height: ${percentage}%"
                         title="Month ${month}: ₹${formatNumber(value)}">
                        <span class="bar-value">₹${formatNumber(value)}</span>
                    </div>
                    <span class="bar-label">Month ${month}</span>
                </div>
            `;
        }
    });
    
    chartHTML += '</div>';
    
    // Add breakeven indicator
    const breakevenMonth = monthlyData.findIndex(d => d.breakeven);
    if (breakevenMonth >= 0) {
        chartHTML += `<p class="breakeven-note">
            <i class="fas fa-check-circle"></i> 
            Breakeven point reached at month ${breakevenMonth + 1}
        </p>`;
    }
    
    chartDiv.innerHTML = chartHTML;
}

function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return num.toLocaleString('en-IN', { maximumFractionDigits: 0 });
}
