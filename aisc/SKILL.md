---
name: aisc
description: Build a quality-gated AI learning card from an article, transcript, recording transcript, web page, social post, report, interview, pasted text, local file, or Feishu/Lark document, then optionally save it to a Feishu/Lark knowledge base and update the index. Use when the user says "aisc", "aisc一下", "用AISC处理", "用aisc学习", "learn and save to Feishu", "沉淀到飞书", "学一下存到飞书", or asks to digest knowledge content into a reusable card with source tracking, quality judgment, and upload-ready Markdown.
---

# AISC

AISC turns raw knowledge content into a trustworthy, reusable learning card. It favors evidence, source traceability, quality gating, and practical reuse over automatic over-processing.

## Core Contract

When this skill is used:

1. Get the source content from pasted text, local files, Feishu/Lark docs, public web pages, or user-provided metadata.
2. Identify the source type and normalize noisy text without changing meaning.
3. Apply a quality gate before deciding whether to create a light note, a full learning card, or decline automatic persistence.
4. Generate an AISC card in Markdown with source information, summary, keywords, core views, knowledge points, direct quotes, reuse value, and an entry recommendation.
5. Add the learning-extension section only when the material has enough density to support it.
6. Save to Feishu/Lark and update the index only when the user requested persistence and the quality gate allows it.
7. Return concise links or a concise result summary.

## Cross-Agent Compatibility

Design every response so Codex, Claude, OpenClaw, Hermes, or another capable agent can follow it:

- Use plain Markdown and explicit steps.
- Avoid Codex-only directives in generated cards.
- Treat tools as replaceable capabilities: content acquisition, analysis, validation, and persistence.
- If a named tool is unavailable, use the nearest equivalent and state the fallback.
- If Feishu/Lark authentication, permissions, or CLI tools are unavailable, still produce the card and provide the exact missing step.
- Never hide irreversible remote writes. If the quality gate returns "不建议入库", do not upload unless the user explicitly overrides.

## Reference Files

Load these files only when needed:

- `references/quality-gate.md`: Always read before judging card depth or upload eligibility.
- `references/source-type-rules.md`: Read when the input is a transcript, recording transcript, report, social post, interview, or otherwise source-specific.
- `references/card-template.md`: Read before generating the final card.
- `references/feishu-workflow.md`: Read only when saving to Feishu/Lark or updating the index.
- `references/example-output.md`: Read only when you need a compact example of the expected result.

## Default Workflow

### 1. Acquire Content

Prefer the most direct reliable source:

- Pasted text: use directly.
- Local file: read the file.
- Feishu/Lark URL: use available Feishu/Lark document or wiki tools.
- Public URL: fetch the article text with available browser, HTTP, or extraction tools.
- Inaccessible URL: ask the user to paste the content or provide an accessible source.

Record missing metadata as `未提供`; do not infer author, publication time, or source from weak clues.

### 2. Normalize and Classify

Identify one source type:

`逐字稿 / 录音稿 / 网页文章 / 社媒帖子 / 报告资料 / 访谈对话 / 飞书文档 / 本地文件 / 其他`

Then classify one content type:

`教程方法论 / 行业观察 / 个人经验 / 案例拆解 / 观点输出 / 知识科普 / 资料整理 / 情绪表达`

For noisy transcripts, remove filler, repeated phrases, obvious transcription artifacts, and broken sentence fragments only when the original meaning remains intact.

### 3. Apply the Quality Gate

Read `references/quality-gate.md` and decide:

- `长期参考`: generate a full card and allow persistence.
- `可二创`: generate a full card and allow persistence.
- `仅存档`: generate a light card; persistence is allowed only when the user asked to save.
- `不建议入库`: generate a brief reason and do not upload unless the user explicitly asks to keep it anyway.

### 4. Generate the Card

Read `references/card-template.md` and fill the template. Requirements:

- The summary must be exactly 3 sentences.
- Keywords must be 5-8 specific, searchable terms.
- Core views must be no more than 3 and grounded in the source.
- Direct quotes must be exact excerpts from the source; write `无` when none qualify.
- Learning-extension fields must not invent methods, data, results, or examples absent from the source.

### 5. Validate

Before finalizing, run the mental checklist in `references/quality-gate.md`.

When a local Markdown card exists, run:

```bash
python scripts/validate-card.py path/to/card.md
```

Fix validation failures before upload or final delivery.

### 6. Persist to Feishu/Lark

Only read `references/feishu-workflow.md` when persistence is requested.

Default knowledge base name:

`学习卡片沉淀库`

Default index title:

`学习卡片沉淀库索引`

Index row format:

```markdown
| 日期 | 标题 | 来源类型 | 内容分类 | 入库建议 | 核心一句话 | 链接 |
```

If upload succeeds but index update fails, return the card link and the exact row the user can add manually.

## Output Policy

For normal use, return only the final card or the Feishu/Lark links. Do not include hidden self-check notes.

When something fails, return:

- What succeeded.
- What failed.
- Why it failed.
- The next concrete action.

Keep the tone concise and useful.
