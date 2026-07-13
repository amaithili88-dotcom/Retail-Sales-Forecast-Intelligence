"""
Main entry point for the Sales Forecasting Project.
"""

from src.pipelines.etl_pipeline import ETLPipeline


def main():

    pipeline = ETLPipeline(
        input_path="data/Walmart.csv",
        output_path="data/processed/walmart_sales_processed.csv"
    )

    pipeline.run()


if __name__ == "__main__":
    main()