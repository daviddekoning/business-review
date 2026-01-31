/* Main App JavaScript */

// ===== Modal Management =====
function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function hideModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Close modal on backdrop click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }
});

// ===== Tabs =====
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const tabId = tab.dataset.tab;

        // Update tab buttons
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabId).classList.add('active');

        // Update URL hash
        window.location.hash = tabId;
    });
});

// Handle initial hash
if (window.location.hash) {
    const tabId = window.location.hash.slice(1);
    const tab = document.querySelector(`.tab[data-tab="${tabId}"]`);
    if (tab) tab.click();
}

// ===== Research Items =====
function toggleItemContent(itemId) {
    const content = document.getElementById(`content-${itemId}`);
    if (content.style.display === 'none') {
        content.style.display = 'block';
        initQuoteHighlighter(itemId);
    } else {
        content.style.display = 'none';
    }
}

function showEditResearchModal(itemId) {
    // Find the item data
    const item = window.researchItems.find(i => i.id === itemId);
    if (!item) return;

    // Create modal dynamically or populate existing one
    // For simplicity, we'll use an alert for now
    alert('Edit functionality - Coming soon. For now, delete and re-add.');
}

// ===== Analysis Frameworks =====
function toggleFramework(slug) {
    const content = document.getElementById(`framework-${slug}`);
    const header = content.parentElement.querySelector('.toggle-icon');

    if (content.style.display === 'none') {
        content.style.display = 'block';
        header.style.transform = 'rotate(180deg)';
    } else {
        content.style.display = 'none';
        header.style.transform = 'rotate(0)';
    }
}

// ===== Summary Editor =====
document.querySelectorAll('.editor-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const view = tab.dataset.view;

        document.querySelectorAll('.editor-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        const textarea = document.getElementById('summary-markdown');
        const preview = document.getElementById('summary-preview');

        if (view === 'edit') {
            textarea.style.display = 'block';
            preview.style.display = 'none';
        } else {
            textarea.style.display = 'none';
            preview.style.display = 'block';
            // Simple markdown preview - just show the text for now
            // A proper markdown parser would be better
            preview.innerHTML = simpleMarkdown(textarea.value);
        }
    });
});

function simpleMarkdown(text) {
    // Very basic markdown conversion
    return text
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*)\*/gim, '<em>$1</em>')
        .replace(/^\- (.*$)/gim, '<li>$1</li>')
        .replace(/\n/gim, '<br>');
}

// Utility: Debounce
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Setup autosave
const summaryTextarea = document.getElementById('summary-markdown');
if (summaryTextarea) {
    const statusEl = document.getElementById('summary-save-status');
    const debouncedSave = debounce(() => {
        saveSummary(true);
    }, 1000);

    summaryTextarea.addEventListener('input', () => {
        if (statusEl) {
            statusEl.textContent = 'Saving...';
            statusEl.style.opacity = '1';
        }
        debouncedSave();
    });
}

function saveSummary(isAutosave = false) {
    const textarea = document.getElementById('summary-markdown');
    if (!textarea) return;

    const businessId = textarea.dataset.businessId;
    const statusEl = document.getElementById('summary-save-status');

    fetch(`/business/${businessId}/summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ markdown: textarea.value })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                if (isAutosave && statusEl) {
                    statusEl.textContent = 'Saved';
                    setTimeout(() => {
                        statusEl.style.opacity = '0';
                    }, 2000);
                } else {
                    showNotification('Summary saved!', 'success');
                    if (statusEl) {
                        statusEl.textContent = '';
                    }
                }
            }
        })
        .catch(err => {
            if (isAutosave && statusEl) {
                statusEl.textContent = 'Error saving';
                statusEl.style.color = '#ef476f';
            } else {
                showNotification('Error saving summary', 'error');
            }
            console.error(err);
        });
}

// ===== Notifications =====
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#06d6a0' : type === 'error' ? '#ef476f' : '#4361ee'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 2000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
