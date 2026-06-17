"""Sub-agent 管理：分离制定者和检查者。

古代对应：封驳 / 审核制度——唐代门下省封驳权，
规划者（中书省）和审查者（门下省）严格分离。
"""

import uuid
from typing import Dict, Optional

from zhenguan_edict.interfaces.agent import Agent
from zhenguan_edict.interfaces.task import Task


class SubAgentManager:
    """管理 Sub-agent 的创建和生命周期。

    对应文档中的实现思路：
    - 当某朝代拓扑包含审核角色时，生成独立的 Sub-agent 用于验证
    - 审查者接收制定者的输出，对照 Skill 中定义的质量标准进行评估
    - 如被驳回，任务连同反馈一起返回给制定者
    """

    def __init__(self):
        self._reviewers: Dict[str, Agent] = {}
        self._planners: Dict[str, Agent] = {}
        self._executors: Dict[str, Agent] = {}

    def register_planner(self, agent: Agent) -> None:
        self._planners[agent.agent_id] = agent

    def register_reviewer(self, agent: Agent) -> None:
        self._reviewers[agent.agent_id] = agent

    def register_executor(self, agent: Agent) -> None:
        self._executors[agent.agent_id] = agent

    def get_reviewer(self, role_id: str) -> Optional[Agent]:
        for agent in self._reviewers.values():
            if agent.role_id == role_id and not agent.is_busy:
                return agent
        return None

    def get_planner(self, role_id: str) -> Optional[Agent]:
        for agent in self._planners.values():
            if agent.role_id == role_id and not agent.is_busy:
                return agent
        return None

    def get_executor(self, role_id: str) -> Optional[Agent]:
        for agent in self._executors.values():
            if agent.role_id == role_id and not agent.is_busy:
                return agent
        return None

    def create_review_session(self, task: Task, reviewer_agent: Agent) -> str:
        session_id = str(uuid.uuid4())
        return session_id
