from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass(frozen=True)
class CommunicationMatrix:
    sender_role: str
    receiver_role: str
    allowed_message_types: Set[str] = field(default_factory=lambda: {"*"})


@dataclass
class StateTransition:
    from_state: str
    to_state: str
    condition: Optional[str] = None


@dataclass
class StateMachineConfig:
    initial_state: str = "new"
    states: Dict[str, str] = field(default_factory=dict)
    transitions: List[StateTransition] = field(default_factory=list)
    rejected_transition: Optional[str] = None
    role_mapping: Dict[str, str] = field(default_factory=dict)

    def copy(self) -> "StateMachineConfig":
        return StateMachineConfig(
            initial_state=self.initial_state,
            states=dict(self.states),
            transitions=[StateTransition(t.from_state, t.to_state, t.condition) for t in self.transitions],
            rejected_transition=self.rejected_transition,
            role_mapping=dict(self.role_mapping),
        )


@dataclass
class ColorScheme:
    accent: str = "#C9A84C"
    accent_dim: str = "#8B7332"
    bg: str = "#0f0c08"
    bg2: str = "#1a1410"
    bg3: str = "#2a221c"
    border: str = "#3a322c"
    text: str = "#e8ddd0"
    text_dim: str = "#9a8a7a"
    text_muted: str = "#6a5a4a"


@dataclass
class RoleDefinition:
    role_id: str
    display_name: str
    abstract_layer: str
    model_type: str
    description: str = ""
    can_reject: bool = False
    can_review: bool = False
    can_execute: bool = False


class DynastyTopology(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @property
    @abstractmethod
    def roles(self) -> Dict[str, RoleDefinition]:
        ...

    @property
    @abstractmethod
    def communication_rules(self) -> List[CommunicationMatrix]:
        ...

    @property
    @abstractmethod
    def state_machine_config(self) -> StateMachineConfig:
        ...

    @abstractmethod
    def can_communicate(
        self, sender_role: str, receiver_role: str, message_type: str = "*"
    ) -> bool:
        ...

    @abstractmethod
    def get_role(self, role_id: str) -> Optional[RoleDefinition]:
        ...
