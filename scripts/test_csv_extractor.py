from src.extractors.csv_extractor import CSVExtractor


def main():

    extractor = CSVExtractor(
        "data/raw/salesmonthly.csv"
    )

    df = extractor.extract()

    print(df.head())


if __name__ == "__main__":
    main()