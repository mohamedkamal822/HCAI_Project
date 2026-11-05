from collections import OrderedDict
from uuid import uuid4


class TraceStore:
    def __init__(self, max_items: int):
        self._items = OrderedDict()
        self._max_items = max_items

    def add(self, trace: dict) -> str:
        trace_id = str(uuid4())
        trace["trace_id"] = trace_id
        self._items[trace_id] = trace
        if len(self._items) > self._max_items:
            self._items.popitem(last=False)
        return trace_id

    def get(self, trace_id: str) -> dict | None:
        return self._items.get(trace_id)
