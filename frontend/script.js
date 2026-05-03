const discoveryForm = document.getElementById('discovery-form');
const checkFieldsBtn = document.getElementById('check-fields-btn');
const urlInput = document.getElementById('url-input');
const messageEl = document.getElementById('message');
const fieldsList = document.getElementById('fields-list');
const queryInput = document.getElementById('query-input');
const formatInput = document.getElementById('format-input');
const limitInput = document.getElementById('limit-input');
const extractBtn = document.getElementById('extract-btn');
const askBtn = document.getElementById('ask-btn');
const resultsSection = document.getElementById('results-section');
const resultsToolbar = document.getElementById('results-toolbar');
const emptyStateCard = document.getElementById('empty-state-card');
const tableSearch = document.getElementById('table-search');
const searchCount = document.getElementById('search-count');
const copyJsonBtn = document.getElementById('copy-json-btn');
const csvDownload = document.getElementById('csv-download');
const askForm = document.getElementById('ask-form');
const answerOutput = document.getElementById('answer-output');
const jsonOutput = document.getElementById('json-output');
const tableTab = document.getElementById('table-tab');
const jsonTab = document.getElementById('json-tab');
const tabButtons = document.querySelectorAll('.tab-button');

const state = {
  discoveredFields: [],
  selectedFields: [],
  lastUrl: '',
  lastResults: [],
  lastAutoQuery: '',
  isQueryAuto: true,
};

const spinnerMap = new Map([
  ['discover', document.querySelector('#check-fields-btn .spinner')],
  ['extract', document.querySelector('#extract-btn .spinner')],
  ['ask', document.querySelector('#ask-btn .spinner')],
]);

const buttonMap = {
  discover: checkFieldsBtn,
  extract: extractBtn,
  ask: askBtn,
};

function setLoading(action, loading) {
  const spinner = spinnerMap.get(action);
  const button = buttonMap[action];
  if (button) {
    button.disabled = loading;
    button.classList.toggle('opacity-70', loading);
    button.classList.toggle('cursor-wait', loading);
  }
  if (!spinner) return;
  spinner.classList.toggle('hidden', !loading);
}

function setStatus(text, isError = false) {
  if (messageEl) {
    messageEl.textContent = text;
  }
}

function buildQuery(fields) {
  return fields.length ? `Extract ${fields.join(', ')}` : '';
}

function syncQuery() {
  const generated = buildQuery(state.selectedFields);
  if (!queryInput) return;
  if (state.isQueryAuto || queryInput.value.trim() === '' || queryInput.value.trim() === state.lastAutoQuery) {
    queryInput.value = generated;
    state.lastAutoQuery = generated;
    state.isQueryAuto = true;
  }
}

function renderFieldCheckboxes(fields) {
  if (!fieldsList) return;
  fieldsList.innerHTML = '';
  state.selectedFields = [...fields];

  if (!fields.length) {
    fieldsList.innerHTML = '<span class="text-muted text-sm">No fields found.</span>';
    syncQuery();
    return;
  }

  fields.forEach((field) => {
    const label = document.createElement('label');
    label.className = 'flex items-center gap-3 p-3 rounded-xl border border-border bg-surface-strong cursor-pointer transition hover:border-accent';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = true;
    checkbox.value = field;
    checkbox.className = 'h-4 w-4 rounded border-border bg-black text-accent focus:ring-accent';
    checkbox.addEventListener('change', () => {
      state.selectedFields = Array.from(fieldsList.querySelectorAll('input[type="checkbox"]:checked')).map((input) => input.value);
      syncQuery();
    });

    const text = document.createElement('div');
    text.className = 'text-sm';
    text.innerHTML = `<span class="font-medium">${field}</span><br><span class="text-muted text-xs">Extract this field from the page</span>`;

    label.appendChild(checkbox);
    label.appendChild(text);
    fieldsList.appendChild(label);
  });

  syncQuery();
}

async function discoverFields() {
  if (!urlInput) return;
  const url = urlInput.value.trim();
  if (!url) {
    setStatus('Please enter a valid URL.', true);
    return;
  }

  resetWorkflow();
  setLoading('discover', true);
  setStatus(`Discovering fields for ${url}...`);

  try {
    const response = await fetch('/discover-fields', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });

    setLoading('discover', false);

    if (!response.ok) {
      const error = await response.text();
      setStatus(`Discovery failed: ${error}`, true);
      return;
    }

    const result = await response.json();
    state.discoveredFields = result.fields || [];
    state.selectedFields = [...state.discoveredFields];
    state.lastUrl = result.url || url;
    state.lastAutoQuery = buildQuery(state.selectedFields);
    state.isQueryAuto = true;

    renderFieldCheckboxes(state.discoveredFields);

    if (state.selectedFields.length) {
      setStatus(`Found ${state.selectedFields.length} candidate fields.`);
    } else {
      setStatus('No candidate fields were discovered.', true);
    }
  } catch (error) {
    setLoading('discover', false);
    setStatus(`Discovery failed: ${error.message}`, true);
  }
}

function onDiscoverySubmit(event) {
  if (event) event.preventDefault();
  discoverFields();
}

function renderResults(data, fields) {
  if (!resultsSection || !resultsToolbar || !emptyStateCard || !jsonOutput || !csvDownload) return;

  if (!Array.isArray(data) || !data.length) {
    resultsSection.style.display = 'none';
    resultsToolbar.classList.add('hidden');
    emptyStateCard.classList.remove('hidden');
    jsonOutput.textContent = '{}';
    csvDownload.classList.add('hidden');
    return;
  }

  resultsSection.style.display = 'block';
  resultsToolbar.classList.remove('hidden');
  emptyStateCard.classList.add('hidden');

  const displayFields = fields.length ? fields : Object.keys(data[0] || {});
  const tableHead = document.querySelector('#results-table thead');
  const tableBody = document.querySelector('#results-table tbody');
  if (!tableHead || !tableBody) return;

  tableHead.innerHTML = `<tr>${displayFields.map((field) => `<th class="text-left px-4 py-3 text-xs uppercase tracking-[0.2em] text-muted">${field}</th>`).join('')}</tr>`;
  tableBody.innerHTML = data.map((row) => {
    return `<tr class="border-t border-border">${displayFields.map((field) => `<td class="px-4 py-3 align-top text-sm text-white">${String(row[field] ?? '').replace(/</g, '&lt;')}</td>`).join('')}</tr>`;
  }).join('');

  jsonOutput.textContent = JSON.stringify(data, null, 2);
  updateCsvDownload(data, displayFields);
  updateTableSearch();
}

function updateCsvDownload(data, fields) {
  if (!csvDownload) return;
  if (!data.length) {
    csvDownload.classList.add('hidden');
    return;
  }

  const header = fields.map((field) => JSON.stringify(field)).join(',');
  const rows = data.map((row) => fields.map((field) => JSON.stringify(row[field] ?? '')).join(','));
  const csvText = `${header}\n${rows.join('\n')}`;
  const blob = new Blob([csvText], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  csvDownload.href = url;
  csvDownload.classList.remove('hidden');
}

function updateTableSearch() {
  if (!tableSearch || !searchCount) return;
  const query = tableSearch.value.trim().toLowerCase();
  const rows = Array.from(document.querySelectorAll('#results-table tbody tr'));
  let visibleCount = 0;

  rows.forEach((row) => {
    const text = row.textContent.toLowerCase();
    const visible = query === '' || text.includes(query);
    row.style.display = visible ? '' : 'none';
    if (visible) visibleCount += 1;
  });

  searchCount.textContent = query === '' ? `${rows.length} rows` : `${visibleCount} matching`;
}

function initializeTabs() {
  if (!tabButtons || !tableTab || !jsonTab) return;
  tabButtons.forEach((button) => {
    button.addEventListener('click', () => {
      tabButtons.forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');
      const target = button.dataset.tab;
      tableTab.classList.toggle('hidden', target !== 'table');
      jsonTab.classList.toggle('hidden', target !== 'json');
    });
  });
}

function resetWorkflow() {
  if (resultsSection) resultsSection.style.display = 'none';
  if (resultsToolbar) resultsToolbar.classList.add('hidden');
  if (emptyStateCard) emptyStateCard.classList.remove('hidden');
  if (csvDownload) csvDownload.classList.add('hidden');
  state.selectedFields = [];
  state.lastUrl = '';
  state.lastResults = [];
  state.lastAutoQuery = '';
  state.isQueryAuto = true;
  if (queryInput) queryInput.value = '';
  if (tableSearch) tableSearch.value = '';
  if (searchCount) searchCount.textContent = '';
}

async function extractData() {
  if (!state.lastUrl) {
    setStatus('Discover fields first before extracting data.', true);
    return;
  }
  if (!queryInput) return;

  const query = queryInput.value.trim();
  if (!query) {
    setStatus('Please enter or preserve an extraction query.', true);
    return;
  }

  setLoading('extract', true);
  setStatus('Extracting data...');

  try {
    const response = await fetch('/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: state.lastUrl,
        query,
        selected_fields: state.selectedFields,
        format: formatInput?.value || 'json',
      }),
    });

    setLoading('extract', false);

    if (!response.ok) {
      const error = await response.text();
      setStatus(`Extraction failed: ${error}`, true);
      return;
    }

    const result = await response.json();
    const limit = Number(limitInput?.value) || 0;
    let data = result.data || [];
    const originalCount = data.length;
    if (limit > 0 && data.length > limit) {
      data = data.slice(0, limit);
    }
    state.lastResults = data;
    renderResults(state.lastResults, result.fields || state.selectedFields);
    setStatus(limit > 0 && originalCount > limit ? `Showing first ${limit} of ${originalCount} scraped items.` : 'Extraction completed successfully.');
  } catch (error) {
    setLoading('extract', false);
    setStatus(`Extraction failed: ${error.message}`, true);
  }
}

async function askQuestion(event) {
  event.preventDefault();
  const questionInput = document.getElementById('question-input');
  if (!questionInput) return;

  const question = questionInput.value.trim();
  if (!state.lastUrl) {
    setStatus('Extract data first before asking a question.', true);
    return;
  }
  if (!question) {
    setStatus('Please enter a question.', true);
    return;
  }

  setLoading('ask', true);
  setStatus('Submitting question...');

  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: state.lastUrl,
        question,
        scope: 'data',
        data: state.lastResults,
      }),
    });

    setLoading('ask', false);

    if (!response.ok) {
      const error = await response.text();
      setStatus(`Question failed: ${error}`, true);
      return;
    }

    const result = await response.json();
    if (answerOutput) {
      answerOutput.innerHTML = `<p class="text-sm text-white">${result.answer ?? 'No answer returned.'}</p>`;
    }
    setStatus('Question answered successfully.');
  } catch (error) {
    setLoading('ask', false);
    setStatus(`Question failed: ${error.message}`, true);
  }
}

function init() {
  if (!discoveryForm || !checkFieldsBtn || !extractBtn || !askForm) {
    console.error('Frontend initialization failed: missing required DOM elements.');
    return;
  }

  discoveryForm.addEventListener('submit', onDiscoverySubmit);
  checkFieldsBtn.addEventListener('click', onDiscoverySubmit);
  extractBtn.addEventListener('click', extractData);
  askForm.addEventListener('submit', askQuestion);
  if (tableSearch) tableSearch.addEventListener('input', updateTableSearch);
  if (copyJsonBtn) copyJsonBtn.addEventListener('click', async () => {
    await navigator.clipboard.writeText(jsonOutput.textContent || '');
    setStatus('JSON copied to clipboard.');
  });
  initializeTabs();
  setStatus('Enter a URL and click Check Available Fields to start.');
}

window.addEventListener('DOMContentLoaded', init);
