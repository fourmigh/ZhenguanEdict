from abc import ABC, abstractmethod
from typing import Optional


class Agent(ABC):

    @property
    @abstractmethod
    def agent_id(self) -> str:
        ...

    @property
    @abstractmethod
    def role_id(self) -> str:
        ...

    @property
    @abstractmethod
    def model_type(self) -> str:
        ...

    @property
    @abstractmethod
    def is_busy(self) -> bool:
        ...

    @abstractmethod
    async def process(self, task: "Task") -> "Message":
        ...
