---
name: go
description: Use when 研判/初步研判/看看这家企业/能不能投/分析一下XX公司/研判报告/投资研判
---

# 投资研判一键交付技能（go / touyan-pb）

## 配置

使用前读取本目录下 `config.yaml` 获取配置项（fund_name, recipient, sms_addressee, local_district, deliverables_dir）。若文件不存在则使用默认值。

默认值：
- fund_name: "你的基金/投资公司名称"
- recipient: "主送单位名称"
- sms_addressee: "董事长"
- local_district: "所在区/县"
- deliverables_dir: "~/deliverables"

> **路径约定**：`{skill_dir}` 指本 SKILL.md 所在目录。脚本位于 `{skill_dir}/scripts/` 下。

## 适用边界

| | 范围 |
|---|---|
| **适用** | 单企业投资初筛、招商投资研判、国资平台出资前判断、拟投企业正式PE尽调框架搭建、投决会前风险和信息缺口梳理 |
| **不适用** | 证券二级市场买卖建议、债券信用评级、纯行业研究、纯法律意见、纯审计报告、税务筹划方案、已签约项目的合同履约争议处理。遇到这些场景只能输出投资研判视角的风险提示，不能替代专业机构意见 |

## 快速否决触发条件

| 触发信号 | 典型表现 | 否决依据 |
|---------|---------|---------|
| **一票否决** | 失信被执行人、重大行政处罚未结、实控人被限制高消费、核心专利全部无效 | P0级信息缺失/风险 |
| **财务硬伤** | 连续两年营收下滑超50%、经营性现金流持续为负且无改善趋势、资产负债率>85% | 基本面不可逆恶化 |
| **国资合规红线** | 明股实债特征、变相保底承诺、资金来源违规、应进场未进场 | 国资合规六项 |
| **关联依赖** | 关联方营收/采购>60%且无合理论证 | 业务独立性缺失 |
| **首创落差** | BP自称首创>10处，发明专利0项 | 核心硬伤 |

命中任一触发信号 → 1次搜索+材料速读确认 → 输出快速否决短信（四段式，见references/sms-rules.md） → 终止，不写完整报告。

快速否决短信模板：
```
{sms_addressee}，关于XX企业，经初步了解，存在以下致命问题，建议不推进：
1. [最致命问题，一句话]
2. [第二严重问题，一句话]
综上，该项目存在根本性缺陷，建议不再投入时间。如需了解详情我可补充。
以上情况，请{sms_addressee}阅示。
```

## 搜索策略概述

### 搜索工具检测与优先级

主session在Phase 2开始前，先检测当前环境中可用的搜索工具，按以下优先级选择：

1. **anysearch CLI**（如已安装）：检测路径 `{skill_dir}/../anysearch/scripts/anysearch_cli.py` 是否存在
   - Claude Code：使用 `python3 {anysearch_path} search "query" --max_results 5`
   - Codex CLI：使用 `python3 {anysearch_path} search "query" --max_results 5`
   - 其他平台：同上（需 Python 3.8+ 和 requests 库）
2. **平台内置搜索工具**：
   - Claude Code → WebSearch 工具
   - Codex CLI → 内置 web_search 工具
   - OpenClaw / Hermes → 平台提供的搜索 MCP 或工具
3. **Web Fetch / mcp__web_reader__webReader**（有URL但需深入抓取时）
4. **无搜索工具时**：仅基于企业材料分析，报告声明"公开搜索不可用"

> **检测方法**：在派搜索Agent前，主session先尝试运行 `python3 {anysearch_path} search "test" --max_results 1`，成功则标记 `search_tool=anysearch`，失败则标记 `search_tool=platform_builtin`。将标记传入搜索Agent的prompt中。

### 搜索维度（6维度，新增招聘+用工验证）

详细搜索维度、关键词、目标说明见 `references/data-sources.md`。

**核心升级：搜索维度从5维扩展为6维，新增"招聘+用工"维度。**

| 搜索序号 | 维度 | 搜索关键词模板 | 数据目标 |
|:---:|------|----------------|---------|
| 1 | 工商+股权+融资+资质 | `"{企业名} 工商信息 股权 融资 专精特新 高新技术"` | 成立时间、注册资本、实缴、股权穿透、资质 |
| 2 | 主营业务+行业+案例 | `"{企业名} 主营业务 行业分析 市场规模 客户"` | 业务方向验证、行业地位、客户名单 |
| 3 | **招聘+用工+团队验证** | `"{企业名} 招聘 拉勾 猎聘 BOSS直聘 员工规模"` + `"{创始人名} 履历 简历 背景"` | **员工规模、融资状态标签、创始人履历验证、薪酬水平** |
| 4 | 财务+可比公司 | `"{企业名} 财务数据 可比公司 PS PE 估值"` | 营收、利润、可比估值 |
| 5 | 法律+负面 | `"{企业名} 诉讼 处罚 被执行人 负面"` | 诉讼、行政处罚、失信 |
| 6 | 上市+退出 | `"{企业名} IPO 上市 退出 并购 收购"` | IPO进度、可比交易 |

**搜索3（招聘+用工）的关键价值**（实战验证）：
- 招聘平台（拉勾/猎聘/BOSS直聘）上的企业主页通常包含：员工规模、融资状态标签、注册资本（可能与工商不一致）、详细地址
- 创始人履历在行业报道、学术数据库、企业官网中可能有痕迹
- 招聘JD可以验证企业的实际业务方向和技术栈
- **注册资本不一致（招聘平台vs工商）是重要矛盾信号**

### 搜索配额（按企业阶段）

| 企业阶段 | 搜索次数上限 | 必搜维度 | 公开信息覆盖 |
|---------|:---:|---------|:---:|
| 成熟期（已上市/已递招股书） | 7-9次 | 工商+财务+法律+退出+行业+可比+招聘 | 70-80% |
| 成长期（多轮融资） | 6次 | 工商+行业+财务+法律+退出+招聘 | 50-60% |
| 早期（A轮前） | 4次 | 工商+行业+法律+招聘 | 30-40% |
| 传统国企（非上市） | 5次 | 工商+法律+舆情+行业+招聘 | 30-40% |

搜索效率铁律：配额用完仍有缺口 → 报告声明数据缺失，不凑数搜索。正式投决/上会材料不受配额限制。

## 执行流程

```
主Session（编排层）
├── Phase 0: 检测搜索工具 → 确定search_tool标记
├── Phase 1: 材料识别 → 读 references/material-identification.md
├── Phase 2: 搜索 → 派搜索Agent（prompt模板+schema见下）
├── Phase 3+4: 铁律核验+报告撰写 → 派写作Agent（prompt模板+schema见下）
├── Phase 5-7: 输出管道 → 派输出Agent（prompt模板+schema见下）
└── Phase 8: 交付
```

### Phase 0：搜索工具检测（主session）

在Phase 1之前，主session执行搜索工具检测：

```
1. 检查 {skill_dir}/../anysearch/scripts/anysearch_cli.py 是否存在
2. 如存在，运行 python3 {path} search "test" --max_results 1
3. 成功 → search_tool="anysearch"，记录CLI路径
4. 失败或不存在 → search_tool="platform_builtin"
5. 将search_tool标记写入搜索Agent的prompt中
```

### Phase 1：材料识别（主session）

- **输入**：用户上传的文件 或 企业名称
- **动作**：读取 `references/material-identification.md`，按文件类型识别矩阵自动识别、初判置信度；执行快速否决检查
- **输出**：结构化数据 + 置信度标签 + 企业阶段判断 + 数据缺口清单

### Phase 2：搜索核验（搜索Agent）

主session完成Phase 0和Phase 1后，派Agent子任务执行搜索。以下为搜索agent的完整prompt模板和schema。

**搜索agent prompt模板**（主session填充`{企业名}`、`{企业阶段}`、`{数据缺口}`、`{search_tool}`、`{anysearch_path}`后传入）：

```
你是投资研判搜索专员。请对以下企业执行公开信息搜索核验，只返回结构化摘要，不要返回原始搜索结果全文。

企业名称：{企业名}
企业阶段：{企业阶段}
数据缺口：{数据缺口}

## 搜索工具选择

当前环境检测到的搜索工具：{search_tool}

**如果 search_tool 为 "anysearch"**：
使用以下命令执行搜索：
  python3 {anysearch_path} search "查询词" --max_results 5
对于需要深入抓取的URL，使用：
  python3 {anysearch_path} extract "URL"

**如果 search_tool 为 "platform_builtin"**：
使用当前平台内置的搜索工具（Claude Code 用 WebSearch，Codex CLI 用 web_search，OpenClaw/Hermes 用平台搜索工具）。
无论哪种平台，搜索关键词模板完全相同。

## 搜索维度（按企业阶段选择执行次数）

按以下维度依次搜索（成长期执行全部6次，早期执行4次[搜索1,2,3,5]，传统国企执行5次[搜索1,2,3,4,5]）：

搜索1（工商+股权+融资+资质）："{企业名} 工商信息 股权 融资 专精特新 高新技术"
搜索2（主营业务+行业+案例）："{企业名} 主营业务 行业分析 市场规模 客户 案例"
搜索3（招聘+用工+团队验证）："{企业名} 招聘 拉勾 猎聘 BOSS直聘 员工规模"
      → 紧接着搜："{创始人/CEO姓名} 履历 简历 背景 行业"
搜索4（财务+可比公司）："{企业名} 财务数据 可比公司 PS PE 估值"
搜索5（法律+负面）："{企业名} 诉讼 处罚 被执行人 负面"
搜索6（上市+退出）："{企业名} IPO 上市 退出 并购 收购"

## 搜索3（招聘+用工）重点提示

这是早期企业最重要的搜索维度。招聘平台（拉勾/猎聘/BOSS直聘）企业主页通常包含：
- 员工规模（15-50人 / 50-150人 / 150-500人）
- 融资状态标签（未融资 / 不需要融资 / A轮 / B轮 等）——注意与BP是否矛盾
- 注册资本（注意与工商查询结果是否一致，不一致是重要信号）
- 详细注册地址
- 招聘JD中的业务描述（验证BP中宣称的业务方向）

如果搜索到招聘平台企业主页，必须提取以上所有字段。如果不同平台的注册资本数据不一致，必须全部记录并标注矛盾。

## 搜索结果处理

每次搜索后立即提取关键数据，丢弃无关结果（如同名不同公司）。
搜到聚合页时用extract深入抓取，只提取有用信息。
发现一票否决信号（失信被执行人/重大处罚）时立即中断，返回fast_reject=true。

你的最终输出必须严格按以下JSON schema返回：
```

**搜索agent JSON schema**：

```json
{
  "type": "object",
  "properties": {
    "fast_reject": {"type": "boolean", "description": "是否触发快速否决"},
    "fast_reject_reason": {"type": "string", "description": "快速否决原因"},
    "company_stage": {"type": "string", "description": "企业阶段判断：成熟期/成长期/早期/传统国企"},
    "searches_executed": {"type": "integer", "description": "实际执行搜索次数"},
    "search_tool_used": {"type": "string", "description": "实际使用的搜索工具：anysearch/platform_builtin/none"},
    "dimensions": {
      "type": "object",
      "properties": {
        "business_registration": {
          "type": "object",
          "properties": {
            "founded_date": {"type": "string"},
            "registered_capital": {"type": "string"},
            "registered_capital_sources": {"type": "string", "description": "各来源的注册资本数据，如不一致需列出"},
            "legal_representative": {"type": "string"},
            "address": {"type": "string"},
            "company_type": {"type": "string"},
            "staff_size": {"type": "string"},
            "key_findings": {"type": "string"}
          }
        },
        "industry": {
          "type": "object",
          "properties": {
            "main_business": {"type": "string"},
            "market_size": {"type": "string"},
            "competition": {"type": "string"},
            "key_findings": {"type": "string"}
          }
        },
        "recruitment": {
          "type": "object",
          "properties": {
            "staff_size_from_job_platforms": {"type": "string", "description": "从招聘平台获取的员工规模"},
            "financing_status_tag": {"type": "string", "description": "招聘平台上的融资状态标签"},
            "registered_capital_from_job_platforms": {"type": "string", "description": "招聘平台显示的注册资本"},
            "capital_data_conflict": {"type": "string", "description": "注册资本数据是否存在跨平台矛盾"},
            "job_description_highlights": {"type": "string", "description": "招聘JD中反映的业务方向和客户类型"},
            "founder_background": {"type": "string", "description": "创始人在公开渠道的履历信息"},
            "key_findings": {"type": "string"}
          }
        },
        "finance": {
          "type": "object",
          "properties": {
            "revenue": {"type": "string"},
            "profit": {"type": "string"},
            "comparable_ps": {"type": "string"},
            "key_findings": {"type": "string"}
          }
        },
        "legal": {
          "type": "object",
          "properties": {
            "litigation": {"type": "string"},
            "penalties": {"type": "string"},
            "negative_news": {"type": "string"},
            "key_findings": {"type": "string"}
          }
        },
        "exit": {
          "type": "object",
          "properties": {
            "ipo_progress": {"type": "string"},
            "comparable_deals": {"type": "string"},
            "key_findings": {"type": "string"}
          }
        }
      }
    },
    "verification_notes": {"type": "string", "description": "BP数据与搜索结果的交叉比对发现"},
    "information_gaps": {
      "type": "array",
      "items": {"type": "string"},
      "description": "搜索后仍存在的主要信息缺口"
    }
  },
  "required": ["fast_reject", "company_stage", "searches_executed", "dimensions"]
}
```

**主session收到搜索结果后**：
- 若 `fast_reject=true` → 走快速否决流程，输出短信级结论，终止
- 否则 → 将结构化搜索摘要传入写作Agent

### Phase 3+4：铁律核验+报告撰写（写作Agent）

主session完成Phase 1和Phase 2后，派写作Agent一次性完成铁律核验和报告撰写。

**写作Agent prompt模板**（主session填充变量后传入）：

```
你是投资研判分析师。请完成铁律核验和报告撰写。

企业名称：{企业名}
企业阶段：{企业阶段}

请按顺序：
1. 读取 references/iron-laws.md，逐条核验10条铁律
2. 读取 references/report-template.md，按模板结构撰写报告
3. 读取 references/confidence-standards.md，标注所有数据的置信度

输入数据：
- 企业材料数据：{phase1_data}
- 搜索结果：{search_results}

输出要求：
- 完整Markdown格式研判报告（4000-8000字）
- 结论必须明确：投/不投/有条件推进
- 信息缺失分级表（P0/P1/P2）
- 五情景DPI表（乐观/基准/保守/回购/清算+概率加权）
- 交易条款数字必须有推导链路
- 领导简报短信（四段式，见references/sms-rules.md）
- 如涉及国资出资，需读取 references/compliance-checklist.md 完成合规核检
```

**写作Agent JSON schema**：

```json
{
  "type": "object",
  "properties": {
    "verdict": {"type": "string", "description": "投/不投/有条件推进"},
    "iron_law_checks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "law_number": {"type": "integer"},
          "status": {"type": "string", "description": "通过/触发/待核实"},
          "finding": {"type": "string"}
        }
      }
    },
    "report_markdown": {"type": "string", "description": "完整的Markdown格式研判报告"},
    "sms_text": {"type": "string", "description": "领导简报短信完整文本"},
    "confidence_table_rows": {
      "type": "array",
      "items": {"type": "array", "items": {"type": "string"}},
      "description": "置信度评分卡行数据"
    }
  },
  "required": ["verdict", "iron_law_checks", "report_markdown", "sms_text"]
}
```

**主session收到写作结果后**：
- 保存Markdown到 `{deliverables_dir}/[企业名]初步研判.md`
- 将report_markdown、sms_text、confidence_table_rows传入输出Agent

### Phase 5-7：输出管道（输出Agent）

主session保存Markdown后，派输出Agent子任务执行质量门禁+短信+docx生成。

**输出Agent prompt模板**（主session填充变量后传入）：

```
你是投资研判输出专员。请读取已完成的研判报告Markdown文件，依次完成以下三步：

1. 质量门禁：运行 python3 {skill_dir}/scripts/quality_gate.py {markdown_path}
   - 若门禁失败，列出失败项并尝试修复Markdown文件，然后重新运行（最多重试2次）
   - 若2次重试仍失败，返回质量门禁失败信息

2. 生成JSON数据：将报告内容转换为docx_generator.py所需的JSON格式。
   关键规则：
   - JSON中所有字符串值必须使用英文双引号，中文引号""必须替换为转义形式或直接使用英文引号
   - sms_appendix.text中必须包含完整的四段式短信文本
   - confidence_table.rows中每行4个元素：[数据点, 来源, 置信度, 需核实]
   保存JSON到 {deliverables_dir}/{company_name}_data.json

3. 生成docx：运行
   python3 {skill_dir}/scripts/docx_generator.py \
     --company "{company_name}" \
     --date "{date}" \
     --data {deliverables_dir}/{company_name}_data.json \
     --output {deliverables_dir}/{company_name}初步研判（{date_short}）.docx

4. 提取短信：从报告附件章节中提取领导简报短信文本

你的最终输出必须严格按以下JSON schema返回：
```

**输出Agent JSON schema**：

```json
{
  "type": "object",
  "properties": {
    "quality_gate_passed": {"type": "boolean"},
    "quality_gate_failures": {"type": "array", "items": {"type": "string"}},
    "docx_path": {"type": "string", "description": "生成的docx文件绝对路径"},
    "sms_text": {"type": "string", "description": "完整的领导简报短信文本"},
    "json_path": {"type": "string", "description": "生成的JSON数据文件路径"},
    "errors": {"type": "array", "items": {"type": "string"}, "description": "遇到的错误"}
  },
  "required": ["quality_gate_passed", "docx_path", "sms_text"]
}
```

**主session收到输出结果后**：
- 若门禁失败 → 修补Markdown，重新派输出agent
- 若docx生成失败 → 检查JSON格式，修复后重新派输出agent
- 成功 → 进入Phase 8交付

### Phase 8：交付（主session）

1. 发送docx文件给用户（告知文件路径）
2. 直接展示短信文本和核心结论速览
3. 输出物清单：
   - `.docx` 公文格式报告（含短信附件）
   - 短信文本（直接展示）
   - `.md` Markdown源文件（备查）
4. 命名规则：`[企业名称]初步研判（YY.M.D）.docx`

### 错误处理

- **搜索agent返回空结果**（早期企业常遇）：主session基于企业材料分析，报告标注"公开信息不足"
- **搜索agent超时/失败**：主session回退到自行搜索模式
- **输出agent JSON生成失败**：主session自行生成JSON并手动运行docx脚本
- **质量门禁2次重试仍失败**：输出agent返回失败项，主session决定是否补充或标注后强行交付

## 输出要求

1. **格式**：中文段落式叙述，二级标题带判断（例："估值显著高于可比公司，对赌设计可对冲风险"）
2. **字数**：4000-8000字，信息量决定篇幅
3. **结论**：绝对明确，投/不投/有条件推进
4. **数据标注**：关键数据必须标注来源和置信度；普通背景事实可集中说明来源
5. **文件输出**：使用 `scripts/docx_generator.py` 生成规范格式docx
6. **命名规则**：`[企业名称]初步研判（YY.M.D）.docx`
7. **信息缺失**：必须包含P0/P1/P2分级表，无缺失也注明"无"
8. **退出分析**：必须有五情景DPI表（乐观/基准/保守/回购/清算+概率加权）
9. **交易条款**：数字必须有推导链路
10. **国资合规**：结论写成段落，不写检查清单

## 跨平台兼容说明

本技能支持以下AI Agent平台：

| 平台 | 搜索工具 | 脚本执行 | Agent调度 |
|------|---------|---------|----------|
| **Claude Code** | anysearch CLI / WebSearch | python3 直接调用 | Agent 工具派子Agent |
| **Codex CLI** | anysearch CLI / 内置 web_search | python3 直接调用 | 内置 Agent 工具 |
| **OpenClaw** | anysearch CLI / MCP 搜索工具 | python3 直接调用 | 按 OpenClaw Agent 规范 |
| **Hermes** | anysearch CLI / 平台搜索工具 | python3 直接调用 | 按 Hermes Agent 规范 |

所有平台的搜索关键词模板、JSON schema、参考文件、Python脚本完全一致。唯一差异是搜索工具的调用方式，由 Phase 0 的检测逻辑自动适配。

## 参考文件索引

按需读取，不在SKILL.md中展开：

| 文件 | 用途 | 读取时机 |
|------|------|---------|
| `references/iron-laws.md` | 10条铁律+快速否决流程 | 写作Agent核验时 |
| `references/material-identification.md` | 文件类型识别矩阵 | Phase 1材料识别 |
| `references/data-sources.md` | 搜索维度、关键词、优先级详情 | Phase 2搜索前 |
| `references/report-template.md` | 报告结构大纲+写作红线 | 写作Agent撰写时 |
| `references/confidence-standards.md` | 四级置信度+交叉验证+时效衰减 | 写作Agent标注时 |
| `references/sms-rules.md` | 领导简报短信四段式规则 | 写作Agent生成短信时 |
| `references/compliance-checklist.md` | 国资合规六大检查项 | 涉及国资出资时 |
| `scripts/quality_gate.py` | 质量门禁检查脚本 | 输出Agent调用 |
| `scripts/docx_generator.py` | 公文docx生成脚本 | 输出Agent调用 |
| `config.yaml` | 配置项 | 执行开始时 |
