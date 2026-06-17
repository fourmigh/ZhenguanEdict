from typing import Dict, List, Optional, Set

from zhenguan_edict.interfaces.dynasty import DynastyTopology
from zhenguan_edict.interfaces.task import Task, TaskState


class TaskStateMachine:
    """任务状态机：管理每个任务在 9 个状态间的生命周期流转。

    状态机是朝代感知的——有些朝代跳过审核（炎黄），有些增加多重审核（宋）。
    标准流转：
        新建 → 待处理 → 规划中 → 审核中 → (驳回 → 重新规划 → 审核中)
                → 派发中 → 执行中 → 验证中 → 已完成
    """

    def __init__(self, topology: Optional[DynastyTopology] = None):
        self._topology = topology

    @property
    def topology(self) -> Optional[DynastyTopology]:
        return self._topology

    @topology.setter
    def topology(self, value: DynastyTopology) -> None:
        self._topology = value

    def _build_transition_map(
        self, topology: DynastyTopology
    ) -> Dict[TaskState, Set[TaskState]]:
        trans_map: Dict[TaskState, Set[TaskState]] = {}
        for t in topology.state_machine_config.transitions:
            from_state = TaskState(t.from_state)
            to_state = TaskState(t.to_state)
            if from_state not in trans_map:
                trans_map[from_state] = set()
            trans_map[from_state].add(to_state)
        return trans_map

    def allowed_transitions(self, current_state: TaskState) -> List[TaskState]:
        if self._topology is None:
            return []
        trans_map = self._build_transition_map(self._topology)
        return list(trans_map.get(current_state, set()))

    def can_transition(self, task: Task, target_state: TaskState) -> bool:
        allowed = self.allowed_transitions(task.state)
        return target_state in allowed

    async def transition(self, task: Task, target_state: TaskState, reason: str = "") -> Task:
        if not self.can_transition(task, target_state):
            raise ValueError(
                f"Cannot transition from {task.state.value} to {target_state.value} "
                f"in dynasty '{task.dynasty}'"
            )
        await task.transition(target_state, reason)
        return task
