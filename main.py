#!/usr/bin/env python3
"""ZhenguanEdict — 历代官制 × 闭环自动化 × 多 Agent 协作框架"""

import os
import subprocess
import sys

# 禁止所有进程（包括 uvicorn reloader 子进程）产生 .pyc 文件
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True


def _ensure_dependencies():
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        print("正在安装依赖 (pip install -r requirements.txt)...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("依赖安装完成")


def _clean_pycache():
    root = os.path.dirname(os.path.abspath(__file__))
    print(">>> Cleaning pycache in", root)
    subprocess.run(
        ["find", root, "-name", "*.pyc", "-delete"],
        capture_output=True,
    )
    subprocess.run(
        ["find", root, "-type", "d", "-name", "__pycache__", "-exec", "rm", "-rf", "{}", "+"],
        capture_output=True,
    )
    print(">>> Clean done")


if __name__ == "__main__":
    _ensure_dependencies()
    _clean_pycache()

    import uvicorn

    uvicorn.run(
        "zhenguan_edict.engine.server:app",
        host="127.0.0.1",
        port=8080,
    )
