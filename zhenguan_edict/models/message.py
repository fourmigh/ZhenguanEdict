from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class MessageModel:
    message_id: str
    task_id: str
    sender_id: str
    sender_role: str
    receiver_id: str
    receiver_role: str
    content: str
    message_type: str
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
