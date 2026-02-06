/* Analysis Forms - Handle form submission and data management */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all analysis forms
    document.querySelectorAll('.analysis-form').forEach(form => {
        // Use focusout (bubbles) for inputs/textareas to save on blur
        form.addEventListener('focusout', (e) => {
            if (e.target.matches('input, textarea, select')) {
                handleAutoSave(form);
            }
        });

        // Use change for selects/checkboxes/radios to save immediately
        form.addEventListener('change', (e) => {
            if (e.target.matches('select, input[type="checkbox"], input[type="radio"]')) {
                handleAutoSave(form);
            }
        });

        // Prevent default submit if Enter is pressed
        form.addEventListener('submit', (e) => e.preventDefault());
    });

    // Initialize Sortable for PESTEL
    const pestelContainer = document.getElementById('pestel-container');
    if (pestelContainer) {
        new Sortable(pestelContainer, {
            animation: 150,
            handle: '.drag-handle',
            ghostClass: 'sortable-ghost',
            onEnd: () => {
                // Save when order changes
                const form = pestelContainer.closest('form');
                if (form) handleAutoSave(form);
            }
        });
    }

    // Initialize VRIO Scores
    document.querySelectorAll('tr.vrio-main-row').forEach(row => {
        // Add listeners
        row.querySelectorAll('input[type="range"]').forEach(input => {
            input.addEventListener('input', () => {
                updateVRIOScore(row);
                // Trigger autosave
                const form = row.closest('form');
                if (form) debouncedAutoSave(form);
            });
        });
        // Initial calc
        updateVRIOScore(row);
    });

    // Check for open analysis to restore
    const openAnalysisId = sessionStorage.getItem('openAnalysisId');
    const openTab = sessionStorage.getItem('openTab');

    if (openTab) {
        // Switch to the correct tab first
        const tabBtn = document.querySelector(`.tab[data-tab="${openTab}"]`);
        if (tabBtn) tabBtn.click();
        sessionStorage.removeItem('openTab');
    }

    if (openAnalysisId) {
        const content = document.getElementById(openAnalysisId);
        if (content) {
            content.style.display = 'block';
            const icon = content.parentElement.querySelector('.toggle-icon');
            if (icon) icon.style.transform = 'rotate(180deg)';

            // Scroll to it
            setTimeout(() => {
                content.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }
        sessionStorage.removeItem('openAnalysisId');
    }
});

// Debounce helper
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

const debouncedAutoSave = debounce((form) => handleAutoSave(form), 1000);

function handleAutoSave(form) {
    const businessId = form.dataset.businessId;
    const analysisId = form.dataset.analysisId;
    const slug = form.dataset.slug;

    // Collect form data based on analysis type
    const data = collectFormData(form, slug);

    // Use ID-based endpoint if analysis ID is available, otherwise use legacy slug-based
    let url, method;
    if (analysisId) {
        url = `/business/${businessId}/analysis/${analysisId}`;
        method = 'PUT';
    } else {
        // Legacy: use slug-based endpoint
        url = `/business/${businessId}/analysis/${slug}`;
        method = 'POST';
    }

    // Save to server
    return fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                // Show save status indicator
                const statusId = analysisId ? `status-${analysisId}` : `status-${slug}`;
                const statusIndicator = document.getElementById(statusId);
                if (statusIndicator) {
                    statusIndicator.textContent = 'Saved';
                    statusIndicator.style.opacity = '1';
                    setTimeout(() => {
                        statusIndicator.style.opacity = '0';
                    }, 2000);
                }
            }
            return result;
        })
        .catch(err => {
            console.error('Error saving analysis:', err);
            throw err;
        });
}

function collectFormData(form, slug) {
    switch (slug) {
        case 'pestel':
            return collectPESTELData(form);
        case 'five_forces':
            return collectFiveForcesData(form);
        case 'vrio':
            return collectVRIOData(form);
        case 'wardley':
            return collectWardleyData(form);
        case 'scenario_planning':
            return collectScenarioPlanningData(form);
        default:
            return {};
    }
}

function collectPESTELData(form) {
    const data = {};

    // Get order from DOM
    const factorGroups = form.querySelectorAll('.factor-group');
    data.order = Array.from(factorGroups).map(group => group.dataset.factor);

    // Collect data for each factor
    data.order.forEach(factor => {
        const factorInputs = form.querySelectorAll(`input[name="${factor}_factor[]"]`);
        const impactInputs = form.querySelectorAll(`input[name="${factor}_impact[]"]`);

        data[factor] = [];
        factorInputs.forEach((input, i) => {
            const factorText = input.value.trim();
            const impactText = impactInputs[i].value.trim();

            if (factorText || impactText) {
                data[factor].push({
                    factor: factorText,
                    impact: impactText
                });
            }
        });
    });

    return data;
}

function collectFiveForcesData(form) {
    const forces = ['new_entrants', 'supplier_power', 'buyer_power', 'substitutes', 'rivalry'];
    const data = {};

    forces.forEach(force => {
        const descriptionInput = form.querySelector(`textarea[name="${force}_description"]`);
        const impactInput = form.querySelector(`textarea[name="${force}_impact"]`);
        const significanceInput = form.querySelector(`input[name="${force}_significance"]:checked`);

        data[force] = {
            description: descriptionInput ? descriptionInput.value.trim() : '',
            impact: impactInput ? impactInput.value.trim() : '',
            significance: significanceInput ? significanceInput.value : 'medium'
        };
    });

    return data;
}

// VRIO Data Collection
function collectVRIOData(form) {
    const mainRows = form.querySelectorAll('tr.vrio-main-row');
    const resources = [];

    mainRows.forEach((row, i) => {
        const nameInput = row.querySelector(`input[name="resource_${i}_name"]`);
        if (!nameInput || !nameInput.value.trim()) return;

        // Description is in the next row
        const descRow = row.nextElementSibling;
        const descInput = descRow.querySelector(`textarea[name="resource_${i}_description"]`);

        resources.push({
            name: nameInput.value.trim(),
            description: descInput ? descInput.value.trim() : '',
            valuable: parseInt(row.querySelector(`input[name="resource_${i}_valuable"]`)?.value || '3'),
            rare: parseInt(row.querySelector(`input[name="resource_${i}_rare"]`)?.value || '3'),
            costly_to_imitate: parseInt(row.querySelector(`input[name="resource_${i}_costly_to_imitate"]`)?.value || '3'),
            organized: parseInt(row.querySelector(`input[name="resource_${i}_organized"]`)?.value || '3')
        });
    });

    return { resources };
}

function collectWardleyData(form) {
    const rows = form.querySelectorAll('tbody tr');
    const components = [];

    rows.forEach((row, i) => {
        const nameInput = row.querySelector(`input[name="component_${i}_name"]`);
        if (!nameInput || !nameInput.value.trim()) return;

        components.push({
            name: nameInput.value.trim(),
            evolution: row.querySelector(`select[name="component_${i}_evolution"]`)?.value || 'genesis',
            visibility: row.querySelector(`select[name="component_${i}_visibility"]`)?.value || 'hidden',
            notes: row.querySelector(`input[name="component_${i}_notes"]`)?.value.trim() || ''
        });
    });

    return { components };
}

// ===== Dynamic Form Helpers =====

// ===== Analysis CRUD =====

// Toggle framework visibility
function toggleFramework(id) {
    const content = document.getElementById(`framework-${id}`);
    const header = content?.previousElementSibling;
    if (content) {
        const isVisible = content.style.display !== 'none';
        content.style.display = isVisible ? 'none' : 'block';
        if (header) {
            const icon = header.querySelector('.toggle-icon');
            if (icon) icon.textContent = isVisible ? '▼' : '▲';
        }
    }
}

// Update default name when type is selected
function updateDefaultName() {
    const typeSelect = document.getElementById('analysis-type');
    const nameInput = document.getElementById('analysis-name');
    const selectedOption = typeSelect.options[typeSelect.selectedIndex];

    if (selectedOption && selectedOption.value) {
        nameInput.value = selectedOption.dataset.name || selectedOption.text;
    } else {
        nameInput.value = '';
    }
}

// Create a new analysis
function createNewAnalysis() {
    const form = document.getElementById('add-analysis-form');
    const businessId = form.dataset.businessId;
    const typeSelect = document.getElementById('analysis-type');
    const nameInput = document.getElementById('analysis-name');

    const templateType = typeSelect.value;
    const name = nameInput.value.trim();

    if (!templateType) {
        alert('Please select an analysis type');
        return;
    }

    if (!name) {
        alert('Please enter a name for the analysis');
        return;
    }

    fetch(`/business/${businessId}/analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template_type: templateType, name: name })
    })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                // Reload the page to show the new analysis
                location.reload();
            } else {
                alert('Error creating analysis: ' + (result.error || 'Unknown error'));
            }
        })
        .catch(err => {
            console.error('Error creating analysis:', err);
            alert('Error creating analysis');
        });
}

// Update analysis name
function updateAnalysisName(analysisId, newName) {
    const framework = document.querySelector(`[data-analysis-id="${analysisId}"]`);
    const businessId = framework?.closest('.analysis-frameworks')?.dataset.businessId;

    if (!businessId || !newName.trim()) return;

    fetch(`/business/${businessId}/analysis/${analysisId}/name`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName.trim() })
    })
        .then(res => res.json())
        .then(result => {
            if (!result.success) {
                console.error('Error updating name:', result.error);
            }
        })
        .catch(err => console.error('Error updating name:', err));
}

// Delete an analysis
function deleteAnalysis(analysisId, name) {
    if (!confirm(`Delete analysis "${name}"? This cannot be undone.`)) {
        return;
    }

    const framework = document.querySelector(`[data-analysis-id="${analysisId}"]`);
    const businessId = framework?.closest('.analysis-frameworks')?.dataset.businessId;

    if (!businessId) return;

    fetch(`/business/${businessId}/analysis/${analysisId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                // Remove from DOM
                framework.remove();
                // Show empty state if no analyses left
                const container = document.querySelector('.analysis-frameworks');
                if (container && container.querySelectorAll('.analysis-framework').length === 0) {
                    container.innerHTML = '<div class="empty-state" id="analysis-empty-state"><p>No analyses yet. Click "+ Add Analysis" to create your first analysis.</p></div>';
                }
            } else {
                alert('Error deleting analysis: ' + (result.error || 'Unknown error'));
            }
        })
        .catch(err => {
            console.error('Error deleting analysis:', err);
            alert('Error deleting analysis');
        });
}

// PESTEL - Add factor item
function addItem(factor) {
    const container = document.querySelector(`[data-factor="${factor}"] .factor-items`);
    const index = container.children.length;

    const div = document.createElement('div');
    div.className = 'factor-item';
    div.dataset.index = index;
    div.innerHTML = `
        <div class="factor-inputs">
            <input type="text" name="${factor}_factor[]" placeholder="Factor" class="factor-input">
            <input type="text" name="${factor}_impact[]" placeholder="Impact on Business" class="impact-input">
        </div>
        <button type="button" class="remove-item" onclick="removeItem(this)">×</button>
    `;
    container.appendChild(div);
    div.querySelector('.factor-input').focus();

    // Save state (empty item)
    const form = container.closest('form');
    handleAutoSave(form);
}

function removeItem(button) {
    const form = button.closest('form');
    button.parentElement.remove();
    handleAutoSave(form);
}



// VRIO - Add row
function addVRIORow() {
    const tbody = document.querySelector('.vrio-table tbody');
    // We count pairs. Logic: find max index or just count pairs? 
    // Safest is to just count .vrio-main-row
    const index = tbody.querySelectorAll('.vrio-main-row').length;

    // Main Row
    const trMain = document.createElement('tr');
    trMain.dataset.index = index;
    trMain.className = 'vrio-main-row';
    trMain.innerHTML = `
        <td>
            <input type="text" name="resource_${index}_name" placeholder="Resource name" class="resource-name">
        </td>
        <td>
            <div class="slider-container">
                <input type="range" name="resource_${index}_valuable" min="1" max="5" step="1" value="3" oninput="this.nextElementSibling.value = this.value">
                <output>3</output>
            </div>
        </td>
        <td>
            <div class="slider-container">
                <input type="range" name="resource_${index}_rare" min="1" max="5" step="1" value="3" oninput="this.nextElementSibling.value = this.value">
                <output>3</output>
            </div>
        </td>
        <td>
            <div class="slider-container">
                <input type="range" name="resource_${index}_costly_to_imitate" min="1" max="5" step="1" value="3" oninput="this.nextElementSibling.value = this.value">
                <output>3</output>
            </div>
        </td>
        <td>
            <div class="slider-container">
                <input type="range" name="resource_${index}_organized" min="1" max="5" step="1" value="3" oninput="this.nextElementSibling.value = this.value">
                <output>3</output>
            </div>
        </td>
        <td class="score-cell">
            <div class="score-value">-</div>
            <div class="score-implication"></div>
        </td>
        <td><button type="button" class="remove-row" onclick="removeVRIORow(this)">×</button></td>
    `;

    // Description Row
    const trDesc = document.createElement('tr');
    trDesc.dataset.index = index;
    trDesc.className = 'vrio-desc-row';
    trDesc.innerHTML = `
        <td colspan="7">
            <textarea name="resource_${index}_description" placeholder="Description / Notes" rows="2" class="resource-desc"></textarea>
        </td>
    `;

    tbody.appendChild(trMain);
    tbody.appendChild(trDesc);
    trMain.querySelector('input').focus();

    // Add listeners for score updates
    trMain.querySelectorAll('input[type="range"]').forEach(input => {
        input.addEventListener('input', () => {
            updateVRIOScore(trMain);
            const form = tbody.closest('form');
            if (form) debouncedAutoSave(form);
        });
    });

    // Initial calculation
    updateVRIOScore(trMain);

    // Save
    const form = tbody.closest('form');
    handleAutoSave(form);
}

function removeVRIORow(button) {
    const form = button.closest('form');
    const row = button.closest('tr'); // This is the main row
    const nextRow = row.nextElementSibling; // This should be the description row

    row.remove();
    if (nextRow && nextRow.classList.contains('vrio-desc-row')) {
        nextRow.remove();
    }

    handleAutoSave(form);
}

function updateVRIOScore(row) {
    const index = row.dataset.index;

    const v = parseInt(row.querySelector(`input[name="resource_${index}_valuable"]`).value) || 1;
    const r = parseInt(row.querySelector(`input[name="resource_${index}_rare"]`).value) || 1;
    const i = parseInt(row.querySelector(`input[name="resource_${index}_costly_to_imitate"]`).value) || 1;
    const o = parseInt(row.querySelector(`input[name="resource_${index}_organized"]`).value) || 1;

    // Formula: (V * 0.35) + (R * 0.35) + (I * 0.20) + (O * 0.10)
    const score = (v * 0.35) + (r * 0.35) + (i * 0.20) + (o * 0.10);

    let implication;
    if (score >= 4.5) implication = 'Sustained Advantage';
    else if (score >= 3.5) implication = 'Temporary Advantage';
    else if (score >= 2.5) implication = 'Competitive Parity';
    else implication = 'Competitive Disadvantage';

    const scoreCell = row.querySelector('.score-cell');
    scoreCell.querySelector('.score-value').textContent = score.toFixed(1);
    scoreCell.querySelector('.score-implication').textContent = implication;
}

// Wardley - Add row
function addWardleyRow() {
    const tbody = document.querySelector('.wardley-table tbody');
    const index = tbody.children.length;

    const tr = document.createElement('tr');
    tr.dataset.index = index;
    tr.innerHTML = `
        <td><input type="text" name="component_${index}_name" placeholder="Component name"></td>
        <td>
            <select name="component_${index}_evolution">
                <option value="genesis">Genesis</option>
                <option value="custom">Custom Built</option>
                <option value="product">Product/Rental</option>
                <option value="commodity">Commodity/Utility</option>
            </select>
        </td>
        <td>
            <select name="component_${index}_visibility">
                <option value="visible">Visible</option>
                <option value="aware">Aware</option>
                <option value="hidden">Hidden</option>
            </select>
        </td>
        <td><input type="text" name="component_${index}_notes" placeholder="Notes"></td>
        <td><button type="button" class="remove-row" onclick="removeWardleyRow(this)">×</button></td>
    `;
    tbody.appendChild(tr);
    tr.querySelector('input').focus();

    const form = tbody.closest('form');
    handleAutoSave(form);
}

function removeWardleyRow(button) {
    const form = button.closest('form');
    button.closest('tr').remove();
    handleAutoSave(form);
}


// ===== Scenario Planning Data Collection =====

function collectScenarioPlanningData(form) {
    // Get data from hidden input
    const dataInput = form.querySelector('.scenario-data');
    let data = { strategies: [], futures: [], cells: {} };

    if (dataInput) {
        try {
            data = JSON.parse(dataInput.value);
        } catch (e) {
            console.error('Error parsing scenario data:', e);
        }
    }

    // Update strategy names from visible inputs
    form.querySelectorAll('.strategy-header').forEach(header => {
        const strategyId = header.dataset.id;
        const nameInput = header.querySelector('.strategy-name');
        if (strategyId && nameInput) {
            const strategy = data.strategies.find(s => s.id === strategyId);
            if (strategy) {
                strategy.name = nameInput.value;
            }
        }
    });

    // Update future names from visible inputs
    form.querySelectorAll('tr[data-future-id]').forEach(row => {
        const futureId = row.dataset.futureId;
        const nameInput = row.querySelector('.future-name');
        if (futureId && nameInput) {
            const future = data.futures.find(f => f.id === futureId);
            if (future) {
                future.name = nameInput.value;
            }
        }
    });

    return data;
}

// Helper to get or create scenario data for a form (also syncs names from inputs)
function getScenarioDataForForm(form) {
    return collectScenarioPlanningData(form);
}

function saveScenarioDataToForm(form, data) {
    const dataInput = form.querySelector('.scenario-data');
    if (dataInput) {
        dataInput.value = JSON.stringify(data);
    }
}

// Generate unique IDs
function generateId() {
    return 'id_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Helper to save state before reload
function saveAnalysisState(form) {
    const content = form.closest('.framework-content');
    if (content) {
        sessionStorage.setItem('openAnalysisId', content.id);
        sessionStorage.setItem('openTab', 'strategic-analysis');
    }
}

// Add strategy within a form context
function addStrategy(button) {
    const form = button.closest('form');
    const data = getScenarioDataForForm(form);

    const newStrategy = {
        id: generateId(),
        name: '',
        description: ''
    };

    data.strategies.push(newStrategy);
    saveScenarioDataToForm(form, data);
    saveAnalysisState(form);

    // Wait for save to complete before reloading
    handleAutoSave(form).then(() => {
        location.reload();
    }).catch(() => {
        location.reload();
    });
}

// Add future within a form context
function addFuture(button) {
    const form = button.closest('form');
    const data = getScenarioDataForForm(form);

    const newFuture = {
        id: generateId(),
        name: '',
        description: ''
    };

    data.futures.push(newFuture);
    saveScenarioDataToForm(form, data);
    saveAnalysisState(form);

    // Wait for save to complete before reloading
    handleAutoSave(form).then(() => {
        location.reload();
    }).catch(() => {
        location.reload();
    });
}

// Remove strategy from form
function removeStrategyFromForm(button, strategyId) {
    if (!confirm('Remove this strategy? All related analysis will be deleted.')) {
        return;
    }

    const form = button.closest('form');
    const data = getScenarioDataForForm(form);

    data.strategies = data.strategies.filter(s => s.id !== strategyId);

    // Remove related cells
    const keysToRemove = Object.keys(data.cells).filter(k => k.startsWith(strategyId + '_'));
    keysToRemove.forEach(k => delete data.cells[k]);

    saveScenarioDataToForm(form, data);
    saveAnalysisState(form);
    handleAutoSave(form).then(() => {
        location.reload();
    }).catch(() => {
        location.reload();
    });
}

// Remove future from form
function removeFutureFromForm(button, futureId) {
    if (!confirm('Remove this future? All related analysis will be deleted.')) {
        return;
    }

    const form = button.closest('form');
    const data = getScenarioDataForForm(form);

    data.futures = data.futures.filter(f => f.id !== futureId);

    // Remove related cells
    const keysToRemove = Object.keys(data.cells).filter(k => k.endsWith('_' + futureId));
    keysToRemove.forEach(k => delete data.cells[k]);

    saveScenarioDataToForm(form, data);
    saveAnalysisState(form);
    handleAutoSave(form).then(() => {
        location.reload();
    }).catch(() => {
        location.reload();
    });
}

// Select cell in form context
function selectScenarioCellInForm(cell, strategyId, futureId) {
    const form = cell.closest('form');
    const container = form.querySelector('.scenario-planning-analysis');
    const panel = container.querySelector('.scenario-detail-panel');
    const data = getScenarioDataForForm(form);

    // Store current selection on the container
    container.dataset.selectedStrategy = strategyId;
    container.dataset.selectedFuture = futureId;

    // Highlight selected cell
    container.querySelectorAll('.scenario-cell').forEach(c => c.classList.remove('selected'));
    cell.classList.add('selected');

    // Get data
    const strategy = data.strategies.find(s => s.id === strategyId);
    const future = data.futures.find(f => f.id === futureId);
    const cellKey = `${strategyId}_${futureId}`;
    const cellData = data.cells[cellKey] || { thoughts: '', summary: '', rag: '' };

    // Update labels
    const strategyLabel = panel.querySelector('.strategy-description-label');
    const futureLabel = panel.querySelector('.future-description-label');
    if (strategyLabel) strategyLabel.textContent = 'Strategy: ' + (strategy?.name || 'Unnamed');
    if (futureLabel) futureLabel.textContent = 'Future: ' + (future?.name || 'Unnamed');

    // Populate form
    panel.querySelector('.strategy-description').value = strategy?.description || '';
    panel.querySelector('.future-description').value = future?.description || '';
    panel.querySelector('.cell-thoughts').value = cellData.thoughts || '';
    panel.querySelector('.cell-summary-input').value = cellData.summary || '';

    // Update RAG selector to show current value
    const currentRag = cellData.rag || '';
    panel.querySelectorAll('.rag-btn').forEach(btn => {
        btn.classList.toggle('selected', btn.dataset.rag === currentRag);
    });

    // Show panel
    panel.style.display = 'block';
    panel.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Set up event listeners for auto-save
    setupScenarioPanelListeners(form, container, panel);
}

// Set RAG rating for current cell
function setScenarioRag(button, ragValue) {
    const panel = button.closest('.scenario-detail-panel');
    const container = panel.closest('.scenario-planning-analysis');
    const form = container.closest('form');
    const data = getScenarioDataForForm(form);

    const strategyId = container.dataset.selectedStrategy;
    const futureId = container.dataset.selectedFuture;
    const cellKey = `${strategyId}_${futureId}`;

    // Update data
    if (!data.cells[cellKey]) data.cells[cellKey] = {};
    data.cells[cellKey].rag = ragValue;

    // Update button selection
    panel.querySelectorAll('.rag-btn').forEach(btn => {
        btn.classList.toggle('selected', btn.dataset.rag === ragValue);
    });

    // Update cell color
    const cell = container.querySelector(`.scenario-cell[data-strategy-id="${strategyId}"][data-future-id="${futureId}"]`);
    if (cell) {
        cell.classList.remove('rag-red', 'rag-amber', 'rag-green');
        if (ragValue) {
            cell.classList.add(`rag-${ragValue}`);
        }
    }

    // Save
    saveScenarioDataToForm(form, data);
    handleAutoSave(form);
}


function setupScenarioPanelListeners(form, container, panel) {
    const strategyDesc = panel.querySelector('.strategy-description');
    const futureDesc = panel.querySelector('.future-description');
    const cellThoughts = panel.querySelector('.cell-thoughts');
    const cellSummary = panel.querySelector('.cell-summary-input');

    const saveChanges = debounce(() => {
        const data = getScenarioDataForForm(form);
        const strategyId = container.dataset.selectedStrategy;
        const futureId = container.dataset.selectedFuture;

        const strategy = data.strategies.find(s => s.id === strategyId);
        const future = data.futures.find(f => f.id === futureId);
        const cellKey = `${strategyId}_${futureId}`;

        if (strategy) strategy.description = strategyDesc.value;
        if (future) future.description = futureDesc.value;

        if (!data.cells[cellKey]) data.cells[cellKey] = {};
        data.cells[cellKey].thoughts = cellThoughts.value;
        data.cells[cellKey].summary = cellSummary.value;

        // Update cell display
        const cell = container.querySelector(`.scenario-cell[data-strategy-id="${strategyId}"][data-future-id="${futureId}"]`);
        if (cell) {
            const summarySpan = cell.querySelector('.cell-summary');
            if (summarySpan) summarySpan.textContent = cellSummary.value || '—';
            cell.classList.toggle('has-summary', !!cellSummary.value);
        }

        saveScenarioDataToForm(form, data);
        handleAutoSave(form);
    }, 500);

    // Remove old listeners and add new ones
    [strategyDesc, futureDesc, cellThoughts, cellSummary].forEach(el => {
        el.oninput = saveChanges;
    });
}

function closeScenarioDetailInForm(button) {
    const panel = button.closest('.scenario-detail-panel');
    const container = panel.closest('.scenario-planning-analysis');

    panel.style.display = 'none';
    container.querySelectorAll('.scenario-cell').forEach(c => c.classList.remove('selected'));
    delete container.dataset.selectedStrategy;
    delete container.dataset.selectedFuture;
}

// ===== Legacy Scenario Planning State (kept for backward compatibility with old data) =====
// These variables are used by legacy code only
let selectedStrategyId = null;
let selectedFutureId = null;
