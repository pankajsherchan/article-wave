.PHONY: local-start local-stop local-crawl-article local-crawl-links local-cdc local-feature-pipeline local-ask local-generate-instruct-dataset evaluate-llm evaluate-rag evaluate-llm-monitoring

PROMPT ?= Write a paragraph to introduce supervised fine-tuning.


local-start:
	docker compose up -d

local-stop:
	docker compose down

local-crawl-article:
	uv run python -m data_crawling.main "$(URL)"

local-crawl-links:
	while IFS= read -r url; do \
		if [ -n "$$url" ]; then \
			echo "Crawling: $$url"; \
			uv run python -m data_crawling.main "$$url"; \
		fi; \
	done < data/links.txt

start: local-cdc local-feature-pipeline local-crawl-links

local-cdc:
	uv run python -m data_cdc.cdc

local-feature-pipeline:
	uv run python -m bytewax.run src/feature_pipeline/main.py

local-ask:
	uv run python -m inference_pipeline.main "$(QUESTION)"

local-generate-instruct-dataset:
	uv run python -m feature_pipeline.generate_dataset.generate

start-training-pipeline-dummy-mode:
	uv run python -m training_pipeline.run_on_sagemaker --is-dummy

start-training-pipeline:
	uv run python -m training_pipeline.run_on_sagemaker

local-test-sagemaker-artifact:
	uv run python -m training_pipeline.infer_sagemaker_artifact --prompt "$(PROMPT)"

evaluate-llm:
	uv run python -m inference_pipeline.evaluation.evaluate

evaluate-rag:
	uv run python -m inference_pipeline.evaluation.evaluate_rag

evaluate-llm-monitoring:
	uv run python -m inference_pipeline.evaluation.evaluate_monitoring
