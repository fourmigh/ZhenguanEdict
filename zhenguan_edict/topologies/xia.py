from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import ColorScheme, CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class XiaTopology(BaseDynastyTopology):
    name = "xia"
    display_name = "夏 · Xia"
    description = "线性三层流水线——规划→审查→执行，最早的分工协作模式。"
    edict_name = "命"
    color_scheme = ColorScheme(accent="#4A8C6F", accent_dim="#2D5A3D", bg="#04140a", bg2="#0a1e12", bg3="#122a1c", border="#1c3828")

    roles: Dict[str, RoleDefinition] = {
        "king": RoleDefinition(
            role_id="king",
            display_name="王",
            abstract_layer="decision",
            model_type="planner",
            description="需求分析、方案设计、决策审批",
            representative="大禹",
        ),
        "priest": RoleDefinition(
            role_id="priest",
            display_name="祭司",
            abstract_layer="review",
            model_type="reviewer",
            description="方案评审、代码审查、质量验收",
            representative="羲和",
            can_review=True,
            can_reject=True,
        ),
        "gongzheng": RoleDefinition(
            role_id="gongzheng",
            display_name="工正",
            abstract_layer="execution",
            model_type="coder",
            description="编码实现、构建部署、技术执行",
            representative="皋陶",
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
