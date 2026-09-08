# yingzao-cli

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://www.python.org/)

把开源 [guizang-yingzao-skill](https://github.com/op7418/guizang-yingzao-skill)（营造）封成 **CLI + AI Agent Skills** — 人类和 AI Agent 都能安装使用。包内自带完整 `yingzao/`。

安装结构对齐飞书 CLI（[larksuite/cli](https://github.com/larksuite/cli) / [feishu-cli.com](https://feishu-cli.com/)）：**人类用户**与 **AI Agent** 两套入口。

[安装](#安装与快速开始) · [AI Agent Skills](#agent-skills) · [命令](#命令) · [批量](#批量任务codex-pro-订阅出图) · [安全](#安全与额度说明)

## 你是人类还是 Agent？

| 你是... | 推荐路径 |
| ------- | -------- |
| **人类** | [快速开始（人类用户）](#快速开始人类用户) |
| **AI Agent** | **直接跳到** [快速开始（AI Agent）](#快速开始ai-agent) |

> 给 AI Agent：只跑 AI Agent 小节；不要走人类交互说明。

## 安装与快速开始

### 环境要求

- Python 3.10+
- Node.js（npx，装 Skills，与飞书相同）
- Git
- 出图：Codex/ChatGPT 订阅，或可选 OPENAI_API_KEY

### 快速开始（人类用户）

> **Note for AI assistants:** 如果你是 AI Agent 且正在协助用户安装，请直接跳转到[快速开始（AI Agent）](#快速开始ai-agent)。

#### 安装（任选其一）

**方式一 — 推荐：**

```bash
git clone https://github.com/Doki21yy/yingzao-cli.git
cd yingzao-cli
./scripts/install.sh
```

**方式二 — 分步（对齐飞书：装 CLI + skills add）：**

```bash
git clone https://github.com/Doki21yy/yingzao-cli.git
cd yingzao-cli
python3 -m venv .venv && .venv/bin/pip install -e .
export PATH="$PWD/.venv/bin:$PATH"
export YINGZAO_SKILL_ROOT="$PWD/yingzao"
npx skills add https://github.com/Doki21yy/yingzao-cli --skill yingzao-cli -y -g
npx skills add https://github.com/op7418/guizang-yingzao-skill --skill yingzao -y -g
```

#### 配置与使用

```bash
source .yingzao-env
yingzao doctor
yingzao batch -i ./photos -o ./output --limit 10
```

装完 Skills 后请重启 Codex / Claude Code / Cursor Agent。

### 快速开始（AI Agent）

> 面向 AI Agent。缺 Node/依赖时把说明发给用户，勿干等交互。

**第 1 步 — 安装**

```bash
git clone https://github.com/Doki21yy/yingzao-cli.git
cd yingzao-cli
./scripts/install.sh --yes
```

**第 2 步 — 验证**

```bash
source .yingzao-env
yingzao which
yingzao doctor
echo "doctor_exit=$?"
```

doctor 非 0：让用户在 `.venv` 里 `pip install -r \"$YINGZAO_SKILL_ROOT/requirements.txt\"`，不要装全局 Python。

**第 3 步 — 使用**

- 单张：按 Skill，优先 `yingzao <cmd>`
- 批量：`yingzao batch -i <dir> -o ./output --limit N`，再把 CODEX_BATCH_PROMPTS.md 分段给 Codex
- prepare READY 后再出图；额度用**当前用户**订阅（约 3–5× 文本）

## Agent Skills

| Skill | 说明 |
| --- | --- |
| `yingzao-cli` | 本仓：CLI / batch / 非交互安装 |
| `yingzao` | 上游营造完整创意合同 |

```bash
npx skills add https://github.com/Doki21yy/yingzao-cli --skill yingzao-cli -y -g
npx skills add https://github.com/op7418/guizang-yingzao-skill --skill yingzao -y -g
```

## 命令

| 命令 | 作用 |
| --- | --- |
| `yingzao doctor` | 依赖检查 |
| `yingzao preflight` / `rectify` / `tokens` / `typeset` / `prepare` / `compare` | 上游确定性脚本 |
| `yingzao batch` | 批量编排（不出图） |
| `yingzao which` / `install-hint` | 路径与安装提示 |

## 批量任务（Codex Pro 订阅出图）

| 层 | 职责 |
| --- | --- |
| `yingzao batch` | manifest + CODEX_BATCH_PROMPTS.md |
| Codex + Skills | 分段出图，用操作者自己的额度 |
| OPENAI_API_KEY（可选） | API 计费 |

## 和飞书 CLI 的对应关系

| 飞书 lark-cli | yingzao-cli |
| --- | --- |
| `npx @larksuite/cli@latest install` | `git clone` + `./scripts/install.sh` |
| `npx skills add larksuite/cli -y -g` | `npx skills add` 本仓 + 上游 yingzao |
| 人类 / AI Agent 两节 + Note for AI assistants | 同上 |

## 安全与额度说明

- 不能把某人的 Pro 额度打包给别人
- 批量请分段
- 不抓取 Codex 登录态做未文档化调用

## 致谢

上游：[op7418/guizang-yingzao-skill](https://github.com/op7418/guizang-yingzao-skill)。文档结构参考飞书 CLI。

## 许可证

封装层 MIT 意图；`yingzao/` 遵循上游许可与署名。

