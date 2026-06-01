---
name: zsk
description: "Use when a user asks an AI agent to use, update, classify, upload, organize, or retrieve from the Zhuge Capital / 诸葛资本 Feishu knowledge base; write or upgrade initial research reports; create project files or meeting notes; decide where new company/project/regulation materials should live; or avoid re-explaining the knowledge-base structure to multiple agents."
---

# ZSK

## Purpose

Use this skill as the operating protocol for the Zhuge Capital Feishu knowledge base. It tells an agent what to read, where to place new material, when to create pages or spaces, and which canonical pages govern investment-stage and sector judgments.

Before using Feishu, also follow the relevant Lark skills (`lark-shared`, `lark-wiki`, `lark-doc`, and `lark-drive` as needed). Prefer `--as user` for user-owned Wiki resources.

## Core Rule

Do not make the user re-explain the knowledge base. Start by classifying the request:

1. **Retrieve/use knowledge**: read the relevant canonical pages before producing output.
2. **Classify/upload material**: decide the destination, then create or update the correct Wiki page/node.
3. **Create an output**: retrieve templates, sample reports, company facts, investment preferences, and regulations as needed.
4. **Unclear material**: propose the destination and rationale before writing.

## Must-Read References

- For space/page IDs, canonical pages, and retrieval order: read `references/knowledge-map.md`.
- For upload routing, create-vs-update rules, and examples: read `references/routing-rules.md`.

## Canonical Pages

When pages conflict, use this priority:

1. `07_投资偏好与赛道口径` for sectors, investment stage, and "投早、投小、投硬科技".
2. `06_公司画像与基础事实` for company identity, positioning, shareholders, governance, and standard company language.
3. `05_初研报告写作规范与样稿提炼` for report-quality standards.
4. `01_初研报告模板`, `02_项目档案模板`, `03_会议纪要模板` for output structure.
5. `规章制度` knowledge space for approvals, compliance, regulations, and institutional basis.

## Safety and Write Boundaries

- Treat Feishu writes as external actions. If the user clearly asks to create/update/move content, proceed. If intent is ambiguous, draft or ask.
- Do not delete, overwrite, or move important pages unless explicitly requested.
- Do not create a new knowledge space by default. Prefer a page/node in an existing space unless the rules in `routing-rules.md` justify a new space.
- For high-risk Lark CLI confirmation prompts, follow `lark-shared`; never auto-add `--yes`.
- Do not hardcode or display secrets.

## Task Playbooks

### Write an initial research report

Read in order:

1. `07_投资偏好与赛道口径`
2. `06_公司画像与基础事实`
3. `01_初研报告模板`
4. `05_初研报告写作规范与样稿提炼`
5. relevant sample reports under `04_初研报告参考样稿`
6. relevant regulations if approval, fund investment, or major-matter issues appear

Then produce the report or create it in Feishu as requested.

### Classify uploaded material

Use `routing-rules.md`. Return:

- material type
- destination space/page/node
- create vs update decision
- whether a new knowledge space is justified
- any missing metadata to ask for

### Use regulations

For approvals, investment authority, fund limits, major matters, or compliance basis, read the `规章制度` space. Prefer its overview and quick tables first, then source regulations.

## Output Expectations

Be practical and explicit. Explain routing decisions in one or two sentences. For research outputs, separate facts, judgments, risks, and next actions. For uncertain content, avoid irreversible writes and provide a proposed placement.
