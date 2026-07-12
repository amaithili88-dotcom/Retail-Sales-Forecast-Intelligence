(() => {
  const TOTAL_KEY = "__all__";
  const payload = window.__PAYLOAD__ || {};

  const categorySelect = document.getElementById("categorySelect");
  const horizonRange = document.getElementById("horizonRange");
  const horizonValue = document.getElementById("horizonValue");
  const forecastMonthEl = document.getElementById("forecastMonth");
  const predictedSalesEl = document.getElementById("predictedSales");
  const growthVsPriorEl = document.getElementById("growthVsPrior");
  const categoryAccuracyEl = document.getElementById("categoryAccuracy");
  const accuracyLabelEl = document.getElementById("accuracyLabel");
  const bestModelNameEl = document.getElementById("bestModelName");
  const scopeTotalBtn = document.getElementById("scopeTotalBtn");
  const scopeCategoryBtn = document.getElementById("scopeCategoryBtn");
  const themeToggle = document.getElementById("themeToggle");

  let currentCategory = TOTAL_KEY;
  let currentHorizon = Number(horizonRange?.value || 2);

  const currency = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });

  function fmtNumber(v) {
    if (v === null || v === undefined || Number.isNaN(v)) return "-";
    return currency.format(v);
  }

  function fmtPct(v) {
    if (v === null || v === undefined || Number.isNaN(v)) return "-";
    return `${v.toFixed(2)}%`;
  }

  function computeAccuracy(monthlyRows) {
    if (!monthlyRows || monthlyRows.length === 0) return null;
    let absErr = 0;
    let absActual = 0;
    monthlyRows.forEach((r) => {
      absErr += Math.abs((r.actual ?? 0) - (r.predicted ?? 0));
      absActual += Math.abs(r.actual ?? 0);
    });
    if (absActual === 0) return null;
    const wmape = (absErr / absActual) * 100;
    return Math.max(0, Math.min(100, 100 - wmape));
  }

  function isDarkTheme() {
    return document.documentElement.getAttribute("data-theme") === "dark";
  }

  function chartColors() {
    if (isDarkTheme()) {
      return {
        font: "#dbe7ff",
        grid: "#2d3f63",
        actual: "#3ed6c8",
        predicted: "#8eb4ff",
        future: "#f8c36f",
        bar: "#8eb4ff",
        line: "#3ed6c8",
      };
    }

    return {
      font: "#0f172a",
      grid: "#e4ebf6",
      actual: "#14b8a6",
      predicted: "#0b5fff",
      future: "#f59e0b",
      bar: "#0b5fff",
      line: "#14b8a6",
    };
  }

  function plotTrend(data, horizon) {
    const colors = chartColors();
    const history = data.history || [];
    const weeklyFuture = data.future_weekly || [];

    const traces = [
      {
        x: history.map((r) => r.date),
        y: history.map((r) => r.actual),
        type: "scatter",
        mode: "lines",
        name: "Actual",
        line: { color: colors.actual, width: 2.4 },
      },
      {
        x: history.map((r) => r.date),
        y: history.map((r) => r.predicted),
        type: "scatter",
        mode: "lines",
        name: "Predicted",
        line: { color: colors.predicted, width: 2.4 },
      },
    ];

    if (weeklyFuture.length) {
      traces.push({
        x: weeklyFuture.map((r) => r.date),
        y: weeklyFuture.map((r) => r.prediction),
        type: "scatter",
        mode: "lines+markers",
        name: `Future (${horizon}m)`,
        line: { color: colors.future, width: 2.2, dash: "dash" },
        marker: { size: 5 },
      });
    }

    const layout = {
      margin: { l: 58, r: 18, t: 10, b: 42 },
      paper_bgcolor: "transparent",
      plot_bgcolor: "transparent",
      font: { family: "IBM Plex Sans, sans-serif", color: colors.font, size: 12 },
      xaxis: { gridcolor: colors.grid },
      yaxis: { gridcolor: colors.grid },
      legend: { orientation: "h", y: 1.13 },
    };

    Plotly.newPlot("trendChart", traces, layout, { displayModeBar: false, responsive: true });
  }

  function plotModelComparison() {
    const colors = chartColors();
    const rows = payload.comparison || [];
    const x = rows.map((r) => r.Model);
    const mae = rows.map((r) => r.MAE);
    const wmape = rows.map((r) => r.WMAPE);

    const traces = [
      {
        x,
        y: mae,
        type: "bar",
        name: "MAE",
        marker: { color: colors.bar },
      },
      {
        x,
        y: wmape,
        type: "scatter",
        mode: "lines+markers",
        name: "WMAPE (%)",
        yaxis: "y2",
        line: { color: colors.line, width: 3 },
      },
    ];

    const layout = {
      margin: { l: 58, r: 52, t: 8, b: 72 },
      paper_bgcolor: "transparent",
      plot_bgcolor: "transparent",
      font: { family: "IBM Plex Sans, sans-serif", color: colors.font, size: 12 },
      xaxis: { tickangle: -16, gridcolor: colors.grid },
      yaxis: { title: "MAE", gridcolor: colors.grid },
      yaxis2: {
        title: "WMAPE %",
        overlaying: "y",
        side: "right",
      },
      legend: { orientation: "h", y: 1.12 },
    };

    Plotly.newPlot("modelChart", traces, layout, { displayModeBar: false, responsive: true });
  }

  function renderTopTable() {
    const tbody = document.querySelector("#topTable tbody");
    tbody.innerHTML = "";

    const rows = [];
    Object.entries(payload.byCategory || {}).forEach(([cat, data]) => {
      const nextMonth = (data.future_monthly || []).find((r) => r.month_index === 1);
      if (!nextMonth) return;
      rows.push({
        category: cat,
        predicted: nextMonth.predicted_sales,
        growth: nextMonth.growth_vs_last_month_pct,
      });
    });

    rows.sort((a, b) => (b.predicted || 0) - (a.predicted || 0));
    rows.slice(0, 10).forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.category}</td>
        <td>${fmtNumber(row.predicted)}</td>
        <td>${fmtPct(row.growth)}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function renderFutureTable(futureMonthly) {
    const tbody = document.querySelector("#futureTable tbody");
    tbody.innerHTML = "";

    futureMonthly.forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.forecast_month || "-"}</td>
        <td>${fmtNumber(row.predicted_sales)}</td>
        <td>${fmtPct(row.growth_vs_previous_month_pct ?? row.growth_vs_last_month_pct)}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function sumBy(items, keyName, valueName) {
    const map = new Map();
    items.forEach((item) => {
      const key = item[keyName];
      const value = Number(item[valueName] ?? 0);
      map.set(key, (map.get(key) || 0) + value);
    });
    return map;
  }

  function buildTotalView() {
    const byCategory = payload.byCategory || {};
    const categories = Object.keys(byCategory);

    const allHistory = [];
    const allWeeklyFuture = [];
    const allMonthlyPredicted = [];
    const allLastMonthSales = [];

    categories.forEach((category) => {
      const data = byCategory[category] || {};
      (data.history || []).forEach((row) => {
        allHistory.push({
          date: row.date,
          actual: Number(row.actual ?? 0),
          predicted: Number(row.predicted ?? 0),
        });
      });

      (data.future_weekly || []).forEach((row) => {
        allWeeklyFuture.push({
          date: row.date,
          prediction: Number(row.prediction ?? 0),
        });
      });

      (data.future_monthly || []).forEach((row) => {
        allMonthlyPredicted.push({
          month_index: Number(row.month_index ?? 0),
          forecast_month: row.forecast_month,
          predicted_sales: Number(row.predicted_sales ?? 0),
        });
        if (Number(row.month_index) === 1 && row.last_month_sales !== null && row.last_month_sales !== undefined) {
          allLastMonthSales.push(Number(row.last_month_sales));
        }
      });
    });

    const historyActual = sumBy(allHistory, "date", "actual");
    const historyPredicted = sumBy(allHistory, "date", "predicted");
    const historyDates = Array.from(new Set([...historyActual.keys(), ...historyPredicted.keys()])).sort();
    const history = historyDates.map((date) => ({
      date,
      actual: historyActual.get(date) || 0,
      predicted: historyPredicted.get(date) || 0,
    }));

    const weeklyMap = sumBy(allWeeklyFuture, "date", "prediction");
    const future_weekly = Array.from(weeklyMap.entries())
      .sort(([a], [b]) => (a < b ? -1 : 1))
      .map(([date, prediction]) => ({ date, prediction }));

    const monthlyMap = new Map();
    allMonthlyPredicted.forEach((row) => {
      const idx = row.month_index;
      const existing = monthlyMap.get(idx) || {
        month_index: idx,
        forecast_month: row.forecast_month,
        predicted_sales: 0,
      };
      existing.predicted_sales += row.predicted_sales;
      if (!existing.forecast_month && row.forecast_month) {
        existing.forecast_month = row.forecast_month;
      }
      monthlyMap.set(idx, existing);
    });

    const future_monthly = Array.from(monthlyMap.values()).sort((a, b) => a.month_index - b.month_index);
    const totalLastMonthSales = allLastMonthSales.reduce((sum, v) => sum + v, 0);

    future_monthly.forEach((row, index) => {
      const prev = index === 0 ? totalLastMonthSales : future_monthly[index - 1].predicted_sales;
      row.last_month_sales = index === 0 ? totalLastMonthSales : future_monthly[index - 1].predicted_sales;
      row.growth_vs_previous_month_pct = prev ? ((row.predicted_sales - prev) / prev) * 100 : null;
      row.growth_vs_last_month_pct = row.growth_vs_previous_month_pct;
    });

    const monthly = history.map((row) => ({
      date: row.date,
      actual: row.actual,
      predicted: row.predicted,
    }));

    return { history, future_weekly, future_monthly, monthly };
  }

  function renderCategory(category, horizon) {
    const data = category === TOTAL_KEY ? buildTotalView() : (payload.byCategory || {})[category];
    if (!data) return;

    const monthly = data.monthly || [];
    const futureMonthly = (data.future_monthly || []).filter((m) => m.month_index <= horizon);
    const latestFuture = futureMonthly.length ? futureMonthly[futureMonthly.length - 1] : null;

    forecastMonthEl.textContent = latestFuture ? latestFuture.forecast_month : "-";
    predictedSalesEl.textContent = latestFuture ? fmtNumber(latestFuture.predicted_sales) : "-";
    growthVsPriorEl.textContent = latestFuture
      ? fmtPct(latestFuture.growth_vs_previous_month_pct ?? latestFuture.growth_vs_last_month_pct)
      : "-";
    categoryAccuracyEl.textContent = fmtPct(computeAccuracy(monthly));
    if (accuracyLabelEl) {
      accuracyLabelEl.textContent = category === TOTAL_KEY ? "Overall Accuracy" : "Category Accuracy";
    }

    plotTrend(data, horizon);
    renderFutureTable(futureMonthly);
  }

  function setScope(scope, horizon) {
    const isTotal = scope === "total";

    if (scopeTotalBtn && scopeCategoryBtn) {
      scopeTotalBtn.classList.toggle("active", isTotal);
      scopeCategoryBtn.classList.toggle("active", !isTotal);
    }

    if (isTotal) {
      categorySelect.value = TOTAL_KEY;
      categorySelect.disabled = true;
      currentCategory = TOTAL_KEY;
      currentHorizon = horizon;
      renderCategory(TOTAL_KEY, horizon);
      return;
    }

    categorySelect.disabled = false;
    if (!categorySelect.value || categorySelect.value === TOTAL_KEY) {
      const firstCategory = payload.categories?.[0];
      if (firstCategory) {
        categorySelect.value = firstCategory;
      }
    }
    currentCategory = categorySelect.value;
    currentHorizon = horizon;
    renderCategory(categorySelect.value, horizon);
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    if (themeToggle) {
      themeToggle.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
    }
    plotModelComparison();
    renderCategory(currentCategory, currentHorizon);
  }

  function init() {
    if (!payload || !payload.categories || !payload.categories.length) return;

    bestModelNameEl.textContent = payload.bestModel?.name || "-";

    const allOption = document.createElement("option");
    allOption.value = TOTAL_KEY;
    allOption.textContent = "All Categories (Total)";
    categorySelect.appendChild(allOption);

    payload.categories.forEach((category) => {
      const option = document.createElement("option");
      option.value = category;
      option.textContent = category;
      categorySelect.appendChild(option);
    });

    categorySelect.value = TOTAL_KEY;

    horizonValue.textContent = horizonRange.value;
    plotModelComparison();
    renderTopTable();
    setScope("total", Number(horizonRange.value));

    const storedTheme = localStorage.getItem("pharmapulse-theme") || "light";
    applyTheme(storedTheme);

    if (themeToggle) {
      themeToggle.addEventListener("click", () => {
        const nextTheme = isDarkTheme() ? "light" : "dark";
        localStorage.setItem("pharmapulse-theme", nextTheme);
        applyTheme(nextTheme);
      });
    }

    if (scopeTotalBtn && scopeCategoryBtn) {
      scopeTotalBtn.addEventListener("click", () => {
        setScope("total", Number(horizonRange.value));
      });

      scopeCategoryBtn.addEventListener("click", () => {
        setScope("category", Number(horizonRange.value));
      });
    }

    categorySelect.addEventListener("change", () => {
      if (categorySelect.value === TOTAL_KEY) {
        setScope("total", Number(horizonRange.value));
        return;
      }
      setScope("category", Number(horizonRange.value));
    });

    horizonRange.addEventListener("input", () => {
      horizonValue.textContent = horizonRange.value;
      renderCategory(categorySelect.value, Number(horizonRange.value));
    });

  }

  window.addEventListener("DOMContentLoaded", init);
})();
