/* LoopBench GitHub Pages — leaderboard UI */
(function () {
  "use strict";

  const TASK_ORDER = ["LB-CR-1", "LB-RS-1", "LB-MA-1", "LB-COMP-1"];

  const TASK_DEFS = {
    "LB-CR-1": {
      name: "Code repair",
      short: "Fix broken code when tests fail (SimEnv code-repair-v1).",
    },
    "LB-RS-1": {
      name: "Research synthesis",
      short: "Synthesize structured briefs under quality/cost evaluators.",
    },
    "LB-MA-1": {
      name: "Multi-agent debate",
      short: "Coordinate multiple agents under debate-style evaluation.",
    },
    "LB-COMP-1": {
      name: "Composed swarm",
      short: "Parallel loop branches merged into one forecast (LSS composition).",
    },
  };

  const METRIC_DEFS = {
    les: {
      label: "LES",
      hint: "Loop Effectiveness Score (observed) — composite 0–100 from eight categories: effectiveness, speed, cost, safety, robustness, scalability, adaptability, autonomy.",
    },
    success: {
      label: "Success@k",
      hint: "Fraction of task instances that reached the goal threshold across all fixed seeds (higher is better).",
    },
    cost: {
      label: "Cost",
      hint: "Mean estimated USD per episode from your LSS cost limits (lower is more efficient).",
    },
  };

  let data = null;
  let activeTask = "LB-CR-1";
  let activeMetric = "les";
  let sortKey = "les_display";
  let sortAsc = false;
  let chart = null;

  const COLORS = [
    "#18181b", "#3f3f46", "#52525b", "#2563eb", "#059669",
    "#0891b2", "#7c3aed", "#c026d3", "#ea580c", "#ca8a04",
  ];

  const CHART = { tick: "#71717a", grid: "#e4e4e7", title: "#71717a" };

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

  function renderHeroStats() {
    document.getElementById("stat-tasks").textContent = String(TASK_ORDER.length);
    document.getElementById("stat-subs").textContent = String(data.entry_count || 0);
    document.getElementById("stat-updated").textContent = data.updated || "—";
  }

  function renderGlossary() {
    const el = document.getElementById("glossary");
    const items = [
      ...Object.entries(METRIC_DEFS).map(([, m]) =>
        `<div><dt>${m.label}</dt><dd>${m.hint}</dd></div>`
      ),
      `<div><dt>Harness</dt><dd>native (LoopGym) or bridged: Cursor, LangGraph, CrewAI.</dd></div>`,
      `<div><dt>baseline / ext</dt><dd>Maintainer reference vs verified community submitter.</dd></div>`,
    ];
    el.innerHTML = items.join("");
  }

  function renderTaskTabs() {
    const wrap = document.getElementById("task-tabs");
    wrap.innerHTML = "";
    TASK_ORDER.forEach((id) => {
      const def = TASK_DEFS[id];
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "task-tab" + (id === activeTask ? " active" : "");
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-selected", id === activeTask ? "true" : "false");
      btn.setAttribute("title", def ? `${def.name}: ${def.short}` : id);
      btn.innerHTML = `<span class="tab-id">${id}</span><span class="tab-name">${def?.name || id}</span>`;
      btn.addEventListener("click", () => selectTask(id));
      wrap.appendChild(btn);
    });
  }

  function renderTaskCards() {
    const wrap = document.getElementById("task-cards");
    wrap.innerHTML = "";
    TASK_ORDER.forEach((id) => {
      const t = data.tasks[id];
      const def = TASK_DEFS[id];
      if (!t) return;
      const card = document.createElement("article");
      card.className = "task-card" + (id === activeTask ? " active" : "");
      card.innerHTML = `
        <div class="task-card-head">
          <span class="task-card-id">${id}</span>
          <span class="task-card-title">${def?.name || t.name}</span>
        </div>
        <p class="task-card-desc">${t.tagline || def?.short || ""}</p>`;
      card.addEventListener("click", () => selectTask(id));
      wrap.appendChild(card);
    });
  }

  function selectTask(id) {
    activeTask = id;
    const t = data.tasks[id];
    const def = TASK_DEFS[id];
    document.getElementById("task-tagline").textContent = t?.tagline || def?.short || "";
    renderTaskTabs();
    renderTaskCards();
    renderTable();
    renderChart();
  }

  function renderTable() {
    const body = document.getElementById("rank-body");
    const rows = sortedEntries();
    body.innerHTML = rows.length
      ? rows
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
          .join("")
      : `<tr><td colspan="8" style="text-align:center;color:var(--text-muted);padding:2rem">No entries for this task yet.</td></tr>`;
  }

  function baseChartOptions() {
    return {
      responsive: true,
      maintainAspectRatio: false,
      layout: { padding: { top: 8, right: 12, bottom: 4, left: 4 } },
      plugins: { legend: { display: false } },
    };
  }

  function renderChart() {
    const canvas = document.getElementById("efficiency-chart");
    const rows = entriesForTask().filter((r) => r.cost_usd_mean > 0 || r.les_display > 0);
    const caption = document.getElementById("chart-caption");
    const taskName = TASK_DEFS[activeTask]?.name || activeTask;

    if (chart) {
      chart.destroy();
      chart = null;
    }

    if (activeMetric === "cost") {
      caption.textContent = `Average cost per episode for ${taskName} (${activeTask}). Lower bars = more cost-efficient loops.`;
      chart = new Chart(canvas, {
        type: "bar",
        data: {
          labels: rows.map((r) => r.loop_name),
          datasets: [{
            label: "Avg cost",
            data: rows.map((r) => r.cost_usd_mean),
            backgroundColor: rows.map((_, i) => COLORS[i % COLORS.length] + "33"),
            borderColor: rows.map((_, i) => COLORS[i % COLORS.length]),
            borderWidth: 1,
          }],
        },
        options: {
          ...baseChartOptions(),
          scales: {
            x: {
              ticks: { color: CHART.tick, maxRotation: 45, minRotation: 0 },
              grid: { display: false },
              title: { display: false },
            },
            y: {
              ticks: { color: CHART.tick, callback: (v) => "$" + v },
              grid: { color: CHART.grid },
              title: { display: true, text: "Avg cost (USD)", color: CHART.title, padding: { bottom: 4 } },
            },
          },
        },
      });
      return;
    }

    const yLabel = activeMetric === "success" ? "Success@k (%)" : "LES";
    caption.textContent =
      activeMetric === "success"
        ? `${taskName}: success rate vs avg cost. Upper-left = high success, low cost.`
        : `${taskName}: LES vs avg cost. Upper-left = high score, low cost.`;

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
          backgroundColor: rows.map((_, i) => COLORS[i % COLORS.length] + "aa"),
          borderColor: rows.map((_, i) => COLORS[i % COLORS.length]),
          pointRadius: 7,
          pointHoverRadius: 9,
        }],
      },
      options: {
        ...baseChartOptions(),
        scales: {
          x: {
            type: "logarithmic",
            ticks: { color: CHART.tick },
            grid: { color: CHART.grid },
            title: {
              display: true,
              text: "Avg cost (USD, log scale)",
              color: CHART.title,
              padding: { top: 8 },
            },
          },
          y: {
            ticks: { color: CHART.tick },
            grid: { color: CHART.grid },
            title: {
              display: true,
              text: yLabel,
              color: CHART.title,
              padding: { bottom: 4 },
            },
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
      renderHeroStats();
      renderGlossary();
      renderTaskTabs();
      renderTaskCards();
      selectTask(activeTask);
      bindSort();
      bindMetrics();
    } catch (err) {
      document.getElementById("stat-subs").textContent = "error";
      console.error(err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
