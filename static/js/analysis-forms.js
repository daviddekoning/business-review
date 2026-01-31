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
    const slug = form.dataset.slug;

    // Collect form data based on analysis type
    const data = collectFormData(form, slug);

    // Save to server
    fetch(`/business/${businessId}/analysis/${slug}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                // Optional: Show a subtle indicator instead of a full notification to avoid spamming
                const statusIndicator = document.getElementById(`status-${slug}`);
                if (statusIndicator) {
                    statusIndicator.textContent = 'Saved';
                    statusIndicator.style.opacity = '1';
                    setTimeout(() => {
                        statusIndicator.style.opacity = '0';
                    }, 2000);
                }
            }
        })
        .catch(err => {
            console.error('Error saving analysis:', err);
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


// ===== Scenario Planning =====

// State for scenario planning
let selectedStrategyId = null;
let selectedFutureId = null;

// Generate unique IDs
function generateId() {
    return 'id_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Get business ID from scenario planning container
function getScenarioBusinessId() {
    const container = document.querySelector('.scenario-planning');
    return container ? container.dataset.businessId : null;
}

// Add a new strategy
function addStrategy() {
    if (!window.scenarioPlanning) {
        window.scenarioPlanning = { strategies: [], futures: [], cells: {} };
    }

    const newStrategy = {
        id: generateId(),
        name: '',
        description: ''
    };

    window.scenarioPlanning.strategies.push(newStrategy);
    saveScenarioPlanning().then(() => {
        // Reload to show new column
        location.reload();
    });
}

// Remove a strategy
function removeStrategy(strategyId) {
    if (!confirm('Remove this strategy? All related analysis will be deleted.')) return;

    window.scenarioPlanning.strategies = window.scenarioPlanning.strategies.filter(s => s.id !== strategyId);

    // Remove related cells
    const keysToRemove = Object.keys(window.scenarioPlanning.cells).filter(k => k.startsWith(strategyId + '_'));
    keysToRemove.forEach(k => delete window.scenarioPlanning.cells[k]);

    saveScenarioPlanning().then(() => location.reload());
}

// Add a new future
function addFuture() {
    if (!window.scenarioPlanning) {
        window.scenarioPlanning = { strategies: [], futures: [], cells: {} };
    }

    const newFuture = {
        id: generateId(),
        name: '',
        description: ''
    };

    window.scenarioPlanning.futures.push(newFuture);
    saveScenarioPlanning().then(() => {
        location.reload();
    });
}

// Remove a future
function removeFuture(futureId) {
    if (!confirm('Remove this future? All related analysis will be deleted.')) return;

    window.scenarioPlanning.futures = window.scenarioPlanning.futures.filter(f => f.id !== futureId);

    // Remove related cells
    const keysToRemove = Object.keys(window.scenarioPlanning.cells).filter(k => k.endsWith('_' + futureId));
    keysToRemove.forEach(k => delete window.scenarioPlanning.cells[k]);

    saveScenarioPlanning().then(() => location.reload());
}

// Select a cell to edit
function selectScenarioCell(strategyId, futureId) {
    selectedStrategyId = strategyId;
    selectedFutureId = futureId;

    // Highlight selected cell
    document.querySelectorAll('.scenario-cell').forEach(c => c.classList.remove('selected'));
    const cell = document.querySelector(`.scenario-cell[data-strategy-id="${strategyId}"][data-future-id="${futureId}"]`);
    if (cell) cell.classList.add('selected');

    // Get strategy and future data
    const strategy = window.scenarioPlanning.strategies.find(s => s.id === strategyId);
    const future = window.scenarioPlanning.futures.find(f => f.id === futureId);
    const cellKey = `${strategyId}_${futureId}`;
    const cellData = window.scenarioPlanning.cells[cellKey] || { thoughts: '', summary: '' };

    // Update labels with actual names
    const strategyName = strategy?.name || 'Strategy';
    const futureName = future?.name || 'Future';
    document.getElementById('strategy-description-label').textContent = 'Strategy: ' + (strategyName || 'Unnamed');
    document.getElementById('future-description-label').textContent = 'Future: ' + (futureName || 'Unnamed');

    // Populate detail panel
    document.getElementById('strategy-description').value = strategy?.description || '';
    document.getElementById('future-description').value = future?.description || '';
    document.getElementById('cell-thoughts').value = cellData.thoughts || '';
    document.getElementById('cell-summary').value = cellData.summary || '';

    // Show detail panel
    document.getElementById('scenario-detail-panel').style.display = 'block';

    // Scroll to panel
    document.getElementById('scenario-detail-panel').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Close detail panel
function closeScenarioDetail() {
    selectedStrategyId = null;
    selectedFutureId = null;
    document.getElementById('scenario-detail-panel').style.display = 'none';
    document.querySelectorAll('.scenario-cell').forEach(c => c.classList.remove('selected'));
}

// Save scenario planning data
async function saveScenarioPlanning() {
    const businessId = getScenarioBusinessId();
    if (!businessId) return;

    const response = await fetch(`/business/${businessId}/scenario-planning`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(window.scenarioPlanning)
    });

    const result = await response.json();
    if (result.success) {
        showScenarioSaveStatus();
    }
    return result;
}

function showScenarioSaveStatus() {
    const status = document.getElementById('scenario-save-status');
    if (status) {
        status.textContent = 'Saved';
        status.style.opacity = '1';
        status.style.color = 'var(--color-success)';
        setTimeout(() => {
            status.style.opacity = '0';
        }, 2000);
    }
}

// Debounced save for scenario planning
const debouncedScenarioSave = debounce(() => saveScenarioPlanning(), 500);

// Initialize scenario planning event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Strategy name inputs
    document.querySelectorAll('.strategy-name').forEach(input => {
        input.addEventListener('input', (e) => {
            const header = e.target.closest('.strategy-header');
            const strategyId = header?.dataset.id;
            if (strategyId) {
                const strategy = window.scenarioPlanning.strategies.find(s => s.id === strategyId);
                if (strategy) {
                    strategy.name = e.target.value;
                    debouncedScenarioSave();
                }
            }
        });
    });

    // Future name inputs
    document.querySelectorAll('.future-name').forEach(input => {
        input.addEventListener('input', (e) => {
            const row = e.target.closest('tr');
            const futureId = row?.dataset.futureId;
            if (futureId) {
                const future = window.scenarioPlanning.futures.find(f => f.id === futureId);
                if (future) {
                    future.name = e.target.value;
                    debouncedScenarioSave();
                }
            }
        });
    });

    // Detail panel inputs
    const strategyDesc = document.getElementById('strategy-description');
    const futureDesc = document.getElementById('future-description');
    const cellThoughts = document.getElementById('cell-thoughts');
    const cellSummary = document.getElementById('cell-summary');

    if (strategyDesc) {
        strategyDesc.addEventListener('input', () => {
            if (selectedStrategyId) {
                const strategy = window.scenarioPlanning.strategies.find(s => s.id === selectedStrategyId);
                if (strategy) {
                    strategy.description = strategyDesc.value;
                    debouncedScenarioSave();
                }
            }
        });
    }

    if (futureDesc) {
        futureDesc.addEventListener('input', () => {
            if (selectedFutureId) {
                const future = window.scenarioPlanning.futures.find(f => f.id === selectedFutureId);
                if (future) {
                    future.description = futureDesc.value;
                    debouncedScenarioSave();
                }
            }
        });
    }

    if (cellThoughts) {
        cellThoughts.addEventListener('input', () => {
            if (selectedStrategyId && selectedFutureId) {
                const cellKey = `${selectedStrategyId}_${selectedFutureId}`;
                if (!window.scenarioPlanning.cells[cellKey]) {
                    window.scenarioPlanning.cells[cellKey] = {};
                }
                window.scenarioPlanning.cells[cellKey].thoughts = cellThoughts.value;
                debouncedScenarioSave();
            }
        });
    }

    if (cellSummary) {
        cellSummary.addEventListener('input', () => {
            if (selectedStrategyId && selectedFutureId) {
                const cellKey = `${selectedStrategyId}_${selectedFutureId}`;
                if (!window.scenarioPlanning.cells[cellKey]) {
                    window.scenarioPlanning.cells[cellKey] = {};
                }
                window.scenarioPlanning.cells[cellKey].summary = cellSummary.value;

                // Update the grid cell display
                const cell = document.querySelector(`.scenario-cell[data-strategy-id="${selectedStrategyId}"][data-future-id="${selectedFutureId}"]`);
                if (cell) {
                    const summarySpan = cell.querySelector('.cell-summary');
                    if (summarySpan) {
                        summarySpan.textContent = cellSummary.value || '—';
                    }
                    if (cellSummary.value) {
                        cell.classList.add('has-summary');
                    } else {
                        cell.classList.remove('has-summary');
                    }
                }

                debouncedScenarioSave();
            }
        });
    }
});
