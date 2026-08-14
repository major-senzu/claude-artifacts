"""チャットごとのセッション状態（直前に生成したファイル名）を保持する。"""
import json
import threading
from pathlib import Path
from typing import Optional


class SessionStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self._data = {}
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def get_last_file(self, chat_id) -> Optional[str]:
        return self._data.get(str(chat_id), {}).get("last_file")

    def set_last_file(self, chat_id, filename: str) -> None:
        with self._lock:
            self._data.setdefault(str(chat_id), {})["last_file"] = filename
            self.path.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
