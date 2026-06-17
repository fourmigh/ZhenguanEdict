from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskState(str, Enum):
    NEW = "new"
    PENDING = "pending"
    PLANNING = "planning"
    REVIEWING = "reviewing"
    REPLANNING = "replanning"
    DISPATCHING = "dispatching"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Task(ABC):

    @property
    @abstractmethod
    def task_id(self) -> str:
        ...

    @property
    @abstractmethod
    def title(self) -> str:
        ...

    @property
    @abstractmethod
    def content(self) -> str:
        ...

    @property
    @abstractmethod
    def state(self) -> TaskState:
        ...

    @property
    @abstractmethod
    def dynasty(self) -> str:
        ...

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def transition(self, new_state: TaskState, reason: str = "") -> None:
        ...

    @abstractmethod
    def assign_role(self, role_id: str) -> None:
        ...
