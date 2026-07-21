# skillup — 提示词入库流水线（多版本可选）

把提示词做成飞书知识库文档的流水线，**先验证再交付**：每个新场景提示词都跑真实模型验证，过不了的标注保留，让你看到全貌。

## 3 个版本，安装时选一个

| 版本 | 适合谁 | 特点 | 场景池 |
|---|---|---|---|
| **v3**（默认·最新） | 想要最强、要建提示词库 | 身份节(6 子能力) + writing-skills 方法论 + A/B 分型 + 致命硬伤制 + 硬伤单一来源 | 4 池 |
| **v2**（分型版） | 要 A/B 分型但不要身份节 | A/B 分型(简单/复杂类) + 致命硬伤制(删打分) | 4 池 |
| **v1**（基础版） | 通用轻量，快速上手 | 基础 7 步流程，最简 | 2 池 |

不知道选哪个 → **装 v3**（默认就是）。

## 安装

```bash
# 1. clone 仓库
git clone https://github.com/hesongshuaige/claude-skills.git
cd claude-skills/skillup

# 2. 装到所有平台（默认 v3）
bash scripts/install.sh --all

# 或装指定版本到指定平台（只装那一个，不会全装）
bash scripts/install.sh --version v1 --claude    # v1 基础版 → Claude Code
bash scripts/install.sh --v2 --codex             # v2 分型版 → Codex
```

支持平台：Claude Code / Codex CLI / OpenClaw / Hermes / Agents（5 平台）。
运行 `bash scripts/install.sh --help` 看全部选项。

## 配置（必做，否则上传步骤跑不通）

skillup **不绑定任何特定飞书库**。提供两个值（任选一种）：

**方式 A**：环境变量（写进 `~/.bashrc`）
```bash
export SKILLUP_SPACE_ID="<你的飞书知识库 space_id>"
export SKILLUP_INDEX_TOKEN="<索引页 file_token>"
```

**方式 B**：配置文件 `~/.config/skillup.conf`
```
SKILLUP_SPACE_ID=...
SKILLUP_INDEX_TOKEN=...
```

另外需要：
- `lark-cli` 已装并 `lark-cli auth login`（user 身份）
- `MINIMAX_API_KEY` 环境变量，或 `~/.secrets/mm.env`（格式 `export MINIMAX_API_KEY=...`）

## 触发

在对应客户端说 `skillup` / `/skillup` / "把这个提示词入库" + 贴背景资料。

## 版本说明

- 三个版本各自独立、都能用（都已去硬编码，不绑定作者私有飞书库）。
- 每版改了啥 → [CHANGELOG.md](CHANGELOG.md)
- 旧版快照在 `archive/`：v1 = `archive/v1-basic`，v2 = `archive/v2-fenxing`。
- 场景池可替换：编辑所装版本的 `REFERENCE.md §一`，整表换成你行业的全链路场景，流程不变。

## 兼容性

5 平台（Claude Code / Codex / OpenClaw / Hermes / Agents）验证。

## 许可

MIT
