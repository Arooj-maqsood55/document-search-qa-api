import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import load_documents, retrieve


def test_retrieve_finds_llm_doc():
    docs = load_documents()
    hits = retrieve("How do reviewers score factual accuracy?", docs, top_k=2)
    assert hits
    assert any("llm_evaluation" in hit["source"] for hit in hits)
