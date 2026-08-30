import argparse

from core.config import settings
from core.opik_utils import configure_opik, create_dataset_from_artifacts
from inference_pipeline.generation import ArticleAnswerGenerator
from opik.evaluation import evaluate
from opik.evaluation.metrics import ContextPrecision, ContextRecall, Hallucination


def evaluation_task(x: dict) -> dict:
    generator = ArticleAnswerGenerator()
    response = generator.generate(x["instruction"])

    context = [evidence.content for evidence in response.evidences]

    return {
        "input": x["instruction"],
        "output": response.answer,
        "context": context,
        "expected_output": x["content"],
        "reference": x["content"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Article Wave RAG.")
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="ArticleWaveArtifactTestDataset",
        help="Name of the dataset to evaluate",
    )

    args = parser.parse_args()

    configure_opik()

    dataset = create_dataset_from_artifacts(
        dataset_name=args.dataset_name,
        artifact_names=[
            "articles-instruct-dataset",
        ],
    )

    if dataset is None:
        print("Dataset can't be created. Exiting.")
        exit(1)

    experiment_config = {
        "model_id": settings.OLLAMA_MODEL_ID,
        "embedding_model_id": settings.EMBEDDING_MODEL_ID,
    }

    scoring_metrics = [
        Hallucination(),
        ContextRecall(),
        ContextPrecision(),
    ]

    evaluate(
        dataset=dataset,
        task=evaluation_task,
        scoring_metrics=scoring_metrics,
        experiment_config=experiment_config,
        # Keep local-first and cheap; one sample proves the evaluation loop works.
        task_threads=1,
        nb_samples=1,
    )


if __name__ == "__main__":
    main()
