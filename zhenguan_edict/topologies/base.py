from typing import Dict, List, Optional, Set

from zhenguan_edict.interfaces.dynasty import (
    CommunicationMatrix,
    DynastyTopology,
    RoleDefinition,
    StateMachineConfig,
    StateTransition,
)


class BaseDynastyTopology(DynastyTopology):

    name = "base"
    display_name = "Base"
    description = ""
    roles: Dict[str, RoleDefinition] = {}
    communication_rules: List[CommunicationMatrix] = []
    state_machine_config: StateMachineConfig = StateMachineConfig(
        initial_state="new",
        states={
            "new": "新建",
            "pending": "待处理",
            "planning": "规划中",
            "reviewing": "审核中",
            "replanning": "重新规划",
            "dispatching": "派发中",
            "executing": "执行中",
            "validating": "验证中",
            "completed": "已完成",
        },
        transitions=[
            StateTransition("new", "pending"),
            StateTransition("pending", "planning"),
            StateTransition("planning", "reviewing"),
            StateTransition("reviewing", "replanning", condition="rejected"),
            StateTransition("replanning", "planning"),
            StateTransition("reviewing", "dispatching", condition="approved"),
            StateTransition("dispatching", "executing"),
            StateTransition("executing", "validating"),
            StateTransition("validating", "completed"),
        ],
    )

    def can_communicate(
        self, sender_role: str, receiver_role: str, message_type: str = "*"
    ) -> bool:
        for rule in self.communication_rules:
            if rule.sender_role == sender_role and rule.receiver_role == receiver_role:
                if message_type in rule.allowed_message_types or "*" in rule.allowed_message_types:
                    return True
        return False

    def get_role(self, role_id: str) -> Optional[RoleDefinition]:
        return self.roles.get(role_id)
