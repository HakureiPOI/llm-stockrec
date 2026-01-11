from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional, Tuple


class TTLCache:
    def __init__(self, ttl_seconds: int = 60):
        self.ttl = max(1, ttl_seconds)
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        ts, value = item
        if time.time() - ts > self.ttl:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time(), value)


def cache_ttl_from_env(default: int = 60) -> int:
    try:
        return int(os.getenv("CACHE_TTL_SECONDS", str(default)))
    except Exception:
        return default
