// ---- 前週比ウィジェット ----
const snapshotBtn = document.getElementById('snapshot-btn');
const snapshotDate = document.getElementById('snapshot-date');
const diffContent = document.getElementById('diff-content');

function formatDiff(n) {
  if (n === null || n === undefined) return { text: '-', cls: 'text-gray-400' };
  if (n > 0) return { text: `+${n}`, cls: 'text-green-600 font-semibold' };
  if (n < 0) return { text: `${n}`, cls: 'text-red-500 font-semibold' };
  return { text: '±0', cls: 'text-gray-400' };
}

function renderDiff(data) {
  if (!data.snapshot_exists) {
    diffContent.innerHTML = '<p class="text-sm text-gray-400">スナップショットがまだ保存されていません。「記録」ボタンを押してください。</p>';
    snapshotDate.textContent = '';
    return;
  }

  const saved = new Date(data.saved_at);
  snapshotDate.textContent = `最終記録: ${saved.toLocaleString('ja-JP')}`;

  const rows = data.diffs.map((d, i) => {
    const likes = formatDiff(d.likes_diff);
    const stocks = formatDiff(d.stocks_diff);
    return `
      <tr class="hover:bg-gray-50">
        <td class="px-4 py-2 text-gray-400">${i + 1}</td>
        <td class="px-4 py-2">
          <a href="${escapeHtml(d.url)}" target="_blank" class="text-blue-500 hover:underline">${escapeHtml(d.title)}</a>
        </td>
        <td class="px-4 py-2 text-center text-gray-700">${d.likes_count}</td>
        <td class="px-4 py-2 text-center ${likes.cls}">${likes.text}</td>
        <td class="px-4 py-2 text-center text-gray-700">${d.stocks_count}</td>
        <td class="px-4 py-2 text-center ${stocks.cls}">${stocks.text}</td>
      </tr>`;
  }).join('');

  diffContent.innerHTML = `
    <table class="w-full text-sm border-collapse">
      <thead>
        <tr class="bg-gray-50 text-left text-gray-600">
          <th class="px-4 py-2 border-b font-medium w-8">#</th>
          <th class="px-4 py-2 border-b font-medium">タイトル</th>
          <th class="px-4 py-2 border-b font-medium w-20 text-center">いいね</th>
          <th class="px-4 py-2 border-b font-medium w-20 text-center">前週比</th>
          <th class="px-4 py-2 border-b font-medium w-20 text-center">ストック</th>
          <th class="px-4 py-2 border-b font-medium w-20 text-center">前週比</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">${rows}</tbody>
    </table>`;
}

async function loadDiff() {
  diffContent.innerHTML = '<p class="text-sm text-gray-400">読み込み中...</p>';
  try {
    const res = await fetch('/api/snapshot/diff');
    const data = await res.json();
    if (data.status === 'error') {
      diffContent.innerHTML = `<p class="text-sm text-red-500">${escapeHtml(data.message)}</p>`;
      return;
    }
    renderDiff(data);
  } catch (e) {
    diffContent.innerHTML = '<p class="text-sm text-red-500">通信エラーが発生しました</p>';
  }
}

snapshotBtn.addEventListener('click', async () => {
  snapshotBtn.disabled = true;
  snapshotBtn.textContent = '記録中...';
  try {
    const res = await fetch('/api/snapshot/save', { method: 'POST' });
    const data = await res.json();
    if (data.status === 'error') {
      alert(data.message);
      return;
    }
    await loadDiff();
  } catch (e) {
    alert('通信エラーが発生しました');
  } finally {
    snapshotBtn.disabled = false;
    snapshotBtn.textContent = '記録';
  }
});

document.addEventListener('DOMContentLoaded', loadDiff);

// ---- 記事一覧 ----
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
