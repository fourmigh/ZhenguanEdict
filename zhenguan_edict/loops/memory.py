"""三层记忆系统：跨运行持久化的状态。

古代对应：起居注（热）→ 实录（温）→ 国史（冷）
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MemoryEntry:
    key: str
    value: Any
    timestamp: float
    ttl: Optional[float] = None


class HotMemory:
    """热记忆（起居注）：活跃任务状态、当前会话。存储于内存。"""

    def __init__(self):
        self._store: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    def list_keys(self) -> List[str]:
        return list(self._store.keys())


class WarmMemory:
    """温记忆（实录）：已完成奏折、近期历史。存储为 JSON/Markdown。"""

    def __init__(self, storage_path: str = "./memory/warm"):
        self._storage_path = storage_path

    def store(self, key: str, data: Any) -> None:
        pass

    def retrieve(self, key: str) -> Optional[Any]:
        return None


class ColdMemory:
    """冷记忆（国史）：历史数据、长期模式。持久化到平面文件或数据库。"""

    def __init__(self, archive_path: str = "./memory/cold"):
        self._archive_path = archive_path

    def archive(self, key: str, data: Any) -> None:
        pass

    def query(self, pattern: str) -> List[Any]:
        return []


class MemoryManager:
    """三层记忆管理器，提供统一接口。"""

    def __init__(self):
        self.hot = HotMemory()
        self.warm = WarmMemory()
        self.cold = ColdMemory()
