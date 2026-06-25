/* LoopBench GitHub Pages — leaderboard UI */
(function () {
  "use strict";

  const TASK_ORDER = ["LB-CR-1", "LB-RS-1", "LB-MA-1", "LB-COMP-1"];
  let data = null;
  let activeTask = "LB-CR-1";
  let activeMetric = "les";
  let sortKey = "les_display";
  let sortAsc = false;
  let chart = null;

  const COLORS = [
    "#8b5cf6", "#60a5fa", "#34d399", "#f472b6", "#fbbf24", "#fb7185", "#a78bfa", "#2dd4bf",
  ];

  async function loadData() {
    const res = await fetch("data/leaderboard.json");
    if (!res.ok) throw new Error("Failed to load leaderboard.json");
    return res.json();
  }

  function fmtCost(v) {
    if (!v || v <= 0) return "—";
    return "$" + v.toFixed(2);
  }

  function fmtPct(v) {
    return Math.round(v * 100) + "%";
  }

  function entriesForTask() {
    if (!data || !data.tasks[activeTask]) return [];
    return [...data.tasks[activeTask].entries];
  }

  function sortedEntries() {
    const rows = entriesForTask();
    rows.sort((a, b) => {
      const av = a[sortKey] ?? 0;
      const bv = b[sortKey] ?? 0;
      return sortAsc ? av - bv : bv - av;
    });
    return rows;
  }

  function renderHero() {
    const el = document.getElementById("hero-meta");
    const total = data.entry_count || 0;
    const updated = data.updated || "unknown";
    el.textContent = `${TASK_ORDER.length} tasks · ${total} submissions · updated ${updated}`;
  }

  function renderTaskTabs() {
    const wrap = document.getElementById("task-tabs");
    wrap.innerHTML = "";
    TASK_ORDER.forEach((id) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "task-tab" + (id === activeTask ? " active" : "");
      btn.textContent = id;
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-selected", id === activeTask ? "true" : "false");
      btn.addEventListener("click", () => selectTask(id));
      wrap.appendChild(btn);
    });
  }

  function renderTaskCards() {
    const wrap = document.getElementById("task-cards");
    wrap.innerHTML = "";
    TASK_ORDER.forEach((id) => {
      const t = data.tasks[id];
      if (!t) return;
      const card = document.createElement("article");
      card.className = "task-card" + (id === activeTask ? " active" : "");
      card.innerHTML = `
        <div class="task-card-id">${id}</div>
        <h3>${t.name}</h3>
        <p>${t.tagline}</p>
      `;
      card.addEventListener("click", () => selectTask(id));
      wrap.appendChild(card);
    });
  }

  function selectTask(id) {
    activeTask = id;
    const t = data.tasks[id];
    document.getElementById("task-tagline").textContent = t ? t.tagline : "";
    renderTaskTabs();
    renderTaskCards();
    renderTable();
    renderChart();
  }

  function renderTable() {
    const body = document.getElementById("rank-body");
    const rows = sortedEntries();
    body.innerHTML = rows
      .map((row, i) => {
        const badge = row.is_external
          ? '<span class="badge external">ext</span>'
          : '<span class="badge internal">baseline</span>';
        const spec = row.spec_path
          ? `<a class="spec-link" href="${row.spec_path}" target="_blank" rel="noopener">view</a>`
          : "—";
        return `<tr>
          <td class="rank-num">${i + 1}</td>
          <td><span class="loop-name">${row.loop_name}</span></td>
          <td><span class="submitter">${row.submitter}</span>${badge}</td>
          <td class="les-cell">${row.les_display.toFixed(1)}</td>
          <td>${fmtPct(row.success_at_k)}</td>
          <td>${fmtCost(row.cost_usd_mean)}</td>
          <td>${row.harness || "native"}</td>
          <td>${spec}</td>
        </tr>`;
      })
      .join("");
  }

  function renderChart() {
    const canvas = document.getElementById("efficiency-chart");
    const rows = entriesForTask().filter((r) => r.cost_usd_mean > 0 || r.les_display > 0);
    const caption = document.getElementById("chart-caption");

    const metricLabels = {
      les: "LES (higher is better)",
      success: "Success@k (higher is better)",
      cost: "Avg cost USD (lower is better)",
    };
    caption.textContent =
      activeMetric === "cost"
        ? "Horizontal bars — avg cost per task (lower is more efficient)."
        : `${metricLabels[activeMetric]} vs submitter — ${data.tasks[activeTask]?.name || activeTask}`;

    if (chart) {
      chart.destroy();
      chart = null;
    }

    if (activeMetric === "cost") {
      chart = new Chart(canvas, {
        type: "bar",
        data: {
          labels: rows.map((r) => r.loop_name),
          datasets: [{
            label: "Avg cost",
            data: rows.map((r) => r.cost_usd_mean),
            backgroundColor: rows.map((_, i) => COLORS[i % COLORS.length] + "99"),
            borderColor: rows.map((_, i) => COLORS[i % COLORS.length]),
            borderWidth: 1,
          }],
        },
        options: chartOptions(false),
      });
      return;
    }

    const yKey = activeMetric === "success" ? "success_at_k" : "les_display";
    const yLabel = activeMetric === "success" ? "Success@k" : "LES";

    chart = new Chart(canvas, {
      type: "scatter",
      data: {
        datasets: [{
          label: yLabel,
          data: rows.map((r) => ({
            x: r.cost_usd_mean || 0.01,
            y: activeMetric === "success" ? r.success_at_k * 100 : r.les_display,
            label: r.loop_name,
          })),
          backgroundColor: rows.map((_, i) => COLORS[i % COLORS.length] + "cc"),
          borderColor: rows.map((_, i) => COLORS[i % COLORS.length]),
          pointRadius: 8,
          pointHoverRadius: 10,
        }],
      },
      options: {
        ...chartOptions(true),
        scales: {
          x: {
            type: "logarithmic",
            title: { display: true, text: "Avg cost (log scale)", color: "#8b92a8" },
            ticks: { color: "#8b92a8" },
            grid: { color: "rgba(255,255,255,0.06)" },
          },
          y: {
            title: { display: true, text: yLabel, color: "#8b92a8" },
            ticks: { color: "#8b92a8" },
            grid: { color: "rgba(255,255,255,0.06)" },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label(ctx) {
                const pt = ctx.raw;
                return `${pt.label}: ${yLabel} ${pt.y.toFixed(1)}, cost ${fmtCost(pt.x)}`;
              },
            },
          },
        },
      },
    });
  }

  function chartOptions(indexAxis) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: indexAxis ? "y" : undefined,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          ticks: { color: "#8b92a8" },
          grid: { color: "rgba(255,255,255,0.06)" },
        },
        y: {
          ticks: { color: "#8b92a8" },
          grid: { color: "rgba(255,255,255,0.06)" },
        },
      },
    };
  }

  function bindSort() {
    document.querySelectorAll(".rank-table th[data-sort]").forEach((th) => {
      th.addEventListener("click", () => {
        const key = th.dataset.sort;
        if (sortKey === key) sortAsc = !sortAsc;
        else {
          sortKey = key;
          sortAsc = false;
        }
        renderTable();
      });
    });
  }

  function bindMetrics() {
    document.querySelectorAll(".metric-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".metric-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        activeMetric = btn.dataset.metric;
        renderChart();
      });
    });
  }

  async function init() {
    try {
      data = await loadData();
      renderHero();
      renderTaskTabs();
      renderTaskCards();
      selectTask(activeTask);
      bindSort();
      bindMetrics();
    } catch (err) {
      document.getElementById("hero-meta").textContent = "Could not load leaderboard data.";
      console.error(err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
