"""奏折持久化存储。

对应架构文档：
- 每个任务产生一份奏折——其生命周期的结构化记录
- 持久化存储（SQLite 或 Markdown 文件）
- 完整审计线索，不可篡改
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from zhenguan_edict.interfaces.memorial import Memorial, MemorialEntry


class MemorialStore:
    def __init__(self, db_path: str = "./memorials.db"):
        self._db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self._db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorials (
                memorial_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                task_title TEXT NOT NULL,
                dynasty TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                entries TEXT NOT NULL DEFAULT '[]'
            )
        """)
        conn.commit()
        conn.close()

    def save(self, memorial: Memorial) -> None:
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            """INSERT OR REPLACE INTO memorials
               (memorial_id, task_id, task_title, dynasty, created_at, completed_at, entries)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                memorial.memorial_id,
                memorial.task_id,
                memorial.task_title,
                memorial.dynasty,
                memorial.created_at.isoformat(),
                memorial.completed_at.isoformat() if memorial.completed_at else None,
                json.dumps(
                    [
                        {
                            "sequence": e.sequence,
                            "timestamp": e.timestamp.isoformat(),
                            "actor_role": e.actor_role,
                            "actor_id": e.actor_id,
                            "action": e.action,
                            "content": e.content,
                            "decision": e.decision,
                            "decision_reason": e.decision_reason,
                            "token_usage": e.token_usage,
                        }
                        for e in memorial.entries
                    ],
                    ensure_ascii=False,
                ),
            ),
        )
        conn.commit()
        conn.close()

    def get(self, memorial_id: str) -> Optional[dict]:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM memorials WHERE memorial_id = ?", (memorial_id,)
        ).fetchone()
        conn.close()
        if row is None:
            return None
        return dict(row)

    def list_by_dynasty(self, dynasty: str) -> List[dict]:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM memorials WHERE dynasty = ? ORDER BY created_at DESC",
            (dynasty,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def list_all(self, limit: int = 50) -> List[dict]:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM memorials ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]
