import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Article Wave LLM behavior.")
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="ArticleWaveArtifactTestDataset",
        help="Name of the dataset to evaluate",
    )

    parser.parse_args()

    raise NotImplementedError(
        "Article Wave non-RAG evaluation is deferred until a non-RAG generation "
        "path exists."
    )


if __name__ == "__main__":
    main()
