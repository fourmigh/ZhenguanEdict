from typing import Dict, List, Optional, Type

from zhenguan_edict.interfaces.dynasty import DynastyTopology


class DynastyRegistry:
    _topologies: Dict[str, Type[DynastyTopology]] = {}

    @classmethod
    def register(cls, topology_cls: Type[DynastyTopology]) -> Type[DynastyTopology]:
        instance = topology_cls()
        cls._topologies[instance.name] = topology_cls
        return topology_cls

    @classmethod
    def get(cls, name: str) -> Optional[DynastyTopology]:
        topology_cls = cls._topologies.get(name)
        if topology_cls is None:
            return None
        return topology_cls()

    @classmethod
    def list_names(cls) -> List[str]:
        return list(cls._topologies.keys())

    @classmethod
    def list_all(cls) -> List[DynastyTopology]:
        return [cls() for cls in cls._topologies.values()]

    @classmethod
    def load_all(cls) -> None:
        from zhenguan_edict.topologies.yanhuang import YanHuangTopology
        from zhenguan_edict.topologies.xia import XiaTopology
        from zhenguan_edict.topologies.shang import ShangTopology
        from zhenguan_edict.topologies.zhou import ZhouTopology
        from zhenguan_edict.topologies.qin import QinTopology
        from zhenguan_edict.topologies.han import HanTopology
        from zhenguan_edict.topologies.suitang import SuiTangTopology
        from zhenguan_edict.topologies.song import SongTopology
        from zhenguan_edict.topologies.ming import MingTopology
        from zhenguan_edict.topologies.qing import QingTopology

        cls.register(YanHuangTopology)
        cls.register(XiaTopology)
        cls.register(ShangTopology)
        cls.register(ZhouTopology)
        cls.register(QinTopology)
        cls.register(HanTopology)
        cls.register(SuiTangTopology)
        cls.register(SongTopology)
        cls.register(MingTopology)
        cls.register(QingTopology)


DynastyRegistry.load_all()
