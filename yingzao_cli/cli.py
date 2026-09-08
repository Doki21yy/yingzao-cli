"""Thin CLI over guizang-yingzao-skill scripts."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

COMMANDS = {
    "doctor": "check_dependencies.py",
    "preflight": "photo_preflight.py",
    "rectify": "rectify.py",
    "tokens": "design_tokens.py",
    "typeset": "typeset_compose.py",
    "prepare": "prepare_generation.py",
    "compare": "make_comparison.py",
}


def package_dir() -> Path:
    # .../yingzao-cli/yingzao_cli/cli.py -> .../yingzao-cli
    return Path(__file__).resolve().parent.parent


def skill_root() -> Path:
    raw = os.environ.get("YINGZAO_SKILL_ROOT", "").strip()
    if raw:
        root = Path(raw).expanduser().resolve()
    else:
        # Bundled full upstream skill (design tokens, references, assets, ...)
        root = package_dir() / "yingzao"
    scripts = root / "scripts"
    if not scripts.is_dir():
        raise SystemExit(
            f"找不到完整 Skill（缺 scripts/）: {root}\n"
            "应包含上游 yingzao/（design_tokens、references、assets）。\n"
            "或手动: export YINGZAO_SKILL_ROOT=/path/to/guizang-yingzao-skill/yingzao"
        )
    return root


def run_script(script_name: str, args: list[str]) -> int:
    root = skill_root()
    script = root / "scripts" / script_name
    if not script.is_file():
        raise SystemExit(f"上游缺少脚本: {script}")
    cmd = [sys.executable, str(script), *args]
    # Upstream scripts expect to be run with skill as cwd for relative imports/assets.
    return subprocess.call(cmd, cwd=str(root))


def print_help() -> None:
    print(
        """yingzao — CLI wrapper for guizang-yingzao-skill

用法:
  yingzao doctor
  yingzao preflight [args...]
  yingzao rectify [args...]
  yingzao tokens [args...]
  yingzao typeset [args...]
  yingzao prepare [args...]
  yingzao compare [args...]
  yingzao which
  yingzao batch -i <图片目录> [-o output] [--limit N]
  yingzao install-hint

环境变量:
  YINGZAO_SKILL_ROOT   指向上游仓库内的 yingzao/ 目录

说明:
  本 CLI 只封装确定性脚本。海报生成仍需 Agent + 图像模型。
  上游: https://github.com/op7418/guizang-yingzao-skill
"""
    )


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help", "help"}:
        print_help()
        raise SystemExit(0)

    cmd, *rest = argv

    if cmd == "which":
        print(skill_root())
        raise SystemExit(0)

    if cmd == "install-hint":
        print(
            "# 人类 / Agent 安装（对齐飞书 CLI 双路径）\n"
            "./scripts/install.sh          # 人类\n"
            "./scripts/install.sh --yes    # Agent 非交互\n"
            "\n"
            "# 等价拆步\n"
            "pip install -e .   # 在 venv 里\n"
            "export YINGZAO_SKILL_ROOT=/path/to/guizang-yingzao-skill/yingzao\n"
            "npx skills add https://github.com/op7418/guizang-yingzao-skill --skill yingzao -y -g\n"
            "yingzao doctor"
        )
        raise SystemExit(0)

    if cmd == "batch":
        from yingzao_cli.batch import main as batch_main

        raise SystemExit(batch_main(rest))

    if cmd not in COMMANDS:
        print(f"未知命令: {cmd}\n", file=sys.stderr)
        print_help()
        raise SystemExit(2)

    raise SystemExit(run_script(COMMANDS[cmd], rest))


if __name__ == "__main__":
    main()
