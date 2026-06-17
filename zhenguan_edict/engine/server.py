"""
ZhenguanEdict Engine — FastAPI HTTP 服务

启动方式：
    python main.py
    # 或
    uvicorn zhenguan_edict.engine.server:app --reload --port 8080
"""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from zhenguan_edict.engine.agent_scheduler import AgentScheduler
from zhenguan_edict.engine.routing_engine import RoutingEngine
from zhenguan_edict.engine.task_state_machine import TaskStateMachine
from zhenguan_edict.engine.topology_loader import TopologyLoader
from zhenguan_edict.interfaces.dynasty import DynastyTopology
from zhenguan_edict.interfaces.memorial import MemorialEntry
from zhenguan_edict.interfaces.task import TaskState
from zhenguan_edict.loops.memory import MemoryManager
from zhenguan_edict.loops.worktree import WorktreeManager
from zhenguan_edict.models.agent import AgentModel
from zhenguan_edict.models.memorial import MemorialModel
from zhenguan_edict.models.task import TaskModel

logger = logging.getLogger(__name__)


# ── Pydantic 请求模型 ──

class SwitchDynastyRequest(BaseModel):
    name: str


class CreateTaskRequest(BaseModel):
    title: str
    content: str = ""
    priority: int = 0


class TransitionRequest(BaseModel):
    state: str
    reason: str = ""


class RegisterAgentRequest(BaseModel):
    role_id: str
    model_type: str = "lite"
    display_name: str = ""


# ── 引擎单例 ──

class EngineServer:
    """引擎状态管理器，持有全部核心组件和运行时数据。"""

    def __init__(self) -> None:
        self.topology_loader = TopologyLoader()
        self.routing_engine = RoutingEngine()
        self.state_machine = TaskStateMachine()
        self.scheduler = AgentScheduler()
        self.memory = MemoryManager()
        self.worktree_manager = WorktreeManager()
        self.tasks: Dict[str, TaskModel] = {}
        self.memorials: Dict[str, MemorialModel] = {}
        self.agents: Dict[str, AgentModel] = {}
        self._sse_queues: List[asyncio.Queue] = []
        self._running = False
        self._task_counter = 0
        self._memorial_counter = 0

    # ═══ 朝代管理 ═══

    def switch_dynasty(self, name: str) -> Optional[DynastyTopology]:
        topology = self.topology_loader.switch(name)
        if topology is None:
            return None
        self.routing_engine.topology = topology
        self.state_machine.topology = topology
        logger.info("Switched to dynasty: %s (%s)", name, topology.display_name)
        self._broadcast_sse({"type": "dynasty_switched", "dynasty": name})
        return topology

    @property
    def active_topology(self) -> Optional[DynastyTopology]:
        return self.topology_loader.active

    # ═══ 任务管理 ═══

    def create_task(self, title: str, content: str, priority: int = 0) -> TaskModel:
        self._task_counter += 1
        now = datetime.now(timezone.utc)
        dynasty = self.active_topology.name if self.active_topology else "unknown"
        task = TaskModel(
            task_id=f"task-{self._task_counter:04d}",
            title=title,
            content=content,
            state=TaskState.NEW,
            dynasty=dynasty,
            priority=priority,
            created_at=now,
            updated_at=now,
            history=[{
                "state": TaskState.NEW.value,
                "timestamp": now.isoformat(),
                "reason": "Task created",
            }],
        )
        self.tasks[task.task_id] = task
        memorial = MemorialModel(
            memorial_id=self._next_memorial_id(),
            task_id=task.task_id,
            task_title=task.title,
            dynasty=task.dynasty,
            created_at=now,
        )
        self.memorials[memorial.memorial_id] = memorial
        self._broadcast_sse({"type": "task_created", "task_id": task.task_id})
        return task

    def get_task(self, task_id: str) -> Optional[TaskModel]:
        return self.tasks.get(task_id)

    def list_tasks(
        self, state: Optional[str] = None, dynasty: Optional[str] = None
    ) -> List[TaskModel]:
        result = list(self.tasks.values())
        if state:
            result = [t for t in result if t.state == TaskState(state)]
        if dynasty:
            result = [t for t in result if t.dynasty == dynasty]
        return sorted(result, key=lambda t: t.created_at, reverse=True)

    async def transition_task(
        self, task_id: str, target: str, reason: str = ""
    ) -> Optional[TaskModel]:
        task = self.tasks.get(task_id)
        if task is None:
            return None
        target_state = TaskState(target)
        topology = self.active_topology
        if topology is None:
            raise HTTPException(503, "No topology loaded")
        self.state_machine.topology = topology
        allowed = self.state_machine.allowed_transitions(task.state)
        if target_state not in allowed:
            raise HTTPException(
                422,
                f"Cannot transition from {task.state.value} to {target_state.value} "
                f"in dynasty '{task.dynasty}'. Allowed: {[s.value for s in allowed]}",
            )
        now = datetime.now(timezone.utc)
        task.state = target_state
        task.updated_at = now
        if target_state == TaskState.COMPLETED:
            task.completed_at = now
        task.history.append({
            "state": target_state.value,
            "timestamp": now.isoformat(),
            "reason": reason,
        })
        self._append_entry(task.task_id, "transition", target_state.value, reason)
        self._broadcast_sse({"type": "task_transitioned", "task_id": task_id, "state": target})
        return task

    # ═══ 奏折管理 ═══

    def _next_memorial_id(self) -> str:
        self._memorial_counter += 1
        return f"memorial-{self._memorial_counter:04d}"

    def _append_entry(
        self, task_id: str, action: str, detail: str, reason: str = ""
    ) -> None:
        for m in self.memorials.values():
            if m.task_id == task_id:
                entry = MemorialEntry(
                    sequence=len(m.entries) + 1,
                    timestamp=datetime.now(timezone.utc),
                    actor_role="system",
                    actor_id="engine",
                    action=action,
                    content=detail if not reason else f"{detail}: {reason}",
                    decision=detail,
                    decision_reason=reason,
                )
                m.entries.append(entry)
                return

    def get_memorial(self, memorial_id: str) -> Optional[MemorialModel]:
        return self.memorials.get(memorial_id)

    def list_memorials(self, dynasty: Optional[str] = None) -> List[MemorialModel]:
        result = list(self.memorials.values())
        if dynasty:
            result = [m for m in result if m.dynasty == dynasty]
        return sorted(result, key=lambda m: m.created_at, reverse=True)

    # ═══ Agent 管理 ═══

    def register_agent(self, role_id: str, model_type: str, display_name: str = "") -> AgentModel:
        agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        agent = AgentModel(
            agent_id=agent_id,
            role_id=role_id,
            model_type=model_type,
            display_name=display_name or role_id,
        )
        self.agents[agent_id] = agent
        logger.info("Agent registered: %s (role=%s, model=%s)", agent_id, role_id, model_type)
        self._broadcast_sse({"type": "agent_registered", "agent_id": agent_id})
        return agent

    def list_agents(self) -> List[AgentModel]:
        return list(self.agents.values())

    # ═══ SSE 事件推送 ═══

    def _broadcast_sse(self, event: Dict[str, Any]) -> None:
        payload = json.dumps(event, default=str)
        dead: List[int] = []
        for i, q in enumerate(self._sse_queues):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                dead.append(i)
        for i in reversed(dead):
            self._sse_queues.pop(i)

    async def sse_generator(self):
        queue: asyncio.Queue = asyncio.Queue(maxsize=128)
        self._sse_queues.append(queue)
        try:
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=5.0)
                    yield {"event": "update", "data": data}
                except asyncio.TimeoutError:
                    if self._running:
                        yield {"event": "heartbeat", "data": ""}
                    else:
                        break
        finally:
            self._sse_queues.remove(queue)

    # ═══ 生命周期 ═══

    async def start(self) -> None:
        self._running = True
        logger.info("ZhenguanEdict Engine started")

    async def stop(self) -> None:
        self._running = False
        self.worktree_manager.destroy_all()
        logger.info("ZhenguanEdict Engine stopped")

    @property
    def is_running(self) -> bool:
        return self._running


# ── FastAPI 应用 ──

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = EngineServer()
    engine.switch_dynasty("suitang")
    app.state.engine = engine
    await engine.start()
    yield
    await engine.stop()


app = FastAPI(
    title="ZhenguanEdict Engine",
    version="0.1.0",
    description="历代官制 × 闭环自动化 × 多 Agent 协作框架",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_engine() -> EngineServer:
    return app.state.engine


# ── 健康检查 ──

@app.get("/api/health")
async def health():
    engine = _get_engine()
    topo = engine.active_topology
    return {
        "status": "running",
        "version": "0.1.0",
        "dynasty": topo.name if topo else None,
        "tasks_total": len(engine.tasks),
        "agents_total": len(engine.agents),
    }


# ── 朝代管理 ──

@app.get("/api/dynasties")
async def list_dynasties():
    engine = _get_engine()
    topologies = engine.topology_loader.list_available_topologies()
    return [
        {
            "name": t.name,
            "display_name": t.display_name,
            "description": t.description,
            "roles_count": len(t.roles),
            "roles": [
                {
                    "role_id": r.role_id,
                    "display_name": r.display_name,
                    "abstract_layer": r.abstract_layer,
                    "model_type": r.model_type,
                }
                for r in t.roles.values()
            ],
        }
        for t in topologies
    ]


@app.get("/api/dynasties/current")
async def current_dynasty():
    engine = _get_engine()
    topo = engine.active_topology
    if topo is None:
        raise HTTPException(503, "No dynasty loaded")
    return {
        "name": topo.name,
        "display_name": topo.display_name,
        "description": topo.description,
        "roles": [
            {
                "role_id": r.role_id,
                "display_name": r.display_name,
                "abstract_layer": r.abstract_layer,
                "model_type": r.model_type,
                "can_review": r.can_review,
                "can_reject": r.can_reject,
                "can_execute": r.can_execute,
            }
            for r in topo.roles.values()
        ],
        "communication_rules": [
            {
                "from": rule.sender_role,
                "to": rule.receiver_role,
                "allowed_types": list(rule.allowed_message_types),
            }
            for rule in topo.communication_rules
        ],
        "state_machine": {
            "initial": topo.state_machine_config.initial_state,
            "states": topo.state_machine_config.states,
            "transitions": [
                {"from": t.from_state, "to": t.to_state, "condition": t.condition}
                for t in topo.state_machine_config.transitions
            ],
        },
    }


@app.post("/api/dynasties/switch")
async def switch_dynasty(req: SwitchDynastyRequest):
    engine = _get_engine()
    topo = engine.switch_dynasty(req.name)
    if topo is None:
        raise HTTPException(404, f"Unknown dynasty: {req.name}")
    return {"status": "switched", "dynasty": topo.name, "display_name": topo.display_name}


# ── 任务管理 ──

@app.get("/api/tasks")
async def list_tasks(
    state: Optional[str] = Query(None),
    dynasty: Optional[str] = Query(None),
):
    engine = _get_engine()
    tasks = engine.list_tasks(state, dynasty)
    return [
        {
            "task_id": t.task_id,
            "title": t.title,
            "content": t.content,
            "state": t.state.value,
            "dynasty": t.dynasty,
            "priority": t.priority,
            "assigned_role": t.assigned_role,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat(),
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        }
        for t in tasks
    ]


@app.post("/api/tasks")
async def create_task(req: CreateTaskRequest):
    engine = _get_engine()
    task = engine.create_task(req.title, req.content, req.priority)
    return {
        "task_id": task.task_id,
        "title": task.title,
        "state": task.state.value,
        "dynasty": task.dynasty,
        "created_at": task.created_at.isoformat(),
    }


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    engine = _get_engine()
    task = engine.get_task(task_id)
    if task is None:
        raise HTTPException(404, f"Task not found: {task_id}")
    return {
        "task_id": task.task_id,
        "title": task.title,
        "content": task.content,
        "state": task.state.value,
        "dynasty": task.dynasty,
        "priority": task.priority,
        "assigned_role": task.assigned_role,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "history": task.history,
        "metadata": task.metadata,
    }


@app.post("/api/tasks/{task_id}/transition")
async def transition_task(task_id: str, req: TransitionRequest):
    engine = _get_engine()
    task = await engine.transition_task(task_id, req.state, req.reason)
    if task is None:
        raise HTTPException(404, f"Task not found: {task_id}")
    return {
        "task_id": task.task_id,
        "state": task.state.value,
        "updated_at": task.updated_at.isoformat(),
    }


# ── Agent 管理 ──

@app.get("/api/agents")
async def list_agents():
    engine = _get_engine()
    agents = engine.list_agents()
    return [
        {
            "agent_id": a.agent_id,
            "role_id": a.role_id,
            "model_type": a.model_type,
            "display_name": a.display_name,
            "is_busy": a.is_busy,
            "current_task_id": a.current_task_id,
            "tasks_completed": a.tasks_completed,
            "total_tokens_consumed": a.total_tokens_consumed,
            "created_at": a.created_at.isoformat(),
        }
        for a in agents
    ]


@app.post("/api/agents")
async def register_agent(req: RegisterAgentRequest):
    engine = _get_engine()
    agent = engine.register_agent(req.role_id, req.model_type, req.display_name)
    return {
        "agent_id": agent.agent_id,
        "role_id": agent.role_id,
        "model_type": agent.model_type,
        "display_name": agent.display_name,
    }


# ── 奏折管理 ──

@app.get("/api/memorials")
async def list_memorials(dynasty: Optional[str] = Query(None)):
    engine = _get_engine()
    memorials = engine.list_memorials(dynasty)
    return [
        {
            "memorial_id": m.memorial_id,
            "task_id": m.task_id,
            "task_title": m.task_title,
            "dynasty": m.dynasty,
            "created_at": m.created_at.isoformat(),
            "completed_at": m.completed_at.isoformat() if m.completed_at else None,
            "entries_count": len(m.entries),
            "total_tokens": m.total_token_usage,
        }
        for m in memorials
    ]


@app.get("/api/memorials/{memorial_id}")
async def get_memorial(memorial_id: str):
    engine = _get_engine()
    memorial = engine.get_memorial(memorial_id)
    if memorial is None:
        raise HTTPException(404, f"Memorial not found: {memorial_id}")
    return {
        "memorial_id": memorial.memorial_id,
        "task_id": memorial.task_id,
        "task_title": memorial.task_title,
        "dynasty": memorial.dynasty,
        "created_at": memorial.created_at.isoformat(),
        "completed_at": memorial.completed_at.isoformat() if memorial.completed_at else None,
        "entries": [
            {
                "sequence": e.sequence,
                "timestamp": e.timestamp.isoformat(),
                "actor_role": e.actor_role,
                "actor_id": e.actor_id,
                "action": e.action,
                "content": e.content,
                "decision": e.decision,
                "decision_reason": e.decision_reason,
                "token_usage": e.token_usage,
            }
            for e in memorial.entries
        ],
        "total_tokens": memorial.total_token_usage,
    }


# ── SSE 事件推送 ──

@app.get("/api/events")
async def event_stream():
    engine = _get_engine()
    return EventSourceResponse(engine.sse_generator())
