---
name: skillup
description: "Use when the user says 'skillup' / '/skillup' / '把这个提示词入库' and pastes prompt background material. Pipeline: extract original prompt → write optimized version + design notes → derive 6 new scenarios from configured pools (default: new-media ops + PE GP/LP) → verify each scenario with MiniMax-M3 (text) or image-01 (image) → upload to Feishu prompt library via lark-cli → update index. Deliver only after all scenarios pass verification."
---

# skillup — 提示词入库流水线

把提示词背景资料做成飞书知识库文档的流水线：提取原版 → 写优化版 + 设计要点 → 举一反三 6 个新场景 → 每个场景用 MiniMax-M3 / image-01 实测验证 → 全通过才用 lark-cli 上传到飞书 AI 提示词工程库 → 自动更新索引。

## 不可违背的硬要求（每次必查）

1. **举一反三场景只用配置的池**：默认两池 = 新媒体运营 + 私募股权 GP/LP（见 REFERENCE.md §一）。两个池可按使用者行业替换（见 REFERENCE.md §一末尾说明）。禁止用健身/外教/驾校等无关场景。
2. **每个新场景提示词必须实测通过才交付**：文本类 M3 跑 3 轮（开场/答错/答对），生图类 image-01 出图。不通过就调提示词重试 2 次，还不行跳过 + 在该场景标注"未通过验证"。
3. **上传文档格式严格 = 背景 → 原版 → 优化版 → 用法 → 设计要点 → 举一反三**。**绝不写**实测过程/评估表/分析/对话流。原版 + 背景必须保留。
4. 验证在后台做，文档里每个场景只给「一句场景说明 + 完整提示词」。

## 流程

1. **提取**：从用户贴的背景资料提取【背景】【原版提示词】【使用场景】。不清楚先问，别猜。
2. **判类型**：学习类（苏格拉底提问）/ 文案类 / 分析类 / 生图类。类型决定验证标准（REFERENCE.md §二）。
3. **写骨架文档**：背景 + 原版 + 优化版（保留人设、补硬约束）+ 设计要点（为什么管用）+ 用法。
4. **举一反三**：按类型从配置的池里选 6 个场景，每个写完整提示词（换人设 + 探测问题，核心机制原样）。
5. **实测**：跑 `scripts/verify_text.py`（文本类）或 `scripts/verify_image.py`（生图类），逐场景验证并记录通过/不通过。
   - 不通过：调提示词重试 2 次；还不行 → 该场景标注"未通过验证"，不删除（让用户看到）。
6. **上传**：跑 `scripts/upload.sh "<标题>" <md文件路径>`，传到飞书库拿 node_token。索引更新由 AI 调 `lark-cli markdown +overwrite --file-token $SKILLUP_INDEX_TOKEN`（见 REFERENCE.md §四）。
7. **交付**：文字回复给「文档链接 + 一句话场景清单 + 哪些场景未通过（如有）」。不写分析/评估。

## 配置（必须先配，否则上传步骤跑不通）

skillup **不绑定任何特定飞书库**。运行上传前需提供两个值（任选一种方式）：

**方式 A：环境变量**（推荐写进 `~/.bashrc`）

```bash
export SKILLUP_SPACE_ID="<你的飞书知识库 space_id>"
export SKILLUP_INDEX_TOKEN="<索引页 file_token>"
```

**方式 B：配置文件** `~/.config/skillup.conf`

```
SKILLUP_SPACE_ID=...
SKILLUP_INDEX_TOKEN=...
```

`scripts/upload.sh` 按 环境变量 → 配置文件 顺序读取；都没有就报错退出。

**MiniMax key**（验证步骤用）：环境变量 `MINIMAX_API_KEY`，或 `~/.secrets/mm.env`、`./.secrets/mm.env` 任一处（文件格式：`export MINIMAX_API_KEY=...`）。

**飞书工具**：需装 `lark-cli` 并 `lark-cli auth login`（user 身份）。

## 本 skill 文件结构

```
skillup/
├── SKILL.md          # 本文件
├── REFERENCE.md      # 场景池 + 验证标准 + 飞书坑 + M3 用法
├── README.md         # 技能说明
└── scripts/
    ├── verify_text.py    # 文本类场景批量验证（M3）
    ├── verify_image.py   # 生图类验证（image-01）
    ├── upload.sh         # 飞书上传（+ 索引更新由 AI 调 overwrite）
    └── install.sh        # 多平台安装（5 平台）
```

## 跨客户端

`scripts/install.sh` 自动检测并把 skill 复制到 5 个平台：

- Claude Code: `~/.claude/skills/skillup/`
- Codex: `~/.codex/skills/skillup/`
- OpenClaw: `~/.openclaw/skills/skillup/`
- Hermes: `~/.hermes/skills/skillup/`
- Agents: `~/.agents/skills/skillup/`

用法：`bash install.sh --all`（默认）或 `bash install.sh --claude`。
