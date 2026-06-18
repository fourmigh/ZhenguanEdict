from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import ColorScheme, CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class ZhouTopology(BaseDynastyTopology):
    name = "zhou"
    display_name = "周 · Zhou"
    description = "星型架构：中央模块规划→诸侯独立并行开发。适合多模块并行交付。"
    edict_name = "命"
    color_scheme = ColorScheme(accent="#C23B22", accent_dim="#8B1A1A", bg="#1a0604", bg2="#260e0a", bg3="#341812", border="#46221a")

    roles: Dict[str, RoleDefinition] = {
        "son_of_heaven": RoleDefinition(
            role_id="son_of_heaven",
            display_name="天子",
            abstract_layer="decision",
            model_type="planner",
            description="架构决策、全局规划、技术选型仲裁",
            representative="周武王",
        ),
        "qingshi": RoleDefinition(
            role_id="qingshi",
            display_name="卿士",
            abstract_layer="planning",
            model_type="planner",
            description="模块设计、接口定义、多模块协调",
            representative="周公旦",
        ),
        "zhuhou_a": RoleDefinition(
            role_id="zhuhou_a",
            display_name="诸侯甲",
            abstract_layer="execution",
            model_type="coder",
            description="独立模块开发、并行编码、本地交付",
            representative="齐太公",
            can_execute=True,
        ),
        "zhuhou_b": RoleDefinition(
            role_id="zhuhou_b",
            display_name="诸侯乙",
            abstract_layer="execution",
            model_type="coder",
            description="独立模块开发、并行编码、本地交付",
            representative="鲁周公",
            can_execute=True,
        ),
        "zhuhou_c": RoleDefinition(
            role_id="zhuhou_c",
            display_name="诸侯丙",
            abstract_layer="execution",
            model_type="coder",
            description="独立模块开发、并行编码、本地交付",
            representative="召公奭",
            can_execute=True,
        ),
    }

    communication_rules: List[CommunicationMatrix] = [
        CommunicationMatrix("son_of_heaven", "qingshi"),
        CommunicationMatrix("son_of_heaven", "zhuhou_a"),
        CommunicationMatrix("son_of_heaven", "zhuhou_b"),
        CommunicationMatrix("son_of_heaven", "zhuhou_c"),
        CommunicationMatrix("qingshi", "son_of_heaven"),
        CommunicationMatrix("qingshi", "zhuhou_a"),
        CommunicationMatrix("qingshi", "zhuhou_b"),
        CommunicationMatrix("qingshi", "zhuhou_c"),
        CommunicationMatrix("zhuhou_a", "son_of_heaven"),
        CommunicationMatrix("zhuhou_a", "qingshi"),
        CommunicationMatrix("zhuhou_b", "son_of_heaven"),
        CommunicationMatrix("zhuhou_b", "qingshi"),
        CommunicationMatrix("zhuhou_c", "son_of_heaven"),
        CommunicationMatrix("zhuhou_c", "qingshi"),
    ]

    state_machine_config = BaseDynastyTopology.state_machine_config.copy()
    state_machine_config.transitions = [
        StateTransition("new", "pending"),
        StateTransition("pending", "planning"),
        StateTransition("planning", "reviewing"),
        StateTransition("reviewing", "dispatching"),
        StateTransition("dispatching", "executing"),
        StateTransition("executing", "validating"),
        StateTransition("validating", "completed"),
    ]
