from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import ColorScheme, CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class QingTopology(BaseDynastyTopology):
    name = "qing"
    display_name = "清 · Qing"
    description = "双速架构：军机处紧急快车道（跳过审查，热修复用）+ 六部标准开发道。"
    edict_name = "旨"
    color_scheme = ColorScheme(accent="#E8B830", accent_dim="#B8860B", bg="#1a1200", bg2="#241c0e", bg3="#30281a", border="#443a26")

    roles: Dict[str, RoleDefinition] = {
        "user": RoleDefinition(
            role_id="user",
            display_name="用户/皇帝",
            abstract_layer="decision",
            model_type="planner",
            description="需求下发、通道选择（紧急/标准）",
            representative="康熙帝",
        ),
        "grand_council": RoleDefinition(
            role_id="grand_council",
            display_name="军机处",
            abstract_layer="planning",
            model_type="planner",
            description="紧急方案快速决策、热修复规划",
            representative="张廷玉",
        ),
        "six_ministries": RoleDefinition(
            role_id="six_ministries",
            display_name="六部",
            abstract_layer="execution",
            model_type="coder",
            description="标准功能开发、多领域实施",
            representative="刘统勋",
            can_execute=True,
            can_review=True,
        ),
        "lifanyuan": RoleDefinition(
            role_id="lifanyuan",
            display_name="理藩院",
            abstract_layer="execution",
            model_type="documenter",
            description="第三方集成、外部系统对接",
            representative="年羹尧",
            can_execute=True,
        ),
        "imperial_household": RoleDefinition(
            role_id="imperial_household",
            display_name="内务府",
            abstract_layer="execution",
            model_type="lite",
            description="内部工具维护、配置管理",
            representative="曹寅",
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
