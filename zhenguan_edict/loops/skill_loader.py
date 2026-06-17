"""Skill 加载：书面化的项目知识——Agent 在每次会话开始时加载。

古代对应：祖制 / 成宪 / 会典——制度知识的汇编。
"""

import os
from pathlib import Path
from typing import Dict, List, Optional


class SkillLoader:
    """加载和管理 Agent 的行为规则（Skill/SOUL 文件）。

    对应文档中的实现思路：
    - 每个角色有一个 SOUL.md 文件
    - 定义其行为准则、输出格式要求和领域约束
    - Skill 在 Agent 实例创建时加载
    """

    def __init__(self, skills_dir: Optional[str] = None):
        self._skills_dir = skills_dir or "./skills"
        self._cache: Dict[str, str] = {}

    def load_skill(self, role_id: str) -> Optional[str]:
        if role_id in self._cache:
            return self._cache[role_id]

        skill_path = Path(self._skills_dir) / role_id / "SOUL.md"
        if skill_path.exists():
            content = skill_path.read_text(encoding="utf-8")
            self._cache[role_id] = content
            return content
        return None

    def load_skills(self, role_ids: List[str]) -> Dict[str, Optional[str]]:
        return {rid: self.load_skill(rid) for rid in role_ids}

    def clear_cache(self) -> None:
        self._cache.clear()
