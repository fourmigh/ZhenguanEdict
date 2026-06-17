from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from zhenguan_edict.interfaces.memorial import MemorialEntry


@dataclass
class MemorialModel:
    memorial_id: str
    task_id: str
    task_title: str
    dynasty: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    entries: List[MemorialEntry] = field(default_factory=list)

    @property
    def total_token_usage(self) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for entry in self.entries:
            for k, v in entry.token_usage.items():
                result[k] = result.get(k, 0) + v
        return result
