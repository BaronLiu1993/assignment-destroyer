# Docs AI Backend

FastAPI backend for an AI-powered writing assistant Chrome extension. Uses Claude to analyze documents and generate improvement plans and edits.

## Setup

```bash
make setup   # start MongoDB + install dependencies
make dev     # run server at http://localhost:8000
make down    # stop MongoDB
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/plan` | Analyze a document and return an improvement plan |
| POST | `/agent` | Execute a plan step and return concrete text edits |
| GET | `/health` | Health check |
