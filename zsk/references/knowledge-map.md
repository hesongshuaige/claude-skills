# ZSK Knowledge Map

This file stores the canonical Feishu Wiki map for Zhuge Capital knowledge operations.

## Identity

- Use Lark user identity: `--as user`.
- Prefer read-only inspection before writes.
- For Feishu docs/wiki operations, follow the local Lark skills:
  - `lark-shared`
  - `lark-wiki`
  - `lark-doc`
  - `lark-drive`

## Knowledge Spaces

### 规章制度

- Purpose: authoritative regulations, policies, approval rules, investment-management basis, major-matter rules.
- `space_id`: `7630116517199219901`
- Current top-level structure:
  - `00_索引与速查`
  - `01_区级制度`
  - `02_公司级制度`

Known useful pages/files:

- `规章制度总览.md`: overview and AI usage guide.
- `审批权限速查表.md`: quick approval level lookup.
- `诸葛资本公司三定方案.md`: source for company identity, registered capital, governance, organization, development goals.
- `诸葛资本投资管理制度（试行）.md`: source for investment process and governance.

Use this space when the task involves:

- approval authority
- investment amount thresholds
- fund-investment limits
- major matters
- compliance basis
- company governance source documents
- policy or regulatory references

### 初研报告

- Purpose: Agent work entry, initial research report templates, project files, meeting notes, sample reports, company profile, investment preference.
- `space_id`: `7641599504172453073`

Top-level nodes:

| Title | Wiki node token | Doc token | Purpose |
|---|---|---|---|
| `00_AI工作入口与总索引` | `K1EgwUcfZiUNuRkBSKJc4AREnud` | `XDIAdYVU9ob1LKxP9zGc8EUIn1d` | Agent entry and retrieval guide |
| `01_初研报告模板` | `QiHJwR6Ioivas4klp0yc4YXKnRh` | `DmzNdSPHmoC3TexWA0gcfIpMnke` | Standard initial research report template |
| `02_项目档案模板` | `MAwwwE4SxiA37BkAEvKcYxo2nOb` | `Tr2Ydmak0o0mMCxdWQKcAoLbnSb` | Project file template |
| `03_会议纪要模板` | `UDf4wuUrmiDxRSkcXbhcUomfnrb` | `S3fUdYkVooEkkwxsuERcRF2UnSd` | Meeting note template |
| `04_初研报告参考样稿` | `ZW3pww530iZpqSkIESXcqZUenoe` | `LnntddcrfoldKTxauaMcDxVhnwf` | Historical sample reports for style/structure reference |
| `05_初研报告写作规范与样稿提炼` | `P1COwqzmOiRefIkLCaKcBajfnGd` | `ZKLpdqEVAomjIzxlci9cwmtVnyg` | Report-quality standard extracted from sample reports |
| `06_公司画像与基础事实` | `XuOTwW8MQi6FookYM4YclaWFnpe` | `EPRRdIrh6o2xDBxDm3NcWZgQnoU` | Company profile and stable facts |
| `07_投资偏好与赛道口径` | `WcAKwyqWUiAQ8kkDf5ncON4Pnjd` | `H3COds91Eo82nExG4NScA48Vnmg` | Canonical sector, stage, and investment preference page |

## Canonical Investment Preference

Use `07_投资偏好与赛道口径` as the final authority.

Current consolidated understanding:

- Actual focus sectors:
  - 生物医药
  - 电子信息
  - 微波射频
  - 文创音乐
- "八大专业赛道" is an upper-level district/government phrasing, not the exact day-to-day project filter.
- Investment covers mature, mid-stage, growth-stage, and some early-stage projects.
- Mature, mid-stage, and growth-stage projects are important investment targets.
- Early-stage projects are currently invested in relatively less often and should be treated as opportunity-driven attention, not the main current focus.
- "投早、投小、投硬科技" is a policy orientation and screening lens, not a reason to exclude mature-stage projects.

## Sample Reports Under `04_初研报告参考样稿`

The sample reports are reference examples, not archival clutter. Use them to learn dimensions, skepticism, evidence standards, and wording.

Known sample themes:

- Robot / embodied intelligence: 七腾机器人, 鹿明机器人
- Satellite / commercial aerospace: 魔方卫星
- Industrial sensor: 深浦电气
- Ultrafast laser / advanced manufacturing: 华创鸿度
- Rail vibration/noise reduction: 卓控环保
- Smart cockpit / automotive electronics: 四维智联
- High-purity metal / materials: 虹华科技

Do not create a separate sample-report index unless the user asks; the user explicitly rejected that optimization.

## Useful Lark CLI Patterns

List root nodes:

```bash
lark-cli wiki +node-list --as user --space-id <SPACE_ID> --page-all
```

List child nodes:

```bash
lark-cli wiki +node-list --as user --space-id <SPACE_ID> --parent-node-token <NODE_TOKEN> --page-all
```

Fetch doc content:

```bash
lark-cli docs +fetch --api-version v2 --as user --doc <DOC_TOKEN>
```

Create a Wiki node:

```bash
lark-cli wiki +node-create --as user --space-id <SPACE_ID> --title "<TITLE>"
```

Update a doc:

```bash
lark-cli docs +update --api-version v2 --as user --doc <DOC_TOKEN> --command append --doc-format xml --content '<p>...</p>'
```
