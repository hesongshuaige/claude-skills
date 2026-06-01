---
name: xx
description: Use when the user wants to mine GitHub, official docs, high-rated repositories, best-practice projects, workflow examples, automation patterns, or ecosystem resources for a changeable topic such as Claude Code, Codex, MCP, Cursor, LangGraph, AI automation, or another technical/business domain, then synthesize non-translated Chinese learning content, create or update a Feishu knowledge base, add source tracking, training plans, templates, checklists, and long-term update guidance.
---

# XX

## Purpose

Turn a user-supplied topic into a sourced Chinese learning system in Feishu/Lark. The topic is variable; the workflow is stable.

Use this skill to research, rank, synthesize, publish, and maintain knowledge bases. Do not simply translate READMEs. Extract methods, tradeoffs, patterns, risks, examples, training tasks, and landing plans.

## Required Inputs

Resolve these from the user request or ask briefly when missing:

- `topic`: the subject to mine, such as Claude Code, Codex, MCP, Cursor, or AI automation.
- `target`: create a new Feishu knowledge base or update an existing one.
- `depth`: quick, standard, deep, or training-system. Default to `standard`.
- `audience`: personal learning, engineering team, operations, research, content, or general. Default to personal learning.
- `angle`: learning path, automation, engineering rollout, business use, or broad survey. Default to broad survey.

## Workflow

1. **Scope the topic**
   - Define what is in scope and out of scope.
   - Pick the closest topic profile from `references/topic-profiles.md`.
   - If no profile fits, use the generic profile and note assumptions.

2. **Research with evidence**
   - Prefer official docs and primary GitHub repositories for facts.
   - Search GitHub for high-rated repositories, awesome lists, best practices, workflow kits, examples, CI/action integrations, skills, subagents, plugins, and automation projects.
   - Use the scoring model in `references/ranking-rubric.md`.
   - Record an evidence ledger using `references/evidence-ledger.md`.

3. **Synthesize**
   - Separate sourced facts, community practice, inference, and recommendation.
   - Identify consensus patterns across sources.
   - Identify gaps versus any existing knowledge base.
   - Use `references/synthesis-rubric.md` to avoid translation-only output.

4. **Design the knowledge base**
   - Use `references/lark-kb-structure.md`.
   - Choose create vs update:
     - Create when the topic is new or the user asks for a new knowledge base.
     - Update when the user provides an existing Feishu/Lark URL/token or says to append/upgrade.
   - For updates, preserve existing pages and add new pages or overwrite only targeted pages.

5. **Publish to Feishu/Lark**
   - Use the relevant Lark skills and `lark-cli` workflows.
   - Prefer user identity for personal/team knowledge spaces.
   - Treat external writes as scoped to the user's explicit request.
   - After publishing, verify page count, index content, and important page fetches.

6. **Quality gate**
   - Run the checklist in `references/quality-checklist.md`.
   - Report sources, created/updated pages, known limits, and suggested next mining direction.

## Output Expectations

For each topic, produce practical Chinese content with:

- Learning path.
- High-value source map.
- Core concepts.
- Expert workflows.
- Tool/ecosystem map.
- Case studies.
- Anti-patterns.
- Templates/checklists.
- Training plan.
- Landing recommendations.
- Source and update log.

## Incremental Update Rules

When updating an existing knowledge base:

- Read or list existing pages first.
- Identify what is missing, stale, or duplicated.
- Prefer adding delta pages over rewriting the whole knowledge base.
- Update the index and source page.
- Add a "what changed" section when the update is substantial.

## Resources

- `references/ranking-rubric.md`: source scoring and exclusion rules.
- `references/evidence-ledger.md`: evidence ledger format.
- `references/synthesis-rubric.md`: synthesis and anti-translation rules.
- `references/lark-kb-structure.md`: Feishu knowledge-base layouts.
- `references/topic-profiles.md`: topic-specific mining profiles.
- `references/quality-checklist.md`: final acceptance checklist.
