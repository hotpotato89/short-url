from datetime import datetime
from decimal import Decimal
import hashlib
import json
from typing import Any


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "hex"):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def _gen_cache_key(
    func_name: str,
    args: tuple,
    kwargs: dict,
    prefix: str | None = None,
) -> str:
    cleaned_args = args[1:] if args and hasattr(args[1:], "__class__") else args
    sorted_kwargs = sorted(dict(kwargs.items()))

    data = {
        "func_name": func_name,
        "args": cleaned_args,
        "kwargs": sorted_kwargs,
    }

    cache_key = hashlib.sha256(
        json.dumps(data, default=str, sort_keys=True).encode()
    ).hexdigest()

    base_key = f"cache:{cache_key}"
    if prefix:
        return f"cache:{prefix}:{base_key}"
    return base_key
