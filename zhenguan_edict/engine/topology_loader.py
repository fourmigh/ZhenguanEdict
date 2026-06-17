from typing import Dict, List, Optional

from zhenguan_edict.interfaces.dynasty import DynastyTopology
from zhenguan_edict.topologies.registry import DynastyRegistry


class TopologyLoader:
    """拓扑加载器：从结构化定义加载朝代配置，支持运行时热切换。

    对应架构文档中的描述：
    - 从结构化定义（Python dict）加载朝代的完整配置
    - 用户切换朝代时热加载新配置，无需重启服务
    """

    def __init__(self):
        self._active: Optional[DynastyTopology] = None

    def load(self, name: str) -> Optional[DynastyTopology]:
        topology = DynastyRegistry.get(name)
        if topology is not None:
            self._active = topology
        return topology

    def reload(self, name: str) -> Optional[DynastyTopology]:
        topology = DynastyRegistry.get(name)
        if topology is not None:
            self._active = topology
        return topology

    def switch(self, name: str) -> Optional[DynastyTopology]:
        return self.load(name)

    @property
    def active(self) -> Optional[DynastyTopology]:
        return self._active

    def list_available(self) -> List[str]:
        return DynastyRegistry.list_names()

    def list_available_topologies(self) -> List[DynastyTopology]:
        return DynastyRegistry.list_all()
