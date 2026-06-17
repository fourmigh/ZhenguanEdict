"""Worktree 管理：为并行 Agent 提供隔离的工作空间。

古代对应：分封制（诸侯独立领地）/ 郡县制（统一规则下的标准单元）。
"""

import shutil
import tempfile
from typing import Dict, Optional


class WorktreeManager:
    """管理隔离的并行工作空间。

    对应文档中的实现思路：
    - 当拓扑要求并行执行时，调度器创建隔离的 Worktree
    - 临时目录，各自拥有独立的工作状态
    - 一个 Agent 的故障不会影响其他 Agent
    """

    def __init__(self):
        self._workspaces: Dict[str, str] = {}

    def create(self, agent_id: str, label: str = "") -> str:
        prefix = f"worktree_{label}_{agent_id}_" if label else f"worktree_{agent_id}_"
        path = tempfile.mkdtemp(prefix=prefix)
        self._workspaces[agent_id] = path
        return path

    def get(self, agent_id: str) -> Optional[str]:
        return self._workspaces.get(agent_id)

    def destroy(self, agent_id: str) -> None:
        path = self._workspaces.pop(agent_id, None)
        if path:
            shutil.rmtree(path, ignore_errors=True)

    def destroy_all(self) -> None:
        for agent_id in list(self._workspaces.keys()):
            self.destroy(agent_id)

    def list_active(self) -> Dict[str, str]:
        return dict(self._workspaces)
