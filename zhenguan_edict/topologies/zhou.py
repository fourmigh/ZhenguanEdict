from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class ZhouTopology(BaseDynastyTopology):
    name = "zhou"
    display_name = "周 · Zhou"
    description = "星状群岛。中央向半自治诸侯授权，在各封地内并行工作。"

    roles: Dict[str, RoleDefinition] = {
        "son_of_heaven": RoleDefinition(
            role_id="son_of_heaven",
            display_name="天子",
            abstract_layer="decision",
            model_type="planner",
            description="天下共主：高层远见、诸侯任命、最终仲裁",
        ),
        "qingshi": RoleDefinition(
            role_id="qingshi",
            display_name="卿士",
            abstract_layer="planning",
            model_type="planner",
            description="中央大臣：政策起草、诸侯间协调",
        ),
        "zhuhou_a": RoleDefinition(
            role_id="zhuhou_a",
            display_name="诸侯甲",
            abstract_layer="execution",
            model_type="coder",
            description="地方领主：并行执行",
            can_execute=True,
        ),
        "zhuhou_b": RoleDefinition(
            role_id="zhuhou_b",
            display_name="诸侯乙",
            abstract_layer="execution",
            model_type="coder",
            description="地方领主：并行执行",
            can_execute=True,
        ),
        "zhuhou_c": RoleDefinition(
            role_id="zhuhou_c",
            display_name="诸侯丙",
            abstract_layer="execution",
            model_type="coder",
            description="地方领主：并行执行",
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
