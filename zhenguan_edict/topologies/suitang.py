from typing import Dict, List

from zhenguan_edict.interfaces.dynasty import ColorScheme, CommunicationMatrix, RoleDefinition, StateTransition
from zhenguan_edict.topologies.base import BaseDynastyTopology


class SuiTangTopology(BaseDynastyTopology):
    name = "suitang"
    display_name = "隋唐 · Sui-Tang"
    description = "三省六部——延续千年的成熟治理。制定者-检查者闭环带封驳驳回权。"
    edict_name = "敕"
    color_scheme = ColorScheme(accent="#C9A84C", accent_dim="#8B7332", bg="#1a0e02", bg2="#24180e", bg3="#34281c", border="#4a3a28")

    roles: Dict[str, RoleDefinition] = {
        "emperor": RoleDefinition(
            role_id="emperor",
            display_name="皇帝",
            abstract_layer="decision",
            model_type="planner",
            description="最高决策者",
            representative="唐太宗",
        ),
        "crown_prince": RoleDefinition(
            role_id="crown_prince",
            display_name="太子",
            abstract_layer="decision",
            model_type="lite",
            description="分拣：区分闲聊与正式任务",
            representative="李治",
        ),
        "zhongshu": RoleDefinition(
            role_id="zhongshu",
            display_name="中书省",
            abstract_layer="planning",
            model_type="planner",
            description="规划中枢：起草方案、拆解子任务",
            representative="房玄龄",
        ),
        "menxia": RoleDefinition(
            role_id="menxia",
            display_name="门下省",
            abstract_layer="review",
            model_type="reviewer",
            description="审议把关：封驳权——可打回重做",
            representative="魏徵",
            can_review=True,
            can_reject=True,
        ),
        "shangshu": RoleDefinition(
            role_id="shangshu",
            display_name="尚书省",
            abstract_layer="planning",
            model_type="lite",
            description="调度大脑：派发任务、协调执行、汇总回奏",
            representative="长孙无忌",
        ),
        "hubu": RoleDefinition(
            role_id="hubu",
            display_name="户部",
            abstract_layer="execution",
            model_type="documenter",
            description="数据处理、资源核算",
            representative="戴胄",
            can_execute=True,
        ),
        "libu": RoleDefinition(
            role_id="libu",
            display_name="礼部",
            abstract_layer="execution",
            model_type="documenter",
            description="文档撰写、标准制定、协议管理",
            representative="虞世南",
            can_execute=True,
        ),
        "bingbu": RoleDefinition(
            role_id="bingbu",
            display_name="兵部",
            abstract_layer="execution",
            model_type="coder",
            description="代码开发、工程实施",
            representative="李靖",
            can_execute=True,
        ),
        "xingbu": RoleDefinition(
            role_id="xingbu",
            display_name="刑部",
            abstract_layer="execution",
            model_type="reviewer",
            description="安全审计、合规检查、风险评估",
            representative="裴寂",
            can_execute=True,
        ),
        "gongbu": RoleDefinition(
            role_id="gongbu",
            display_name="工部",
            abstract_layer="execution",
            model_type="coder",
            description="CI/CD、部署、工具链",
            representative="阎立德",
            can_execute=True,
        ),
        "libu_personnel": RoleDefinition(
            role_id="libu_personnel",
            display_name="吏部",
            abstract_layer="execution",
            model_type="lite",
            description="Agent 管理、权限维护、配置管理",
            representative="高士廉",
            can_execute=True,
        ),
    }

    communication_rules: List[CommunicationMatrix] = [
        CommunicationMatrix("emperor", "crown_prince"),
        CommunicationMatrix("emperor", "zhongshu"),
        CommunicationMatrix("emperor", "menxia"),
        CommunicationMatrix("emperor", "shangshu"),
        CommunicationMatrix("crown_prince", "zhongshu"),
        CommunicationMatrix("zhongshu", "emperor"),
        CommunicationMatrix("zhongshu", "menxia"),
        CommunicationMatrix("zhongshu", "shangshu"),
        CommunicationMatrix("menxia", "emperor"),
        CommunicationMatrix("menxia", "zhongshu"),
        CommunicationMatrix("menxia", "shangshu"),
        CommunicationMatrix("shangshu", "emperor"),
        CommunicationMatrix("shangshu", "zhongshu"),
        CommunicationMatrix("shangshu", "menxia"),
        CommunicationMatrix("shangshu", "hubu"),
        CommunicationMatrix("shangshu", "libu"),
        CommunicationMatrix("shangshu", "bingbu"),
        CommunicationMatrix("shangshu", "xingbu"),
        CommunicationMatrix("shangshu", "gongbu"),
        CommunicationMatrix("shangshu", "libu_personnel"),
        CommunicationMatrix("hubu", "shangshu"),
        CommunicationMatrix("libu", "shangshu"),
        CommunicationMatrix("bingbu", "shangshu"),
        CommunicationMatrix("xingbu", "shangshu"),
        CommunicationMatrix("gongbu", "shangshu"),
        CommunicationMatrix("libu_personnel", "shangshu"),
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
