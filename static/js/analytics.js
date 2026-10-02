/**
 * Community Health Data Collection & Analysis
 * Advanced Epidemiological Analytics & Cross-Tabulations
 */

let analyticsCharts = {};

document.addEventListener('DOMContentLoaded', () => {
    initAnalytics();

    const locationFilter = document.getElementById('analytics-location-filter');
    if (locationFilter) {
        locationFilter.addEventListener('change', (e) => {
            loadAnalyticsData(e.target.value);
        });
    }
});

async function initAnalytics() {
    await loadAnalyticsData();
}

async function loadAnalyticsData(location = '') {
    try {
        const url = location ? `/api/charts/data?location=${encodeURIComponent(location)}` : '/api/charts/data';
        const response = await fetch(url);
        const data = await response.json();

        renderActivityImpactChart(data.activity_impact);
        renderAgeRiskChart(data.age_groups, data.hypertension);
        renderBmiDiabetesChart(data.bmi_categories, data.diabetes);
        renderRiskBreakdownChart(data.risk_breakdown);
    } catch (err) {
        console.error('Failed to load analytics data:', err);
    }
}

/**
 * Chart 1: Physical Activity vs Chronic Condition Burden
 */
function renderActivityImpactChart(activityData) {
    const ctx = document.getElementById('chart-activity-impact');
    if (!ctx) return;

    if (analyticsCharts.activity) analyticsCharts.activity.destroy();

    const labels = activityData.map(d => d.physical_activity);
    const total = activityData.map(d => d.total);
    const chronic = activityData.map(d => d.chronic_cases);

    analyticsCharts.activity = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total Sample Screened',
                    data: total,
                    backgroundColor: 'rgba(100, 116, 139, 0.4)',
                    borderColor: '#64748b',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    label: 'Chronic Cases (HTN / Diabetes)',
                    data: chronic,
                    backgroundColor: 'rgba(239, 68, 68, 0.75)',
                    borderColor: '#ef4444',
                    borderWidth: 1,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', labels: { boxWidth: 12, padding: 12 } }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}

/**
 * Chart 2: Age Cohort vs Hypertension Vulnerability
 */
function renderAgeRiskChart(ageGroups) {
    const ctx = document.getElementById('chart-age-risk');
    if (!ctx) return;

    if (analyticsCharts.ageRisk) analyticsCharts.ageRisk.destroy();

    const labels = Object.keys(ageGroups);
    const values = Object.values(ageGroups);

    analyticsCharts.ageRisk = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Population Screened',
                data: values,
                borderColor: '#0f766e',
                backgroundColor: 'rgba(15, 118, 110, 0.15)',
                borderWidth: 2.5,
                fill: true,
                tension: 0.35,
                pointBackgroundColor: '#0f766e',
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', labels: { boxWidth: 12, padding: 12 } }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}

/**
 * Chart 3: BMI vs Diabetes Risk Correlation
 */
function renderBmiDiabetesChart(bmiCats) {
    const ctx = document.getElementById('chart-bmi-diabetes');
    if (!ctx) return;

    if (analyticsCharts.bmiDiabetes) analyticsCharts.bmiDiabetes.destroy();

    analyticsCharts.bmiDiabetes = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(bmiCats),
            datasets: [{
                data: Object.values(bmiCats),
                backgroundColor: [
                    '#0284c7', // Underweight
                    '#10b981', // Normal
                    '#f59e0b', // Overweight
                    '#ef4444'  // Obese
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12 } }
            },
            cutout: '65%'
        }
    });
}

/**
 * Chart 4: Risk Score Tier Breakdown (Polar Area)
 */
function renderRiskBreakdownChart(riskData) {
    const ctx = document.getElementById('chart-risk-polar');
    if (!ctx) return;

    if (analyticsCharts.riskPolar) analyticsCharts.riskPolar.destroy();

    analyticsCharts.riskPolar = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: ['Low Risk', 'Moderate Risk', 'High Risk'],
            datasets: [{
                data: [riskData.Low || 0, riskData.Moderate || 0, riskData.High || 0],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.75)',
                    'rgba(245, 158, 11, 0.75)',
                    'rgba(239, 68, 68, 0.75)'
                ],
                borderColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 1.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12 } }
            }
        }
    });
}
