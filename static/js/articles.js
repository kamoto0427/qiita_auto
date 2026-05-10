const fetchBtn = document.getElementById('fetch-btn');
const copyBtn = document.getElementById('copy-btn');
const statusMsg = document.getElementById('status-msg');
const resultsArea = document.getElementById('results-area');
const tbody = document.getElementById('articles-tbody');

let fetchedTitles = [];

function setStatus(message, color = 'text-gray-500') {
  statusMsg.className = `text-sm ${color}`;
  statusMsg.textContent = message;
}

fetchBtn.addEventListener('click', async () => {
  fetchBtn.disabled = true;
  copyBtn.disabled = true;
  resultsArea.classList.add('hidden');
  tbody.innerHTML = '';
  fetchedTitles = [];
  setStatus('取得中...', 'text-gray-400');

  try {
    const res = await fetch('/api/articles');
    const data = await res.json();

    if (data.status === 'error') {
      setStatus(data.message, 'text-red-500');
      return;
    }

    fetchedTitles = data.articles.map(a => a.title);

    data.articles.forEach((article, i) => {
      const date = article.created_at.slice(0, 10);
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-gray-50';
      tr.innerHTML = `
        <td class="px-4 py-2 text-gray-400">${i + 1}</td>
        <td class="px-4 py-2">${escapeHtml(article.title)}</td>
        <td class="px-4 py-2 text-gray-500">${date}</td>
        <td class="px-4 py-2">
          <a href="${escapeHtml(article.url)}" target="_blank"
             class="text-blue-500 hover:underline">開く</a>
        </td>
      `;
      tbody.appendChild(tr);
    });

    resultsArea.classList.remove('hidden');
    copyBtn.disabled = false;
    setStatus(`${data.count} 件取得しました`, 'text-green-600');
  } catch (e) {
    setStatus('通信エラーが発生しました', 'text-red-500');
  } finally {
    fetchBtn.disabled = false;
  }
});

copyBtn.addEventListener('click', () => {
  navigator.clipboard.writeText(fetchedTitles.join('\n')).then(() => {
    const original = copyBtn.textContent;
    copyBtn.textContent = 'コピーしました！';
    setTimeout(() => { copyBtn.textContent = original; }, 1500);
  });
});

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}
