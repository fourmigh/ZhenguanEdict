#!/usr/bin/env python3
"""ZhenguanEdict — 历代官制 × 闭环自动化 × 多 Agent 协作框架"""

import subprocess
import sys


def _ensure_dependencies():
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        print("正在安装依赖 (pip install -r requirements.txt)...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("依赖安装完成")


if __name__ == "__main__":
    _ensure_dependencies()

    import uvicorn

    uvicorn.run(
        "zhenguan_edict.engine.server:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
