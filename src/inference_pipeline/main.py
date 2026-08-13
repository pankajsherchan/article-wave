import argparse

from inference_pipeline.generation import ArticleAnswerGenerator
from inference_pipeline.retrieval import ArticleRetriever


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search indexed Article Wave evidence."
    )

    parser.add_argument(
        "question",
        help="Question to search for in indexed articles.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of evidence snippets to retrieve.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    generator = ArticleAnswerGenerator(
        retriever=ArticleRetriever(limit=args.limit)
    )
    response = generator.generate(args.question)

    print(f"Question: {response.question}")
    print()
    print(response.answer)
    print()

    if response.evidences:
        print("Sources:")
        print()

    for index, evidence in enumerate(response.evidences, start=1):
        print(f"[{index}] {evidence.title}")
        print(f"URL: {evidence.canonical_url or evidence.source_url}")
        print(f"Score: {evidence.score}")
        print()


if __name__ == "__main__":
    main()
