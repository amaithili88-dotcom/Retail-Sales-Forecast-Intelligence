import numpy as np
import pandas as pd


class FutureForecaster:
	"""
	Generates future forecasts using recursive one-step-ahead prediction.
	"""

	def __init__(self, feature_engineering, trainer):
		self.feature_engineering = feature_engineering
		self.trainer = trainer

	@staticmethod
	def _safe_growth(current_value, previous_value):
		if previous_value == 0 or np.isnan(previous_value):
			return np.nan
		return (current_value - previous_value) / previous_value * 100

	def _forecast_category_weeks(self, history_df, category, weeks_ahead=8):
		category_history = (
			history_df[history_df["category"] == category]
			.sort_values("date")
			.copy()
		)

		if category_history.empty:
			return pd.DataFrame()

		optional_columns = [
			col for col in [
				"Holiday_Flag",
				"Temperature",
				"Fuel_Price",
				"CPI",
				"Unemployment"
			] if col in category_history.columns
		]

		last_known_date = category_history["date"].max()
		future_rows = []

		for step in range(1, weeks_ahead + 1):
			future_date = last_known_date + pd.Timedelta(days=7 * step)

			new_row = {
				"category": category,
				"date": future_date,
				"sales_units": np.nan,
			}

			for col in optional_columns:
				new_row[col] = category_history[col].iloc[-1]

			category_history = pd.concat(
				[category_history, pd.DataFrame([new_row])],
				ignore_index=True
			)

			engineered = self.feature_engineering.create_features(category_history)

			candidate = engineered[
				engineered["date"] == future_date
			].copy()

			if candidate.empty:
				continue

			predicted_value = float(self.trainer.predict(candidate)[0])

			category_history.loc[
				category_history["date"] == future_date,
				"sales_units"
			] = predicted_value

			future_rows.append(
				{
					"category": category,
					"date": future_date,
					"prediction": predicted_value,
				}
			)

		return pd.DataFrame(future_rows)

	def forecast_next_month(self, history_df, weeks_ahead=16, months_ahead=3):
		history_df = history_df.copy()
		history_df["date"] = pd.to_datetime(history_df["date"])

		categories = sorted(history_df["category"].astype(str).unique())
		all_weekly_forecasts = []

		for category in categories:
			weekly_forecast = self._forecast_category_weeks(
				history_df=history_df,
				category=category,
				weeks_ahead=weeks_ahead
			)

			if not weekly_forecast.empty:
				all_weekly_forecasts.append(weekly_forecast)

		if not all_weekly_forecasts:
			return pd.DataFrame(), pd.DataFrame()

		weekly_df = pd.concat(all_weekly_forecasts, ignore_index=True)
		weekly_df["date"] = pd.to_datetime(weekly_df["date"])

		max_historical_date = history_df["date"].max()
		last_period = max_historical_date.to_period("M")

		weekly_df["forecast_period"] = weekly_df["date"].dt.to_period("M")

		monthly_forecast = (
			weekly_df
			.groupby(["category", "forecast_period"], as_index=False)["prediction"]
			.sum()
			.rename(columns={"prediction": "predicted_sales"})
		)

		monthly_forecast = monthly_forecast[
			monthly_forecast["forecast_period"] > last_period
		].copy()

		if monthly_forecast.empty:
			return weekly_df, pd.DataFrame()

		monthly_forecast = monthly_forecast.sort_values(
			["category", "forecast_period"]
		).reset_index(drop=True)

		monthly_forecast["month_index"] = (
			monthly_forecast.groupby("category").cumcount() + 1
		)

		monthly_forecast = monthly_forecast[
			monthly_forecast["month_index"] <= months_ahead
		].copy()

		last_month_actual = (
			history_df[history_df["date"].dt.to_period("M") == last_period]
			.groupby("category", as_index=False)["sales_units"]
			.sum()
			.rename(columns={"sales_units": "last_month_sales"})
		)

		monthly_forecast = monthly_forecast.merge(
			last_month_actual,
			on="category",
			how="left"
		)

		monthly_forecast["growth_vs_last_month_pct"] = monthly_forecast.apply(
			lambda row: self._safe_growth(
				row["predicted_sales"],
				row["last_month_sales"]
			),
			axis=1
		)

		monthly_forecast["growth_vs_previous_month_pct"] = np.nan

		for category in monthly_forecast["category"].unique():
			cat_idx = monthly_forecast[monthly_forecast["category"] == category].index
			previous_value = float(monthly_forecast.loc[cat_idx[0], "last_month_sales"])

			for idx in cat_idx:
				current_value = float(monthly_forecast.loc[idx, "predicted_sales"])
				monthly_forecast.loc[idx, "growth_vs_previous_month_pct"] = self._safe_growth(
					current_value,
					previous_value
				)
				previous_value = current_value

		monthly_forecast["forecast_month"] = monthly_forecast["forecast_period"].astype(str)

		# Backward compatibility for existing consumers expecting next-month field name.
		monthly_forecast["predicted_sales_next_month"] = monthly_forecast["predicted_sales"]

		monthly_forecast = monthly_forecast.drop(columns=["forecast_period"])

		return weekly_df, monthly_forecast
