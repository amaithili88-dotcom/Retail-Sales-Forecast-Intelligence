from pprint import pprint

from src.extractors.csv_extractor import CSVExtractor
from src.validators.sales_validator import SalesValidator


def main():

    extractor = CSVExtractor("data/Walmart.csv")
    df = extractor.extract()

    validator = SalesValidator()

    report = validator.validate(df)

    pprint(report)


if __name__ == "__main__":
    main()