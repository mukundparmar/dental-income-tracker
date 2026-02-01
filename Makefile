.PHONY: dev ingest process rollup

DEV_CMD=docker-compose up --build


dev:
	$(DEV_CMD)

ingest:
	python scripts/ingest.py

process:
	python scripts/process.py

rollup:
	python scripts/rollup.py --week-start $(week)
