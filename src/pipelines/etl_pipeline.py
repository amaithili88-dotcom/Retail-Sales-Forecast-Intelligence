from src.extractors.csv_extractor import CSVExtractor
from src.validators.sales_validator import SalesValidator
from src.transformers.sales_transformer import SalesTransformer
from src.loaders.csv_loader import CSVLoader


class ETLPipeline:

    def __init__(self, input_path: str, output_path: str):
        self.extractor = CSVExtractor(input_path)
        self.validator = SalesValidator()
        self.transformer = SalesTransformer()
        self.loader = CSVLoader(output_path)

    def run(self):

        print("=" * 60)
        print("PHARMA SALES ETL PIPELINE")
        print("=" * 60)

        # Step 1 - Extract
        print("\n[1/4] Extracting data...")
        df = self.extractor.extract()

        # Step 2 - Validate
        print("\n[2/4] Validating data...")
        report = self.validator.validate(df)

        print("\nValidation Report")
        print("-" * 40)

        for key, value in report.items():
            print(f"{key}: {value}")

        if report["missing_columns"]:
            raise ValueError(
                f"Missing columns found: {report['missing_columns']}"
            )

        print("\nValidation successful.")

        # Step 3 - Transform
        print("\n[3/4] Transforming data...")
        transformed_df = self.transformer.transform(df)

        print(f"Rows after transformation: {len(transformed_df)}")
        print(transformed_df.head())

        # Step 4 - Load
        print("\n[4/4] Saving processed data...")
        self.loader.load(transformed_df)

        print("\n" + "=" * 60)
        print("ETL PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

        return transformed_df