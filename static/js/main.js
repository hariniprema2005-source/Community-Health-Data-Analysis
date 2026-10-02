/**
 * Community Health Data Collection & Analysis
 * Global Application JavaScript Utilities
 */

// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.sidebar-toggle-btn');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('mobile-open');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 992 && !sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
                sidebar.classList.remove('mobile-open');
            }
        });
    }

    // Auto-dismiss Flash Alerts after 5 seconds
    const flashAlerts = document.querySelectorAll('.flash-alert');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });
});

/**
 * Displays a non-blocking toast notification.
 * @param {string} message - Notification text
 * @param {string} type - 'success', 'danger', 'warning', 'info'
 */
function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'check-circle';
    if (type === 'danger') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    if (type === 'info') icon = 'info-circle';

    toast.innerHTML = `
        <i class="fas fa-${icon}" style="font-size: 1.1rem; color: var(--${type === 'success' ? 'status-normal' : type === 'danger' ? 'status-danger' : 'status-elevated'});"></i>
        <div class="toast-message">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(30px)';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

/**
 * Resets the community database with fresh realistic sample data.
 */
async function resetSampleData() {
    if (!confirm("Are you sure you want to reset the database to sample records? Any custom entered records will be replaced.")) {
        return;
    }

    try {
        const response = await fetch('/api/reset-sample-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();

        if (result.success) {
            showToast(result.message, 'success');
            setTimeout(() => window.location.reload(), 900);
        } else {
            showToast("Failed to reset dataset: " + (result.error || "Unknown error"), 'danger');
        }
    } catch (err) {
        showToast("Error resetting dataset: " + err.message, 'danger');
    }
}
