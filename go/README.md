# 投资研判一键交付技能（go / touyan-pb）

一句话介绍：PE投资初筛自动化工具——从企业材料到研判报告 + 领导简报短信 + 公文格式Word，一键交付。

## 功能特性
- 🔍 **6维度搜索核验**（工商/行业/招聘/财务/法律/退出）——新增招聘+用工维度，自动发现注册资本矛盾、员工规模、融资标签差异
- ⚡ 快速否决通道（致命项目3分钟出局）
- 📝 4000-8000字专业研判报告
- 💬 领导简报短信（四段式，可直接转发）
- 📄 公文格式docx（方正公文小标宋/仿宋_GB2312排版）
- 🛡️ 国资合规六项核检（12号令/32号令/36号令）
- 🔒 铁律10条硬约束（信息缺失分级、退出DPI量化、首创落差核验）
- 🔗 搜索增强：自动检测并集成 anysearch CLI，未安装时无缝降级

## 快速安装

```bash
# 方式1：从 claude-skills 仓库安装（推荐，含搜索增强）
git clone https://github.com/hesongshuaige/claude-skills.git
cd claude-skills/go && bash install.sh

# 方式2：单独安装 go 技能
git clone https://github.com/hesongshuaige/claude-skills.git
cp -r claude-skills/go ~/.claude/skills/go
pip3 install python-docx
```

安装脚本会自动：
1. 检测并安装 Python 依赖（python-docx）
2. 检测并安装搜索增强组件（anysearch）
3. 创建输出目录（~/deliverables）

## 搜索增强（可选但推荐）

安装 **anysearch** 技能可获得更强的实时搜索能力：
- 招聘平台数据抓取（拉勾/猎聘/BOSS直聘的员工规模、融资标签、注册资本对比）
- 工商数据交叉验证（多源注册资本对比，发现矛盾信号）
- 创始人履历深度搜索

未安装 anysearch 时，技能将自动使用平台内置搜索工具（WebSearch/web_search）运行，功能完整但搜索精度略低。

安装方式：`install.sh` 会自动尝试安装，也可手动：
```bash
cp -r claude-skills/anysearch ~/.claude/skills/anysearch
```

## 使用方法

对 AI Agent 说：
> "帮我研判一下XX企业"

或者上传企业BP/财务报表后说：
> "分析一下这家公司能不能投"

**支持的平台**：Claude Code / Codex CLI / OpenClaw / Hermes

## 配置说明

编辑 `config.yaml`：
- fund_name：你的基金/投资公司名称
- recipient：报告主送单位
- sms_addressee：领导简报短信中的称呼
- local_district：产业匹配度分析的属地
- deliverables_dir：输出文件保存目录

## 输出物

| 输出 | 说明 |
|------|------|
| docx报告 | 公文格式，含短信附件、置信度评分卡 |
| 短信文本 | 四段式，可直接复制发送 |
| Markdown源文件 | 完整研判报告 |

## 技能架构

采用 thin orchestrator + references + 3 agents 设计：
- **编排层**（SKILL.md）：Phase 0 搜索工具检测 → Phase 1 材料识别 → Phase 2 搜索 → Phase 3-4 铁律核验+报告 → Phase 5-7 输出管道 → Phase 8 交付
- **参考文件**（references/）：铁律/模板/标准按需加载
- **3个子Agent**：搜索Agent（上下文隔离）→ 写作Agent（干净上下文写报告）→ 输出Agent（质量门禁+docx）

## 适用场景
- PE/VC投资初筛
- 招商引资项目研判
- 国资平台出资前判断
- 投决会前风险梳理

## 不适用场景
- 证券二级市场建议
- 债券信用评级
- 纯法律/税务/审计意见

## 依赖
- AI Agent（Claude Code / Codex CLI / OpenClaw / Hermes）
- Python 3.8+
- python-docx（install.sh 自动安装）
- anysearch（可选，install.sh 自动尝试安装）

## License
MIT
