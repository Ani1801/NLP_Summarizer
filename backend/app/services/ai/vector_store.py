"""
VectorStoreService — embedding generation and vector indexing.

Chunks produced by PDFProcessor are embedded with
`sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) and upserted into
Pinecone under a per-user namespace (`user_{user_id}`), so one user's contracts
are never retrievable from another user's session.

If `PINECONE_API_KEY` is absent (or Pinecone is unreachable), the service falls
back to a local in-memory index with the same API, so the application remains
fully functional for development without any cloud vector database. The local
index is persisted to disk so it survives a backend restart.

The embedding model is loaded lazily on first use — importing this module must
stay cheap, because the API routes instantiate the service at import time.
"""

from __future__ import annotations

import math
import os
import pickle
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from langchain_core.documents import Document

from app.services.ai.processor import classify_clause_type

from app.core.config import settings
from app.core.logging import logger

# Metadata values longer than this are truncated before being sent to Pinecone,
# which caps total metadata size per vector.
MAX_METADATA_TEXT = 1500


def namespace_for(user_id: str) -> str:
    """Pinecone namespace for a user — the isolation boundary."""
    return f"user_{user_id}"


# ─────────────────────────────────────────────────────────────────────────────
# Local fallback index
# ─────────────────────────────────────────────────────────────────────────────
class LocalVectorIndex:
    """
    Minimal cosine-similarity vector index used when Pinecone is unavailable.

    Vectors live in memory and are mirrored to a pickle file under the uploads
    directory, so an audit indexed before a restart is still searchable after.
    """

    def __init__(self, persist_path: Path):
        self._persist_path = persist_path
        self._lock = threading.Lock()
        # namespace -> list of (vector, text, metadata)
        self._store: Dict[str, List[Tuple[List[float], str, dict]]] = {}
        self._load()

    def _load(self) -> None:
        if not self._persist_path.exists():
            return
        try:
            with open(self._persist_path, "rb") as fh:
                self._store = pickle.load(fh)
            total = sum(len(v) for v in self._store.values())
            logger.info(f"[VectorStore:local] restored {total} vector(s) from disk")
        except Exception as e:
            logger.warning(f"[VectorStore:local] could not restore index: {e}")
            self._store = {}

    def _save(self) -> None:
        try:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._persist_path, "wb") as fh:
                pickle.dump(self._store, fh)
        except Exception as e:
            logger.warning(f"[VectorStore:local] could not persist index: {e}")

    def add(self, namespace: str, vectors: List[List[float]], texts: List[str],
            metadatas: List[dict]) -> None:
        with self._lock:
            bucket = self._store.setdefault(namespace, [])
            bucket.extend(zip(vectors, texts, metadatas))
            self._save()

    def search(self, namespace: str, query_vector: List[float], k: int,
               filters: Optional[dict] = None) -> List[Tuple[float, str, dict]]:
        with self._lock:
            bucket = list(self._store.get(namespace, []))

        scored: List[Tuple[float, str, dict]] = []
        for vector, text, metadata in bucket:
            if filters and any(metadata.get(key) != value for key, value in filters.items()):
                continue
            scored.append((self._cosine(query_vector, vector), text, metadata))
        scored.sort(key=lambda row: row[0], reverse=True)
        return scored[:k]

    def delete(self, namespace: str, filters: dict) -> int:
        with self._lock:
            bucket = self._store.get(namespace, [])
            kept = [
                row for row in bucket
                if any(row[2].get(key) != value for key, value in filters.items())
            ]
            removed = len(bucket) - len(kept)
            self._store[namespace] = kept
            self._save()
        return removed

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# ─────────────────────────────────────────────────────────────────────────────
# Vector store service
# ─────────────────────────────────────────────────────────────────────────────
class VectorStoreService:
    def __init__(self):
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "legal-auditor")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY") or ""
        self.pinecone_host = os.getenv("PINECONE_HOST") or ""
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

        self._embeddings = None
        self._local_index: Optional[LocalVectorIndex] = None
        # None = not probed yet, True/False = Pinecone usable or not.
        self._pinecone_ok: Optional[bool] = None if self.pinecone_api_key else False

        if not self.pinecone_api_key:
            logger.warning(
                "[VectorStore] PINECONE_API_KEY not set — using the local in-memory index."
            )

    # ── Embeddings (lazy) ───────────────────────────────────────────────
    @property
    def embeddings(self):
        """The HuggingFace embedding model, loaded on first access."""
        if self._embeddings is None:
            from langchain_huggingface import HuggingFaceEmbeddings

            logger.info(f"[VectorStore] loading embedding model '{self.model_name}'...")
            self._embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
        return self._embeddings

    @property
    def local_index(self) -> LocalVectorIndex:
        if self._local_index is None:
            base = Path(__file__).resolve().parents[3] / settings.UPLOAD_DIR
            self._local_index = LocalVectorIndex(base / ".local_vector_index.pkl")
        return self._local_index

    @property
    def backend(self) -> str:
        """
        Which index is in use — surfaced in API responses.

        Before the first call `_pinecone_ok` is None, meaning a key is configured
        but Pinecone has not been reached yet; report it as the intended backend.
        """
        return "local" if self._pinecone_ok is False else "pinecone"

    # ── Metadata ────────────────────────────────────────────────────────
    @staticmethod
    def build_metadata(chunk: Document, user_id: str, audit_id: str,
                       clause_type: Optional[str] = None) -> dict:
        """
        Flatten a chunk into the metadata stored next to its vector.

        `raw_text` is duplicated here so a retrieved match can be quoted
        verbatim in a citation without a second round trip to MongoDB.
        """
        source = chunk.metadata or {}
        if clause_type is None:
            clause_type = classify_clause_type(
                chunk.page_content, str(source.get("section_title", ""))
            )
        return {
            "user_id": user_id,
            "audit_id": audit_id,
            "doc_id": audit_id,
            "file_name": source.get("file_name", "document.pdf"),
            "page_number": int(source.get("page_number", 1) or 1),
            "section_ref": str(source.get("section_ref", "") or ""),
            "section_title": str(source.get("section_title", "") or ""),
            "section_label": str(source.get("section_label", "") or ""),
            "clause_type": clause_type,
            "raw_text": chunk.page_content[:MAX_METADATA_TEXT],
        }

    # ── Upsert ──────────────────────────────────────────────────────────
    def upsert_chunks(self, chunks: List[Document], user_id: str, audit_id: str) -> dict:
        """
        Embed and index every chunk under the user's namespace.

        Returns a summary dict: {"indexed": int, "backend": "pinecone"|"local"}.
        Never raises on a Pinecone outage — it degrades to the local index so an
        upload still completes and chat still works.
        """
        if not chunks:
            return {"indexed": 0, "backend": self.backend}

        namespace = namespace_for(user_id)
        texts, metadatas = [], []
        for chunk in chunks:
            metadata = self.build_metadata(chunk, user_id, audit_id)
            chunk.metadata.update(metadata)
            texts.append(chunk.page_content)
            metadatas.append(metadata)

        return self._upsert(texts, metadatas, namespace)

    # ── Canonical indexing ──────────────────────────────────────────────
    def index_document(self, document) -> dict:
        """
        Index a CanonicalDocument's chunks — the entry point the pipeline uses.

        Chunks already carry their page range, section and clause type, so
        nothing is recomputed here. Pinecone is not the source of truth for the
        text (MongoDB is), but `raw_text` rides along with each vector so a
        retrieved match can be quoted verbatim without a second round trip.
        """
        chunks = getattr(document, "chunks", None) or []
        if not chunks:
            return {"indexed": 0, "backend": self.backend}

        namespace = namespace_for(document.user_id)
        texts, metadatas = [], []
        for chunk in chunks:
            texts.append(chunk.text)
            metadatas.append({
                "user_id": chunk.user_id,
                "document_id": chunk.document_id,
                "doc_id": chunk.document_id,
                # The chat and comparison code filters on audit_id; the document
                # id and the audit id are the same value by design.
                "audit_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "file_name": document.file_name,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "page_number": chunk.page_start,
                "section_id": chunk.section_id,
                "section_number": chunk.section_number,
                "section_title": chunk.section_title,
                "section_label": chunk.section_label,
                # Classify on demand when the caller has not already done so,
                # so vector metadata always carries a real clause type.
                "clause_type": chunk.clause_type or classify_clause_type(
                    chunk.text, chunk.section_title
                ),
                "token_count": chunk.token_count,
                "raw_text": chunk.text[:MAX_METADATA_TEXT],
            })

        return self._upsert(texts, metadatas, namespace)

    def _upsert(self, texts, metadatas, namespace: str) -> dict:
        """Send vectors to Pinecone, degrading to the local index on failure."""
        if self._pinecone_ok is not False:
            try:
                self._pinecone_store().add_texts(
                    texts=texts, metadatas=metadatas, namespace=namespace
                )
                self._pinecone_ok = True
                logger.info(
                    f"[VectorStore] upserted {len(texts)} vector(s) to Pinecone ns={namespace}"
                )
                return {"indexed": len(texts), "backend": "pinecone"}
            except Exception as e:
                logger.warning(
                    f"[VectorStore] Pinecone upsert failed ({e}) — falling back to local index."
                )
                self._pinecone_ok = False

        vectors = self.embeddings.embed_documents(texts)
        self.local_index.add(namespace, vectors, texts, metadatas)
        logger.info(f"[VectorStore] upserted {len(texts)} vector(s) to local index ns={namespace}")
        return {"indexed": len(texts), "backend": "local"}

    # ── Search ──────────────────────────────────────────────────────────
    def search_similar(self, query: str, user_id: str, audit_id: str,
                       k: int = 5) -> List[Document]:
        """
        Cosine-similarity search restricted to one document inside one user's
        namespace. Returns LangChain Documents, so callers (the RAG chat) keep
        working unchanged.
        """
        if not query or not query.strip():
            return []

        namespace = namespace_for(user_id)
        filters = {"audit_id": audit_id}

        if self._pinecone_ok is not False:
            try:
                results = self._pinecone_store().similarity_search(
                    query, k=k, namespace=namespace, filter=filters
                )
                self._pinecone_ok = True
                if results:
                    return results
                # An empty Pinecone result may just mean this audit was indexed
                # locally during an earlier outage — try the local index too.
            except Exception as e:
                logger.warning(
                    f"[VectorStore] Pinecone search failed ({e}) — falling back to local index."
                )
                self._pinecone_ok = False

        query_vector = self.embeddings.embed_query(query)
        matches = self.local_index.search(namespace, query_vector, k=k, filters=filters)
        return [
            Document(page_content=text, metadata=metadata)
            for _score, text, metadata in matches
        ]

    # ── Delete ──────────────────────────────────────────────────────────
    def delete_audit_vectors(self, user_id: str, audit_id: str) -> None:
        """Remove every vector belonging to one audit (used on failed uploads)."""
        namespace = namespace_for(user_id)
        if self._pinecone_ok:
            try:
                self._pinecone_index().delete(
                    filter={"audit_id": audit_id}, namespace=namespace
                )
            except Exception as e:
                logger.warning(f"[VectorStore] Pinecone delete failed: {e}")
        if self._local_index is not None or not self._pinecone_ok:
            self.local_index.delete(namespace, {"audit_id": audit_id})

    # ── Pinecone plumbing ───────────────────────────────────────────────
    def _pinecone_index(self):
        from pinecone import Pinecone

        client = Pinecone(api_key=self.pinecone_api_key)
        if self.pinecone_host:
            return client.Index(host=self.pinecone_host)
        return client.Index(self.index_name)

    def _pinecone_store(self):
        """A PineconeVectorStore bound to the configured index."""
        from langchain_pinecone import PineconeVectorStore

        return PineconeVectorStore(
            index=self._pinecone_index(),
            embedding=self.embeddings,
            text_key="text",
        )


# Shared instance — the embedding model is heavy, so load it once per process.
vector_store_service = VectorStoreService()
