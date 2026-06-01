# ZSK Routing Rules

Use these rules to decide where new material goes and what context to retrieve.

## Default Decision

Do **not** create a new knowledge space by default. Most material should become a page/node in either:

- `规章制度`
- `初研报告`

Create a new knowledge space only when the material has a long-term independent domain, distinct permissions, and recurring volume that would clutter existing spaces.

## Material Classification

| Material type | Destination | Action |
|---|---|---|
| Regulations, official policies, approval rules, investment-management rules | `规章制度` | Create under the appropriate top-level category; add or update summary/quick lookup if high-value |
| Company identity, governance, shareholder, org, standard company language | `初研报告` -> `06_公司画像与基础事实` | Update the page; do not scatter facts into reports |
| Sector focus, investment stage, investment preference | `初研报告` -> `07_投资偏好与赛道口径` | Update canonical page; other pages should reference it |
| Project BP, company intro, project materials | `初研报告` | Create/update a project file from `02_项目档案模板` |
| Meeting transcript or notes | `初研报告` | Create a meeting note from `03_会议纪要模板`; link to project file if known |
| Initial research report draft | `初研报告` | If historical/reference, place under `04_初研报告参考样稿`; if active project, store with the project |
| Request to write/upgrade a report | `初研报告` | Read templates, writing standard, investment preference, company profile, relevant samples |
| Industry/policy research for a project | `初研报告` unless it is a formal policy/regulation | Attach to project file or create a project research page |
| Unknown/mixed material | No immediate write | Propose classification and destination first |

## Create vs Update

Create a new page when:

- the material is about a new project/company;
- it is a standalone meeting with separate decisions/actions;
- it is a new historical sample report;
- it starts a new durable reference domain.

Update an existing page when:

- it changes company facts or standard language;
- it clarifies investment preference, stage, or sector focus;
- it supplements an existing project;
- it corrects a previous page's canonical wording.

## New Knowledge Space Criteria

Only recommend a new knowledge space when at least two are true:

- The domain will have many pages over time.
- Permissions should differ from `规章制度` or `初研报告`.
- The material is not mainly regulation, project work, reports, meeting notes, or company profile.
- The domain has its own stable workflows, templates, and retrieval rules.

Examples that might justify a new space later:

- full fund operations / LP reporting;
- post-investment portfolio management;
- external publication/content operations;
- confidential personnel/HR material with separate permission needs.

## Retrieval Playbooks

### Classify/upload a new project material

Read:

1. `07_投资偏好与赛道口径`
2. `02_项目档案模板`
3. existing root/child nodes to avoid duplicates

Then decide create/update. Capture at least:

- project/company name
- sector
- stage
- source/date
- active owner if provided
- whether it needs an initial research report

### Write an initial research report

Read:

1. `07_投资偏好与赛道口径`
2. `06_公司画像与基础事实`
3. `01_初研报告模板`
4. `05_初研报告写作规范与样稿提炼`
5. relevant sample reports under `04_初研报告参考样稿`
6. `规章制度` if approvals/compliance/investment authority arise

Report must include:

- one-page conclusion
- company basics
- financing and landing plan
- industry/competition
- company competitiveness
- financial/valuation view
- Wuhou/Zhuge fit
- compliance/approval concerns
- risks
- next diligence questions
- work recommendation

### Upgrade an existing initial research report

Read:

1. original report
2. `05_初研报告写作规范与样稿提炼`
3. `07_投资偏好与赛道口径`
4. similar sample reports

Improve structure, evidence, stage/sector judgment, risk list, valuation logic, and next-action clarity.

### Create meeting notes

Read:

1. `03_会议纪要模板`
2. related project file/report if known
3. `07_投资偏好与赛道口径` if investment judgment appears

Output decisions, facts, pending questions, risks, owners, deadlines, and follow-up materials.

## Wording Guardrails

- Say "actual focus sectors" for 生物医药、电子信息、微波射频、文创音乐.
- Say "upper-level district/government phrasing" for 八大专业赛道.
- Say "investment covers mature, mid-stage, growth-stage, and some early-stage projects."
- Say "early-stage projects are currently relatively less common; treat as opportunity-driven attention."
- Do not imply Zhuge Capital only invests early-stage projects.
- Do not reject a mature project merely because it is not early.
- Do not accept an early project merely because it is "hard tech"; verify technology, team, engineering path, customers, and financing path.

## Response Pattern For Routing

When classifying a user-provided material, answer with:

```text
分类：...
建议位置：...
动作：新建 / 更新 / 先不写入
理由：...
需要补充：...
```

Keep it short unless the user asks for a detailed plan.
