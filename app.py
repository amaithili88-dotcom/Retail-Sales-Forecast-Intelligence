from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


def _load_csv(path: Path):
    if not path.exists():
        return None
    return pd.read_csv(path)


def _safe_float(value):
    if pd.isna(value):
        return None
    return float(value)


def build_dashboard_payload():
    predictions = _load_csv(DATA_DIR / "global_predictions.csv")
    comparison = _load_csv(DATA_DIR / "model_comparison.csv")
    future_weekly = _load_csv(DATA_DIR / "future_weekly_predictions.csv")
    future_month = _load_csv(DATA_DIR / "future_month_forecast.csv")

    if predictions is None or comparison is None:
        raise FileNotFoundError(
            "Required files missing. Run scripts/train_all_categories.py and scripts/model_comparison.py first."
        )

    predictions["date"] = pd.to_datetime(predictions["date"])
    predictions["category"] = predictions["category"].astype(str)
    predictions = predictions.sort_values(["category", "date"])  # deterministic JSON order

    comparison = comparison.sort_values("MAE").reset_index(drop=True)

    if future_weekly is not None and not future_weekly.empty:
        future_weekly["date"] = pd.to_datetime(future_weekly["date"])
        future_weekly["category"] = future_weekly["category"].astype(str)

    if future_month is not None and not future_month.empty:
        future_month["category"] = future_month["category"].astype(str)

    categories = sorted(predictions["category"].unique().tolist())

    by_category = {}
    for category in categories:
        cat_df = predictions[predictions["category"] == category].copy()

        monthly = (
            cat_df.assign(month_period=cat_df["date"].dt.to_period("M"))
            .groupby("month_period", as_index=False)[["sales_units", "prediction"]]
            .sum()
        )
        monthly["date"] = monthly["month_period"].dt.to_timestamp(how="end").dt.normalize()
        monthly["period_label"] = monthly["date"].dt.strftime("%b %Y")

        category_payload = {
            "history": [
                {
                    "date": row["date"].strftime("%Y-%m-%d"),
                    "actual": _safe_float(row["sales_units"]),
                    "predicted": _safe_float(row["prediction"]),
                }
                for _, row in cat_df.iterrows()
            ],
            "monthly": [
                {
                    "date": row["date"].strftime("%Y-%m-%d"),
                    "period_label": row["period_label"],
                    "actual": _safe_float(row["sales_units"]),
                    "predicted": _safe_float(row["prediction"]),
                }
                for _, row in monthly.iterrows()
            ],
            "future_weekly": [],
            "future_monthly": [],
        }

        if future_weekly is not None and not future_weekly.empty:
            future_cat = future_weekly[future_weekly["category"] == category].copy()
            category_payload["future_weekly"] = [
                {
                    "date": row["date"].strftime("%Y-%m-%d"),
                    "prediction": _safe_float(row["prediction"]),
                }
                for _, row in future_cat.iterrows()
            ]

        if future_month is not None and not future_month.empty:
            future_month_cat = future_month[future_month["category"] == category].copy()
            future_month_cat = future_month_cat.sort_values("month_index")
            category_payload["future_monthly"] = [
                {
                    "forecast_month": str(row.get("forecast_month", "")),
                    "month_index": int(row.get("month_index", 1)),
                    "predicted_sales": _safe_float(row.get("predicted_sales_next_month", row.get("predicted_sales"))),
                    "last_month_sales": _safe_float(row.get("last_month_sales")),
                    "growth_vs_previous_month_pct": _safe_float(row.get("growth_vs_previous_month_pct")),
                    "growth_vs_last_month_pct": _safe_float(row.get("growth_vs_last_month_pct")),
                }
                for _, row in future_month_cat.iterrows()
            ]

        by_category[category] = category_payload

    best_model = comparison.iloc[0].to_dict()

    total_future_next_month = 0.0
    for cat_data in by_category.values():
        first_month = next((m for m in cat_data.get("future_monthly", []) if m.get("month_index") == 1), None)
        if first_month and first_month.get("predicted_sales") is not None:
            total_future_next_month += float(first_month["predicted_sales"])

    return {
        "categories": categories,
        "byCategory": by_category,
        "comparison": comparison.to_dict(orient="records"),
        "site": {
            "title": "Sales Forecast Platform",
            "description": "Enterprise forecasting for demand planning with explainable metrics and faster decision-making.",
            "tagline": "Predict demand, defend decisions, accelerate growth.",
            "metaDescription": "Sales Forecast Platform helps planning teams forecast demand with reliable model performance, category intelligence, and executive reporting.",
        },
        "globalStats": {
            "categoriesTracked": len(categories),
            "nextMonthTotalPredicted": _safe_float(total_future_next_month),
            "modelCount": int(len(comparison)),
            "bestModelMAE": _safe_float(best_model.get("MAE")),
            "bestModelWMAPE": _safe_float(best_model.get("WMAPE")),
        },
        "bestModel": {
            "name": best_model.get("Model"),
            "mae": _safe_float(best_model.get("MAE")),
            "rmse": _safe_float(best_model.get("RMSE")),
            "wmape": _safe_float(best_model.get("WMAPE")),
            "smape": _safe_float(best_model.get("sMAPE")),
            "r2": _safe_float(best_model.get("R2")),
        },
    }


@app.route("/")
def dashboard():
    payload = build_dashboard_payload()
    return render_template("index.html", payload=payload)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/robots.txt")
def robots():
    return "User-agent: *\nAllow: /\nDisallow: /data/\n", 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=False)