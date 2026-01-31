/* Quote Highlighter - Select text to create quotes */

function initQuoteHighlighter(itemId) {
    const container = document.querySelector(`[data-item-id="${itemId}"] .text-container`);
    if (!container || container.dataset.initialized) return;

    container.dataset.initialized = 'true';

    const textContent = container.querySelector('.text-content');
    const quotesData = JSON.parse(container.dataset.quotes || '[]');

    // Render existing quotes as highlights
    renderHighlights(textContent, quotesData);

    // Listen for text selection
    textContent.addEventListener('mouseup', () => {
        const selection = window.getSelection();
        if (selection.rangeCount === 0 || selection.isCollapsed) return;

        const range = selection.getRangeAt(0);
        const selectedText = selection.toString().trim();

        if (selectedText.length < 3) return;

        // Calculate offsets relative to the text content
        const offsets = getSelectionOffsets(textContent, range);
        if (!offsets) return;

        // Create the quote
        createQuote(itemId, offsets.start, offsets.end, selectedText);

        // Clear selection
        selection.removeAllRanges();
    });
}

function getSelectionOffsets(container, range) {
    const preRange = document.createRange();
    preRange.selectNodeContents(container);
    preRange.setEnd(range.startContainer, range.startOffset);
    const start = preRange.toString().length;

    const fullRange = document.createRange();
    fullRange.selectNodeContents(container);
    fullRange.setEnd(range.endContainer, range.endOffset);
    const end = fullRange.toString().length;

    return { start, end };
}

function createQuote(itemId, startOffset, endOffset, text) {
    fetch(`/research/${itemId}/quote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            start_offset: startOffset,
            end_offset: endOffset,
            text: text
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Add to quotes list
                const quotesList = document.querySelector(`[data-item-id="${itemId}"] .quotes-list`);
                const quoteEl = document.createElement('div');
                quoteEl.className = 'quote';
                quoteEl.dataset.quoteId = data.id;
                quoteEl.innerHTML = `
                <span class="quote-text">"${escapeHtml(text)}"</span>
                <button class="remove-quote" onclick="deleteQuote(${data.id})">&times;</button>
            `;
                quotesList.appendChild(quoteEl);

                // Re-render highlights
                const container = document.querySelector(`[data-item-id="${itemId}"] .text-container`);
                const textContent = container.querySelector('.text-content');
                const quotesData = JSON.parse(container.dataset.quotes || '[]');
                quotesData.push({ id: data.id, start_offset: startOffset, end_offset: endOffset, text });
                container.dataset.quotes = JSON.stringify(quotesData);
                renderHighlights(textContent, quotesData);

                showNotification('Quote created!', 'success');
            }
        })
        .catch(err => {
            showNotification('Error creating quote', 'error');
            console.error(err);
        });
}

function deleteQuote(quoteId) {
    if (!confirm('Delete this quote?')) return;

    fetch(`/quote/${quoteId}/delete`, {
        method: 'POST'
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Remove from DOM
                const quoteEl = document.querySelector(`[data-quote-id="${quoteId}"]`);
                if (quoteEl) {
                    const container = quoteEl.closest('.research-item').querySelector('.text-container');
                    quoteEl.remove();

                    // Update quotes data and re-render
                    const quotesData = JSON.parse(container.dataset.quotes || '[]');
                    const newQuotes = quotesData.filter(q => q.id !== quoteId);
                    container.dataset.quotes = JSON.stringify(newQuotes);

                    const textContent = container.querySelector('.text-content');
                    renderHighlights(textContent, newQuotes);
                }

                showNotification('Quote deleted', 'success');
            }
        })
        .catch(err => {
            showNotification('Error deleting quote', 'error');
            console.error(err);
        });
}

function renderHighlights(textContent, quotes) {
    const originalText = textContent.textContent;

    if (quotes.length === 0) {
        textContent.textContent = originalText;
        return;
    }

    // Sort quotes by start offset
    const sortedQuotes = [...quotes].sort((a, b) => a.start_offset - b.start_offset);

    // Build highlighted HTML
    let html = '';
    let lastEnd = 0;

    for (const quote of sortedQuotes) {
        // Add text before this quote
        if (quote.start_offset > lastEnd) {
            html += escapeHtml(originalText.slice(lastEnd, quote.start_offset));
        }

        // Add highlighted quote
        html += `<mark>${escapeHtml(originalText.slice(quote.start_offset, quote.end_offset))}</mark>`;
        lastEnd = quote.end_offset;
    }

    // Add remaining text
    if (lastEnd < originalText.length) {
        html += escapeHtml(originalText.slice(lastEnd));
    }

    textContent.innerHTML = html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
