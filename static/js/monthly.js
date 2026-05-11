async function loadMonthly() {
  const loading = document.getElementById("loading");
  const errorMsg = document.getElementById("error-msg");
  const canvas = document.getElementById("monthly-chart");

  try {
    const res = await fetch("/api/monthly");
    const data = await res.json();

    if (data.status !== "ok") {
      loading.classList.add("hidden");
      errorMsg.textContent = data.message;
      errorMsg.classList.remove("hidden");
      return;
    }

    document.getElementById("total-count").textContent = data.total;
    document.getElementById("active-months").textContent = data.monthly.length;
    const avg = data.monthly.length
      ? Math.round((data.total / data.monthly.length) * 10) / 10
      : 0;
    document.getElementById("avg-per-month").textContent = avg;

    const labels = data.monthly.map((d) => d.month);
    const counts = data.monthly.map((d) => d.count);

    loading.classList.add("hidden");
    canvas.classList.remove("hidden");

    new Chart(canvas, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "投稿数",
            data: counts,
            backgroundColor: "rgba(59, 130, 246, 0.7)",
            borderColor: "rgba(59, 130, 246, 1)",
            borderWidth: 1,
            borderRadius: 4,
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
  } catch (e) {
    loading.classList.add("hidden");
    errorMsg.textContent = `エラーが発生しました: ${e.message}`;
    errorMsg.classList.remove("hidden");
  }
}

loadMonthly();
