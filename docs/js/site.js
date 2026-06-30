/* LoopBench GitHub Pages — generalist · suite · micro-task views */
(function () {
  "use strict";

  const TASK_COUNT = 19;

  const SUITE_ORDER = [
    { id: "generalist", label: "Generalist", short: "Grand composite — mean of four suite scores." },
    { id: "suite-repair", label: "Repair", short: "Code, tool, reflexion, DSPy repair." },
    { id: "suite-agent", label: "Agent", short: "Crews, graphs, debate, ToT, voting." },
    { id: "suite-knowledge", label: "Knowledge", short: "Synthesis, retrieval, bootstrap, autonomy." },
    { id: "suite-rigor", label: "Rigor", short: "Compose, nest, sim, HITL, memory." },
    { id: "tasks", label: "Micro-tasks", short: "Per-task rankings across 19 micro-tasks." },
  ];

  const TASK_ORDER = [
    "LB-CR-1", "LB-RS-1", "LB-MA-1", "LB-COMP-1",
    "LB-REACT-1", "LB-GRAPH-1", "LB-CREW-1", "LB-REFLEX-1", "LB-AUTO-1",
  ];

  const TASK_DEFS = {
    "LB-CR-1": { name: "Code repair", short: "Fix broken code when tests fail (SimEnv code-repair-v1)." },
    "LB-RS-1": { name: "Research synthesis", short: "Synthesize structured briefs under quality/cost evaluators." },
    "LB-MA-1": { name: "Multi-agent debate", short: "Coordinate multiple agents under debate-style evaluation." },
    "LB-COMP-1": { name: "Composed swarm", short: "Parallel loop branches merged into one forecast (LSS composition)." },
    "LB-REACT-1": { name: "ReAct tool loop", short: "Reason-act-observe under repair SimEnv." },
    "LB-GRAPH-1": { name: "State graph routing", short: "LangGraph-style parallel routing." },
    "LB-CREW-1": { name: "Sequential crew", short: "CrewAI-style role pipeline." },
    "LB-REFLEX-1": { name: "Reflexion memory", short: "Verbal RL with episodic memory." },
    "LB-AUTO-1": { name: "Long-horizon autonomy", short: "Plan-execute under synthesis env." },
  };

  const METRIC_DEFS = {
    les: {
      label: "LES",
      hint: "Loop Effectiveness Score (observed) — composite 0–100 from eight categories.",
    },
    success: {
      label: "Success@k",
      hint: "Fraction of task instances that reached the goal threshold across all fixed seeds.",
    },
    cost: {
      label: "Cost",
      hint: "Mean estimated USD per episode from your LSS cost limits (micro-task view only).",
    },
  };

  let data = null;
  let viewMode = "generalist";
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
    if (v == null || v <= 0) return "—";
    return "$" + Number(v).toFixed(2);
  }

  function fmtPct(v) {
    if (v == null) return "—";
    return Math.round(Number(v) * 100) + "%";
  }

  function loopNameFromSpec(specPath) {
    if (!specPath) return "unknown";
    const base = specPath.replace(/\/$/, "").split("/").pop();
    return base.replace(/\.ya?ml$/i, "");
  }

  function isTaskView() {
    return viewMode === "tasks";
  }

  function currentRows() {
    if (!data) return [];

    if (viewMode === "generalist") {
      return (data.generalist || []).map(normalizeGeneralistRow);
    }

    if (viewMode.startsWith("suite-") && data.suites && data.suites[viewMode]) {
      return (data.suites[viewMode].entries || []).map((row) =>
        normalizeSuiteRow(row, data.suites[viewMode].label)
      );
    }

    if (isTaskView() && data.tasks && data.tasks[activeTask]) {
      return (data.tasks[activeTask].entries || []).map(normalizeTaskRow);
    }

    return [];
  }

  function normalizeGeneralistRow(row) {
    return {
      loop_name: loopNameFromSpec(row.spec_path),
      submitter: row.submitter,
      les_display: Number(row.les_display ?? row.les_observed * 100),
      les_observed: Number(row.les_observed ?? 0),
      success_at_k: null,
      cost_usd_mean: null,
      harness: row.harness || "native",
      spec_path: row.spec_path,
      repro_command: row.repro_command || "",
      is_external: Boolean(row.is_external),
      primary_suite: row.primary_suite,
    };
  }

  function normalizeSuiteRow(row, suiteLabel) {
    return {
      loop_name: loopNameFromSpec(row.spec_path),
      submitter: row.submitter,
      les_display: Number(row.les_display ?? row.les_observed * 100),
      les_observed: Number(row.les_observed ?? 0),
      success_at_k: null,
      cost_usd_mean: null,
      harness: row.harness || "native",
      spec_path: row.spec_path,
      repro_command: row.repro_command || "",
      is_external: Boolean(row.is_external),
      primary_suite: suiteLabel,
    };
  }

  function normalizeTaskRow(row) {
    return {
      loop_name: row.loop_name || loopNameFromSpec(row.spec_path),
      submitter: row.submitter,
      les_display: Number(row.les_display ?? 0),
      les_observed: Number(row.les_observed ?? 0),
      success_at_k: row.success_at_k,
      cost_usd_mean: row.cost_usd_mean,
      harness: row.harness || "native",
      spec_path: row.spec_path,
      repro_command: row.repro_command || "",
      is_external: Boolean(row.is_external),
      primary_suite: null,
    };
  }

  function sortedEntries() {
    const rows = currentRows();
    rows.sort((a, b) => {
      const av = a[sortKey] ?? 0;
      const bv = b[sortKey] ?? 0;
      return sortAsc ? av - bv : bv - av;
    });
    return rows;
  }

  function viewLabel() {
    const suite = SUITE_ORDER.find((s) => s.id === viewMode);
    if (suite) return suite.label;
    if (isTaskView()) {
      const def = TASK_DEFS[activeTask] || (data.tasks && data.tasks[activeTask]);
      return def?.name || activeTask;
    }
    return viewMode;
  }

  function viewTagline() {
    const suite = SUITE_ORDER.find((s) => s.id === viewMode);
    if (suite) return suite.short;
    if (isTaskView() && data.tasks && data.tasks[activeTask]) {
      return data.tasks[activeTask].tagline || TASK_DEFS[activeTask]?.short || "";
    }
    return "";
  }

  function renderHeroStats() {
    document.getElementById("stat-tasks").textContent = String(TASK_COUNT);
    document.getElementById("stat-subs").textContent = String(data.entry_count || 0);
    document.getElementById("stat-updated").textContent = data.updated || "—";
  }

  function renderGlossary() {
    const el = document.getElementById("glossary");
    const items = [
      ...Object.entries(METRIC_DEFS).map(([, m]) =>
        `<div><dt>${m.label}</dt><dd>${m.hint}</dd></div>`
      ),
      `<div><dt>Generalist</dt><dd>Grand composite — mean of four suite LES scores (primary rank).</dd></div>`,
      `<div><dt>Harness</dt><dd>native (LoopGym) or bridged: Cursor, LangGraph, CrewAI.</dd></div>`,
      `<div><dt>baseline / ext</dt><dd>Maintainer reference vs verified community submitter.</dd></div>`,
    ];
    el.innerHTML = items.join("");
  }

  function renderSuiteTabs() {
    const wrap = document.getElementById("suite-tabs");
    wrap.innerHTML = "";
    SUITE_ORDER.forEach((suite) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "task-tab" + (suite.id === viewMode ? " active" : "");
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-selected", suite.id === viewMode ? "true" : "false");
      btn.setAttribute("title", suite.short);
      btn.innerHTML = `<span class="tab-id">${suite.label}</span>`;
      btn.addEventListener("click", () => selectView(suite.id));
      wrap.appendChild(btn);
    });
  }

  function renderTaskTabs() {
    const wrap = document.getElementById("task-tabs");
    wrap.innerHTML = "";
    const taskIds = data.tasks ? Object.keys(data.tasks) : TASK_ORDER;
    const order = TASK_ORDER.filter((id) => taskIds.includes(id));
    const rest = taskIds.filter((id) => !order.includes(id)).sort();
    [...order, ...rest].forEach((id) => {
      const def = TASK_DEFS[id] || (data.tasks[id] ? { name: data.tasks[id].name } : null);
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "task-tab" + (id === activeTask ? " active" : "");
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-selected", id === activeTask ? "true" : "false");
      btn.setAttribute("title", def ? `${def.name}` : id);
      btn.innerHTML = `<span class="tab-id">${id}</span><span class="tab-name">${def?.name || id}</span>`;
      btn.addEventListener("click", () => selectTask(id));
      wrap.appendChild(btn);
    });
  }

  function renderTaskCards() {
    const wrap = document.getElementById("task-cards");
    wrap.innerHTML = "";
    if (!isTaskView()) {
      wrap.innerHTML = `<p class="task-cards-hint">Switch to <strong>Micro-tasks</strong> to browse all ${TASK_COUNT} task cards.</p>`;
      return;
    }
    const taskIds = data.tasks ? Object.keys(data.tasks) : TASK_ORDER;
    taskIds.forEach((id) => {
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

  function updateControlsVisibility() {
    const taskRow = document.getElementById("task-tabs-row");
    taskRow.style.display = isTaskView() ? "" : "none";
  }

  function selectView(mode) {
    viewMode = mode;
    sortKey = "les_display";
    sortAsc = false;
    if (activeMetric === "success" && !isTaskView()) {
      activeMetric = "les";
      document.querySelectorAll(".metric-btn").forEach((b) => {
        b.classList.toggle("active", b.dataset.metric === "les");
      });
    }
    document.querySelectorAll(".metric-btn[data-metric='success']").forEach((b) => {
      b.disabled = !isTaskView();
      b.title = isTaskView() ? "Success@k" : "Success@k (micro-task view only)";
    });
    document.getElementById("task-tagline").textContent = viewTagline();
    updateControlsVisibility();
    renderSuiteTabs();
    renderTaskTabs();
    renderTaskCards();
    renderTable();
    renderChart();
  }

  function selectTask(id) {
    if (!isTaskView()) {
      viewMode = "tasks";
    }
    activeTask = id;
    document.getElementById("task-tagline").textContent = viewTagline();
    updateControlsVisibility();
    renderSuiteTabs();
    renderTaskTabs();
    renderTaskCards();
    renderTable();
    renderChart();
  }

  function externalBadge(row) {
    return row.is_external
      ? '<span class="badge external">ext</span>'
      : '<span class="badge internal">baseline</span>';
  }

  function reproCell(row) {
    if (!row.repro_command) return "—";
    const cmd = row.repro_command.replace(/"/g, "&quot;");
    return `<button type="button" class="repro-btn" data-repro="${cmd}" title="Copy reproduction command">copy</button>`;
  }

  function bindReproButtons() {
    document.querySelectorAll(".repro-btn").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const cmd = btn.getAttribute("data-repro");
        try {
          await navigator.clipboard.writeText(cmd);
          const prev = btn.textContent;
          btn.textContent = "copied";
          setTimeout(() => { btn.textContent = prev; }, 1200);
        } catch {
          btn.textContent = "err";
        }
      });
    });
  }

  function renderTable() {
    const body = document.getElementById("rank-body");
    const rows = sortedEntries();
    const emptyMsg = isTaskView()
      ? `No entries for ${activeTask} yet.`
      : `No entries for ${viewLabel()} yet.`;

    body.innerHTML = rows.length
      ? rows
          .map((row, i) => {
            const spec = row.spec_path
              ? `<a class="spec-link" href="${row.spec_path}" target="_blank" rel="noopener">view</a>`
              : "—";
            return `<tr>
          <td class="rank-num">${i + 1}</td>
          <td><span class="loop-name">${row.loop_name}</span></td>
          <td><span class="submitter">${row.submitter}</span>${externalBadge(row)}</td>
          <td class="les-cell">${row.les_display.toFixed(1)}</td>
          <td>${fmtPct(row.success_at_k)}</td>
          <td>${fmtCost(row.cost_usd_mean)}</td>
          <td>${row.harness || "native"}</td>
          <td>${spec}</td>
          <td>${reproCell(row)}</td>
        </tr>`;
          })
          .join("")
      : `<tr><td colspan="9" style="text-align:center;color:var(--text-muted);padding:2rem">${emptyMsg}</td></tr>`;

    bindReproButtons();
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
    const rows = currentRows();
    const caption = document.getElementById("chart-caption");
    const label = viewLabel();

    if (chart) {
      chart.destroy();
      chart = null;
    }

    if (!rows.length) {
      caption.textContent = `No data for ${label}.`;
      return;
    }

    if (activeMetric === "cost" && isTaskView()) {
      const costRows = rows.filter((r) => r.cost_usd_mean > 0 || r.les_display > 0);
      caption.textContent = `Average cost per episode for ${label} (${activeTask}). Lower bars = more cost-efficient loops.`;
      chart = new Chart(canvas, {
        type: "bar",
        data: {
          labels: costRows.map((r) => r.loop_name),
          datasets: [{
            label: "Avg cost",
            data: costRows.map((r) => r.cost_usd_mean || 0),
            backgroundColor: costRows.map((_, i) => COLORS[i % COLORS.length] + "33"),
            borderColor: costRows.map((_, i) => COLORS[i % COLORS.length]),
            borderWidth: 1,
          }],
        },
        options: {
          ...baseChartOptions(),
          scales: {
            x: {
              ticks: { color: CHART.tick, maxRotation: 45, minRotation: 0 },
              grid: { display: false },
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

    if (!isTaskView() || activeMetric === "les") {
      const barRows = rows.filter((r) => r.les_display > 0);
      const title = isTaskView() ? `${label} (${activeTask})` : label;
      caption.textContent = isTaskView() && barRows.some((r) => r.cost_usd_mean > 0)
        ? `${title}: LES vs avg cost. Upper-left = high score, low cost.`
        : `${title}: LES ranking (higher is better).`;

      if (isTaskView() && barRows.some((r) => r.cost_usd_mean > 0)) {
        chart = new Chart(canvas, {
          type: "scatter",
          data: {
            datasets: [{
              label: "LES",
              data: barRows.map((r) => ({
                x: r.cost_usd_mean || 0.01,
                y: r.les_display,
                label: r.loop_name,
              })),
              backgroundColor: barRows.map((_, i) => COLORS[i % COLORS.length] + "aa"),
              borderColor: barRows.map((_, i) => COLORS[i % COLORS.length]),
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
                title: { display: true, text: "Avg cost (USD, log scale)", color: CHART.title, padding: { top: 8 } },
              },
              y: {
                ticks: { color: CHART.tick },
                grid: { color: CHART.grid },
                title: { display: true, text: "LES", color: CHART.title, padding: { bottom: 4 } },
              },
            },
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label(ctx) {
                    const pt = ctx.raw;
                    return `${pt.label}: LES ${pt.y.toFixed(1)}, cost ${fmtCost(pt.x)}`;
                  },
                },
              },
            },
          },
        });
        return;
      }

      chart = new Chart(canvas, {
        type: "bar",
        data: {
          labels: barRows.map((r) => r.loop_name),
          datasets: [{
            label: "LES",
            data: barRows.map((r) => r.les_display),
            backgroundColor: barRows.map((_, i) => COLORS[i % COLORS.length] + "33"),
            borderColor: barRows.map((_, i) => COLORS[i % COLORS.length]),
            borderWidth: 1,
          }],
        },
        options: {
          ...baseChartOptions(),
          scales: {
            x: {
              ticks: { color: CHART.tick, maxRotation: 45, minRotation: 0 },
              grid: { display: false },
            },
            y: {
              ticks: { color: CHART.tick },
              grid: { color: CHART.grid },
              title: { display: true, text: "LES", color: CHART.title, padding: { bottom: 4 } },
            },
          },
        },
      });
      return;
    }

    const yLabel = "Success@k (%)";
    caption.textContent = `${label} (${activeTask}): success rate vs avg cost.`;
    chart = new Chart(canvas, {
      type: "scatter",
      data: {
        datasets: [{
          label: yLabel,
          data: rows.map((r) => ({
            x: r.cost_usd_mean || 0.01,
            y: (r.success_at_k || 0) * 100,
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
            title: { display: true, text: "Avg cost (USD, log scale)", color: CHART.title, padding: { top: 8 } },
          },
          y: {
            ticks: { color: CHART.tick },
            grid: { color: CHART.grid },
            title: { display: true, text: yLabel, color: CHART.title, padding: { bottom: 4 } },
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
        if (btn.disabled) return;
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
      renderSuiteTabs();
      renderTaskTabs();
      updateControlsVisibility();
      document.querySelectorAll(".metric-btn[data-metric='success']").forEach((b) => {
        b.disabled = !isTaskView();
      });
      renderTaskCards();
      renderTable();
      renderChart();
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
