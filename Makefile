.PHONY: local-start local-stop local-crawl-article local-crawl-links local-cdc local-feature-pipeline

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

local-cdc:
	uv run python -m data_cdc.cdc

local-feature-pipeline:
	uv run python -m bytewax.run src/feature_pipeline/main.py
