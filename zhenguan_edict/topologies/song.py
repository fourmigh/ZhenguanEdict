from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class SongTopology(BaseDynastyTopology):
    name = "song"
    display_name = "宋 · Song"
    description = "权力分散，多条并行审核路径。Agent 冗余——关键任务多方独立验证。"

    roles: Dict[str, RoleDefinition] = {
        "emperor": RoleDefinition(
            role_id="emperor",
            display_name="皇帝",
            abstract_layer="decision",
            model_type="planner",
            description="最高决策者",
        ),
        "zhongshu_menxia": RoleDefinition(
            role_id="zhongshu_menxia",
            display_name="中书门下",
            abstract_layer="planning",
            model_type="planner",
            description="合并的规划与审核（民政）",
        ),
        "shumiyuan": RoleDefinition(
            role_id="shumiyuan",
            display_name="枢密院",
            abstract_layer="planning",
            model_type="planner",
            description="军事策略，独立于民政",
        ),
        "sansi": RoleDefinition(
            role_id="sansi",
            display_name="三司使",
            abstract_layer="planning",
            model_type="reviewer",
            description="财政：收入、支出、专卖——民政财务三分",
            can_review=True,
        ),
        "six_ministries": RoleDefinition(
            role_id="six_ministries",
            display_name="六部",
            abstract_layer="execution",
            model_type="coder",
            description="六部执行，权威减弱",
            can_execute=True,
        ),
    }

    communication_rules: List[CommunicationMatrix] = [
        CommunicationMatrix("emperor", "zhongshu_menxia"),
        CommunicationMatrix("emperor", "shumiyuan"),
        CommunicationMatrix("emperor", "sansi"),
        CommunicationMatrix("emperor", "six_ministries"),
        CommunicationMatrix("zhongshu_menxia", "emperor"),
        CommunicationMatrix("zhongshu_menxia", "shumiyuan"),
        CommunicationMatrix("zhongshu_menxia", "sansi"),
        CommunicationMatrix("zhongshu_menxia", "six_ministries"),
        CommunicationMatrix("shumiyuan", "emperor"),
        CommunicationMatrix("shumiyuan", "zhongshu_menxia"),
        CommunicationMatrix("shumiyuan", "sansi"),
        CommunicationMatrix("shumiyuan", "six_ministries"),
        CommunicationMatrix("sansi", "emperor"),
        CommunicationMatrix("sansi", "zhongshu_menxia"),
        CommunicationMatrix("sansi", "shumiyuan"),
        CommunicationMatrix("sansi", "six_ministries"),
        CommunicationMatrix("six_ministries", "emperor"),
        CommunicationMatrix("six_ministries", "zhongshu_menxia"),
        CommunicationMatrix("six_ministries", "shumiyuan"),
        CommunicationMatrix("six_ministries", "sansi"),
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
