from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import ColorScheme, CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class ShangTopology(BaseDynastyTopology):
    name = "shang"
    display_name = "商 · Shang"
    description = "四节点流水线带预写日志。验证与执行分离，史官引入永久记录。"
    edict_name = "命"
    color_scheme = ColorScheme(accent="#E8E0D0", accent_dim="#A09888", bg="#181612", bg2="#201e1a", bg3="#2c2a26", border="#3e3c38", text="#e8e0d0", text_dim="#a09888", text_muted="#70685c")

    roles: Dict[str, RoleDefinition] = {
        "king": RoleDefinition(
            role_id="king",
            display_name="王",
            abstract_layer="decision",
            model_type="planner",
            description="国王：战略方向、资源分配",
            representative="商汤",
        ),
        "zhenren": RoleDefinition(
            role_id="zhenren",
            display_name="贞人",
            abstract_layer="review",
            model_type="reviewer",
            description="占卜官：独立验证、仪式审批",
            representative="巫咸",
            can_review=True,
            can_reject=True,
        ),
        "shiguan": RoleDefinition(
            role_id="shiguan",
            display_name="史官",
            abstract_layer="record",
            model_type="documenter",
            description="书记官：记录决策、维护档案",
            representative="伊尹",
        ),
        "gongzheng": RoleDefinition(
            role_id="gongzheng",
            display_name="工正",
            abstract_layer="execution",
            model_type="coder",
            description="工程主管：跨项目执行",
            representative="傅说",
            can_execute=True,
        ),
    }

    communication_rules: List[CommunicationMatrix] = [
        CommunicationMatrix("king", "zhenren"),
        CommunicationMatrix("king", "shiguan"),
        CommunicationMatrix("king", "gongzheng"),
        CommunicationMatrix("zhenren", "king"),
        CommunicationMatrix("zhenren", "shiguan"),
        CommunicationMatrix("zhenren", "gongzheng"),
        CommunicationMatrix("shiguan", "zhenren"),
        CommunicationMatrix("shiguan", "gongzheng"),
        CommunicationMatrix("gongzheng", "king"),
        CommunicationMatrix("gongzheng", "shiguan"),
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
        StateTransition("executing", "validating"),
        StateTransition("validating", "completed"),
    ]
