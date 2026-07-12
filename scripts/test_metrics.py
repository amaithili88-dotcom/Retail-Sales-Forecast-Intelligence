from src.forecasting.metrics import ForecastMetrics


actual = [100, 120, 130, 140, 150]
predicted = [98, 125, 128, 145, 147]

print("=" * 50)
print("FORECAST METRICS")
print("=" * 50)

print(f"MAE  : {ForecastMetrics.mae(actual, predicted):.2f}")
print(f"RMSE : {ForecastMetrics.rmse(actual, predicted):.2f}")
print(f"MAPE : {ForecastMetrics.mape(actual, predicted):.2f}%")
print(f"sMAPE: {ForecastMetrics.smape(actual, predicted):.2f}%")
print(f"WMAPE: {ForecastMetrics.wmape(actual, predicted):.2f}%")
print(f"R2   : {ForecastMetrics.r2(actual, predicted):.4f}")