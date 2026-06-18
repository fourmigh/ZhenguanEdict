import json
import logging
import subprocess
import time
import urllib.error
import urllib.request
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434"

MODEL_MAP: Dict[str, str] = {
    "planner": "qwen2.5:1.5b",
    "coder": "qwen2.5:1.5b",
    "reviewer": "qwen2.5:1.5b",
    "documenter": "qwen2.5:1.5b",
    "lite": "qwen2.5:1.5b",
}


def ensure_ollama(timeout: int = 10) -> bool:
    """检查 Ollama 是否运行，未运行则自动启动。"""
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3)
        return True
    except (urllib.error.URLError, OSError):
        logger.info("Ollama not running, trying to start...")
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            for _ in range(timeout):
                time.sleep(1)
                try:
                    urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2)
                    logger.info("Ollama started successfully")
                    return True
                except Exception:
                    pass
            logger.warning("Ollama did not start within %ds", timeout)
            return False
        except FileNotFoundError:
            logger.warning("ollama command not found in PATH")
            return False


def ensure_models() -> None:
    """检查所需模型是否已拉取，缺失则自动 pull。"""
    try:
        resp = urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5)
        tags = json.loads(resp.read())
        local = {t["name"] for t in tags.get("models", [])}
    except Exception as e:
        logger.warning("Cannot check model list: %s", e)
        return
    for model in set(MODEL_MAP.values()):
        if model not in local:
            logger.info("Pulling model %s (may take a while)...", model)
            subprocess.run(["ollama", "pull", model], timeout=600)
            logger.info("Model %s pulled", model)

def build_system_prompt(topo_name: str, role_display_name: str, representative: str, description: str, model_type: str = "") -> str:
    base = f"你是{representative}，{topo_name}时期的{role_display_name}。{description}。"
    style_map = {
        "planner":    "输出技术方案文档：包含架构设计、接口定义、数据流说明。语言技术化、结构化。",
        "coder":      "直接输出可运行的代码，使用代码块包裹。不要输出方案、计划、解释或古风奏折。",
        "reviewer":   "输出评审意见：用条款形式列出问题、风险和改进建议。",
        "documenter": "输出技术文档：包含用途说明、使用方法、注意事项。清晰分段。",
    }
    return base + style_map.get(model_type, "请用古代官场奏对风格回答，言简意赅。")

async def chat(model: str, messages: List[Dict], timeout: int = 30) -> Optional[str]:
    import asyncio
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
