# Dental Income Tracker

A lightweight MVP to track a dentist's weekly income across multiple clinics. Upload daily production/collection screenshots into `data/uploads/`, run the ingestion + OCR pipeline, and view weekly rollups in a simple FastAPI dashboard.

## Quick Start

```bash
cp .env.example .env
make dev
```

Open <http://localhost:8000> to view the dashboard.

### Local (without Docker)

1. Install Tesseract locally (required for OCR):
   - macOS: `brew install tesseract`
   - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
2. Create a virtualenv and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r apps/api/requirements.txt
   ```
3. Run the API:
   ```bash
   python -m uvicorn apps.api.main:app --reload
   ```

## Folder Structure

```
/apps
  /api
    main.py
    requirements.txt
    Dockerfile
    /src
      /routes
      /services
      /models
      /db
      /utils
  /web (optional minimal UI)
/data
  /uploads
  /processed
  /samples
/scripts
  ingest.py
  process.py
  rollup.py
```

## End-to-End Workflow

1. **Drop images** in `data/uploads/`.
2. **Ingest** new files into SQLite:
   ```bash
   make ingest
   ```
3. **Process OCR + parsing**:
   ```bash
   make process
   ```
4. **Generate weekly rollups**:
   ```bash
   make rollup week=2024-02-05
   ```
5. **Review dashboard** at `/`.

## API Endpoints

- `GET /clinics`
- `POST /clinics`
- `GET /entries`
- `GET /weekly-rollups`
- `POST /reprocess/{upload_id}`

## Adding a Clinic

Update `data/clinics.json` (or set `CLINICS_CONFIG`) with:

```json
[
  {
    "name": "Downtown Dental",
    "pay_percentage": 0.35
  }
]
```

Restart the API or run any script to seed the new clinic.

## Parsing Rules

Parsing is regex-first and pluggable. Add a new parser under `apps/api/src/services/rules/` and register it in `apps/api/src/services/rules/__init__.py` keyed by clinic name.

## Local Development

- `make dev` runs the FastAPI app in Docker.
- `make ingest` registers new uploads.
- `make process` runs OCR and parsing.
- `make rollup week=YYYY-MM-DD` calculates weekly totals.

## Notes

- OCR uses Tesseract via `pytesseract` (installed in the API container).
- Data is stored in local SQLite (`data/db.sqlite3`).
- The storage/OCR layers are modular so S3/Lambda/ECS can replace local components later.
