from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import ColorScheme, CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class QinTopology(BaseDynastyTopology):
    name = "qin"
    display_name = "秦 · Qin"
    description = "严格层级，硬编码路由，无自由裁量权。御史只读监控。"
    edict_name = "制"
    color_scheme = ColorScheme(accent="#7E8A9E", accent_dim="#4A5568", bg="#040618", bg2="#0a0e22", bg3="#141830", border="#242842", text="#b8bcd0", text_dim="#6a7288", text_muted="#4a4e5a")

    roles: Dict[str, RoleDefinition] = {
        "emperor": RoleDefinition(
            role_id="emperor",
            display_name="皇帝",
            abstract_layer="decision",
            model_type="planner",
            description="唯一决策权、最终签署",
        ),
        "chancellor": RoleDefinition(
            role_id="chancellor",
            display_name="丞相",
            abstract_layer="planning",
            model_type="planner",
            description="行政执行、政策实施",
        ),
        "censor": RoleDefinition(
            role_id="censor",
            display_name="御史",
            abstract_layer="review",
            model_type="reviewer",
            description="监督、合规监控、审计（只读，无驳回权）",
            can_review=True,
        ),
        "tingwei": RoleDefinition(
            role_id="tingwei",
            display_name="廷尉",
            abstract_layer="execution",
            model_type="reviewer",
            description="规则解释、争议解决",
            can_execute=True,
        ),
        "junshou": RoleDefinition(
            role_id="junshou",
            display_name="郡守",
            abstract_layer="execution",
            model_type="coder",
            description="地方长官：统一规则执行",
            can_execute=True,
        ),
    }

    communication_rules: List[CommunicationMatrix] = [
        CommunicationMatrix("emperor", "chancellor"),
        CommunicationMatrix("emperor", "censor"),
        CommunicationMatrix("emperor", "tingwei"),
        CommunicationMatrix("emperor", "junshou"),
        CommunicationMatrix("chancellor", "emperor"),
        CommunicationMatrix("chancellor", "tingwei"),
        CommunicationMatrix("chancellor", "junshou"),
        CommunicationMatrix("censor", "emperor"),
        CommunicationMatrix("censor", "chancellor"),
        CommunicationMatrix("censor", "tingwei"),
        CommunicationMatrix("censor", "junshou"),
        CommunicationMatrix("tingwei", "emperor"),
        CommunicationMatrix("tingwei", "censor"),
        CommunicationMatrix("junshou", "emperor"),
        CommunicationMatrix("junshou", "chancellor"),
    ]

    state_machine_config = BaseDynastyTopology.state_machine_config.copy()
    state_machine_config.transitions = [
        StateTransition("new", "pending"),
        StateTransition("pending", "planning"),
        StateTransition("planning", "dispatching"),
        StateTransition("dispatching", "executing"),
        StateTransition("executing", "validating"),
        StateTransition("validating", "completed"),
    ]
