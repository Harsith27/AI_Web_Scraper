const urlInput = document.getElementById('url-input');
const checkFieldsBtn = document.getElementById('check-fields-btn');
const messageEl = document.getElementById('message');
const fieldsList = document.getElementById('fields-list');

checkFieldsBtn.addEventListener('click', () => {
  const url = urlInput.value.trim();
  messageEl.textContent = url ? `Ready to scan ${url}` : 'Please enter a URL';
  fieldsList.textContent = '';
});