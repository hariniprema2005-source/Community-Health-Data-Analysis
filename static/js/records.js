/**
 * Community Health Data Collection & Analysis
 * Records Management: Search, Filter, Sort, Pagination, View, and Delete
 */

let currentPage = 1;
let currentPerPage = 15;
let currentSortBy = 'id';
let currentSortOrder = 'desc';
let recordToDeleteId = null;

document.addEventListener('DOMContentLoaded', () => {
    initRecordsTable();
    setupEventListeners();
});

function setupEventListeners() {
    // Search input with debounce
    const searchInput = document.getElementById('record-search');
    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                currentPage = 1;
                fetchRecords();
            }, 300);
        });
    }

    // Filter selects
    const filterSelects = [
        'filter-location', 'filter-gender', 'filter-diabetes',
        'filter-hypertension', 'filter-bmi', 'filter-risk'
    ];
    filterSelects.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', () => {
                currentPage = 1;
                fetchRecords();
            });
        }
    });

    // Reset filters button
    const resetBtn = document.getElementById('btn-reset-filters');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetAllFilters);
    }

    // Export CSV with current filters
    const exportCsvBtn = document.getElementById('btn-export-filtered-csv');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', exportFilteredCsv);
    }

    // Sortable table headers
    document.querySelectorAll('.data-table th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-sort');
            if (currentSortBy === col) {
                currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortBy = col;
                currentSortOrder = 'asc';
            }
            updateSortIcons();
            fetchRecords();
        });
    });

    // Page size change
    const pageSizeSelect = document.getElementById('per-page-select');
    if (pageSizeSelect) {
        pageSizeSelect.addEventListener('change', (e) => {
            currentPerPage = parseInt(e.target.value);
            currentPage = 1;
            fetchRecords();
        });
    }

    // Delete confirmation modal confirm button
    const confirmDeleteBtn = document.getElementById('btn-confirm-delete');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', executeDeleteRecord);
    }
}

function updateSortIcons() {
    document.querySelectorAll('.data-table th.sortable').forEach(th => {
        const icon = th.querySelector('i');
        const col = th.getAttribute('data-sort');
        if (col === currentSortBy) {
            icon.className = currentSortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
            th.style.color = 'var(--primary)';
        } else {
            icon.className = 'fas fa-sort';
            th.style.color = '';
        }
    });
}

function initRecordsTable() {
    fetchRecords();
}

/**
 * Fetches records from API with active search, filter, and pagination states.
 */
async function fetchRecords() {
    const tableBody = document.getElementById('records-table-body');
    const tableInfo = document.getElementById('records-table-info');
    if (!tableBody) return;

    tableBody.innerHTML = `
        <tr>
            <td colspan="10" style="text-align:center; padding: 2.5rem; color: var(--text-muted);">
                <i class="fas fa-spinner fa-spin" style="font-size: 1.5rem; color: var(--primary);"></i>
                <p style="margin-top: 0.5rem;">Loading community records...</p>
            </td>
        </tr>
    `;

    const search = document.getElementById('record-search')?.value.trim() || '';
    const location = document.getElementById('filter-location')?.value || '';
    const gender = document.getElementById('filter-gender')?.value || '';
    const diabetes = document.getElementById('filter-diabetes')?.value || '';
    const hypertension = document.getElementById('filter-hypertension')?.value || '';
    const bmi_cat = document.getElementById('filter-bmi')?.value || '';
    const risk = document.getElementById('filter-risk')?.value || '';

    const params = new URLSearchParams({
        search, location, gender, diabetes, hypertension,
        bmi_cat, risk, sort_by: currentSortBy, sort_order: currentSortOrder,
        page: currentPage, per_page: currentPerPage
    });

    try {
        const response = await fetch(`/api/records?${params.toString()}`);
        const data = await response.json();

        renderTableRows(data.records);
        renderPagination(data.total, data.page, data.total_pages);

        if (tableInfo) {
            const start = data.total === 0 ? 0 : (data.page - 1) * data.per_page + 1;
            const end = Math.min(data.page * data.per_page, data.total);
            tableInfo.textContent = `Showing ${start} to ${end} of ${data.total} records`;
        }
    } catch (err) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="10" style="text-align:center; padding: 2rem; color: var(--status-danger);">
                    <i class="fas fa-exclamation-triangle"></i> Error fetching records. Please refresh the page.
                </td>
            </tr>
        `;
    }
}

function renderTableRows(records) {
    const tableBody = document.getElementById('records-table-body');
    if (!tableBody) return;

    if (!records || records.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="10">
                    <div class="empty-state">
                        <i class="fas fa-notes-medical empty-state-icon"></i>
                        <h3>No Health Records Found</h3>
                        <p>No records matched your search filters. Try clearing the filter options or adding a new record.</p>
                        <button class="btn btn-outline btn-sm" onclick="resetAllFilters()">
                            <i class="fas fa-undo"></i> Reset Filters
                        </button>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = records.map(r => {
        // BMI category badge class
        let bmiBadgeClass = 'badge-normal';
        if (r.bmi_category === 'Underweight') bmiBadgeClass = 'badge-underweight';
        if (r.bmi_category === 'Overweight') bmiBadgeClass = 'badge-overweight';
        if (r.bmi_category === 'Obese') bmiBadgeClass = 'badge-obese';

        // BP category badge class
        let bpBadgeClass = 'badge-normal';
        if (r.bp_category === 'Elevated') bpBadgeClass = 'badge-elevated';
        if (r.bp_category.includes('Hypertension')) bpBadgeClass = 'badge-danger';
        if (r.bp_category.includes('Crisis')) bpBadgeClass = 'badge-danger';

        // Risk badge
        let riskBadge = 'badge-low';
        if (r.risk_score === 'Moderate') riskBadge = 'badge-moderate';
        if (r.risk_score === 'High') riskBadge = 'badge-high';

        return `
            <tr>
                <td><strong>${r.record_code}</strong></td>
                <td>${r.age} yrs</td>
                <td>${r.gender}</td>
                <td><i class="fas fa-map-marker-alt" style="color:var(--primary); font-size:0.8rem; margin-right:4px;"></i>${r.location}</td>
                <td>
                    ${r.bmi} <span class="badge ${bmiBadgeClass}" style="margin-left: 4px;">${r.bmi_category}</span>
                </td>
                <td>
                    ${r.systolic_bp}/${r.diastolic_bp} <span class="badge ${bpBadgeClass}">${r.bp_category}</span>
                </td>
                <td>
                    ${r.blood_glucose} <span style="font-size:0.75rem; color:var(--text-muted);">mg/dL</span>
                </td>
                <td>
                    <span class="badge ${r.diabetes === 'Yes' ? 'badge-danger' : r.diabetes === 'Pre-diabetic' ? 'badge-warning' : 'badge-normal'}">
                        ${r.diabetes}
                    </span>
                </td>
                <td>
                    <span class="badge ${r.hypertension === 'Yes' ? 'badge-danger' : 'badge-normal'}">
                        ${r.hypertension}
                    </span>
                </td>
                <td>
                    <span class="badge ${riskBadge}">${r.risk_score}</span>
                </td>
                <td>
                    <div class="table-actions">
                        <button class="table-btn" title="View Details" onclick="viewRecordDetails(${r.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <a href="/edit-record/${r.id}" class="table-btn" title="Edit Record">
                            <i class="fas fa-edit"></i>
                        </a>
                        <button class="table-btn delete-btn" title="Delete Record" onclick="promptDeleteRecord(${r.id}, '${r.record_code}')">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function renderPagination(total, page, totalPages) {
    const nav = document.getElementById('pagination-nav');
    if (!nav) return;

    if (totalPages <= 1) {
        nav.innerHTML = '';
        return;
    }

    let html = `
        <button class="page-btn" ${page <= 1 ? 'disabled' : ''} onclick="changePage(${page - 1})">
            <i class="fas fa-chevron-left"></i>
        </button>
    `;

    for (let p = 1; p <= totalPages; p++) {
        // Show smart range of page buttons
        if (p === 1 || p === totalPages || (p >= page - 1 && p <= page + 1)) {
            html += `
                <button class="page-btn ${p === page ? 'active' : ''}" onclick="changePage(${p})">
                    ${p}
                </button>
            `;
        } else if (p === page - 2 || p === page + 2) {
            html += `<span style="padding: 0 4px; color: var(--text-muted);">...</span>`;
        }
    }

    html += `
        <button class="page-btn" ${page >= totalPages ? 'disabled' : ''} onclick="changePage(${page + 1})">
            <i class="fas fa-chevron-right"></i>
        </button>
    `;

    nav.innerHTML = html;
}

function changePage(newPage) {
    currentPage = newPage;
    fetchRecords();
}

function resetAllFilters() {
    const searchInput = document.getElementById('record-search');
    if (searchInput) searchInput.value = '';

    const filterSelects = [
        'filter-location', 'filter-gender', 'filter-diabetes',
        'filter-hypertension', 'filter-bmi', 'filter-risk'
    ];
    filterSelects.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });

    currentPage = 1;
    fetchRecords();
}

function exportFilteredCsv() {
    const location = document.getElementById('filter-location')?.value || '';
    const gender = document.getElementById('filter-gender')?.value || '';
    const diabetes = document.getElementById('filter-diabetes')?.value || '';
    const hypertension = document.getElementById('filter-hypertension')?.value || '';

    const params = new URLSearchParams({ location, gender, diabetes, hypertension });
    window.location.href = `/export/csv?${params.toString()}`;
}

/**
 * View Record Modal
 */
async function viewRecordDetails(recordId) {
    try {
        const res = await fetch(`/api/records/${recordId}`);
        const data = await res.json();
        if (!data.success) {
            showToast('Record not found', 'danger');
            return;
        }

        const r = data.record;
        const modalBody = document.getElementById('view-modal-content');
        if (!modalBody) return;

        modalBody.innerHTML = `
            <div style="margin-bottom: 1.25rem; display: flex; align-items:center; justify-content: space-between;">
                <div>
                    <h2 style="font-size: 1.4rem; font-weight: 800; color: var(--text-main);">${r.record_code}</h2>
                    <span style="font-size: 0.82rem; color: var(--text-muted);"><i class="fas fa-calendar-alt"></i> Screened: ${r.created_at}</span>
                </div>
                <div>
                    <span class="badge ${r.risk_score === 'High' ? 'badge-danger' : r.risk_score === 'Moderate' ? 'badge-warning' : 'badge-normal'}" style="font-size: 0.85rem; padding: 0.35rem 0.85rem;">
                        <i class="fas fa-shield-alt"></i> ${r.risk_score} Risk Tier
                    </span>
                </div>
            </div>

            <div class="patient-profile-grid">
                <div class="profile-field">
                    <div class="profile-field-label">Age & Gender</div>
                    <div class="profile-field-val">${r.age} Years (${r.gender})</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Community Location</div>
                    <div class="profile-field-val"><i class="fas fa-map-marker-alt" style="color:var(--primary);"></i> ${r.location}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Height & Weight</div>
                    <div class="profile-field-val">${r.height_cm} cm / ${r.weight_kg} kg</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Body Mass Index (BMI)</div>
                    <div class="profile-field-val">${r.bmi} <span class="badge badge-secondary">${r.bmi_category}</span></div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Blood Pressure</div>
                    <div class="profile-field-val">${r.systolic_bp} / ${r.diastolic_bp} mmHg <br><small style="color:var(--primary); font-weight:500;">${r.bp_category}</small></div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Fasting Blood Glucose</div>
                    <div class="profile-field-val">${r.blood_glucose} mg/dL <br><small style="color:var(--text-muted);">${r.glucose_status}</small></div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Diabetes Status</div>
                    <div class="profile-field-val">${r.diabetes}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Hypertension Status</div>
                    <div class="profile-field-val">${r.hypertension}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Smoking Status</div>
                    <div class="profile-field-val">${r.smoking_status}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Physical Activity</div>
                    <div class="profile-field-val">${r.physical_activity}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Alcohol Intake</div>
                    <div class="profile-field-val">${r.alcohol_intake}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Healthcare Access</div>
                    <div class="profile-field-val">${r.healthcare_access}</div>
                </div>
            </div>

            <div class="profile-field" style="margin-top: 1rem;">
                <div class="profile-field-label">Clinical / Field Notes</div>
                <div class="profile-field-val" style="font-weight: 400; font-size: 0.9rem; margin-top: 0.35rem;">
                    ${r.notes || 'No specific field notes recorded for this individual.'}
                </div>
            </div>
        `;

        openModal('view-record-modal');
    } catch (err) {
        showToast('Error loading record details', 'danger');
    }
}

/**
 * Delete Modal confirmation
 */
function promptDeleteRecord(recordId, recordCode) {
    recordToDeleteId = recordId;
    const msgEl = document.getElementById('delete-modal-msg');
    if (msgEl) {
        msgEl.innerHTML = `Are you sure you want to permanently delete record <strong>${recordCode}</strong>? This action cannot be undone.`;
    }
    openModal('delete-confirm-modal');
}

async function executeDeleteRecord() {
    if (!recordToDeleteId) return;

    try {
        const res = await fetch(`/api/records/${recordToDeleteId}`, {
            method: 'DELETE'
        });
        const data = await res.json();

        closeModal('delete-confirm-modal');

        if (data.success) {
            showToast(data.message, 'success');
            fetchRecords();
        } else {
            showToast(data.error || 'Failed to delete record', 'danger');
        }
    } catch (err) {
        showToast('Error deleting record: ' + err.message, 'danger');
    } finally {
        recordToDeleteId = null;
    }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
}
