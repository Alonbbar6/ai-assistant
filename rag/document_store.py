"""
RAG document store using ChromaDB.
Index local files/PDFs, then query them with semantic search.
"""

import hashlib
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_DIR


def _get_collection() -> Any:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection("documents", embedding_function=ef)


def index_document(path: str, chunk_size: int = 800, overlap: int = 100) -> str:
    """Chunk and embed a text or PDF file into the vector store."""
    path = Path(path)
    if not path.exists():
        return f"File not found: {path}"

    if path.suffix.lower() == ".pdf":
        from tools.pdf_tool import extract_pdf_text
        text = extract_pdf_text(str(path))
    else:
        try:
            text = path.read_text(errors="replace")
        except Exception as e:
            return f"Could not read file: {e}"

    chunks = _chunk_text(text, chunk_size, overlap)
    if not chunks:
        return "No text content found in document."

    collection = _get_collection()
    doc_id = hashlib.md5(str(path).encode()).hexdigest()

    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metas = [{"source": str(path), "chunk": i, "filename": path.name} for i in range(len(chunks))]

    # Remove old chunks for this document before re-indexing
    try:
        old = collection.get(where={"source": str(path)})
        if old["ids"]:
            collection.delete(ids=old["ids"])
    except Exception:
        pass

    collection.add(documents=chunks, ids=ids, metadatas=metas)
    return f"Indexed {len(chunks)} chunks from {path.name}"


def query_documents(question: str, top_k: int = 5) -> list[dict]:
    """Semantic search over indexed documents. Returns ranked passages."""
    collection = _get_collection()
    try:
        results = collection.query(query_texts=[question], n_results=top_k)
    except Exception as e:
        return [{"error": str(e)}]

    passages = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        passages.append({
            "text": doc,
            "source": meta.get("filename", "unknown"),
            "path": meta.get("source", ""),
            "relevance": round(1 - dist, 3),
        })
    return passages


def list_indexed_documents() -> list[str]:
    """Return filenames of all indexed documents."""
    collection = _get_collection()
    all_metas = collection.get(include=["metadatas"])["metadatas"]
    seen = set()
    names = []
    for m in all_metas:
        src = m.get("source", "")
        if src not in seen:
            seen.add(src)
            names.append(src)
    return names


def _chunk_text(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = " ".join(words[i : i + size])
        if chunk.strip():
            chunks.append(chunk)
        i += size - overlap
    return chunks
