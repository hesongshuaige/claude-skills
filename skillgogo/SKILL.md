---
name: skillgogo
description: Use when a user needs skill work such as creating a new Agent Skill, improving an existing SKILL.md, or governing a reusable agent workflow.
---

# SkillGoGo

## Overview

SkillGoGo is a thin orchestration skill for skill work. It does not replace
Superpowers, SkillGo, writing-skills, review-skill, or domain skills. It routes
them in the right order, keeps scope tight, and forces verification and
iteration.

Core principle: **Superpowers provides skill-use discipline; SkillGo provides
skill-engineering process; SkillGoGo coordinates both without duplicating them.**

SkillGoGo uses the six-layer workflow frame only where it adds value:
Context, Source, Prompt/Procedure, Harness, Verification, and Iteration. Use
the full frame for complex, repeated, collaborative, quality-sensitive, or
risk-sensitive skill work. Use a reduced frame for small edits.

## When to Use

Use this when the user asks to:

- create, write, fork, merge, split, or package a skill
- audit, review, improve, optimize, validate, or publish a `SKILL.md`
- compare skill quality, decide whether a skill is worth creating, or design a
  reusable skill workflow
- run `skill-validator`, `skillgrade`, pressure scenarios, or skill governance
- "use Superpowers and SkillGo together" or asks which process should govern
  skill work

## When NOT to Use

- The user wants ordinary coding, writing, research, or product work with no
  reusable skill artifact.
- A domain skill directly handles the task and no skill creation/review is
  involved. Use that domain skill instead.
- The request is a one-off project rule that belongs in `AGENTS.md`, not a
  reusable skill.
- The request is a tiny low-risk edit where `writing-skills` plus a quick
  validation check is sufficient.

## Operating Sequence

### 0. Activate The Right Skills

Before acting, identify explicit and implied skills. Load only the relevant
ones:

For installation, dependency checks, and safe download locations, read
`references/dependency-manifest.md` before telling another agent what to
install.

| Situation | Required skill path |
|-----------|---------------------|
| User names Superpowers or any skill may apply | `using-superpowers` first |
| New skill, fork, merge, or "does this skill exist?" | `skill-scout` |
| Skill audit, improvement, packaging, governance | `skillgo` |
| Editing or authoring `SKILL.md` | `writing-skills` |
| Formal structure/content review | `review-skill` or `skill-validator` |
| Behavioral evaluation | `skillgrade` or lightweight pressure scenarios |
| Domain-specific workflow | Load the relevant domain skill too |

Do not paste or merge these skill bodies into the target skill. Use them as
process inputs.

### 1. Intake

Capture the minimum facts needed:

- target skill name and path, or proposed new name
- task type: create / merge / audit / optimize / validate / publish
- intended users and platforms: Codex, Claude, Lark/Feishu, team library, local
- expected output shape and unacceptable failure modes
- external action boundaries: publish, upload, push, paid tools, credentials
- whether the work needs the full six-layer frame or a reduced path

Ask at most three short questions only when missing information blocks progress.
Otherwise proceed with stated assumptions.

### 2. Choose The Workflow Depth

Use the smallest workflow that can still be checked.

| Situation | Use |
|-----------|-----|
| Typo, phrasing, frontmatter, one small rule | Reduced path: Context + Change + Verification |
| Existing skill optimization or audit | Standard path: Context + Source + Procedure + Harness + Verification |
| New team skill, governance, publishing, high-risk domain, repeated SOP | Full six-layer path including Iteration |
| Human/team operating process rather than AI skill | Management frame: owner, collaborators, source, deliverable, deadline, acceptance, escalation |

When the full frame applies, read `references/six-layer-skill-frame.md`.

### 3. Decide The Shape

Choose the smallest structure that solves the problem:

| Need | Preferred shape |
|------|-----------------|
| Combine multiple processes | Thin orchestration skill |
| Deep domain knowledge | Domain skill plus references |
| Long checklists, templates, rubrics | `references/` files |
| Deterministic checks | Script or validator, not prose |
| One-off project convention | `AGENTS.md`, not a skill |
| Two skills with same trigger | Merge or deprecate one |
| One skill with unrelated workflows | Split it |

Default to orchestration over copy-paste merging.

### 4. Build Or Improve The Skill

Apply the selected workflow depth:

1. **Context**: define trigger, non-use cases, users, platform, authority,
   permissions, and compliance boundaries.
2. **Source**: identify source material, trusted references, data cutoff,
   conflict resolution rules, and which content is only background.
3. **Prompt/Procedure**: turn intent into ordered instructions, expected
   output, required files, and tool use.
4. **Harness**: add process guardrails: required checks, forbidden behavior,
   style/format standards, examples, scripts, or rubrics.
5. **Verification**: define how the result is accepted after completion:
   validator, manual rubric, pressure scenarios, factual checks, review owner,
   and publish checks.
6. **Iteration**: record what should be updated after feedback, failures,
   model/tool changes, or repeated use.

Keep AI-facing instructions focused on role, allowed materials, output shape,
forbidden behavior, self-checks, and how to handle missing information. For
human/team workflows, add owner, collaborators, deadline, acceptance criteria,
and escalation path.

### 5. Pressure Scenarios

Before finalizing, define at least two pressure scenarios:

1. **Normal path**: a complete, well-scoped request the skill should handle.
2. **Ambiguous path**: unclear target, missing path, or broad "make it better".
3. **Boundary path**: request to publish, upload, modify credentials, or use
   paid/external systems.
4. **Failure path**: the agent would likely skip validation, skip references,
   over-optimize, or overwrite user changes.

For lightweight work, evaluate manually. For higher-risk team skills, create
formal `skillgrade` evals.

### 6. Edit Rules

When editing skill files:

- Preserve user intent and existing working behavior.
- Prefer small, high-leverage changes over broad rewrites.
- Keep frontmatter descriptions trigger-only; do not summarize workflow there.
- Keep `SKILL.md` focused. Move heavy examples, rubrics, schemas, and templates
  into `references/`.
- Add `agents/openai.yaml` only when the environment uses that metadata.
- Never remove unrelated user changes to make diffs cleaner.
- Keep Harness and Verification separate: guardrails guide the work while
  acceptance checks judge the completed result.

### 7. Validation

Run validation after edits:

```bash
skill-validator check <skill-dir>
```

Interpret results:

| Result | Action |
|--------|--------|
| Errors | Fix before calling the skill ready |
| Warnings that affect use | Fix or document the residual risk |
| Environment-specific warnings | Preserve required local metadata and explain |
| Pass | Continue to pressure scenario review |

If `skill-validator` is unavailable, install it when the user asks or document
that automated validation was skipped.

### 8. Completion Report

End with:

- what changed and why
- files touched
- validator result
- pressure scenario result
- residual warnings or risks
- iteration notes: whether rules, references, tests, or governance should be
  updated later
- whether further optimization is actually worth doing

Do not claim the skill is ready if validation or pressure scenarios found
blocking issues.

## Output Template

```markdown
Verdict: Pass / Pass with warnings / Blocked

Changed:
- ...

Validation:
- skill-validator: ...
- pressure scenarios: ...

Residual risk:
- ...

Recommendation:
- Use as-is / minor follow-up / significant rework
```

## Common Mistakes

| Mistake | Correct approach |
|---------|------------------|
| Copying Superpowers and SkillGo into one large file | Build a thin orchestration skill |
| Optimizing because a checklist exists | Only change issues that affect behavior, reliability, or maintainability |
| Applying the full six-layer frame to tiny edits | Use the reduced path and still verify |
| Writing only prompts with no Context or Source | Define trigger boundaries and trusted inputs first |
| Mixing Harness and Verification | Keep process guardrails separate from final acceptance checks |
| Treating human delegation like AI prompting | Add owner, deadline, collaborators, acceptance, and escalation |
| Treating validator warnings as all equal | Distinguish real quality issues from environment metadata warnings |
| Skipping pressure scenarios | Always test at least normal and boundary paths |
| Making description a workflow summary | Keep description as trigger conditions only |
| Skipping Iteration for repeated work | Record what should become a template, reference, eval, or governance rule |
