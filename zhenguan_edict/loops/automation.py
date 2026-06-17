"""Automation 构建块：定时/事件/状态驱动的调度器。

古代对应：早朝 / 朝会——定期、结构化、有固定仪式的会议。
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Optional

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    SCHEDULED = "scheduled"
    EVENT = "event"
    STATE = "state"


@dataclass
class Trigger:
    trigger_type: TriggerType
    name: str
    callback: Callable[..., Any]
    cron_expr: Optional[str] = None
    event_source: Optional[str] = None
    interval_seconds: Optional[float] = None
    enabled: bool = True


class AutomationLoop:
    """轻量级调度器（类似 cron）触发出每个朝代的 '早朝' 事件。"""

    def __init__(self):
        self._triggers: List[Trigger] = {}
        self._tasks: List[asyncio.Task] = []

    def register(self, trigger: Trigger) -> None:
        self._triggers.append(trigger)

    async def _run_scheduled(self, trigger: Trigger) -> None:
        while True:
            await asyncio.sleep(trigger.interval_seconds or 60.0)
            if trigger.enabled:
                try:
                    await trigger.callback()
                except Exception:
                    logger.exception("Trigger '%s' failed", trigger.name)

    async def start(self) -> None:
        for trigger in self._triggers:
            if trigger.trigger_type == TriggerType.SCHEDULED and trigger.interval_seconds:
                task = asyncio.create_task(self._run_scheduled(trigger))
                self._tasks.append(task)
                logger.info("Automation trigger registered: %s", trigger.name)

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
