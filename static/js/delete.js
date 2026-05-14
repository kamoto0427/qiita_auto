const fetchBtn = document.getElementById('fetch-btn');
const selectAllBtn = document.getElementById('select-all-btn');
const deselectAllBtn = document.getElementById('deselect-all-btn');
const deleteBtn = document.getElementById('delete-btn');
const statusMsg = document.getElementById('status-msg');
const resultsArea = document.getElementById('results-area');
const tbody = document.getElementById('articles-tbody');
const selectionInfo = document.getElementById('selection-info');
const selectedCountEl = document.getElementById('selected-count');

let articles = [];

function setStatus(message, color = 'text-gray-500') {
  statusMsg.className = `text-sm ${color}`;
  statusMsg.textContent = message;
}

function updateSelectionCount() {
  const checked = tbody.querySelectorAll('input[type="checkbox"]:checked').length;
  selectedCountEl.textContent = checked;
  deleteBtn.disabled = checked === 0;
}

fetchBtn.addEventListener('click', async () => {
  fetchBtn.disabled = true;
  selectAllBtn.disabled = true;
  deselectAllBtn.disabled = true;
  deleteBtn.disabled = true;
  resultsArea.classList.add('hidden');
  selectionInfo.classList.add('hidden');
  tbody.innerHTML = '';
  articles = [];
  setStatus('取得中...', 'text-gray-400');

  try {
    const res = await fetch('/api/articles');
    const data = await res.json();

    if (data.status === 'error') {
      setStatus(data.message, 'text-red-500');
      return;
    }

    articles = data.articles;

    articles.forEach((article) => {
      const date = article.created_at.slice(0, 10);
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-gray-50';
      tr.dataset.id = article.id;
      tr.innerHTML = `
        <td class="px-4 py-2 text-center">
          <input type="checkbox" class="article-checkbox w-4 h-4 cursor-pointer" data-id="${escapeHtml(article.id)}">
        </td>
        <td class="px-4 py-2">
          <a href="${escapeHtml(article.url)}" target="_blank" class="text-blue-600 hover:underline">
            ${escapeHtml(article.title)}
          </a>
        </td>
        <td class="px-4 py-2 text-center text-gray-600">${article.likes_count}</td>
        <td class="px-4 py-2 text-center text-gray-600">${article.stocks_count}</td>
        <td class="px-4 py-2 text-gray-500">${date}</td>
      `;
      tbody.appendChild(tr);
    });

    tbody.querySelectorAll('.article-checkbox').forEach(cb => {
      cb.addEventListener('change', updateSelectionCount);
    });

    resultsArea.classList.remove('hidden');
    selectionInfo.classList.remove('hidden');
    selectAllBtn.disabled = false;
    deselectAllBtn.disabled = false;
    setStatus(`${data.count} 件取得しました`, 'text-green-600');
    updateSelectionCount();
  } catch (e) {
    setStatus('通信エラーが発生しました', 'text-red-500');
  } finally {
    fetchBtn.disabled = false;
  }
});

selectAllBtn.addEventListener('click', () => {
  tbody.querySelectorAll('.article-checkbox').forEach(cb => { cb.checked = true; });
  updateSelectionCount();
});

deselectAllBtn.addEventListener('click', () => {
  tbody.querySelectorAll('.article-checkbox').forEach(cb => { cb.checked = false; });
  updateSelectionCount();
});

deleteBtn.addEventListener('click', async () => {
  const checkedBoxes = Array.from(tbody.querySelectorAll('.article-checkbox:checked'));
  const itemIds = checkedBoxes.map(cb => cb.dataset.id);

  if (itemIds.length === 0) return;

  const confirmed = window.confirm(
    `選択した ${itemIds.length} 件の記事を削除しますか？\nこの操作は取り消せません。`
  );
  if (!confirmed) return;

  fetchBtn.disabled = true;
  selectAllBtn.disabled = true;
  deselectAllBtn.disabled = true;
  deleteBtn.disabled = true;
  setStatus('削除中...', 'text-gray-400');

  try {
    const res = await fetch('/api/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_ids: itemIds }),
    });
    const data = await res.json();

    if (data.status === 'error') {
      setStatus(data.message, 'text-red-500');
      return;
    }

    // 削除成功した行をテーブルから除去
    data.deleted.forEach(id => {
      const row = tbody.querySelector(`tr[data-id="${id}"]`);
      if (row) row.remove();
    });

    let msg = `${data.deleted_count} 件削除しました`;
    if (data.errors.length > 0) {
      msg += `（${data.errors.length} 件失敗）`;
      setStatus(msg, 'text-yellow-600');
    } else {
      setStatus(msg, 'text-green-600');
    }

    updateSelectionCount();
  } catch (e) {
    setStatus('通信エラーが発生しました', 'text-red-500');
  } finally {
    fetchBtn.disabled = false;
    selectAllBtn.disabled = false;
    deselectAllBtn.disabled = false;
  }
});

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}
