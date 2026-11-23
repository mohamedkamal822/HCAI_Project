import json
import logging
from pathlib import Path
from threading import Lock


class JsonlAuditLog:
    def __init__(self, directory: Path):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._logger = logging.getLogger(__name__)

    def append(self, name: str, record: dict) -> None:
        path = self.directory / name
        try:
            line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
            with self._lock, path.open("a", encoding="utf-8") as file:
                file.write(line + "\n")
        except OSError:
            self._logger.exception("Could not append an audit log record to %s", path)
