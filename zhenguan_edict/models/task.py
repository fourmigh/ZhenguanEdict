from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from zhenguan_edict.interfaces.task import TaskState


@dataclass
class TaskModel:
    task_id: str
    title: str
    content: str
    state: TaskState
    dynasty: str
    assigned_role: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
