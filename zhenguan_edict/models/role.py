from dataclasses import dataclass, field
from typing import List


@dataclass
class RoleModel:
    role_id: str
    display_name: str
    abstract_layer: str
    model_type: str
    description: str = ""
    can_reject: bool = False
    can_review: bool = False
    can_execute: bool = False
    skills: List[str] = field(default_factory=list)
