/**
 * Analytics Dashboard - Frontend Logic
 */

document.addEventListener('DOMContentLoaded', function() {
    loadAnalytics();
});

async function loadAnalytics() {
    try {
        // Load all analytics data
        await Promise.all([
            loadOverviewStats(),
            loadRecommendations(),
            loadUsagePatterns(),
            loadEfficiencyAnalysis(),
            loadCostAnalysis(),
            loadWaitTimeAnalysis(),
            loadRecentActivity()
        ]);
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

async function loadOverviewStats() {
    try {
        const response = await fetch('/api/analytics/overview');
        const data = await response.json();

        // Update stat cards
        document.getElementById('totalCharges').textContent = data.total_charges || 0;
        document.getElementById('periodDays').textContent = `Last ${data.period_days} days`;
        
        document.getElementById('totalSpent').textContent = `₹${formatNumber(data.total_cost)}`;
        document.getElementById('avgPerCharge').textContent = `Avg per charge: ₹${formatNumber(data.avg_cost_per_charge)}`;
        
        document.getElementById('co2Saved').textContent = `${formatNumber(data.environmental_impact.co2_saved_kg)} kg`;
        document.getElementById('treesEquiv').textContent = `Trees equivalent: ${formatNumber(data.environmental_impact.trees_equivalent)}`;
        
        document.getElementById('totalSavings').textContent = `₹${formatNumber(data.financial_savings.vs_petrol)}`;
        document.getElementById('savingsPercent').textContent = `${formatNumber(data.financial_savings.savings_percentage)}% saved`;

    } catch (error) {
        console.error('Error loading overview stats:', error);
    }
}

async function loadRecommendations() {
    try {
        const response = await fetch('/api/analytics/recommendations');
        const data = await response.json();
        
        const grid = document.getElementById('recommendationsGrid');
        
        if (!data.recommendations || data.recommendations.length === 0) {
            grid.innerHTML = '<p class="no-data">No recommendations available at this time.</p>';
            return;
        }

        grid.innerHTML = '';
        data.recommendations.forEach(rec => {
            const card = document.createElement('div');
            card.className = `recommendation-card ${rec.type}`;
            card.innerHTML = `
                <div class="rec-icon">
                    <i class="fas fa-${rec.icon}"></i>
                </div>
                <div class="rec-content">
                    <h4>${rec.title}</h4>
                    <p>${rec.message}</p>
                </div>
            `;
            grid.appendChild(card);
        });

    } catch (error) {
        console.error('Error loading recommendations:', error);
    }
}

async function loadUsagePatterns() {
    try {
        const response = await fetch('/api/analytics/usage-patterns');
        const data = await response.json();

        // Daily pattern
        displayDailyPattern(data.hourly_distribution);
        
        // Weekly distribution
        displayWeeklyDistribution(data.daily_distribution, data.daily_amounts);

    } catch (error) {
        console.error('Error loading usage patterns:', error);
    }
}

async function loadEfficiencyAnalysis() {
    try {
        const response = await fetch('/api/analytics/efficiency');
        const data = await response.json();

        document.getElementById('avgEfficiency').textContent = `${data.average_efficiency || 0} km/kg`;
        document.getElementById('bestEfficiency').textContent = `${data.best_efficiency || 0} km/kg`;
        
        // Trend indicator
        const trendIndicator = document.getElementById('trendIndicator');
        let icon = 'minus';
        let text = 'Stable';
        let color = '#6b7280';
        
        if (data.trend === 'improving') {
            icon = 'arrow-up';
            text = `Up ${data.trend_percentage}%`;
            color = '#10b981';
        } else if (data.trend === 'declining') {
            icon = 'arrow-down';
            text = `Down ${Math.abs(data.trend_percentage)}%`;
            color = '#ef4444';
        }
        
        trendIndicator.innerHTML = `<i class="fas fa-${icon}"></i> ${text}`;
        trendIndicator.style.color = color;

    } catch (error) {
        console.error('Error loading efficiency analysis:', error);
    }
}

async function loadCostAnalysis() {
    try {
        const response = await fetch('/api/analytics/cost-analysis');
        const data = await response.json();

        displayMonthlySpending(data.monthly_breakdown);

    } catch (error) {
        console.error('Error loading cost analysis:', error);
    }
}

async function loadWaitTimeAnalysis() {
    try {
        const response = await fetch('/api/analytics/wait-time-analysis');
        const data = await response.json();

        document.getElementById('avgWaitTime').textContent = `${formatNumber(data.average_wait_time)} min`;
        
        // Find best time to charge (lowest wait)
        const hourlyAvg = data.hourly_average || {};
        const hours = Object.keys(hourlyAvg).map(Number);
        if (hours.length > 0) {
            const bestHour = hours.reduce((a, b) => hourlyAvg[a] < hourlyAvg[b] ? a : b);
            document.getElementById('bestTimeToCharge').textContent = `${bestHour}:00 - ${bestHour + 1}:00`;
        }
        
        // Peak hours
        const peakHours = data.peak_wait_hours || [];
        if (peakHours.length > 0) {
            document.getElementById('peakHours').textContent = peakHours.map(h => `${h}:00`).join(', ');
        }
        
        // Display hourly chart
        displayHourlyWaitChart(hourlyAvg);

    } catch (error) {
        console.error('Error loading wait time analysis:', error);
    }
}

async function loadRecentActivity() {
    try {
        const response = await fetch('/api/analytics/recent-activity?limit=10');
        const data = await response.json();
        
        const tbody = document.getElementById('recentActivityTable');
        
        if (!data.activity || data.activity.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="no-data">No recent activity</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        data.activity.forEach(activity => {
            const row = document.createElement('tr');
            const date = new Date(activity.date);
            row.innerHTML = `
                <td>${date.toLocaleDateString()} ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                <td>${activity.amount_kg} kg</td>
                <td>₹${formatNumber(activity.cost)}</td>
                <td>${activity.station_type}</td>
                <td>${activity.wait_time} min</td>
                <td>${activity.efficiency} km/kg</td>
            `;
            tbody.appendChild(row);
        });

    } catch (error) {
        console.error('Error loading recent activity:', error);
    }
}

function displayDailyPattern(hourlyData) {
    const container = document.getElementById('dailyPattern');
    
    if (!hourlyData || hourlyData.length === 0) {
        container.innerHTML = '<p class="no-data">No data available</p>';
        return;
    }

    const maxValue = Math.max(...hourlyData);
    
    let chartHTML = '<div class="horizontal-chart">';
    
    hourlyData.forEach((count, hour) => {
        const percentage = maxValue > 0 ? (count / maxValue) * 100 : 0;
        chartHTML += `
            <div class="chart-row">
                <span class="chart-label">${hour}:00</span>
                <div class="chart-bar-bg">
                    <div class="chart-bar-fill" style="width: ${percentage}%"></div>
                </div>
                <span class="chart-value">${count}</span>
            </div>
        `;
    });
    
    chartHTML += '</div>';
    container.innerHTML = chartHTML;
}

function displayWeeklyDistribution(dailyCharges, dailyAmounts) {
    const container = document.getElementById('weeklyDistribution');
    
    if (!dailyCharges || dailyCharges.length === 0) {
        container.innerHTML = '<p class="no-data">No data available</p>';
        return;
    }

    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const maxValue = Math.max(...dailyCharges);
    
    let chartHTML = '<div class="vertical-chart">';
    
    dailyCharges.forEach((count, index) => {
        const percentage = maxValue > 0 ? (count / maxValue) * 100 : 0;
        const amount = dailyAmounts ? dailyAmounts[index] : 0;
        
        chartHTML += `
            <div class="chart-column">
                <div class="column-bar-container">
                    <div class="column-bar" style="height: ${percentage}%" 
                         title="${count} charges, ${formatNumber(amount)} kg"></div>
                </div>
                <span class="column-label">${days[index]}</span>
                <span class="column-value">${count}</span>
            </div>
        `;
    });
    
    chartHTML += '</div>';
    container.innerHTML = chartHTML;
}

function displayMonthlySpending(monthlyData) {
    const container = document.getElementById('monthlySpending');
    
    if (!monthlyData || monthlyData.length === 0) {
        container.innerHTML = '<p class="no-data">No data available</p>';
        return;
    }

    const maxValue = Math.max(...monthlyData.map(m => m.total_cost));
    
    let chartHTML = '<div class="vertical-chart">';
    
    monthlyData.forEach(month => {
        const percentage = maxValue > 0 ? (month.total_cost / maxValue) * 100 : 0;
        const monthLabel = new Date(month.month + '-01').toLocaleDateString('en-US', { month: 'short' });
        
        chartHTML += `
            <div class="chart-column">
                <div class="column-bar-container">
                    <div class="column-bar" style="height: ${percentage}%" 
                         title="₹${formatNumber(month.total_cost)}"></div>
                </div>
                <span class="column-label">${monthLabel}</span>
                <span class="column-value">₹${formatNumber(month.total_cost)}</span>
            </div>
        `;
    });
    
    chartHTML += '</div>';
    container.innerHTML = chartHTML;
}

function displayHourlyWaitChart(hourlyAvg) {
    const container = document.getElementById('hourlyWaitChart');
    
    if (!hourlyAvg || Object.keys(hourlyAvg).length === 0) {
        container.innerHTML = '<p class="no-data">No data available</p>';
        return;
    }

    const hours = Object.keys(hourlyAvg).map(Number).sort((a, b) => a - b);
    const maxValue = Math.max(...hours.map(h => hourlyAvg[h]));
    
    let chartHTML = '<div class="horizontal-chart">';
    
    hours.forEach(hour => {
        const wait = hourlyAvg[hour];
        const percentage = maxValue > 0 ? (wait / maxValue) * 100 : 0;
        
        chartHTML += `
            <div class="chart-row">
                <span class="chart-label">${hour}:00</span>
                <div class="chart-bar-bg">
                    <div class="chart-bar-fill wait-time" style="width: ${percentage}%"></div>
                </div>
                <span class="chart-value">${formatNumber(wait)} min</span>
            </div>
        `;
    });
    
    chartHTML += '</div>';
    container.innerHTML = chartHTML;
}

function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return num.toLocaleString('en-IN', { maximumFractionDigits: 2 });
}
