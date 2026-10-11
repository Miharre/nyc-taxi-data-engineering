.PHONY: test up demo verify down

test:
	pytest -q

up:
	docker compose up -d postgres

demo:
	docker compose run --rm pipeline

verify:
	docker compose exec -T postgres psql -U taxi -d taxi_dw -c "SELECT status, source_rows, accepted_rows, rejected_rows, started_at, finished_at FROM meta.pipeline_runs ORDER BY started_at DESC LIMIT 5;"
	docker compose exec -T postgres psql -U taxi -d taxi_dw -c "SELECT COUNT(*) AS fact_trips FROM analytics.fact_trips;"

down:
	docker compose down
