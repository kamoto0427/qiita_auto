const cache = {};
let currentTab = 'likes';

const statusMsg = document.getElementById('status-msg');
const summaryArea = document.getElementById('summary-area');
const resultsArea = document.getElementById('results-area');
const tbody = document.getElementById('ranking-tbody');
const countHeader = document.getElementById('count-header');

function setStatus(message, color = 'text-gray-400') {
  statusMsg.className = `text-sm ${color} mb-4`;
  statusMsg.textContent = message;
}

function switchTab(type) {
  currentTab = type;

  // タブのスタイル切り替え
  ['likes', 'stocks'].forEach(t => {
    const btn = document.getElementById(`tab-${t}`);
    if (t === type) {
      btn.className = 'px-6 py-3 text-sm font-medium border-b-2 border-blue-600 text-blue-600 transition-colors';
    } else {
      btn.className = 'px-6 py-3 text-sm font-medium border-b-2 border-transparent text-gray-500 hover:text-gray-700 transition-colors';
    }
  });

  countHeader.textContent = type === 'likes' ? 'いいね数' : 'ストック数';
  loadTab(type);
}

async function loadTab(type) {
  if (cache[type]) {
    renderData(cache[type]);
    return;
  }

  summaryArea.classList.add('hidden');
  resultsArea.classList.add('hidden');
  setStatus('取得中...', 'text-gray-400');

  try {
    const res = await fetch(`/api/ranking/${type}`);
    const data = await res.json();

    if (data.status === 'error') {
      setStatus(data.message, 'text-red-500');
      return;
    }

    cache[type] = data;
    renderData(data);
  } catch (e) {
    setStatus('通信エラーが発生しました', 'text-red-500');
  }
}

function renderData(data) {
  // サマリー
  document.getElementById('summary-total').textContent = data.summary.total_count.toLocaleString();
  document.getElementById('summary-avg').textContent = data.summary.avg_count.toLocaleString();
  document.getElementById('summary-max').textContent = data.summary.max_count.toLocaleString();
  summaryArea.classList.remove('hidden');

  // テーブル
  tbody.innerHTML = '';
  data.ranking.forEach(item => {
    const date = item.created_at.slice(0, 10);
    const medalClass = item.rank === 1 ? 'text-yellow-500 font-bold' :
                       item.rank === 2 ? 'text-gray-400 font-bold' :
                       item.rank === 3 ? 'text-amber-600 font-bold' : 'text-gray-500';
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-gray-50';
    tr.innerHTML = `
      <td class="px-4 py-2 ${medalClass} text-center">${item.rank}</td>
      <td class="px-4 py-2">${escapeHtml(item.title)}</td>
      <td class="px-4 py-2 text-right font-medium text-gray-700">${item.count.toLocaleString()}</td>
      <td class="px-4 py-2 text-gray-500">${date}</td>
      <td class="px-4 py-2">
        <a href="${escapeHtml(item.url)}" target="_blank"
           class="text-blue-500 hover:underline">開く</a>
      </td>
    `;
    tbody.appendChild(tr);
  });

  resultsArea.classList.remove('hidden');
  setStatus(`${data.total} 件取得しました`, 'text-green-600');
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

// 初期表示
loadTab('likes');
