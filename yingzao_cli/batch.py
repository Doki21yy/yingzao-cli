"""Batch orchestration for Yingzao.

Does NOT call image APIs. Prepares per-item workdirs and a Codex handoff
manifest so an Agent (Codex Pro subscription) or a later API runner can
generate images using the user's own quota/key.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic"}


def list_images(input_dir: Path) -> list[Path]:
    files = sorted(
        p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )
    return files


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_batch(input_dir: Path, out_dir: Path, limit: int | None, dry_run: bool) -> int:
    images = list_images(input_dir)
    if limit is not None:
        images = images[:limit]
    if not images:
        print(f"未找到图片: {input_dir}", file=sys.stderr)
        return 2

    batch_id = time.strftime("%Y%m%d-%H%M%S")
    batch_root = out_dir / "yingzao" / f"batch-{batch_id}"
    batch_root.mkdir(parents=True, exist_ok=True)

    items = []
    for i, src in enumerate(images, 1):
        item_id = f"{i:04d}-{src.stem}"
        item_dir = batch_root / item_id
        item_dir.mkdir(parents=True, exist_ok=True)
        dest = item_dir / f"source{src.suffix.lower()}"
        if not dry_run:
            shutil.copy2(src, dest)
        else:
            dest.write_text("")  # placeholder in dry-run? better skip
            if dest.exists() and dest.stat().st_size == 0:
                dest.unlink(missing_ok=True)
            # dry-run: only record paths, don't copy
            dest = src

        handoff = {
            "item_id": item_id,
            "source": str(src.resolve()),
            "workdir": str(item_dir.resolve()),
            "status": "pending_image_gen",
            "image_route": "codex_agent",  # or openai_api
            "agent_prompt": (
                f"用 $yingzao 处理这张图并生成 1 张编辑海报。"
                f"源图: {src}。"
                f"工作目录: {item_dir}。"
                f"先 yingzao doctor / preflight，再 prepare；"
                f"仅 READY 后用 Codex 图像能力出图（消耗当前账号订阅额度）。"
                f"不要用别人的 Key；完成后把成图写到 {item_dir}/poster.png 并更新 handoff.json status=done。"
            ),
            "cli_hints": [
                "yingzao doctor",
                f"yingzao preflight {dest}",
                "yingzao prepare ...  # 按上游 SKILL 参数补齐",
            ],
        }
        if not dry_run:
            write_json(item_dir / "handoff.json", handoff)
        items.append(handoff)
        print(f"[{i}/{len(images)}] {src.name} -> {item_dir}")

    manifest = {
        "batch_id": batch_id,
        "input_dir": str(input_dir.resolve()),
        "batch_root": str(batch_root.resolve()),
        "count": len(items),
        "image_route_default": "codex_agent",
        "note": (
            "本 batch 只做编排与清单。出图请在 Codex 中按 items[].agent_prompt 执行，"
            "消耗操作者自己的 Codex/ChatGPT 订阅额度；或改用 OPENAI_API_KEY 走 API 计费。"
        ),
        "items": items,
    }
    manifest_path = batch_root / "batch-manifest.json"
    if not dry_run:
        write_json(manifest_path, manifest)
        # Convenience prompts file for pasting into Codex
        prompts = batch_root / "CODEX_BATCH_PROMPTS.md"
        lines = [
            f"# Yingzao batch {batch_id}",
            "",
            "在 Codex 中逐条或分段执行。图像消耗你的订阅额度（约比纯文本快 3–5 倍）。",
            "建议每 10–20 张休息/检查限额。",
            "",
        ]
        for it in items:
            lines.append(f"## {it['item_id']}")
            lines.append("")
            lines.append(it["agent_prompt"])
            lines.append("")
        prompts.write_text("\n".join(lines), encoding="utf-8")

    print(f"\n完成编排 {len(items)} 张")
    print(f"清单: {manifest_path if not dry_run else '(dry-run)'}")
    if not dry_run:
        print(f"Codex 提示词汇总: {batch_root / 'CODEX_BATCH_PROMPTS.md'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Yingzao batch orchestrator (no image API calls)")
    p.add_argument("--input", "-i", type=Path, required=True, help="输入图片目录")
    p.add_argument("--out", "-o", type=Path, default=Path("output"), help="输出根目录")
    p.add_argument("--limit", type=int, default=None, help="最多处理 N 张")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    if not args.input.is_dir():
        print(f"输入目录不存在: {args.input}", file=sys.stderr)
        return 2
    return run_batch(args.input, args.out, args.limit, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
