# Core Service

FastAPI backend service for Learnora learning path planning.

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Setup and Run

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Run the development server:**
   ```bash
   uv run fastapi dev app/main.py
   ```

The API will be available at `http://127.0.0.1:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
