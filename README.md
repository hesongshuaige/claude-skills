# 🧠 Claude Skills Collection

25 个生产级 AI Agent 技能，适用于 **Claude Code**、**Codex**、**OpenClaw**、**Hermes** 等 Agent 平台。

## 技能索引

| 技能 | 用途 | 说明 |
|------|------|------|
| **sc** | 技能上架工具 | 把本地技能打包发布到飞书 AI 技能库，生成说明页、附件和总索引 |
| **xx** | 学习资料挖掘 | 围绕主题挖掘 GitHub、官方文档、优质仓库，整理成中文学习内容发布到飞书 |
| **zsk** | 知识库导航 | 飞书知识库的智能路由，按请求类型自动匹配空间、页面和操作流程 |
| **fenxi** | 六帽分析 | 多维度决策分析工具：六帽思考、红队对抗、前验尸、SWOT 等，支持投资/招商/绩效/日常四种场景 |
| **xuexi** | 学习卡片 | 把文章/视频/课程消化成结构化学习卡片，可选导出到飞书知识库 |
| **xuexi2** | 小白学习稿 | 把文章/课程/教程降噪后转成小白能看懂、能行动、能自查、能举一反三的学习稿 |
| **pb** | 公文排版 | GB/T 9704-2012 国标公文排版，自动生成 Word 文档（方正公文小标宋/黑体/仿宋，28磅行距） |
| **skillgo** | 技能工程 | 把需求、SOP、提示词转化为标准 Agent 技能，支持六层架构设计和质量评审 |
| **hermes-agent-builder** | Hermes 智能体构建 | 把模糊需求转成可运行、可验收、可回滚的 Hermes 智能体，覆盖独立 Profile、飞书接入、权限、测试和长期运行 |
| **gzh** | 公众号运营 | 一键生成/审核/发布公众号文章，含 AI 合规审查和三审流程 |
| **skillgogo** | 技能评审 | 创建、审查、改进技能的质量评审工具，输出结构化评分和改进建议 |
| **fyg** | 发言稿写作 | 政府/国企正式发言稿写作引擎：座谈会、招商会见、干部推荐、换届材料，六层质量管控 |
| **hyfy** | 发言稿工坊 | 对内对外各种场合发言稿生成器，三角平衡（对上×对下×对外）+ A+C 双风格金句库 + 用户偏好沉淀，可联动 pb 排版 |
| **ldyq** | 董事长文稿与推进方案 | 诸葛资本董事长文稿和工作推进适配器：对内知己、向上争取、对外公开三类模式，强化真实底数、堵点打法、需协调事项和数据核对 |
| **rjgx** | 国企人际关系 | 国企职场人际关系诊断与策略：向上管理、向下管理、跨部门协调、拒绝/婉拒话术 |
| **go** | 投资研判 | PE投资初筛自动化：6维度搜索核验（含招聘验证）+ 铁律10条 + 研判报告 + 领导短信 + 公文docx |
| **anysearch** | 搜索增强 | 统一实时搜索引擎，支持网页/垂直领域/批量搜索/URL提取，匿名可用 |
| **reddit-scraper** | Reddit 爬虫 | 抓取 Reddit 热帖、搜索结果、帖子评论，支持多种排序和子版块 |
| **hermes-tweet** | X/Twitter 工作流 | 为 Hermes Agent 配置 X/Twitter 检索、时间线、导出、监控和受控写入流程 |
| **aisc** | 质量闸门知识沉淀 | 把文章、逐字稿、录音稿、网页和报告生成可验证学习卡片，按入库价值自动分层，并可上传飞书知识库更新索引 |
| **sx** | 学习内容升级 | 把没讲透的学习文章升级成小白能看懂 + 专业可信 + 能落地的版本（5 段轻量版 / 7 段完整版），含反例库 + 自查清单 |
| **AIfy** | AI 落地翻译 | 面向企业老板的 AI 落地引导工具：梳理业务路径→筛选 AI 场景→四层拆解→输出落地方案 |
| **skillup** | 提示词入库 | 提示词入库流水线：身份节(6子能力)→提取原版→A/B判型→写优化版+设计要点→举一反三(4池选6条:新媒体/私募GP-LP/人事/财务)→MiniMax-M3/image-01实测(致命硬伤收敛)→lark-cli上传飞书+更新索引；零硬编码，不绑定特定飞书库 |
| **skillyes** | 提示词查找 | 从飞书提示词库匹配可直接复用的提示词，并用样例和变式教会用户迁移使用 |
| **cybgup** | 以投促招研判 | 国资以投促招项目初步研判报告：20维度研判+三层验证引擎(查证→推断→盲区)+浏览器优先搜索+可比公司估值+DCF情景分析+国标公文Word |

## 快速安装

```bash
# 克隆仓库
git clone https://github.com/hesongshuaige/claude-skills.git

# 安装单个技能到 Claude Code
cp -r claude-skills/pb ~/.claude/skills/

# 安装单个技能到 Codex
cp -r claude-skills/pb ~/.codex/skills/

# 推荐：使用各技能自带的 install.sh（自动检测 4 平台）
cd claude-skills/hyfy && bash install.sh
cd claude-skills/ldyq && bash install.sh
cd claude-skills/go && bash install.sh
cd claude-skills/aisc && bash install.sh
cd claude-skills/cybgup && bash install.sh
cd claude-skills/hermes-agent-builder && bash install.sh

# 批量安装全部技能
for skill in claude-skills/*/; do
  if [ -f "$skill/install.sh" ]; then
    bash "$skill/install.sh"
  else
    cp -r "$skill" ~/.claude/skills/
  fi
done
```

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
- `pb` 公文排版 · `hyfy` 发言稿工坊（对内对外+风格化） · `fyg` 发言稿（正式公文+流程化） · `ldyq` 董事长文稿与推进方案 · `gzh` 公众号

**分析与研判：**
- `fenxi` 六帽分析 · `go` 投资研判（6维度搜索 + 铁律10条 + DPI量化） · `cybgup` 以投促招研判（20维度 + 三层验证引擎 + 浏览器优先搜索 + DCF估值）

**搜索工具：**
- `anysearch` 搜索增强（go 技能推荐安装，匿名模式可用）
- `xx` 学习挖掘 · `xuexi` 学习卡片 · `xuexi2` 小白学习稿 · `zsk` 知识库导航 · `aisc` 质量闸门知识沉淀

**技能工程：**
- `sc` 技能上架 · `skillgo` 技能构建 · `skillgogo` 技能评审 · `hermes-agent-builder` Hermes 智能体构建

**职场工具：**
- `rjgx` 人际关系 · `AIfy` AI 落地引导

**内容优化：**
- `sx` 学习内容升级（小白化 + 专业性 + 能落地，5 段轻量版 / 7 段完整版）

**数据采集：**
- `reddit-scraper` Reddit 爬虫 · `hermes-tweet` X/Twitter 工作流

## 兼容性

所有技能均通过以下平台验证：
- ✅ Claude Code (`~/.claude/skills/`)
- ✅ Codex (`~/.codex/skills/`)
- ✅ OpenClaw (`~/.openclaw/skills/`)
- ✅ Hermes (`~/.hermes/skills/`)
- ✅ Agents (`~/.agents/skills/`)

`hermes-agent-builder` 的兼容约定：

- `SKILL.md` 只使用标准 YAML frontmatter（元数据）和 Markdown（通用文档格式），Claude、Codex、Hermes 都可直接读取。
- `references/`（参考资料）按需读取，不依赖特定平台的工具名称；没有对应工具时必须使用等价能力并说明替代方案。
- `agents/openai.yaml` 只提供 Codex/OpenAI 展示信息，不影响 Claude、Hermes 读取主技能。
- `install.sh` 支持 `--claude`、`--codex`、`--openclaw`、`--hermes`、`--agents` 和 `--all`；Hermes 使用独立 Profile 时可通过 `HERMES_SKILLS_DIR` 指定 Profile 的技能目录。
- 技能本身不携带飞书密钥、服务器权限或系统级删除守卫；这些仍由各平台的运行时和操作系统配置负责。

## 许可

MIT License
