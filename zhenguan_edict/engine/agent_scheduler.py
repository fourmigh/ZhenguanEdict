import asyncio
import tempfile
from typing import Dict, List, Optional

from zhenguan_edict.interfaces.agent import Agent
from zhenguan_edict.interfaces.task import Task


class AgentScheduler:
    """Agent 调度器：管理实际执行——将任务分配到模型实例。

    对应架构文档中的描述：
    - 为并行执行创建 Worktree
    - 管理队列积压
    - 处理重试和失败
    - 按需创建/移除 Agent 实例
    """

    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._worktrees: Dict[str, str] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._max_retries: int = 3

    def register_agent(self, agent: Agent) -> None:
        self._agents[agent.agent_id] = agent

    def unregister_agent(self, agent_id: str) -> None:
        self._agents.pop(agent_id, None)

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self._agents.get(agent_id)

    def list_agents(self) -> List[Agent]:
        return list(self._agents.values())

    def get_idle_agents(self, role_id: Optional[str] = None) -> List[Agent]:
        result = []
        for agent in self._agents.values():
            if not agent.is_busy:
                if role_id is None or agent.role_id == role_id:
                    result.append(agent)
        return result

    def create_worktree(self, agent_id: str, base_branch: str = "main") -> str:
        path = tempfile.mkdtemp(prefix=f"worktree_{agent_id}_")
        self._worktrees[agent_id] = path
        return path

    def destroy_worktree(self, agent_id: str) -> None:
        path = self._worktrees.pop(agent_id, None)
        if path is not None:
            import shutil
            shutil.rmtree(path, ignore_errors=True)

    def get_worktree(self, agent_id: str) -> Optional[str]:
        return self._worktrees.get(agent_id)

    async def enqueue_task(self, task: Task) -> None:
        await self._queue.put(task)

    async def dequeue_task(self) -> Optional[Task]:
        try:
            return await asyncio.wait_for(self._queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None

    async def dispatch(self, task: Task, agent: Agent) -> None:
        response = await agent.process(task)

    def queue_size(self) -> int:
        return self._queue.qsize()
