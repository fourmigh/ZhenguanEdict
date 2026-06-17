from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import ColorScheme, CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class QingTopology(BaseDynastyTopology):
    name = "qing"
    display_name = "清 · Qing"
    description = "双速循环：军机处紧急快车道（跳过审核）+ 六部标准审核道。"
    edict_name = "旨"
    color_scheme = ColorScheme(accent="#E8B830", accent_dim="#B8860B", bg="#1a1200", bg2="#241c0e", bg3="#30281a", border="#443a26")

    roles: Dict[str, RoleDefinition] = {
        "user": RoleDefinition(
            role_id="user",
            display_name="用户/皇帝",
            abstract_layer="decision",
            model_type="planner",
            description="入口：选择紧急或标准通道",
        ),
        "grand_council": RoleDefinition(
            role_id="grand_council",
            display_name="军机处",
            abstract_layer="planning",
            model_type="planner",
            description="紧急决策，绕过正常流程",
        ),
        "six_ministries": RoleDefinition(
            role_id="six_ministries",
            display_name="六部",
            abstract_layer="execution",
            model_type="coder",
            description="标准领域执行（户/礼/兵/刑/工/吏）",
            can_execute=True,
            can_review=True,
        ),
        "lifanyuan": RoleDefinition(
            role_id="lifanyuan",
            display_name="理藩院",
            abstract_layer="execution",
            model_type="documenter",
            description="非汉民族事务，专门领域",
            can_execute=True,
        ),
        "imperial_household": RoleDefinition(
            role_id="imperial_household",
            display_name="内务府",
            abstract_layer="execution",
            model_type="lite",
            description="皇室内部事务，独立于民政",
            can_execute=True,
        ),
    }

    communication_rules: List[CommunicationMatrix] = [
        CommunicationMatrix("user", "grand_council"),
        CommunicationMatrix("user", "six_ministries"),
        CommunicationMatrix("user", "lifanyuan"),
        CommunicationMatrix("user", "imperial_household"),
        CommunicationMatrix("grand_council", "user"),
        CommunicationMatrix("grand_council", "six_ministries"),
        CommunicationMatrix("six_ministries", "user"),
        CommunicationMatrix("lifanyuan", "user"),
        CommunicationMatrix("imperial_household", "user"),
    ]

    state_machine_config = BaseDynastyTopology.state_machine_config.copy()
    state_machine_config.transitions = [
        StateTransition("new", "pending"),
        StateTransition("pending", "planning"),
        StateTransition("planning", "reviewing"),
        StateTransition("reviewing", "dispatching", condition="approved"),
        StateTransition("dispatching", "executing"),
        StateTransition("executing", "validating"),
        StateTransition("validating", "completed"),
    ]
