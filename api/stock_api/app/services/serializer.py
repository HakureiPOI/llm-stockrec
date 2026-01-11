from __future__ import annotations

import math
from typing import Any

import numpy as np

def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively convert NaN/Inf to None for strict JSON compliance.
    """
    # numpy scalar -> python scalar
    if isinstance(obj, (np.floating, np.integer)):
        obj = obj.item()

    if isinstance(obj, float):
        if not math.isfinite(obj) or math.isnan(obj):
            return None
        return obj

    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]

    return obj
