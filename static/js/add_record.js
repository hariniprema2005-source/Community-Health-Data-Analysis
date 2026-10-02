/**
 * Community Health Data Collection & Analysis
 * Add/Edit Record Form: Real-time Health Biomarker Calculator & Live Validation
 */

document.addEventListener('DOMContentLoaded', () => {
    setupLiveCalculators();
    setupFormValidation();
    // Run initial calculation in case fields are pre-filled (e.g. edit mode)
    calculateLiveMetrics();
});

function setupLiveCalculators() {
    const inputs = [
        'input-height', 'input-weight', 'input-systolic',
        'input-diastolic', 'input-glucose', 'input-age',
        'select-diabetes', 'select-hypertension', 'select-smoking',
        'select-activity'
    ];

    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', calculateLiveMetrics);
            el.addEventListener('change', calculateLiveMetrics);
        }
    });
}

/**
 * Computes BMI, BP classification, Glucose classification, and Risk Level locally in real time.
 */
function calculateLiveMetrics() {
    const heightCm = parseFloat(document.getElementById('input-height')?.value) || 0;
    const weightKg = parseFloat(document.getElementById('input-weight')?.value) || 0;
    const sbp = parseInt(document.getElementById('input-systolic')?.value) || 0;
    const dbp = parseInt(document.getElementById('input-diastolic')?.value) || 0;
    const glucose = parseFloat(document.getElementById('input-glucose')?.value) || 0;
    const age = parseInt(document.getElementById('input-age')?.value) || 30;

    const diabetes = document.getElementById('select-diabetes')?.value || 'No';
    const hypertension = document.getElementById('select-hypertension')?.value || 'No';
    const smoking = document.getElementById('select-smoking')?.value || 'Never';
    const activity = document.getElementById('select-activity')?.value || 'Moderate';

    // 1. BMI Calculation
    let bmi = 0;
    let bmiCategory = '—';
    let bmiBadgeClass = 'badge-secondary';

    if (heightCm > 0 && weightKg > 0) {
        const heightM = heightCm / 100.0;
        bmi = (weightKg / (heightM * heightM)).toFixed(1);

        if (bmi < 18.5) {
            bmiCategory = 'Underweight';
            bmiBadgeClass = 'badge-underweight';
        } else if (bmi < 25.0) {
            bmiCategory = 'Normal';
            bmiBadgeClass = 'badge-normal';
        } else if (bmi < 30.0) {
            bmiCategory = 'Overweight';
            bmiBadgeClass = 'badge-overweight';
        } else {
            bmiCategory = 'Obese';
            bmiBadgeClass = 'badge-obese';
        }
    }

    const previewBmiEl = document.getElementById('preview-bmi-value');
    const previewBmiCatEl = document.getElementById('preview-bmi-category');
    if (previewBmiEl) previewBmiEl.textContent = bmi > 0 ? bmi : '—';
    if (previewBmiCatEl) {
        previewBmiCatEl.textContent = bmiCategory;
        previewBmiCatEl.className = `badge ${bmiBadgeClass}`;
    }

    // 2. Blood Pressure Classification
    let bpCategory = '—';
    let bpBadgeClass = 'badge-secondary';

    if (sbp > 0 && dbp > 0) {
        if (sbp >= 180 || dbp >= 120) {
            bpCategory = 'Crisis';
            bpBadgeClass = 'badge-danger';
        } else if (sbp >= 140 || dbp >= 90) {
            bpCategory = 'Stage 2';
            bpBadgeClass = 'badge-danger';
        } else if ((sbp >= 130 && sbp <= 139) || (dbp >= 80 && dbp <= 89)) {
            bpCategory = 'Stage 1';
            bpBadgeClass = 'badge-warning';
        } else if (sbp >= 120 && sbp <= 129 && dbp < 80) {
            bpCategory = 'Elevated';
            bpBadgeClass = 'badge-warning';
        } else {
            bpCategory = 'Normal';
            bpBadgeClass = 'badge-normal';
        }
    }

    const previewBpCatEl = document.getElementById('preview-bp-category');
    if (previewBpCatEl) {
        previewBpCatEl.textContent = bpCategory;
        previewBpCatEl.className = `badge ${bpBadgeClass}`;
    }

    // 3. Fasting Glucose Classification
    let glucoseStatus = '—';
    let glucoseBadgeClass = 'badge-secondary';

    if (glucose > 0) {
        if (glucose < 100.0) {
            glucoseStatus = 'Normal';
            glucoseBadgeClass = 'badge-normal';
        } else if (glucose < 126.0) {
            glucoseStatus = 'Prediabetic';
            glucoseBadgeClass = 'badge-warning';
        } else {
            glucoseStatus = 'Diabetic';
            glucoseBadgeClass = 'badge-danger';
        }
    }

    const previewGlucoseStatusEl = document.getElementById('preview-glucose-status');
    if (previewGlucoseStatusEl) {
        previewGlucoseStatusEl.textContent = glucoseStatus;
        previewGlucoseStatusEl.className = `badge ${glucoseBadgeClass}`;
    }

    // 4. Overall Health Risk Tier Score
    let riskScore = 0;
    if (age >= 55) riskScore += 1;
    if (age >= 65) riskScore += 1;
    if (bmiCategory === 'Overweight') riskScore += 1;
    if (bmiCategory === 'Obese') riskScore += 2;
    if (bpCategory === 'Stage 1') riskScore += 1;
    if (bpCategory === 'Stage 2' || bpCategory === 'Crisis') riskScore += 2;
    if (glucoseStatus === 'Diabetic' || diabetes === 'Yes') riskScore += 2;
    else if (glucoseStatus === 'Prediabetic' || diabetes === 'Pre-diabetic') riskScore += 1;
    if (hypertension === 'Yes') riskScore += 1;
    if (smoking === 'Current') riskScore += 2;
    else if (smoking === 'Former') riskScore += 1;
    if (activity === 'Sedentary') riskScore += 1;

    let riskTier = 'Low';
    let riskClass = 'risk-low';

    if (riskScore > 5) {
        riskTier = 'High';
        riskClass = 'risk-high';
    } else if (riskScore > 2) {
        riskTier = 'Moderate';
        riskClass = 'risk-moderate';
    }

    const riskMeter = document.getElementById('preview-risk-meter');
    const riskScoreVal = document.getElementById('preview-risk-value');
    if (riskMeter) {
        riskMeter.className = `risk-meter ${riskClass}`;
    }
    if (riskScoreVal) {
        riskScoreVal.textContent = `${riskTier} Risk`;
    }

    // Live BP cross-validation check
    const bpError = document.getElementById('bp-cross-error');
    if (bpError) {
        if (sbp > 0 && dbp > 0 && dbp >= sbp) {
            bpError.style.display = 'flex';
            bpError.textContent = 'Diastolic BP must be lower than Systolic BP.';
        } else {
            bpError.style.display = 'none';
        }
    }

    // Friendly clinical alignment suggestions
    const diabetesHint = document.getElementById('diabetes-clinical-hint');
    if (diabetesHint) {
        if (glucose >= 126 && diabetes === 'No') {
            diabetesHint.style.display = 'block';
            diabetesHint.textContent = 'Tip: Glucose >= 126 mg/dL indicates diabetic range.';
        } else {
            diabetesHint.style.display = 'none';
        }
    }
}

function setupFormValidation() {
    const form = document.getElementById('health-record-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        const sbp = parseInt(document.getElementById('input-systolic')?.value) || 0;
        const dbp = parseInt(document.getElementById('input-diastolic')?.value) || 0;

        if (sbp > 0 && dbp > 0 && dbp >= sbp) {
            e.preventDefault();
            showToast('Diastolic BP must be lower than Systolic BP.', 'danger');
            document.getElementById('input-diastolic')?.focus();
        }
    });
}
