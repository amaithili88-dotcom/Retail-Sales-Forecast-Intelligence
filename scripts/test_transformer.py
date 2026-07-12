from src.extractors.csv_extractor import CSVExtractor
from src.transformers.sales_transformer import SalesTransformer


def main():

    extractor = CSVExtractor("data/raw/salesmonthly.csv")

    df = extractor.extract()

    transformer = SalesTransformer()

    transformed = transformer.transform(df)

    print(transformed.head())

    print()

    print("Shape:", transformed.shape)


if __name__ == "__main__":
    main()