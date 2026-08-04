# 🧠 Claude Skills Collection

19 个可复用 AI Agent 技能，适用于 **Claude Code**、**Codex**、**OpenClaw**、**Hermes** 等 Agent 平台。

## 技能索引

| 技能 | 用途 | 说明 |
|------|------|------|
| **sc** | 技能上架工具 | 把本地技能打包发布到飞书 AI 技能库，生成说明页、附件和总索引 |
| **xx** | 学习资料挖掘 | 围绕主题挖掘 GitHub、官方文档、优质仓库，整理成中文学习内容发布到飞书 |
| **zsk** | 知识库导航 | 飞书知识库的智能路由，按请求类型自动匹配空间、页面和操作流程 |
| **fenxi** | 六帽分析 | 多维度决策分析工具：六帽思考、红队对抗、前验尸、SWOT 等，支持投资/招商/绩效/日常四种场景 |
| **xuexi** | 学习卡片 | 把文章/视频/课程消化成结构化学习卡片，可选导出到飞书知识库 |
| **pb** | 公文排版 | GB/T 9704-2012 国标公文排版，自动生成 Word 文档（方正公文小标宋/黑体/仿宋，28磅行距） |
| **skillgo** | 技能工程 | 把需求、SOP、提示词转化为标准 Agent 技能，支持六层架构设计和质量评审 |
| **gzh** | 公众号运营 | 一键生成/审核/发布公众号文章，含 AI 合规审查和三审流程 |
| **skillgogo** | 技能评审 | 创建、审查、改进技能的质量评审工具，输出结构化评分和改进建议 |
| **fyg** | 发言稿写作 | 政府/国企正式发言稿写作引擎：座谈会、招商会见、干部推荐、换届材料，六层质量管控 |
| **hyfy** | 发言稿工坊 | 对内对外各种场合发言稿生成器，三角平衡（对上×对下×对外）+ A+C 双风格金句库 + 用户偏好沉淀，可联动 pb 排版 |
| **rjgx** | 国企人际关系 | 国企职场人际关系诊断与策略：向上管理、向下管理、跨部门协调、拒绝/婉拒话术 |
| **go** | 投资研判 | PE投资初筛自动化：6维度搜索核验（含招聘验证）+ 铁律10条 + 研判报告 + 领导短信 + 公文docx |
| **anysearch** | 搜索增强 | 统一实时搜索引擎，支持网页/垂直领域/批量搜索/URL提取，匿名可用 |
| **reddit-scraper** | Reddit 爬虫 | 抓取 Reddit 热帖、搜索结果、帖子评论，支持多种排序和子版块 |
| **aisc** | 质量闸门知识沉淀 | 把文章、逐字稿、录音稿、网页和报告生成可验证学习卡片，按入库价值自动分层，并可上传飞书知识库更新索引 |
| **sx** | 学习内容升级 | 把没讲透的学习文章升级成小白能看懂 + 专业可信 + 能落地的版本（5 段轻量版 / 7 段完整版），含反例库 + 自查清单 |
| **AIfy** | AI 落地翻译 | 面向企业老板的 AI 落地引导工具：梳理业务路径→筛选 AI 场景→四层拆解→输出落地方案 |
| **agentgo** | Hermes 智能体上线 | 创建、修复或交接独立 Hermes profile 和独立飞书机器人，处理用户授权，生成 SOUL.md、AGENTS.md、README.md、PROJECT.md 四类上下文文件，并做安全与分层验证 |

## 快速安装

```bash
# 克隆仓库
git clone https://github.com/hesongshuaige/claude-skills.git
```

### 腾讯云 Linux 安装 AgentGo

以下四种方式**任选一种**，不要把四块命令全部执行。

**方式一：Claude Code**

```bash
mkdir -p ~/.claude/skills/agentgo
cp -r claude-skills/agentgo/. ~/.claude/skills/agentgo/
test -f ~/.claude/skills/agentgo/SKILL.md || { echo "AgentGo 安装检查失败"; exit 1; }
```

**方式二：Codex**

```bash
mkdir -p ~/.codex/skills/agentgo
cp -r claude-skills/agentgo/. ~/.codex/skills/agentgo/
test -f ~/.codex/skills/agentgo/SKILL.md || { echo "AgentGo 安装检查失败"; exit 1; }
```

**方式三：Hermes 默认 profile**

先确认默认档案已经初始化，只创建其下的技能子目录：

```bash
hermes skills --help
test -f "$HOME/.hermes/config.yaml" || { echo "Hermes 默认档案不存在，请先初始化"; exit 1; }
mkdir -p ~/.hermes/skills/agentgo
cp -r claude-skills/agentgo/. ~/.hermes/skills/agentgo/
test -f ~/.hermes/skills/agentgo/SKILL.md || { echo "AgentGo 安装检查失败"; exit 1; }
```

**方式四：Hermes 命名 profile**

先列出现有档案。必须把下面所有 `<真实档案名>` 替换为清单中的已有名称；存在性检查通过后，才会创建该档案下的技能子目录：

```bash
hermes skills --help
hermes profile list
test -f "$HOME/.hermes/profiles/<真实档案名>/profile.yaml" || { echo "Hermes 命名档案不存在，停止安装"; exit 1; }
mkdir -p "$HOME/.hermes/profiles/<真实档案名>/skills/agentgo"
cp -r claude-skills/agentgo/. "$HOME/.hermes/profiles/<真实档案名>/skills/agentgo/"
test -f "$HOME/.hermes/profiles/<真实档案名>/skills/agentgo/SKILL.md" || { echo "AgentGo 安装检查失败"; exit 1; }
```

以上命令适用于已经克隆仓库的腾讯云 Linux。整目录复制是为了同时带上参考资料、模板、验证器和测试；不要只下载 `SKILL.md`。Hermes 的 profile 选择方式会随版本变化，必须以本机帮助和已有档案清单为准，不能靠 `mkdir` 新造档案根目录。安装检查通过后，重启当前客户端或新开会话，让技能重新加载。

### 其他技能安装

```bash
# 安装单个技能到 Claude Code
cp -r claude-skills/pb ~/.claude/skills/

# 安装单个技能到 Codex
cp -r claude-skills/pb ~/.codex/skills/

# 推荐：使用各技能自带的 install.sh（自动检测 4 平台）
cd claude-skills/hyfy && bash install.sh
cd claude-skills/go && bash install.sh
cd claude-skills/aisc && bash install.sh

# 批量安装全部技能
for skill in claude-skills/*/; do
  if [ -f "$skill/install.sh" ]; then
    bash "$skill/install.sh"
  else
    cp -r "$skill" ~/.claude/skills/
  fi
done
```

## AgentGo 调用示例

安装后，在 Claude Code、Codex 或已选中正确 profile 的 Hermes 会话中直接说：

若没有自动触发，就在自然语言请求开头显式写 `$agentgo`；这不是 shell 命令，不要在终端里执行。

```text
帮我新建一个独立的 Hermes 聊天机器人，只处理飞书私聊。请使用独立 profile 和独立飞书应用，先验证模型，再分层验收网关、主动发送和私聊；不要启用用户资源权限。
```

```text
请为我的个人飞书知识库配置用户授权。先核对当前 Hermes profile、飞书应用和 lark-cli profile 是否一致，只申请读取目标知识库所需的最小权限；我确认前不要授权或写入。
```

```text
请修复已有的 Hermes profile。先只读检查模型、飞书应用独占、网关、用户授权和四类上下文文件，只修失败或缺失的层；不要替换仍然健康的飞书应用，也不要显示任何凭据值。
```

## AgentGo 当前验证状态

已通过技能静态检查、profile 验证器测试和两轮受限安全行为评测；两轮均为 9/12，安全违规 0。尚未完成 live E2E：真实飞书应用创建、用户授权、消息端到端测试，以及真实 Windows 到 Linux 中文文件传输仍需在目标租户和主机验收；当前不能据此宣称完整生产可用。

## 技能结构

每个技能目录包含：

```
skill-name/
├── SKILL.md          # 技能主文件（YAML frontmatter + Markdown 正文）
├── README.md         # 技能说明（部分技能有）
├── references/       # 参考文件（部分技能有）
├── examples/         # 案例文件（部分技能有）
├── agents/           # Agent 适配配置（部分技能有）
└── scripts/          # 辅助脚本（部分技能有）
```

## 技能分类

**写作与内容：**
- `pb` 公文排版 · `hyfy` 发言稿工坊（对内对外+风格化） · `fyg` 发言稿（正式公文+流程化） · `gzh` 公众号

**分析与研判：**
- `fenxi` 六帽分析 · `go` 投资研判（6维度搜索 + 铁律10条 + DPI量化）

**搜索工具：**
- `anysearch` 搜索增强（go 技能推荐安装，匿名模式可用）
- `xx` 学习挖掘 · `xuexi` 学习卡片 · `zsk` 知识库导航 · `aisc` 质量闸门知识沉淀

**技能工程：**
- `sc` 技能上架 · `skillgo` 技能构建 · `skillgogo` 技能评审 · `agentgo` Hermes 智能体上线与交接

**职场工具：**
- `rjgx` 人际关系 · `AIfy` AI 落地引导

**内容优化：**
- `sx` 学习内容升级（小白化 + 专业性 + 能落地，5 段轻量版 / 7 段完整版）

**数据采集：**
- `reddit-scraper` Reddit 爬虫

## 兼容性

仓库按以下常见技能目录和格式组织；这不表示每个技能都完成了全平台功能验证，具体功能验证以各技能自己的说明为准：

- Claude Code (`~/.claude/skills/`)
- Codex (`~/.codex/skills/`)
- OpenClaw (`~/.openclaw/skills/`)
- Hermes (`~/.hermes/skills/` 或命名 profile 的 `skills/` 子目录)
- Agents (`~/.agents/skills/`)

## 许可

MIT License
