# Example Conversions

Use these examples as models when converting raw material into an agent skill.
They are intentionally compact. Real skills should keep only always-needed
instructions in `SKILL.md` and move long details into `references/`.

## Example 1: Repeated Prompt To AI Skill

Raw request:

```text
Whenever I ask for a policy brief, collect the official policy source, summarize
the key changes, identify affected stakeholders, and include risks. Do not rely
on random web summaries.
```

Six-layer interpretation:

| Layer | Decision |
|-------|----------|
| Context | Use for recurring policy brief requests; not for casual news summaries |
| Source | Official policy text wins; agency notices and approved internal notes can support; web summaries are background only |
| Prompt/Procedure | Find source, extract changes, map stakeholders, note risks, produce brief |
| Harness | No unsupported claims; cite source authority; flag missing official text |
| Verification | Check each claim against source; run normal and source-conflict scenarios |
| Iteration | Add new source types and failure cases after each review cycle |

Possible `SKILL.md` shape:

```markdown
---
name: policy-briefing
description: Use when creating a policy brief from official policy material or approved internal source notes.
---

# Policy Briefing

## When To Use

Use for recurring policy brief requests that require source-backed analysis.
Do not use for casual news summaries or unsupported commentary.

## Procedure

1. Identify the official source and any approved internal material.
2. Extract the policy change, effective date, affected stakeholders, and risks.
3. Produce a concise brief with source-backed claims only.
4. Flag missing or conflicting source material instead of guessing.

## Verification

- Confirm each key claim is backed by the official source or approved material.
- Identify unresolved source conflicts.
- Record any assumptions or missing documents.
```

## Example 2: Human SOP To Agent Skill

Raw SOP:

```text
For weekly project tracking, the operations owner collects updates from each
department by Thursday noon, prepares a status table, highlights blocked items,
and escalates missing inputs by 16:00.
```

Six-layer interpretation:

| Layer | Decision |
|-------|----------|
| Context | Recurring weekly project tracking; audience is operations and leadership |
| Source | Department updates, project tracker, meeting notes; owner resolves conflicts |
| Prompt/Procedure | Collect, normalize, summarize, flag blockers, prepare table |
| Harness | Preserve owner/deadline/escalation fields; do not invent missing updates |
| Verification | Check every row has source, owner, status, blocker, next action |
| Iteration | Update template when repeated blockers or missing fields appear |

Important conversion rule:

Do not turn the human workflow into a pure prompt. Preserve management fields:
owner, collaborators, deadline, acceptance criteria, and escalation path.

Possible `SKILL.md` shape:

```markdown
---
name: project-tracking-summary
description: Use when preparing a recurring project tracking summary from department updates and project tracker material.
---

# Project Tracking Summary

## When To Use

Use for recurring project status consolidation. Do not use when the user only
needs a one-off sentence edit or when no source updates are available.

## Procedure

1. Identify the reporting period, owner, source tracker, and required departments.
2. Normalize updates into one table with project, owner, status, blocker, next action, and source.
3. Flag missing updates instead of inventing them.
4. Separate factual status from recommended escalation.

## Harness

- Preserve deadlines, owners, and escalation rules from the SOP.
- Do not change project status without source support.
- Keep unresolved conflicts visible.

## Verification

- Every row has an owner, source, status, blocker field, and next action.
- Missing department inputs are listed separately.
- Escalation recommendations match the SOP.
```
