from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import ColorScheme, CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class MingTopology(BaseDynastyTopology):
    name = "ming"
    display_name = "明 · Ming"
    description = "双轨制：正式通道（内阁票拟→批红）+ 影子通道（司礼监会签与厂卫暗访）。"
    edict_name = "谕"
    color_scheme = ColorScheme(accent="#DC3023", accent_dim="#A02010", bg="#1a0804", bg2="#26100a", bg3="#341a12", border="#482618")

    roles: Dict[str, RoleDefinition] = {
        "emperor": RoleDefinition(
            role_id="emperor",
            display_name="皇帝",
            abstract_layer="decision",
            model_type="planner",
            description="最终决策、批红",
        ),
        "grand_secretariat": RoleDefinition(
            role_id="grand_secretariat",
            display_name="内阁",
            abstract_layer="planning",
            model_type="planner",
            description="起草政策回应（票拟）、向皇帝汇报",
        ),
        "silijian": RoleDefinition(
            role_id="silijian",
            display_name="司礼监",
            abstract_layer="review",
            model_type="reviewer",
            description="宦官机构：次级审批通道、会签",
            can_review=True,
        ),
        "changwei": RoleDefinition(
            role_id="changwei",
            display_name="厂卫",
            abstract_layer="review",
            model_type="reviewer",
            description="独立情报、影子验证",
            can_review=True,
        ),
        "six_ministries": RoleDefinition(
            role_id="six_ministries",
            display_name="六部",
            abstract_layer="execution",
            model_type="coder",
            description="领域执行",
            can_execute=True,
        ),
    }

    communication_rules: List[CommunicationMatrix] = [
        CommunicationMatrix("emperor", "grand_secretariat"),
        CommunicationMatrix("emperor", "silijian"),
        CommunicationMatrix("emperor", "changwei"),
        CommunicationMatrix("emperor", "six_ministries"),
        CommunicationMatrix("grand_secretariat", "emperor"),
        CommunicationMatrix("grand_secretariat", "six_ministries"),
        CommunicationMatrix("silijian", "emperor"),
        CommunicationMatrix("silijian", "changwei"),
        CommunicationMatrix("silijian", "six_ministries"),
        CommunicationMatrix("changwei", "emperor"),
        CommunicationMatrix("changwei", "six_ministries"),
        CommunicationMatrix("six_ministries", "emperor"),
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
