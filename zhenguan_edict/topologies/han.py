from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class HanTopology(BaseDynastyTopology):
    name = "han"
    display_name = "汉 · Han"
    description = "三公三路并行校审，九卿专门领域执行。第一次成熟的分权体系。"

    roles: Dict[str, RoleDefinition] = {
        "emperor": RoleDefinition(
            role_id="emperor",
            display_name="皇帝",
            abstract_layer="decision",
            model_type="planner",
            description="最高决策",
        ),
        "chancellor": RoleDefinition(
            role_id="chancellor",
            display_name="丞相",
            abstract_layer="planning",
            model_type="planner",
            description="行政领导",
        ),
        "taiwei": RoleDefinition(
            role_id="taiwei",
            display_name="太尉",
            abstract_layer="planning",
            model_type="planner",
            description="军事监督",
        ),
        "censor_in_chief": RoleDefinition(
            role_id="censor_in_chief",
            display_name="御史大夫",
            abstract_layer="review",
            model_type="reviewer",
            description="独立监督，掌管御史台（纯审查，不参与执行）",
            can_review=True,
            can_reject=True,
        ),
        "nine_ministers": RoleDefinition(
            role_id="nine_ministers",
            display_name="九卿",
            abstract_layer="execution",
            model_type="coder",
            description="九位大臣：司法、财政、礼仪等专门领域",
            can_execute=True,
        ),
    }

    communication_rules: List[CommunicationMatrix] = [
        CommunicationMatrix("emperor", "chancellor"),
        CommunicationMatrix("emperor", "taiwei"),
        CommunicationMatrix("emperor", "censor_in_chief"),
        CommunicationMatrix("emperor", "nine_ministers"),
        CommunicationMatrix("chancellor", "emperor"),
        CommunicationMatrix("chancellor", "taiwei"),
        CommunicationMatrix("chancellor", "censor_in_chief"),
        CommunicationMatrix("chancellor", "nine_ministers"),
        CommunicationMatrix("taiwei", "emperor"),
        CommunicationMatrix("taiwei", "chancellor"),
        CommunicationMatrix("taiwei", "censor_in_chief"),
        CommunicationMatrix("taiwei", "nine_ministers"),
        CommunicationMatrix("censor_in_chief", "emperor"),
        CommunicationMatrix("censor_in_chief", "chancellor"),
        CommunicationMatrix("censor_in_chief", "taiwei"),
        CommunicationMatrix("censor_in_chief", "nine_ministers"),
        CommunicationMatrix("nine_ministers", "emperor"),
        CommunicationMatrix("nine_ministers", "chancellor"),
        CommunicationMatrix("nine_ministers", "taiwei"),
        CommunicationMatrix("nine_ministers", "censor_in_chief"),
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
