from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MemorialEntry:
    sequence: int
    timestamp: datetime
    actor_role: str
    actor_id: str
    action: str
    content: str
    decision: Optional[str] = None
    decision_reason: Optional[str] = None
    token_usage: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class Memorial(ABC):

    @property
    @abstractmethod
    def memorial_id(self) -> str:
        ...

    @property
    @abstractmethod
    def task_id(self) -> str:
        ...

    @property
    @abstractmethod
    def task_title(self) -> str:
        ...

    @property
    @abstractmethod
    def dynasty(self) -> str:
        ...

    @property
    @abstractmethod
    def created_at(self) -> datetime:
        ...

    @property
    @abstractmethod
    def completed_at(self) -> Optional[datetime]:
        ...

    @property
    @abstractmethod
    def entries(self) -> List[MemorialEntry]:
        ...

    @property
    @abstractmethod
    def total_token_usage(self) -> Dict[str, int]:
        ...

    @abstractmethod
    def add_entry(self, entry: MemorialEntry) -> None:
        ...
