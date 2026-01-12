from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class _Entry:
    value: Any
    expire_at: float


class TTLCache:
    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self._data: dict[str, _Entry] = {}

    def get(self, key: str):
        ent = self._data.get(key)
        if ent is None:
            return None
        if time.time() >= ent.expire_at:
            self._data.pop(key, None)
            return None
        return ent.value

    def set(self, key: str, value: Any):
        self._data[key] = _Entry(value=value, expire_at=time.time() + self.ttl_seconds)
