from typing import Optional

from zhenguan_edict.interfaces.dynasty import DynastyTopology
from zhenguan_edict.interfaces.message import Message


class RoutingEngine:
    """路由引擎：执行当前朝代的权限矩阵定义的通信规则。

    对应架构文档中的描述：
    - 决定哪些 Agent 可以和谁通信
    - 允许什么消息类型
    - 消息是否需要审批后才能转发
    """

    def __init__(self, topology: Optional[DynastyTopology] = None):
        self._topology = topology

    @property
    def topology(self) -> Optional[DynastyTopology]:
        return self._topology

    @topology.setter
    def topology(self, value: DynastyTopology) -> None:
        self._topology = value

    def can_send(
        self, sender_role: str, receiver_role: str, message_type: str = "*"
    ) -> bool:
        if self._topology is None:
            return False
        return self._topology.can_communicate(sender_role, receiver_role, message_type)

    def route_message(self, message: Message) -> bool:
        if self._topology is None:
            return False
        return self.can_send(
            message.sender_role,
            message.receiver_role,
            message.message_type,
        )

    def validate_route(
        self, sender_role: str, receiver_role: str, message_type: str = "*"
    ) -> str:
        if self._topology is None:
            return "no_topology_loaded"
        if self.can_send(sender_role, receiver_role, message_type):
            return "allowed"
        return "blocked"
