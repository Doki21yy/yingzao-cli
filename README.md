# yingzao-cli

把 [guizang-yingzao-skill](https://github.com/op7418/guizang-yingzao-skill)（营造）封成 **CLI + Agent Skills** 双件套——学飞书 `lark-cli`：人能装，Agent 也能按文档自己装。

| 组件 | 作用 |
| --- | --- |
| `yingzao` 命令 | 确定性脚本入口（doctor / preflight / …） |
| `skills/` 里的 SKILL.md | 教 Agent 何时、怎么调这些命令 |

出图仍需：支持 Skills 的 Agent + 图像模型（上游推荐 GPT Image）。本 CLI **不**自己调图像 API。

> **完整度说明：** 包内自带上游完整 `yingzao/`（含 `scripts/design_tokens.py`、`references/`、`assets/`、官方 `SKILL.md`）。  
> CLI 默认打这份目录，不必再另设 `YINGZAO_SKILL_ROOT`（仍可用环境变量覆盖）。


---

## 安装与快速开始

### 环境要求

- Python 3.10+
- Node.js（`npx`）——只为安装 Agent Skills（与飞书 CLI 相同）
- 上游 Skill 目录（含 `scripts/`）

### 快速开始（人类用户）

> **Note for AI assistants:** 如果你是 AI Agent 且正在协助用户安装，请直接跳到 [快速开始（AI Agent）](#快速开始ai-agent)。

#### 安装（任选其一）

**方式一 — 一键脚本（推荐）：**

```bash
# 在本仓库根目录
./scripts/install.sh
```

脚本会：

1. 创建/使用 `.venv` 并 `pip install -e .`
2. 若未设置，提示你 clone 上游并导出 `YINGZAO_SKILL_ROOT`
3. 执行 `npx skills add <本仓库或上游> -y -g` 写入本机 Agent Skills

**方式二 — 手动：**

```bash
git clone https://github.com/op7418/guizang-yingzao-skill.git
export YINGZAO_SKILL_ROOT="$PWD/guizang-yingzao-skill/yingzao"

cd yingzao-cli
python3 -m venv .venv
.venv/bin/pip install -e .
export PATH="$PWD/.venv/bin:$PATH"

# 装 Agent Skills（必需，否则 Agent 不知道怎么调 CLI）
npx skills add https://github.com/op7418/guizang-yingzao-skill --skill yingzao -y -g
# 若已发布本封装仓库，可改为：
# npx skills add <your/yingzao-cli> -y -g
```

#### 验证

```bash
yingzao --help
yingzao which
yingzao doctor
```

然后在 Agent 里说：`用 $yingzao 把这张照片做成 3:4 海报；先跑 yingzao doctor。`

---

### 快速开始（AI Agent）

> 面向 Agent。需要用户配合的步骤（授权、确认路径）请把链接/问题发给用户，不要干等交互式输入。

**第 1 步 — 安装 CLI + Skills**

```bash
cd <yingzao-cli 仓库根目录>
./scripts/install.sh --yes
```

若没有 `install.sh`，等价执行：

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
# 确保 yingzao 在 PATH
export PATH="$(pwd)/.venv/bin:$PATH"

# 上游 skill 根目录
test -n "$YINGZAO_SKILL_ROOT" || {
  git clone --depth 1 https://github.com/op7418/guizang-yingzao-skill.git /tmp/guizang-yingzao-skill
  export YINGZAO_SKILL_ROOT=/tmp/guizang-yingzao-skill/yingzao
}

npx skills add https://github.com/op7418/guizang-yingzao-skill --skill yingzao -y -g
```

**第 2 步 — 验证（非交互）**

```bash
yingzao which
yingzao doctor
echo "ok=$?"
```

`doctor` 缺依赖时会非 0 退出并打印说明；把缺包列表告诉用户，让用户在 `.venv` 里 `pip install -r "$YINGZAO_SKILL_ROOT/requirements.txt"`，**不要**静默装到全局 Python。

**第 3 步 — 使用**

读取已安装的 `yingzao` Skill，按其中流程调用 `yingzao <cmd>`；仅当 `yingzao prepare` 返回 READY 后再调图像模型。

---

## 和飞书 CLI 的对应关系

| 飞书 lark-cli | 本项目 yingzao-cli |
| --- | --- |
| `npx @larksuite/cli@latest install` 装二进制 | `./scripts/install.sh` / `pip install -e .` 装 `yingzao` |
| `npx skills add larksuite/cli -y -g` 装 Skills | `npx skills add …yingzao… -y -g` |
| README 分「人类 / AI Agent」两节 | 同上 |
| 命令干活，Skill 教 Agent 何时调命令 | 同上 |
| `auth login --no-wait` 等 Agent 友好交互 | 本项目无 OAuth；依赖/路径问题用非交互退出码 + 明文提示 |

---

## 命令一览

- `yingzao doctor` → `check_dependencies.py`
- `yingzao preflight …` → `photo_preflight.py`
- `yingzao rectify …` → `rectify.py`
- `yingzao tokens …` → `design_tokens.py`
- `yingzao typeset …` → `typeset_compose.py`
- `yingzao prepare …` → `prepare_generation.py`
- `yingzao compare …` → `make_comparison.py`
- `yingzao which` / `yingzao install-hint`

产物：调用者目录 `output/yingzao/<run-id>/`，勿写入 Skill 包。

## 致谢

上游能力：[op7418/guizang-yingzao-skill](https://github.com/op7418/guizang-yingzao-skill)。安装体验对齐 [larksuite/cli](https://github.com/larksuite/cli)。

---

## 批量任务（Codex Pro 订阅出图）

架构约定：

| 层 | 职责 |
| --- | --- |
| `yingzao batch` | 扫描目录、建工作区、写 `batch-manifest.json` + `CODEX_BATCH_PROMPTS.md` |
| Codex Agent + `$yingzao` Skill | 按清单逐张/分段出图，**消耗操作者自己的 Codex/ChatGPT 额度** |
| `OPENAI_API_KEY`（可选） | 以后可接 API 出图；与订阅是两本账 |

```bash
# 1) 安装
cd yingzao-cli && ./scripts/install.sh
source .yingzao-env

# 2) 编排批量（不出图）
yingzao batch -i ~/Desktop/photos -o ./output --limit 100

# 3) 打开 Codex，安装 Skill 后执行汇总提示
# npx skills add https://github.com/op7418/guizang-yingzao-skill --skill yingzao -y -g
# 把 output/yingzao/batch-*/CODEX_BATCH_PROMPTS.md 交给 Codex 分段跑
```

注意：

- 图像大约比纯文本更吃额度（官方量级约 3–5×）；100 张请分段。
- **不能**把你的 Pro 额度打包进 GitHub 给别人用；每人用自己的登录或 Key。
- 本仓库不抓取 Codex 登录态做黑产式调用。

## 发布到 GitHub（给任何人下载）

1. 新建公开仓库（例如 `yourname/yingzao-cli`）
2. 推送本目录（已含上游 `yingzao/` 时请遵守上游 License / 致谢）
3. README 保留「人类 / AI Agent」双安装 + 本批量章节
4. 别人：`git clone` → `./scripts/install.sh` → `yingzao batch` → 用**自己的** Codex 出图

