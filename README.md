# 🧠 Claude Skills Collection

17 个生产级 AI Agent 技能，适用于 **Claude Code**、**Codex**、**OpenClaw**、**Hermes** 等 Agent 平台。

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
| **fy** | 发言稿工坊 | 对内对外各种场合发言稿生成器，三角平衡（对上×对下×对外）+ A+C 双风格金句库 + 用户偏好沉淀，可联动 pb 排版 |
| **rjgx** | 国企人际关系 | 国企职场人际关系诊断与策略：向上管理、向下管理、跨部门协调、拒绝/婉拒话术 |
| **go** | 投资研判 | PE投资初筛自动化：6维度搜索核验（含招聘验证）+ 铁律10条 + 研判报告 + 领导短信 + 公文docx |
| **anysearch** | 搜索增强 | 统一实时搜索引擎，支持网页/垂直领域/批量搜索/URL提取，匿名可用 |
| **reddit-scraper** | Reddit 爬虫 | 抓取 Reddit 热帖、搜索结果、帖子评论，支持多种排序和子版块 |
| **aisc** | 知识沉淀 | 把学习内容分析整理后自动上传到飞书知识库，生成索引卡片 |
| **AIfy** | AI 落地翻译 | 面向企业老板的 AI 落地引导工具：梳理业务路径→筛选 AI 场景→四层拆解→输出落地方案 |

## 快速安装

```bash
# 克隆仓库
git clone https://github.com/hesongshuaige/claude-skills.git

# 安装单个技能到 Claude Code
cp -r claude-skills/pb ~/.claude/skills/

# 安装单个技能到 Codex
cp -r claude-skills/pb ~/.codex/skills/

# 批量安装全部技能
for skill in claude-skills/*/; do
  cp -r "$skill" ~/.claude/skills/
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
- `pb` 公文排版 · `fy` 发言稿工坊（对内对外+风格化） · `fyg` 发言稿（正式公文+流程化） · `gzh` 公众号

**分析与研判：**
- `fenxi` 六帽分析 · `go` 投资研判（6维度搜索 + 铁律10条 + DPI量化）

**搜索工具：**
- `anysearch` 搜索增强（go 技能推荐安装，匿名模式可用）
- `xx` 学习挖掘 · `xuexi` 学习卡片 · `zsk` 知识库导航 · `aisc` 知识沉淀

**技能工程：**
- `sc` 技能上架 · `skillgo` 技能构建 · `skillgogo` 技能评审

**职场工具：**
- `rjgx` 人际关系 · `AIfy` AI 落地引导

**数据采集：**
- `reddit-scraper` Reddit 爬虫

## 兼容性

所有技能均通过以下平台验证：
- ✅ Claude Code (`~/.claude/skills/`)
- ✅ Codex (`~/.codex/skills/`)
- ✅ OpenClaw (`~/.openclaw/skills/`)
- ✅ Hermes (`~/.hermes/skills/`)
- ✅ Agents (`~/.agents/skills/`)

## 许可

MIT License
