const statusMsg = document.getElementById('status-msg');
const resultsArea = document.getElementById('results-area');
const tbody = document.getElementById('trending-tbody');

function setStatus(message, color = 'text-gray-400') {
  statusMsg.className = `text-sm ${color} mb-4`;
  statusMsg.textContent = message;
}

async function fetchTrending() {
  resultsArea.classList.add('hidden');
  tbody.innerHTML = '';
  setStatus('取得中...', 'text-gray-400');

  try {
    const res = await fetch('/api/trending');
    const data = await res.json();

    if (data.status === 'error') {
      setStatus(data.message, 'text-red-500');
      return;
    }

    renderData(data);
  } catch (e) {
    setStatus('通信エラーが発生しました', 'text-red-500');
  }
}

function renderData(data) {
  data.articles.forEach(item => {
    const date = item.created_at.slice(0, 10);
    const tags = item.tags.map(t => `<span class="inline-block bg-gray-100 text-gray-600 rounded px-1 mr-1">${escapeHtml(t)}</span>`).join('');
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-gray-50';
    tr.innerHTML = `
      <td class="px-4 py-2">
        <a href="${escapeHtml(item.url)}" target="_blank"
           class="text-blue-600 hover:underline">${escapeHtml(item.title)}</a>
      </td>
      <td class="px-4 py-2 text-right font-medium text-gray-700">${item.likes_count.toLocaleString()}</td>
      <td class="px-4 py-2 text-right font-medium text-gray-700">${item.stocks_count.toLocaleString()}</td>
      <td class="px-4 py-2 text-gray-600">${escapeHtml(item.user)}</td>
      <td class="px-4 py-2">${tags}</td>
      <td class="px-4 py-2 text-gray-500">${date}</td>
    `;
    tbody.appendChild(tr);
  });

  resultsArea.classList.remove('hidden');
  setStatus(`${data.count} 件取得しました`, 'text-green-600');
}

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}
