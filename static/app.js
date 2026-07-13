(() => {
  const TOTAL_KEY = "__all__";
  const payload = window.__PAYLOAD__ || {};
  const body = document.body;
  const currency = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
  let rerenderActivePage = null;

  function fmtNumber(value) {
    if (value === null || value === undefined || Number.isNaN(value)) return "-";
    return currency.format(value);
  }

  function fmtDecimal(value, digits = 2) {
    if (value === null || value === undefined || Number.isNaN(value)) return "-";
    return Number(value).toFixed(digits);
  }

  function fmtPct(value) {
    if (value === null || value === undefined || Number.isNaN(value)) return "-";
    return `${Number(value).toFixed(2)}%`;
  }

  function parseDate(value) {
    if (!value) return null;
    const d = new Date(value);
    return Number.isNaN(d.getTime()) ? null : d;
  }

  function toIsoDate(value) {
    const d = parseDate(value);
    if (!d) return "";
    return d.toISOString().slice(0, 10);
  }

  function getDateBounds(rows, dateKey = "date") {
    const timestamps = rows
      .map((row) => parseDate(row[dateKey]))
      .filter(Boolean)
      .map((d) => d.getTime())
      .sort((a, b) => a - b);

    if (!timestamps.length) return { min: "", max: "" };

    return {
      min: new Date(timestamps[0]).toISOString().slice(0, 10),
      max: new Date(timestamps[timestamps.length - 1]).toISOString().slice(0, 10),
    };
  }

  function isDarkTheme() {
    return document.documentElement.getAttribute("data-theme") === "dark";
  }

  function chartColors() {
    if (isDarkTheme()) {
      return {
        font: "#d9e5f8",
        grid: "#304761",
        actual: "#44c7af",
        predicted: "#6ea2f8",
        future: "#e4ad67",
        bar: "#6ea2f8",
        line: "#44c7af",
        error: "#e57f88",
      };
    }

    return {
      font: "#122035",
      grid: "#d8e2f2",
      actual: "#0f9f95",
      predicted: "#1d4ed8",
      future: "#c77700",
      bar: "#1d4ed8",
      line: "#0f9f95",
      error: "#d14343",
    };
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const themeToggle = document.getElementById("themeToggle");
    if (themeToggle) {
      themeToggle.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
    }
    if (typeof rerenderActivePage === "function") {
      rerenderActivePage();
    }
  }

  function wireThemeToggle() {
    const themeToggle = document.getElementById("themeToggle");
    const storedTheme = localStorage.getItem("sales-forecast-theme") || "light";
    applyTheme(storedTheme);

    if (!themeToggle) return;

    themeToggle.addEventListener("click", () => {
      const nextTheme = isDarkTheme() ? "light" : "dark";
      localStorage.setItem("sales-forecast-theme", nextTheme);
      applyTheme(nextTheme);
    });
  }

  function wireHistoryButtons() {
    const backBtn = document.getElementById("navBack");
    const forwardBtn = document.getElementById("navForward");

    if (backBtn) {
      backBtn.addEventListener("click", () => {
        window.history.back();
      });
    }

    if (forwardBtn) {
      forwardBtn.addEventListener("click", () => {
        window.history.forward();
      });
    }
  }

  function aggregateByDate(rows) {
    const map = new Map();
    rows.forEach((row) => {
      const key = row.date;
      const existing = map.get(key) || { date: key, actual: 0, predicted: 0, absError: 0 };
      existing.actual += Number(row.actual || 0);
      existing.predicted += Number(row.predicted || 0);
      existing.absError += Number(row.absError || 0);
      map.set(key, existing);
    });

    return Array.from(map.values()).sort((a, b) => (a.date < b.date ? -1 : 1));
  }

  function computeMetrics(rows) {
    if (!rows.length) {
      return { totalActual: null, totalPredicted: null, mae: null, rmse: null, wmape: null };
    }

    let totalActual = 0;
    let totalPredicted = 0;
    let totalAbsError = 0;
    let sumSquaredError = 0;

    rows.forEach((row) => {
      const actual = Number(row.actual || 0);
      const predicted = Number(row.predicted || 0);
      const error = actual - predicted;
      totalActual += actual;
      totalPredicted += predicted;
      totalAbsError += Math.abs(error);
      sumSquaredError += error * error;
    });

    const mae = totalAbsError / rows.length;
    const rmse = Math.sqrt(sumSquaredError / rows.length);
    const wmape = totalActual !== 0 ? (totalAbsError / Math.abs(totalActual)) * 100 : null;

    return {
      totalActual,
      totalPredicted,
      mae,
      rmse,
      wmape,
    };
  }

  function buildHistoricalRows() {
    const rows = [];
    Object.entries(payload.byCategory || {}).forEach(([category, data]) => {
      (data.history || []).forEach((row) => {
        const actual = Number(row.actual || 0);
        const predicted = Number(row.predicted || 0);
        rows.push({
          category,
          date: row.date,
          actual,
          predicted,
          absError: Math.abs(actual - predicted),
        });
      });
    });
    return rows.sort((a, b) => (a.date < b.date ? -1 : 1));
  }

  function buildFutureRows() {
    const rows = [];
    Object.entries(payload.byCategory || {}).forEach(([category, data]) => {
      (data.future_monthly || []).forEach((row) => {
        rows.push({
          category,
          month_index: Number(row.month_index || 0),
          forecast_month: row.forecast_month || "",
          date: row.forecast_month ? `${row.forecast_month}-01` : "",
          predicted_sales: Number(row.predicted_sales || 0),
          growth_vs_previous_month_pct: row.growth_vs_previous_month_pct,
        });
      });
    });
    return rows;
  }

  function filterRows(rows, filters, dateKey = "date") {
    const year = filters.year;
    const start = filters.startDate ? parseDate(filters.startDate) : null;
    const end = filters.endDate ? parseDate(filters.endDate) : null;

    return rows.filter((row) => {
      if (filters.category && filters.category !== TOTAL_KEY && row.category !== filters.category) {
        return false;
      }

      const rowDate = parseDate(row[dateKey]);
      if (!rowDate) return false;

      if (year && year !== TOTAL_KEY && rowDate.getFullYear() !== Number(year)) {
        return false;
      }

      if (start && rowDate < start) return false;
      if (end && rowDate > end) return false;

      return true;
    });
  }

  function fillSelect(select, options, includeAllLabel) {
    if (!select) return;
    select.innerHTML = "";

    const allOption = document.createElement("option");
    allOption.value = TOTAL_KEY;
    allOption.textContent = includeAllLabel;
    select.appendChild(allOption);

    options.forEach((item) => {
      const option = document.createElement("option");
      option.value = String(item);
      option.textContent = String(item);
      select.appendChild(option);
    });

    select.value = TOTAL_KEY;
  }

  function getYearOptions(rows, dateKey = "date") {
    const years = new Set();
    rows.forEach((row) => {
      const date = parseDate(row[dateKey]);
      if (date) years.add(date.getFullYear());
    });
    return Array.from(years).sort((a, b) => a - b);
  }

  function plot(targetId, traces, layout) {
    if (typeof Plotly === "undefined") return;
    Plotly.newPlot(targetId, traces, layout, { displayModeBar: false, responsive: true });
  }

  function initResultsPage() {
    if (!body.classList.contains("page-results")) return;

    const historicalRows = buildHistoricalRows();
    const futureRows = buildFutureRows();

    const categorySelect = document.getElementById("resultsCategory");
    const yearSelect = document.getElementById("resultsYear");
    const startDateInput = document.getElementById("resultsStartDate");
    const endDateInput = document.getElementById("resultsEndDate");
    const applyBtn = document.getElementById("resultsApply");
    const resetBtn = document.getElementById("resultsReset");

    const totalActualEl = document.getElementById("resultsTotalActual");
    const totalPredictedEl = document.getElementById("resultsTotalPredicted");
    const wmapeEl = document.getElementById("resultsWmape");
    const nextMonthEl = document.getElementById("resultsNextMonth");

    fillSelect(categorySelect, payload.categories || [], "All Categories");
    fillSelect(yearSelect, getYearOptions(historicalRows), "All Years");

    const bounds = getDateBounds(historicalRows);
    startDateInput.value = bounds.min;
    endDateInput.value = bounds.max;

    function render() {
      const filters = {
        category: categorySelect.value,
        year: yearSelect.value,
        startDate: startDateInput.value,
        endDate: endDateInput.value,
      };

      const selectedRows = filterRows(historicalRows, filters, "date");
      const selectedFuture = filterRows(futureRows, filters, "date").sort((a, b) => a.month_index - b.month_index);
      const metrics = computeMetrics(selectedRows);
      const colors = chartColors();

      totalActualEl.textContent = fmtNumber(metrics.totalActual);
      totalPredictedEl.textContent = fmtNumber(metrics.totalPredicted);
      wmapeEl.textContent = fmtPct(metrics.wmape);
      nextMonthEl.textContent = selectedFuture.length ? fmtNumber(selectedFuture[0].predicted_sales) : "-";

      const trendRows = aggregateByDate(selectedRows);
      plot(
        "resultsTrendChart",
        [
          {
            x: trendRows.map((r) => r.date),
            y: trendRows.map((r) => r.actual),
            type: "scatter",
            mode: "lines",
            name: "Actual",
            line: { color: colors.actual, width: 2.6 },
          },
          {
            x: trendRows.map((r) => r.date),
            y: trendRows.map((r) => r.predicted),
            type: "scatter",
            mode: "lines",
            name: "Predicted",
            line: { color: colors.predicted, width: 2.6 },
          },
        ],
        {
          margin: { l: 56, r: 16, t: 10, b: 44 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { family: "IBM Plex Sans, sans-serif", color: colors.font },
          xaxis: { gridcolor: colors.grid },
          yaxis: { gridcolor: colors.grid },
          legend: { orientation: "h", y: 1.1 },
        }
      );

      plot(
        "resultsForecastChart",
        [
          {
            x: selectedFuture.map((r) => r.forecast_month),
            y: selectedFuture.map((r) => r.predicted_sales),
            type: "bar",
            marker: { color: colors.future },
            name: "Predicted Sales",
          },
        ],
        {
          margin: { l: 56, r: 16, t: 10, b: 44 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { family: "IBM Plex Sans, sans-serif", color: colors.font },
          xaxis: { gridcolor: colors.grid },
          yaxis: { gridcolor: colors.grid },
        }
      );

      const resultsBody = document.querySelector("#resultsTable tbody");
      resultsBody.innerHTML = "";
      selectedRows.slice(0, 400).forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${toIsoDate(row.date)}</td>
          <td>${row.category}</td>
          <td>${fmtNumber(row.actual)}</td>
          <td>${fmtNumber(row.predicted)}</td>
          <td>${fmtNumber(row.absError)}</td>
        `;
        resultsBody.appendChild(tr);
      });

      const futureBody = document.querySelector("#resultsFutureTable tbody");
      futureBody.innerHTML = "";
      selectedFuture.slice(0, 120).forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.forecast_month || "-"}</td>
          <td>${row.category}</td>
          <td>${fmtNumber(row.predicted_sales)}</td>
          <td>${fmtPct(row.growth_vs_previous_month_pct)}</td>
        `;
        futureBody.appendChild(tr);
      });
    }

    applyBtn.addEventListener("click", render);
    resetBtn.addEventListener("click", () => {
      categorySelect.value = TOTAL_KEY;
      yearSelect.value = TOTAL_KEY;
      startDateInput.value = bounds.min;
      endDateInput.value = bounds.max;
      render();
    });

    rerenderActivePage = render;
    render();
  }

  function initModelPerformancePage() {
    if (!body.classList.contains("page-model-performance")) return;

    const historicalRows = buildHistoricalRows();

    const categorySelect = document.getElementById("perfCategory");
    const yearSelect = document.getElementById("perfYear");
    const startDateInput = document.getElementById("perfStartDate");
    const endDateInput = document.getElementById("perfEndDate");
    const applyBtn = document.getElementById("perfApply");
    const resetBtn = document.getElementById("perfReset");

    const maeEl = document.getElementById("perfMae");
    const rmseEl = document.getElementById("perfRmse");
    const wmapeEl = document.getElementById("perfWmape");
    const r2El = document.getElementById("perfR2");
    const bestModelEl = document.getElementById("perfBestModel");
    const bestMaeEl = document.getElementById("perfBestMae");
    const bestRmseEl = document.getElementById("perfBestRmse");
    const bestWmapeEl = document.getElementById("perfBestWmape");

    const bestModelSummary = payload.bestModel || {};

    fillSelect(categorySelect, payload.categories || [], "All Categories");
    fillSelect(yearSelect, getYearOptions(historicalRows), "All Years");

    const bounds = getDateBounds(historicalRows);
    startDateInput.value = bounds.min;
    endDateInput.value = bounds.max;
    bestModelEl.textContent = payload.bestModel?.name || "-";
    if (bestMaeEl) bestMaeEl.textContent = fmtDecimal(bestModelSummary.mae);
    if (bestRmseEl) bestRmseEl.textContent = fmtDecimal(bestModelSummary.rmse);
    if (bestWmapeEl) bestWmapeEl.textContent = fmtPct(bestModelSummary.wmape);

    function render() {
      const filters = {
        category: categorySelect.value,
        year: yearSelect.value,
        startDate: startDateInput.value,
        endDate: endDateInput.value,
      };

      const selectedRows = filterRows(historicalRows, filters, "date");
      const metrics = computeMetrics(selectedRows);
      const colors = chartColors();

      maeEl.textContent = fmtDecimal(metrics.mae);
      rmseEl.textContent = fmtDecimal(metrics.rmse);
      wmapeEl.textContent = fmtPct(metrics.wmape);

      if (r2El) {
        const selectedR2 = selectedRows.length > 1
          ? (() => {
              const actual = selectedRows.map((r) => Number(r.actual || 0));
              const predicted = selectedRows.map((r) => Number(r.predicted || 0));
              const meanActual = actual.reduce((s, v) => s + v, 0) / actual.length;
              const ssRes = actual.reduce((s, v, i) => s + Math.pow(v - predicted[i], 2), 0);
              const ssTot = actual.reduce((s, v) => s + Math.pow(v - meanActual, 2), 0);
              if (ssTot === 0) return null;
              return 1 - (ssRes / ssTot);
            })()
          : null;

        r2El.textContent = fmtDecimal(selectedR2, 4);
      }

      const modelRows = payload.comparison || [];
      plot(
        "perfModelChart",
        [
          {
            x: modelRows.map((r) => r.Model),
            y: modelRows.map((r) => r.MAE),
            type: "bar",
            name: "MAE",
            marker: { color: colors.bar },
          },
          {
            x: modelRows.map((r) => r.Model),
            y: modelRows.map((r) => r.WMAPE),
            type: "scatter",
            mode: "lines+markers",
            name: "WMAPE (%)",
            yaxis: "y2",
            line: { color: colors.line, width: 3 },
          },
        ],
        {
          margin: { l: 56, r: 52, t: 10, b: 66 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { family: "IBM Plex Sans, sans-serif", color: colors.font },
          xaxis: { tickangle: -16, gridcolor: colors.grid },
          yaxis: { title: "MAE", gridcolor: colors.grid },
          yaxis2: {
            title: "WMAPE %",
            overlaying: "y",
            side: "right",
          },
          legend: { orientation: "h", y: 1.1 },
        }
      );

      const trendRows = aggregateByDate(selectedRows);
      plot(
        "perfErrorTrendChart",
        [
          {
            x: trendRows.map((r) => r.date),
            y: trendRows.map((r) => r.absError),
            type: "scatter",
            mode: "lines",
            name: "Absolute Error",
            line: { color: colors.error, width: 2.6 },
          },
        ],
        {
          margin: { l: 56, r: 16, t: 10, b: 44 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { family: "IBM Plex Sans, sans-serif", color: colors.font },
          xaxis: { gridcolor: colors.grid },
          yaxis: { gridcolor: colors.grid },
        }
      );

      const modelBody = document.querySelector("#perfModelTable tbody");
      modelBody.innerHTML = "";
      modelRows.forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.Model || "-"}</td>
          <td>${fmtDecimal(row.MAE)}</td>
          <td>${fmtDecimal(row.RMSE)}</td>
          <td>${fmtPct(row.WMAPE)}</td>
          <td>${fmtDecimal(row.R2, 4)}</td>
        `;
        modelBody.appendChild(tr);
      });

      const categoryMap = new Map();
      selectedRows.forEach((row) => {
        const current = categoryMap.get(row.category) || {
          category: row.category,
          count: 0,
          absError: 0,
          absActual: 0,
        };
        current.count += 1;
        current.absError += row.absError;
        current.absActual += Math.abs(row.actual || 0);
        categoryMap.set(row.category, current);
      });

      const categoryRows = Array.from(categoryMap.values())
        .map((item) => ({
          category: item.category,
          rows: item.count,
          mae: item.count ? item.absError / item.count : null,
          wmape: item.absActual ? (item.absError / item.absActual) * 100 : null,
        }))
        .sort((a, b) => (a.wmape || 0) - (b.wmape || 0));

      const categoryBody = document.querySelector("#perfCategoryTable tbody");
      categoryBody.innerHTML = "";
      categoryRows.forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.category}</td>
          <td>${row.rows}</td>
          <td>${fmtDecimal(row.mae)}</td>
          <td>${fmtPct(row.wmape)}</td>
        `;
        categoryBody.appendChild(tr);
      });
    }

    applyBtn.addEventListener("click", render);
    resetBtn.addEventListener("click", () => {
      categorySelect.value = TOTAL_KEY;
      yearSelect.value = TOTAL_KEY;
      startDateInput.value = bounds.min;
      endDateInput.value = bounds.max;
      render();
    });

    rerenderActivePage = render;
    render();
  }

  function initLandingPage() {
    if (!body.classList.contains("page-landing")) return;
    rerenderActivePage = null;
  }

  function init() {
    wireThemeToggle();
    wireHistoryButtons();
    initLandingPage();
    initResultsPage();
    initModelPerformancePage();
  }

  window.addEventListener("DOMContentLoaded", init);
})();
