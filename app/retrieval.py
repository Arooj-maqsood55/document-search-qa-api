"""Simple keyword-based passage retrieval."""

from __future__ import annotations

import re
from pathlib import Path


def load_documents(data_dir: Path) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    for path in sorted(data_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        documents.append({"id": path.stem, "title": path.stem.replace("_", " ").title(), "text": text})
    return documents


def tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def split_passages(text: str, size: int = 280) -> list[str]:
    chunks: list[str] = []
    current = []
    count = 0
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        current.append(sentence)
        count += len(sentence)
        if count >= size:
            chunks.append(" ".join(current).strip())
            current = []
            count = 0
    if current:
        chunks.append(" ".join(current).strip())
    return [chunk for chunk in chunks if chunk]


def retrieve(question: str, documents: list[dict[str, str]], top_k: int = 3) -> list[dict[str, str]]:
    q_tokens = tokenize(question)
    scored: list[tuple[int, dict[str, str]]] = []
    for doc in documents:
        for index, passage in enumerate(split_passages(doc["text"])):
            overlap = len(q_tokens & tokenize(passage))
            if overlap:
                scored.append(
                    (
                        overlap,
                        {
                            "document_id": doc["id"],
                            "title": doc["title"],
                            "passage_id": f"{doc['id']}-{index}",
                            "text": passage,
                            "score": str(overlap),
                        },
                    )
                )
    scored.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in scored[:top_k]]


def answer_from_sources(question: str, passages: list[dict[str, str]]) -> str:
    if not passages:
        return "No relevant passages found in the document collection."
    joined = " ".join(passage["text"] for passage in passages[:2])
    return (
        f"Based on the retrieved sources for '{question}': {joined} "
        f"(sources: {', '.join(p['passage_id'] for p in passages)})"
    )
