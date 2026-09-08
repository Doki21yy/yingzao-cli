---
name: yingzao-cli
description: Use when installing or running Yingzao (营造) via the yingzao CLI, especially batch jobs. Prefer `yingzao <cmd>` and `yingzao batch`. Image generation uses the current Codex/ChatGPT account quota when run inside Codex; never share another user's subscription. For Chinese architecture / place posters.
---

# Yingzao via CLI（批量 + Codex Pro）

## 安装

```bash
./scripts/install.sh --yes
source .yingzao-env
yingzao doctor
npx skills add https://github.com/op7418/guizang-yingzao-skill --skill yingzao -y -g
```

## 批量（编排）

```bash
yingzao batch -i <图片目录> -o ./output --limit 100
```

然后打开生成的 `CODEX_BATCH_PROMPTS.md`，在 Codex 中分段执行每条 `agent_prompt`。  
出图走 Codex 图像能力 → 消耗**当前用户**订阅额度。

## 单张

按上游 `$yingzao` Skill；确定性步骤用 `yingzao doctor|preflight|tokens|typeset|prepare|compare`。

产物：`output/yingzao/...`，勿写入 Skill 包。
