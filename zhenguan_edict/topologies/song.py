from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import ColorScheme, CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class SongTopology(BaseDynastyTopology):
    name = "song"
    display_name = "宋 · Song"
    description = "权力分散架构：民政、军事、财政三条规划线并行独立，互不统属。关键任务多方冗余审查。"
    edict_name = "制"
    color_scheme = ColorScheme(accent="#A82222", accent_dim="#6B1010", bg="#180606", bg2="#220e0a", bg3="#301812", border="#401e16")

    roles: Dict[str, RoleDefinition] = {
        "emperor": RoleDefinition(
            role_id="emperor",
            display_name="皇帝",
            abstract_layer="decision",
            model_type="planner",
            description="目标确立、最终决策",
            representative="宋仁宗",
        ),
        "zhongshu_menxia": RoleDefinition(
            role_id="zhongshu_menxia",
            display_name="中书门下",
            abstract_layer="planning",
            model_type="planner",
            description="民政方案规划、功能设计评审",
            representative="王安石",
        ),
        "shumiyuan": RoleDefinition(
            role_id="shumiyuan",
            display_name="枢密院",
            abstract_layer="planning",
            model_type="planner",
            description="技术架构规划、系统安全策略",
            representative="狄青",
        ),
        "sansi": RoleDefinition(
            role_id="sansi",
            display_name="三司使",
            abstract_layer="planning",
            model_type="reviewer",
            description="预算审计、资源核算、成本审查",
            representative="包拯",
            can_review=True,
        ),
        "six_ministries": RoleDefinition(
            role_id="six_ministries",
            display_name="六部",
            abstract_layer="execution",
            model_type="coder",
            description="多领域开发实施、功能交付",
            representative="范仲淹",
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
