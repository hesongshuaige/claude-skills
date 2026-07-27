# skillyes — 提示词出库查找 + 学习教练

遇到问题不知道用哪个提示词时，从飞书「AI提示词工程库」匹配对症提示词，**贴全文拿来即用** + **教你这类框架**（脚手架渐隐·跨次记忆）。跟 [skillup](../skillup)（入库）对称闭环。

## 它解决什么
- **痛点**：飞书库里几十上百条提示词，每次遇到问题翻飞书半天找不到，或乱问导致答案质量差。
- **skillyes**：贴问题 → 30 秒拿到对症提示词全文 + 学这类问题的通用框架。

## 安装

```bash
# 1. clone 仓库
git clone https://github.com/hesongshuaige/claude-skills.git
cd claude-skills/skillyes

# 2. 装到所有平台
bash scripts/install.sh --all

# 或装指定平台
bash scripts/install.sh --claude           # 仅 Claude Code
bash scripts/install.sh --codex --hermes   # Codex + Hermes
```

支持平台：Claude Code / Codex CLI / OpenClaw / Hermes / Agents（5 平台）。
运行 `bash scripts/install.sh --help` 看全部选项。

## 配置（必做，否则 fetch 跑不通）

skillyes **不绑定任何特定飞书库**。提供两个值（任选一种）：

**方式 A**：环境变量（写进 `~/.bashrc`）
```bash
export SKILLYES_SPACE_ID="<你的飞书知识库 space_id>"
export SKILLYES_INDEX_TOKEN="<索引页 file_token>"
```

**方式 B**：配置文件 `~/.config/skillyes.conf`
```
SKILLYES_SPACE_ID=...
SKILLYES_INDEX_TOKEN=...
```

> 索引页要求是 agent 友好格式：每条带 6 字段（🔗链接 / 干啥 / 什么时候用 / 你给它 / 它给你 / 关键词）+ 9 类标签（写作/拆解/分析/开发/驾驭/决策/设计/学习/框架）。库不是这个格式的话，先用 [skillup](../skillup) 整理。

另外需要：
- `lark-cli` 已装并 `lark-cli auth login`（user 身份）

## 触发

在对应客户端说 `帮我找个提示词` / `不知道用啥提示词` / `/skillyes` + 贴你的问题。

## 各 agent 兼容性

| Agent | 装到 | 触发 |
|---|---|---|
| Claude Code | `~/.claude/skills/skillyes/` | 原生 `/skillyes` |
| Codex CLI | `~/.codex/skills/skillyes/` | 说"帮我找个提示词" |
| OpenClaw | `~/.openclaw/skills/skillyes/` | 说"帮我找个提示词" |
| Hermes | `~/.hermes/skills/skillyes/` | 说"帮我找个提示词"（若不识别见下） |
| Agents | `~/.agents/skills/skillyes/` | 通用 |

⚠️ **Hermes / OpenClaw 若不自动识别 skills 目录**：在各端的 `AGENTS.md`（如 `~/.hermes/AGENTS.md`）注入一行——
> 当用户说 skillyes / 找提示词 / 不知道用啥提示词时，执行 `~/.<agent>/skills/skillyes/SKILL.md`。

各端真触发能力以实测为准。

## 跟 skillup 的关系

- **skillup**：提示词**入库**（优化 + 实测 + 存飞书库）
- **skillyes**：提示词**出库**（从库找对症 + 教学）

俩配合：skillup 造提示词进库 → skillyes 从库找提示词用，库越用越全。找不到时 skillyes 引导你用 skillup 造一条。

## 许可

MIT
