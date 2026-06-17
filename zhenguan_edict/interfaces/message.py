from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class Message(ABC):

    @property
    @abstractmethod
    def message_id(self) -> str:
        ...

    @property
    @abstractmethod
    def task_id(self) -> str:
        ...

    @property
    @abstractmethod
    def sender_id(self) -> str:
        ...

    @property
    @abstractmethod
    def sender_role(self) -> str:
        ...

    @property
    @abstractmethod
    def receiver_id(self) -> str:
        ...

    @property
    @abstractmethod
    def receiver_role(self) -> str:
        ...

    @property
    @abstractmethod
    def content(self) -> str:
        ...

    @property
    @abstractmethod
    def message_type(self) -> str:
        ...

    @property
    @abstractmethod
    def created_at(self) -> datetime:
        ...

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        ...
