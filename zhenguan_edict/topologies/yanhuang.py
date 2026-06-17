from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import ColorScheme, CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class YanHuangTopology(BaseDynastyTopology):
    name = "yanhuang"
    display_name = "炎黄 · Yan-Huang"
    description = "部落联盟，二人分工。P2P 对等结构，无层级、无审核。"
    edict_name = "命"
    color_scheme = ColorScheme(accent="#D4A84B", accent_dim="#8B7332", bg="#1a0e04", bg2="#221810", bg3="#32281c", border="#4a3a28")

    roles: Dict[str, RoleDefinition] = {
        "yandi": RoleDefinition(
            role_id="yandi",
            display_name="炎帝",
            abstract_layer="decision",
            model_type="planner",
            description="农耕与规划：资源评估、策略制定",
            representative="神农氏",
            can_review=True,
        ),
        "huangdi": RoleDefinition(
            role_id="huangdi",
            display_name="黄帝",
            abstract_layer="execution",
            model_type="coder",
            description="征伐与执行：策略实施、行动协调",
            representative="轩辕氏",
            can_execute=True,
        ),
    }

    communication_rules: List[CommunicationMatrix] = [
        CommunicationMatrix("yandi", "huangdi"),
        CommunicationMatrix("huangdi", "yandi"),
    ]

    state_machine_config = BaseDynastyTopology.state_machine_config.copy()
    state_machine_config.transitions = [
        StateTransition("new", "pending"),
        StateTransition("pending", "executing"),
        StateTransition("executing", "completed"),
    ]
