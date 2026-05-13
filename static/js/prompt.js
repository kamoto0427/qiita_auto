const generateBtn = document.getElementById('generate-btn');
const copyBtn = document.getElementById('copy-btn');
const statusMsg = document.getElementById('status-msg');
const resultsArea = document.getElementById('results-area');
const promptOutput = document.getElementById('prompt-output');

function setStatus(message, color = 'text-gray-500') {
  statusMsg.className = `text-sm ${color}`;
  statusMsg.textContent = message;
}

generateBtn.addEventListener('click', async () => {
  generateBtn.disabled = true;
  copyBtn.disabled = true;
  resultsArea.classList.add('hidden');
  promptOutput.value = '';
  setStatus('記事を取得中...', 'text-gray-400');

  try {
    const res = await fetch('/api/prompt');
    const data = await res.json();

    if (data.status === 'error') {
      setStatus(data.message, 'text-red-500');
      return;
    }

    promptOutput.value = data.prompt;
    resultsArea.classList.remove('hidden');
    copyBtn.disabled = false;
    setStatus('プロンプトを生成しました', 'text-green-600');
  } catch (e) {
    setStatus('通信エラーが発生しました', 'text-red-500');
  } finally {
    generateBtn.disabled = false;
  }
});

copyBtn.addEventListener('click', () => {
  navigator.clipboard.writeText(promptOutput.value).then(() => {
    const original = copyBtn.textContent;
    copyBtn.textContent = 'コピーしました！';
    setTimeout(() => { copyBtn.textContent = original; }, 1500);
  });
});
