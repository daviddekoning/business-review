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
});

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
        const levelSelect = form.querySelector(`select[name="${force}_level"]`);
        const factorInputs = form.querySelectorAll(`input[name="${force}_factors[]"]`);

        data[force] = {
            level: levelSelect ? levelSelect.value : 'medium',
            factors: Array.from(factorInputs).map(input => input.value.trim()).filter(v => v)
        };
    });

    return data;
}

function collectVRIOData(form) {
    const rows = form.querySelectorAll('tbody tr');
    const resources = [];

    rows.forEach((row, i) => {
        const nameInput = row.querySelector(`input[name="resource_${i}_name"]`);
        if (!nameInput || !nameInput.value.trim()) return;

        resources.push({
            name: nameInput.value.trim(),
            valuable: row.querySelector(`input[name="resource_${i}_valuable"]`)?.checked || false,
            rare: row.querySelector(`input[name="resource_${i}_rare"]`)?.checked || false,
            costly_to_imitate: row.querySelector(`input[name="resource_${i}_costly_to_imitate"]`)?.checked || false,
            organized: row.querySelector(`input[name="resource_${i}_organized"]`)?.checked || false
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

// Five Forces - Add factor item
function addForceItem(force) {
    const container = document.querySelector(`[data-force="${force}"] .force-factors`);
    const index = container.children.length;

    const div = document.createElement('div');
    div.className = 'factor-item';
    div.dataset.index = index;
    div.innerHTML = `
        <input type="text" name="${force}_factors[]" placeholder="Add factor...">
        <button type="button" class="remove-item" onclick="removeItem(this)">×</button>
    `;
    container.appendChild(div);
    div.querySelector('input').focus();

    const form = container.closest('form');
    handleAutoSave(form);
}

// VRIO - Add row
function addVRIORow() {
    const tbody = document.querySelector('.vrio-table tbody');
    const index = tbody.children.length;

    const tr = document.createElement('tr');
    tr.dataset.index = index;
    tr.innerHTML = `
        <td><input type="text" name="resource_${index}_name" placeholder="Resource name"></td>
        <td><input type="checkbox" name="resource_${index}_valuable"></td>
        <td><input type="checkbox" name="resource_${index}_rare"></td>
        <td><input type="checkbox" name="resource_${index}_costly_to_imitate"></td>
        <td><input type="checkbox" name="resource_${index}_organized"></td>
        <td class="implication">-</td>
        <td><button type="button" class="remove-row" onclick="removeVRIORow(this)">×</button></td>
    `;
    tbody.appendChild(tr);
    tr.querySelector('input').focus();

    // Add change listeners for implication updates
    tr.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', () => updateVRIOImplication(tr));
    });

    // Save
    const form = tbody.closest('form');
    handleAutoSave(form);
}

function removeVRIORow(button) {
    const form = button.closest('form');
    button.closest('tr').remove();
    handleAutoSave(form);
}

function updateVRIOImplication(row) {
    const index = row.dataset.index;
    const valuable = row.querySelector(`input[name="resource_${index}_valuable"]`).checked;
    const rare = row.querySelector(`input[name="resource_${index}_rare"]`).checked;
    const costly = row.querySelector(`input[name="resource_${index}_costly_to_imitate"]`).checked;
    const organized = row.querySelector(`input[name="resource_${index}_organized"]`).checked;

    let implication;
    if (!valuable) implication = 'Competitive Disadvantage';
    else if (!rare) implication = 'Competitive Parity';
    else if (!costly) implication = 'Temporary Advantage';
    else if (!organized) implication = 'Unused Advantage';
    else implication = 'Sustained Advantage';

    row.querySelector('.implication').textContent = implication;
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
