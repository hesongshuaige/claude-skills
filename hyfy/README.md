# 发言稿工坊（fy / speech-craft）

一句话介绍：**对内对外各种场合的发言稿生成器**——三角平衡（对上管理 × 对下担当 × 对外姿态）+ 金句库 + 用户偏好沉淀，让所有听众觉得你说得好。

> **版本：** 1.0.1 | **最后更新：** 2026-06-04 | **适用平台：** Claude Code / Codex / OpenClaw / Hermes / Agents

## ⚠️ 跟 `fyg` 的关键差异

仓库已有 `fyg`（发言稿写作引擎），定位偏**流程化**（六层质量管控、座谈会/招商/干部推荐/换届材料）。本 skill `fy` 定位偏**风格化**：

| 维度 | `fyg` | `fy`（本 skill） |
|---|---|---|
| 核心机制 | 六层质量管控（Context→Source→Procedure→Harness→Verification→Iteration） | 三角平衡（上×下×外）+ 金句库 + 用户偏好 |
| 典型场景 | 座谈会、招商会见、干部推荐、换届材料 | 商务会谈、项目推进、签约揭牌、调研接待、即兴讲话 |
| 风格 | 偏正式公文 | 70% 市场化 + 30% 政治（A 默认）/ 90% 市场化（C 备选） |
| 输出 | 长稿（5000 字+） | 短中长全覆盖（3 段式 3 分钟 / 5 段式 5-10 分钟） |
| 联动 | 独立 | **强烈建议**联动 `pb` 排版成公文 .docx |

> **简单说**：`fyg` 适合"严格按规范出大稿"；`fy` 适合"在各种场合让全场觉得你讲得好"。

## 🎯 核心特性

- 🎭 **三角平衡机制** —— 对上管理（请放心）+ 对下担当（不当旁观者）+ 对外姿态（既尊重 X 也体现 X）一个都不能少
- ✨ **A+C 双风格金句库** —— A（70/30 主流混合）默认，C（90/10 高度市场）可选
- 🎨 **8 类场景差异化打法** —— 商务会谈 / 项目推进 / 工作汇报 / 接待致辞 / 签约揭牌 / 调研接待 / 党建 / 即兴讲话
- 🛡️ **8 条铁律** —— 每段必有抓手、金句可独立引用、政治表述 ≤30%、副职不越位
- 🇨🇳 **5 类合规红线** —— 不编造政策、不编造数据、不编造领导人原话、不编造对方信息、不编造历史事件
- 📚 **12 项自检清单** —— 每次出稿后自检（参见 `examples/joint-venture.md`）
- 🧠 **用户偏好沉淀** —— 你历次反馈自动沉淀到 `references/user-preferences.md`，下次用 fy 时自动应用
- 🔗 **强联动 `pb`** —— fy 写内容 + pb 排版 = 公文格式 Word 文档直接上飞书云空间

## 📦 快速安装

### 方式 1：从 claude-skills 仓库安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/hesongshuaige/claude-skills.git

# 复制到对应平台目录（任选）
cp -r claude-skills/fy ~/.claude/skills/fy       # Claude Code
cp -r claude-skills/fy ~/.codex/skills/fy        # Codex
cp -r claude-skills/fy ~/.openclaw/skills/fy     # OpenClaw
cp -r claude-skills/fy ~/.hermes/skills/fy       # Hermes
cp -r claude-skills/fy ~/.agents/skills/fy       # 通用 agents
```

### 方式 2：单文件 GitHub 下载

```bash
# 下载 fy skill（pin 到 v1.0.1）
curl -L -o fy.zip https://github.com/hesongshuaige/claude-skills/archive/refs/heads/main.zip
unzip fy.zip "claude-skills-main/fy/*"
mv claude-skills-main/fy ~/.claude/skills/fy
```

## 🗣️ 触发词

**核心触发**：`fy`、`发言稿`、`致辞`、`讲话稿`、`领导讲话`、`会议发言`、`致辞稿`

**场景触发**：`工作表态`、`项目推进表态`、`接待致辞`、`签约致辞`、`揭牌致辞`、`汇报发言`、`调研发言`、`即兴讲话`

**意图触发**：
- "帮我写个致辞"
- "我马上要去发言"
- "起草一份领导讲话"
- "今天有个 X 会议，帮我准备讲话提纲"
- "给我写个表态稿"

## 🔄 6 步工作流

```
[1] 角色定位  → 决定语气（一把手可"讲要求"，副职只能"做表态"）
[2] 场合识别  → 决定结构（5 段式 / 3 段式 / 即兴式）
[3] 听众画像  → 决定金句投放（对上 / 对下 / 对外 / 全场）
[4] 核心三段  → 态度/立场 + 干货/抓手 + 表态/承诺
[5] 金句 1-3  → 嵌入正文 **加粗** 作为讲话的"重音位"
[6] 收尾收束  → 共同愿景 + 具体抓手 + 再次致谢
```

## 🔗 强烈建议联动：`pb` 排版

`fy` 负责写内容，`pb` 负责排版成公文格式 Word：

```
fy 出稿 → 加粗金句 → "建议联动 pb 排版" → pb 生成 .docx → 上传飞书云空间 → 返回链接
```

不排版 = 效果减半。详细联动流程见 `references/pairing-pb.md`。

## 📂 目录结构

```
fy/
├── SKILL.md                          # 主文件（核心机制 + 6 步工作流 + 8 条铁律）
├── README.md                         # 本文件
├── agents/
│   └── openai.yaml                   # Codex CLI 隐式触发配置
├── references/
│   ├── scenes.md                     # 8 类场景差异化打法
│   ├── golden-lines.md               # A+C 双风格金句库（含禁用句清单）
│   ├── structure.md                  # 5 段式/3 段式/即兴式骨架
│   ├── compliance.md                 # 国企/政务/党建合规红线
│   ├── pairing-pb.md                 # fy + pb 联动流程
│   └── user-preferences.md           # 用户偏好沉淀（自动维护）
└── examples/
    ├── joint-venture.md              # 通号合资公司案例（对外商务会谈，5 段式）
    ├── joint-venture-speech-final.md # 终稿
    ├── mid-year-push.md              # 年中工作推进案例（对内推进，3 段式）
    └── cheatsheet.md                 # 一页纸快速上手
```

## 💡 快速使用

对 AI Agent 说：

> "用 fy 帮我写个下周去拜访 XX 集团的发言稿，5 分钟，董事长用"

Agent 会：
1. 自动加载你的偏好（`references/user-preferences.md`）
2. 询问 5 个必问信息（场景/角色/听众/素材/风格）
3. 按 6 步工作流出稿（含 7-8 句加粗金句）
4. 提示联动 `pb` 排版
5. 上传飞书云空间，返回下载链接

整个流程 5-10 分钟，从"零"到"董事长可以直接念的稿子"。

## ✅ 兼容性

本 skill 通过以下平台验证：

- ✅ **Claude Code** (`~/.claude/skills/`)
- ✅ **Codex** (`~/.codex/skills/`)
- ✅ **OpenClaw** (`~/.openclaw/skills/`)
- ✅ **Hermes** (`~/.hermes/skills/`)
- ✅ **Agents** (`~/.agents/skills/`)

`agents/openai.yaml` 提供 Codex CLI 隐式触发配置。

## 🧪 已验证案例

| 案例 | 场景 | 结构 | 时长 | 效果 |
|---|---|---|---|---|
| 通号合资公司 | 对外商务会谈（央地合作） | 5 段式 | 5 分钟 | 用户验证"写得不错" |
| 年中工作推进 | 对内推进表态 | 3 段式 | 3 分钟 | 自检 12 项全通过 |

## 📋 5 个必问信息（用 fy 之前准备好）

| # | 问题 | 备选 |
|---|---|---|
| 1 | **场景**：什么类型？时长？ | 商务会谈 / 项目推进 / 汇报 / 致辞 / 签约揭牌 / 调研接待 / 党建 / 即兴 |
| 2 | **角色**：几把手？代表单位还是个人？ | 一把手 / 副职 / 部门负责人 |
| 3 | **听众**：在场最关键的人？ | 按"上/平/下/外"分类 |
| 4 | **素材**：已确定的数字、项目、机制？ | 直接给素材或说"暂无" |
| 5 | **风格**：A / C / A+C？ | 70/30 / 90/10 / 混搭 |

## 🛡️ 权限边界

`fy` **不会**自动执行以下操作（必须由用户明确授权）：
- ❌ 不会自动发布、上传、推送发言稿
- ❌ 不会自动调用 `pb` 技能排版（仅"建议"）
- ❌ 不会自动上传到飞书云空间
- ❌ 不会编造政策文件、数据、领导人原话
- ❌ 不会替代用户的最终判断——所有稿子必须用户审阅

## 📜 许可

MIT License
