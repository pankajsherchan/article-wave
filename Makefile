.PHONY: local-start local-stop

local-start:
	docker compose up -d

local-stop:
	docker compose down
