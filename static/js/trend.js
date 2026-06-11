let trendChart = null;

async function loadTrend(keyword) {
  const loading = document.getElementById("loading");
  const errorMsg = document.getElementById("error-msg");
  const resultArea = document.getElementById("result-area");

  loading.classList.remove("hidden");
  errorMsg.classList.add("hidden");
  resultArea.classList.add("hidden");

  // プリセットボタンのアクティブ状態を更新
  document.querySelectorAll(".preset-btn").forEach((btn) => {
    if (btn.dataset.keyword === keyword) {
      btn.classList.add("bg-blue-600", "text-white", "border-blue-600");
    } else {
      btn.classList.remove("bg-blue-600", "text-white", "border-blue-600");
    }
  });

  try {
    const res = await fetch(`/api/trend?keyword=${encodeURIComponent(keyword)}`);
    const data = await res.json();

    loading.classList.add("hidden");

    if (data.status !== "ok") {
      errorMsg.textContent = data.message;
      errorMsg.classList.remove("hidden");
      return;
    }

    document.getElementById("total-count").textContent = data.total;
    document.getElementById("current-keyword").textContent = data.keyword;

    // 月別投稿推移グラフ
    const labels = data.monthly.map((d) => d.month);
    const counts = data.monthly.map((d) => d.count);
    const canvas = document.getElementById("trend-chart");

    if (trendChart) {
      trendChart.destroy();
    }
    trendChart = new Chart(canvas, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "投稿数",
            data: counts,
            borderColor: "rgba(59, 130, 246, 1)",
            backgroundColor: "rgba(59, 130, 246, 0.1)",
            borderWidth: 2,
            tension: 0.3,
            fill: true,
            pointRadius: 3,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.parsed.y} 件`,
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1 },
            title: { display: true, text: "投稿数" },
          },
          x: {
            title: { display: true, text: "年月" },
          },
        },
      },
    });

    // 共起タグ Top20
    const tagList = document.getElementById("tag-list");
    tagList.innerHTML = "";
    const maxCount = data.top_tags.length > 0 ? data.top_tags[0].count : 1;
    data.top_tags.forEach((t, i) => {
      const barWidth = Math.round((t.count / maxCount) * 100);
      const li = document.createElement("li");
      li.innerHTML = `
        <div class="flex items-center justify-between mb-0.5">
          <span class="text-gray-700">${i + 1}. ${t.tag}</span>
          <span class="text-gray-500 text-xs">${t.count}</span>
        </div>
        <div class="h-1.5 bg-gray-100 rounded-full mb-1">
          <div class="h-1.5 bg-blue-400 rounded-full" style="width: ${barWidth}%"></div>
        </div>`;
      tagList.appendChild(li);
    });

    // 人気記事 Top10
    const tbody = document.getElementById("articles-tbody");
    tbody.innerHTML = "";
    data.top_articles.forEach((a, i) => {
      const tr = document.createElement("tr");
      tr.className = "border-b border-gray-100 hover:bg-gray-50";
      tr.innerHTML = `
        <td class="py-2 pr-2 text-gray-400">${i + 1}</td>
        <td class="py-2 pr-2">
          <a href="${a.url}" target="_blank" rel="noopener noreferrer"
             class="text-blue-600 hover:underline line-clamp-2">${a.title}</a>
          <div class="text-gray-400 text-xs">${a.created_at}</div>
        </td>
        <td class="py-2 text-right font-medium">${a.likes_count}</td>`;
      tbody.appendChild(tr);
    });

    resultArea.classList.remove("hidden");
  } catch (e) {
    loading.classList.add("hidden");
    errorMsg.textContent = `エラーが発生しました: ${e.message}`;
    errorMsg.classList.remove("hidden");
  }
}

document.querySelectorAll(".preset-btn").forEach((btn) => {
  btn.addEventListener("click", () => loadTrend(btn.dataset.keyword));
});

// 初期表示は Claude Code
loadTrend("Claude Code");
