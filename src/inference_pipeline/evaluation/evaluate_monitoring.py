import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate Article Wave monitoring traces."
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="ArticleWaveMonitoringDataset",
        help="Name of the monitoring dataset to evaluate",
    )

    parser.parse_args()

    raise NotImplementedError(
        "Article Wave monitoring evaluation is deferred until inference traces "
        "are logged to Opik."
    )


if __name__ == "__main__":
    main()