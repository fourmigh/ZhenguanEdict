from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class XiaTopology(BaseDynastyTopology):
    name = "xia"
    display_name = "夏 · Xia"
    description = "线性三层。祭司作为占卜关卡——最早的 QA 审批节点。"

    roles: Dict[str, RoleDefinition] = {
        "king": RoleDefinition(
            role_id="king",
            display_name="王",
            abstract_layer="decision",
            model_type="planner",
            description="国王：目标设定、最终批准",
        ),
        "priest": RoleDefinition(
            role_id="priest",
            display_name="祭司",
            abstract_layer="review",
            model_type="reviewer",
            description="占卜官：质量检查、解读天意",
            can_review=True,
            can_reject=True,
        ),
        "gongzheng": RoleDefinition(
            role_id="gongzheng",
            display_name="工正",
            abstract_layer="execution",
            model_type="coder",
            description="工程主管：执行、建设、实施",
            can_execute=True,
        ),
    }

    communication_rules: List[CommunicationMatrix] = [
        CommunicationMatrix("king", "priest"),
        CommunicationMatrix("king", "gongzheng"),
        CommunicationMatrix("priest", "king"),
        CommunicationMatrix("priest", "gongzheng"),
        CommunicationMatrix("gongzheng", "king"),
    ]

    state_machine_config = BaseDynastyTopology.state_machine_config.copy()
    state_machine_config.transitions = [
        StateTransition("new", "pending"),
        StateTransition("pending", "planning"),
        StateTransition("planning", "reviewing"),
        StateTransition("reviewing", "replanning", condition="rejected"),
        StateTransition("replanning", "planning"),
        StateTransition("reviewing", "dispatching", condition="approved"),
        StateTransition("dispatching", "executing"),
        StateTransition("executing", "completed"),
    ]
