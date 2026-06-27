const generateBtn = document.getElementById('generate-btn');
const statusMsg   = document.getElementById('status-msg');
const resultsArea = document.getElementById('results-area');
const totalFetched   = document.getElementById('total-fetched');
const totalFiltered  = document.getElementById('total-filtered');
const markdownRaw    = document.getElementById('markdown-raw');
const markdownPreview = document.getElementById('markdown-preview');
const copyBtn     = document.getElementById('copy-btn');

// プルダウンで「その他」選択時にカスタム入力欄を表示
document.getElementById('query-select').addEventListener('change', (e) => {
  const custom = document.getElementById('query-custom');
  if (e.target.value === '__custom__') {
    custom.classList.remove('hidden');
    custom.focus();
  } else {
    custom.classList.add('hidden');
  }
});

generateBtn.addEventListener('click', async () => {
  const select    = document.getElementById('query-select');
  const query     = select.value === '__custom__'
    ? document.getElementById('query-custom').value.trim()
    : select.value;
  const dateFrom  = document.getElementById('date-from').value;
  const dateTo    = document.getElementById('date-to').value;
  const minLikes  = parseInt(document.getElementById('min-likes').value, 10) || 0;
  const minStocks = parseInt(document.getElementById('min-stocks').value, 10) || 0;

  if (!query) {
    statusMsg.textContent = 'キーワードまたはタグを入力してください。';
    statusMsg.className = 'text-sm text-red-500';
    return;
  }

  generateBtn.disabled = true;
  generateBtn.innerHTML = '<span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2 align-middle"></span>取得中...';
  statusMsg.textContent = '記事を取得中です。しばらくお待ちください...';
  statusMsg.className = 'text-sm text-gray-500';
  resultsArea.classList.add('hidden');

  try {
    const res = await fetch('/api/trend-article', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        date_from: dateFrom,
        date_to: dateTo,
        min_likes: minLikes,
        min_stocks: minStocks,
      }),
    });
    const data = await res.json();

    if (data.status !== 'ok') {
      statusMsg.textContent = `エラー: ${data.message}`;
      statusMsg.className = 'text-sm text-red-500';
      return;
    }

    totalFetched.textContent  = data.total_fetched;
    totalFiltered.textContent = data.total_filtered;
    markdownRaw.value = data.markdown;
    markdownPreview.innerHTML = marked.parse(data.markdown);
    markdownPreview.classList.add('markdown-body');

    resultsArea.classList.remove('hidden');
    switchTab('preview');

    statusMsg.textContent = '生成完了！';
    statusMsg.className = 'text-sm text-green-600';
  } catch (e) {
    statusMsg.textContent = `通信エラー: ${e.message}`;
    statusMsg.className = 'text-sm text-red-500';
  } finally {
    generateBtn.disabled = false;
    generateBtn.textContent = '記事を生成';
  }
});

copyBtn.addEventListener('click', () => {
  navigator.clipboard.writeText(markdownRaw.value).then(() => {
    const orig = copyBtn.textContent;
    copyBtn.textContent = 'コピーしました！';
    setTimeout(() => { copyBtn.textContent = orig; }, 2000);
  });
});

function switchTab(tab) {
  const preview = document.getElementById('pane-preview');
  const raw     = document.getElementById('pane-raw');
  const tabPreview = document.getElementById('tab-preview');
  const tabRaw     = document.getElementById('tab-raw');

  if (tab === 'preview') {
    preview.classList.remove('hidden');
    raw.classList.add('hidden');
    tabPreview.classList.add('border-blue-600', 'text-blue-600');
    tabPreview.classList.remove('border-transparent', 'text-gray-500');
    tabRaw.classList.remove('border-blue-600', 'text-blue-600');
    tabRaw.classList.add('border-transparent', 'text-gray-500');
  } else {
    raw.classList.remove('hidden');
    preview.classList.add('hidden');
    tabRaw.classList.add('border-blue-600', 'text-blue-600');
    tabRaw.classList.remove('border-transparent', 'text-gray-500');
    tabPreview.classList.remove('border-blue-600', 'text-blue-600');
    tabPreview.classList.add('border-transparent', 'text-gray-500');
  }
}
