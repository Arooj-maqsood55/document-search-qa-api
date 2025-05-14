"""Document Search & Q&A API using simple keyword retrieval."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
app = FastAPI(title="Document Search & Q&A API", version="1.0.0")


class AskRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=3, ge=1, le=10)


def load_documents() -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
    for path in sorted(DATA_DIR.glob("*.txt")):
        docs.append({"id": path.stem, "source": path.name, "text": path.read_text(encoding="utf-8")})
    return docs


def tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def retrieve(question: str, docs: list[dict[str, str]], top_k: int) -> list[dict[str, Any]]:
    q_tokens = tokenize(question)
    ranked: list[dict[str, Any]] = []
    for doc in docs:
        overlap = q_tokens & tokenize(doc["text"])
        if not overlap:
            continue
        ranked.append(
            {
                "source": doc["source"],
                "score": len(overlap),
                "passage": doc["text"][:280].strip(),
                "matched_terms": sorted(overlap),
            }
        )
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask")
def ask(payload: AskRequest) -> dict[str, Any]:
    docs = load_documents()
    if not docs:
        raise HTTPException(status_code=500, detail="No documents available")
    hits = retrieve(payload.question, docs, payload.top_k)
    if not hits:
        return {
            "question": payload.question,
            "answer": "No relevant passages found in the document set.",
            "sources": [],
        }
    answer = "Based on the retrieved sources: " + " ".join(hit["passage"] for hit in hits[:2])
    return {"question": payload.question, "answer": answer, "sources": hits}
