# Document Search & Q&A API

Python FastAPI service that retrieves relevant document passages and returns source-based answers.

**Timeline:** Built during AI/engineering project work spanning late 2025 into 2026 freelance evaluation focus.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"How are LLM responses evaluated?"}'
```
