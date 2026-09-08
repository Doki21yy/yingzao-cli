#!/usr/bin/env bash
# Human + Agent install: CLI + bundled full Skill + Agent Skills registry.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
YES=0
[[ "${1:-}" == "--yes" || "${1:-}" == "-y" ]] && YES=1

echo "==> [1/3] Python venv + install yingzao CLI"
cd "$ROOT"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -e . -q
echo "    yingzao -> $(command -v yingzao)"

echo "==> [2/3] Full Skill tree (design tokens / references / assets)"
if [[ -d "$ROOT/yingzao/scripts" ]]; then
  export YINGZAO_SKILL_ROOT="$ROOT/yingzao"
  echo "    bundled: $YINGZAO_SKILL_ROOT"
else
  echo "    包内缺少 yingzao/，正在拉取上游…"
  TMP="${TMPDIR:-/tmp}/guizang-yingzao-skill"
  rm -rf "$TMP"
  git clone --depth 1 https://github.com/op7418/guizang-yingzao-skill.git "$TMP"
  rm -rf "$ROOT/yingzao"
  cp -R "$TMP/yingzao" "$ROOT/yingzao"
  export YINGZAO_SKILL_ROOT="$ROOT/yingzao"
  echo "    installed: $YINGZAO_SKILL_ROOT"
fi

# sanity: design tokens must exist
test -f "$YINGZAO_SKILL_ROOT/scripts/design_tokens.py"
test -d "$YINGZAO_SKILL_ROOT/references"
echo "    design_tokens.py + references/ OK"

ENV_FILE="$ROOT/.yingzao-env"
{
  echo "export YINGZAO_SKILL_ROOT=\"$YINGZAO_SKILL_ROOT\""
  echo "export PATH=\"$ROOT/.venv/bin:\$PATH\""
} > "$ENV_FILE"
echo "    wrote $ENV_FILE"

echo "==> [3/3] Install Agent Skills (npx skills)"
if ! command -v npx >/dev/null 2>&1; then
  echo "    警告: 无 npx。CLI+完整文件已就绪；装 Node 后再:"
  echo "    npx skills add https://github.com/op7418/guizang-yingzao-skill --skill yingzao -y -g"
  exit 0
fi
npx skills add https://github.com/op7418/guizang-yingzao-skill --skill yingzao -y -g || true
if [[ -f "$ROOT/skills/yingzao-cli/SKILL.md" ]]; then
  npx skills add "$ROOT" --skill yingzao-cli -y -g 2>/dev/null || true
fi

echo "==> Done. source $ENV_FILE && yingzao doctor && yingzao tokens --help"
