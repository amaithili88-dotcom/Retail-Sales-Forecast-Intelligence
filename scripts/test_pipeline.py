from src.forecasting.forecasting_pipeline import ForecastingPipeline

pipeline = ForecastingPipeline()

output = pipeline.run()

print("=" * 60)
print("PIPELINE EXECUTED")
print("=" * 60)

print("\nMetrics")
print("-" * 60)

for metric, value in output["metrics"].items():
    if metric == "MAPE":
        print(f"{metric:<5}: {value:.2f}%")
    else:
        print(f"{metric:<5}: {value:.2f}")

print("\nPrediction Sample")
print("-" * 60)

print(
    output["results"][
        [
            "date",
            "category",
            "sales_units",
            "prediction"
        ]
    ].head(15)
)