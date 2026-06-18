import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434"

MODEL_MAP: Dict[str, str] = {
    "planner": "qwen2.5:0.5b",
    "coder": "qwen2.5:0.5b",
    "reviewer": "qwen2.5:0.5b",
    "documenter": "qwen2.5:0.5b",
    "lite": "qwen2.5:0.5b",
}

def build_system_prompt(topo_name: str, role_display_name: str, representative: str, description: str) -> str:
    return (
        f"你是{representative}，{topo_name}时期的{role_display_name}。{description}。"
        f"请用古代官场奏对风格回答，言简意赅。"
    )

async def chat(model: str, messages: List[Dict], timeout: int = 30) -> Optional[str]:
    import asyncio
    import urllib.request
    import socket
    data = json.dumps({"model": model, "messages": messages, "stream": False}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    loop = asyncio.get_event_loop()
    try:
        resp = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=timeout)),
            timeout=timeout + 5,
        )
        body = json.loads(resp.read())
        return body.get("message", {}).get("content")
    except asyncio.TimeoutError:
        logger.warning("Ollama call timed out after %ss", timeout)
        return None
    except Exception as e:
        logger.warning("Ollama call failed: %s", e)
        return None
