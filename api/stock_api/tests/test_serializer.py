from app.services.serializer import sanitize_for_json
import numpy as np

def test_sanitize_for_json():
    obj = {"a": np.nan, "b": float("inf"), "c": [1.0, np.float64("nan")]}
    out = sanitize_for_json(obj)
    assert out["a"] is None
    assert out["b"] is None
    assert out["c"][1] is None
