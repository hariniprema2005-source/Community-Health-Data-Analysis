/**
 * Community Health Data Collection & Analysis
 * Dashboard Chart.js Visualizations & Dynamic Filtering
 */

let charts = {};

// Color Palettes
const CHART_COLORS = {
    teal: '#0d9488',
    tealLight: 'rgba(13, 148, 136, 0.75)',
    blue: '#0284c7',
    blueLight: 'rgba(2, 132, 199, 0.75)',
    emerald: '#10b981',
    emeraldLight: 'rgba(16, 185, 129, 0.75)',
    amber: '#f59e0b',
    amberLight: 'rgba(245, 158, 11, 0.75)',
    rose: '#ef4444',
    roseLight: 'rgba(239, 68, 68, 0.75)',
    purple: '#8b5cf6',
    purpleLight: 'rgba(139, 92, 246, 0.75)',
    slate: '#64748b'
};

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();

    const locationFilter = document.getElementById('dashboard-location-filter');
    if (locationFilter) {
        locationFilter.addEventListener('change', (e) => {
            loadChartData(e.target.value);
        });
    }
});

async function initDashboard() {
    await loadChartData();
}

/**
 * Fetches chart data from backend API and renders/updates all Chart.js instances.
 */
async function loadChartData(location = '') {
    try {
        const url = location ? `/api/charts/data?location=${encodeURIComponent(location)}` : '/api/charts/data';
        const response = await fetch(url);
        const data = await response.json();

        renderDiabetesChart(data.diabetes);
        renderHypertensionChart(data.hypertension);
        renderAgeGroupChart(data.age_groups);
        renderGenderChart(data.genders);
        renderBmiChart(data.bmi_categories);
        renderBpChart(data.bp_categories);
        renderLocationChart(data.location_stats);
    } catch (err) {
        console.error('Failed to load chart data:', err);
    }
}

/**
 * Chart 1: Diabetes Distribution (Doughnut)
 */
function renderDiabetesChart(data) {
    const ctx = document.getElementById('chart-diabetes');
    if (!ctx) return;

    if (charts.diabetes) charts.diabetes.destroy();

    charts.diabetes = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Diabetic (Yes)', 'Non-Diabetic (No)', 'Pre-Diabetic'],
            datasets: [{
                data: [data.Yes || 0, data.No || 0, data['Pre-diabetic'] || 0],
                backgroundColor: [CHART_COLORS.rose, CHART_COLORS.emerald, CHART_COLORS.amber],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, padding: 14 } },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` ${ctx.label}: ${ctx.raw} individuals`
                    }
                }
            },
            cutout: '68%'
        }
    });
}

/**
 * Chart 2: Hypertension Distribution (Doughnut)
 */
function renderHypertensionChart(data) {
    const ctx = document.getElementById('chart-hypertension');
    if (!ctx) return;

    if (charts.hypertension) charts.hypertension.destroy();

    charts.hypertension = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Hypertensive (Yes)', 'Normal BP (No)'],
            datasets: [{
                data: [data.Yes || 0, data.No || 0],
                backgroundColor: [CHART_COLORS.rose, CHART_COLORS.teal],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, padding: 14 } },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` ${ctx.label}: ${ctx.raw} individuals`
                    }
                }
            },
            cutout: '68%'
        }
    });
}

/**
 * Chart 3: Age Group Distribution (Bar)
 */
function renderAgeGroupChart(data) {
    const ctx = document.getElementById('chart-age');
    if (!ctx) return;

    if (charts.age) charts.age.destroy();

    charts.age = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Individuals Screened',
                data: Object.values(data),
                backgroundColor: CHART_COLORS.tealLight,
                borderColor: CHART_COLORS.teal,
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 },
                    grid: { color: '#f1f5f9' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

/**
 * Chart 4: Gender Distribution (Doughnut)
 */
function renderGenderChart(data) {
    const ctx = document.getElementById('chart-gender');
    if (!ctx) return;

    if (charts.gender) charts.gender.destroy();

    charts.gender = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Male', 'Female', 'Other'],
            datasets: [{
                data: [data.Male || 0, data.Female || 0, data.Other || 0],
                backgroundColor: [CHART_COLORS.blue, '#ec4899', CHART_COLORS.purple],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, padding: 14 } }
            },
            cutout: '65%'
        }
    });
}

/**
 * Chart 5: BMI Category Breakdown (Horizontal Bar)
 */
function renderBmiChart(data) {
    const ctx = document.getElementById('chart-bmi');
    if (!ctx) return;

    if (charts.bmi) charts.bmi.destroy();

    charts.bmi = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Underweight', 'Normal', 'Overweight', 'Obese'],
            datasets: [{
                label: 'Individuals',
                data: [data.Underweight || 0, data.Normal || 0, data.Overweight || 0, data.Obese || 0],
                backgroundColor: [
                    CHART_COLORS.blueLight,
                    CHART_COLORS.emeraldLight,
                    CHART_COLORS.amberLight,
                    CHART_COLORS.roseLight
                ],
                borderColor: [
                    CHART_COLORS.blue,
                    CHART_COLORS.emerald,
                    CHART_COLORS.amber,
                    CHART_COLORS.rose
                ],
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#f1f5f9' } },
                y: { grid: { display: false } }
            }
        }
    });
}

/**
 * Chart 6: Blood Pressure Category Distribution (Bar)
 */
function renderBpChart(data) {
    const ctx = document.getElementById('chart-bp');
    if (!ctx) return;

    if (charts.bp) charts.bp.destroy();

    charts.bp = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Normal', 'Elevated', 'Stage 1', 'Stage 2', 'Crisis'],
            datasets: [{
                label: 'Cases',
                data: [
                    data.Normal || 0,
                    data.Elevated || 0,
                    data['Hypertension Stage 1'] || 0,
                    data['Hypertension Stage 2'] || 0,
                    data['Hypertensive Crisis'] || 0
                ],
                backgroundColor: [
                    CHART_COLORS.emeraldLight,
                    CHART_COLORS.blueLight,
                    CHART_COLORS.amberLight,
                    CHART_COLORS.roseLight,
                    'rgba(153, 27, 27, 0.85)'
                ],
                borderColor: [
                    CHART_COLORS.emerald,
                    CHART_COLORS.blue,
                    CHART_COLORS.amber,
                    CHART_COLORS.rose,
                    '#991b1b'
                ],
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}

/**
 * Chart 7: Location-wise Health Statistics (Grouped Bar)
 */
function renderLocationChart(locationsData) {
    const ctx = document.getElementById('chart-location');
    if (!ctx) return;

    if (charts.location) charts.location.destroy();

    const labels = locationsData.map(d => d.location);
    const totalScreened = locationsData.map(d => d.total);
    const diabetesCases = locationsData.map(d => d.diabetes_count);
    const hypertensionCases = locationsData.map(d => d.hypertension_count);

    charts.location = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total Screened',
                    data: totalScreened,
                    backgroundColor: 'rgba(100, 116, 139, 0.4)',
                    borderColor: '#64748b',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    label: 'Hypertension Cases',
                    data: hypertensionCases,
                    backgroundColor: CHART_COLORS.amberLight,
                    borderColor: CHART_COLORS.amber,
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    label: 'Diabetes Cases',
                    data: diabetesCases,
                    backgroundColor: CHART_COLORS.roseLight,
                    borderColor: CHART_COLORS.rose,
                    borderWidth: 1,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', labels: { boxWidth: 12, padding: 14 } }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}
