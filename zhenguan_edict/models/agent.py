from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class AgentModel:
    agent_id: str
    role_id: str
    model_type: str
    display_name: str = ""
    is_busy: bool = False
    current_task_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    total_tokens_consumed: int = 0
    tasks_completed: int = 0
    skills: List[str] = field(default_factory=list)
