"""
Cache Service — Redis/Upstash caching with graceful fallback.

If Redis is unavailable, all operations silently no-op so the app
continues to function without caching.
"""

import os
import json
import hashlib
from typing import Optional

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False


CACHE_TTL = 3600  # 1 hour


class CacheService:
    def __init__(self):
        self.client = None
        self.enabled = False

        if not HAS_REDIS:
            print("[Cache] redis package not installed. Caching disabled.")
            return

        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            print("[Cache] REDIS_URL not set. Caching disabled.")
            return

        try:
            self.client = redis.from_url(redis_url, decode_responses=True, socket_timeout=2)
            self.client.ping()
            self.enabled = True
            print("[Cache] Connected to Redis successfully.")
        except Exception as e:
            print(f"[Cache] Failed to connect to Redis: {e}. Caching disabled.")
            self.client = None
            self.enabled = False

    def _make_key(self, user_id: str, audit_id: str, question: str) -> str:
        """Generate a cache key from user, audit, and question."""
        q_hash = hashlib.sha256(question.lower().strip().encode()).hexdigest()[:16]
        return f"chat:{user_id}:{audit_id}:{q_hash}"

    def get_cached_answer(self, user_id: str, audit_id: str, question: str) -> Optional[dict]:
        """Retrieve a cached chat response. Returns None if not found or cache disabled."""
        if not self.enabled:
            return None

        try:
            key = self._make_key(user_id, audit_id, question)
            data = self.client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"[Cache] Get error: {e}")

        return None

    def cache_answer(self, user_id: str, audit_id: str, question: str, answer: str, sources: list):
        """Cache a chat response with TTL."""
        if not self.enabled:
            return

        try:
            key = self._make_key(user_id, audit_id, question)
            payload = json.dumps({"answer": answer, "sources": sources})
            self.client.setex(key, CACHE_TTL, payload)
        except Exception as e:
            print(f"[Cache] Set error: {e}")
