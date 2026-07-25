"""Owned by Member B: wraps RAG retrieval behind the AgriTool interface.

Backed by a persistent ChromaDB collection, auto-seeded on first use from the
static agronomy knowledge base in app/data/knowledge_base.py.
"""

import threading

import chromadb

from app.config import get_settings
from app.data.knowledge_base import KNOWLEDGE_BASE
from app.schemas.tool_io import RAGInput, RAGOutput, RetrievedPassage
from app.tools.base import AgriTool

settings = get_settings()

_lock = threading.Lock()
_collection = None


def _get_collection():
    global _collection
    if _collection is not None:
        return _collection
    with _lock:
        if _collection is not None:
            return _collection
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        collection = client.get_or_create_collection(name=settings.chroma_collection_name)
        if collection.count() == 0:
            collection.add(
                ids=[doc["id"] for doc in KNOWLEDGE_BASE],
                documents=[doc["text"] for doc in KNOWLEDGE_BASE],
                metadatas=[{"source": doc["source"]} for doc in KNOWLEDGE_BASE],
            )
        _collection = collection
        return _collection


class RAGTool(AgriTool):
    name = "rag_search"
    description = (
        "Searches the agronomy knowledge base for passages relevant to a query "
        "(e.g. crop-soil fit, water needs, seasonal suitability). Call this to "
        "ground crop recommendations in retrieved evidence rather than guessing."
    )
    input_schema = RAGInput
    output_schema = RAGOutput

    def run(self, input_data: RAGInput) -> RAGOutput:
        collection = _get_collection()
        result = collection.query(
            query_texts=[input_data.query],
            n_results=input_data.n_results,
        )

        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0] if result.get("distances") else []

        results = [
            RetrievedPassage(
                text=documents[i],
                source=(metadatas[i] or {}).get("source", "unknown"),
                score=distances[i] if i < len(distances) else None,
            )
            for i in range(len(documents))
        ]

        return RAGOutput(
            passages=[r.text for r in results],
            sources=[r.source for r in results],
            results=results,
        )
