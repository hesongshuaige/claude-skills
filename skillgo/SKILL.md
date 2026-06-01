---
name: skillgo
description: "Use when a team or multi-agent workflow needs to turn requirements, SOPs, prompts, domain procedures, or repeated agent behaviors into reusable AI agent skills; review or improve existing SKILL.md files; decide whether a skill is worth creating; validate skill quality; run lightweight or formal skill evaluations; package and publish skills to a shared Feishu/Lark AI skill library."
---

# SkillGo

## Overview

Use this as the team's standard operating protocol for creating, reviewing, testing, publishing, and maintaining reusable AI agent skills. The default path is self-contained: agents can follow SkillGo without downloading every external reference repo first.

SkillGo uses the six-layer frame as the skill engineering backbone: Context,
Source, Prompt/Procedure, Harness, Verification, and Iteration. The frame is a
depth selector, not mandatory paperwork. Small low-risk edits use a reduced
path; complex, repeated, collaborative, quality-sensitive, or risk-sensitive
skills use the full frame.

External repos and tools are optional accelerators:
- Use downloaded examples when improving structure or style.
- Use validators and eval tools when quality gates matter.
- Use `sc` only when publishing to Feishu/Lark is requested.

## Best Answer For Team Distribution

Do not require every teammate or agent to pre-download all reference repos before using SkillGo.

Recommended distribution:
- Ship SkillGo as the single entrypoint.
- Include only the references that are needed for routine work.
- Let ordinary agents follow the built-in phases and rubrics.
- Let maintainer agents install optional tools such as `skill-validator`, `skillgrade`, and `sc`.
- Download large external repositories only for authors, reviewers, or CI jobs that need examples, automated review, or formal evaluation.

This keeps adoption lightweight while preserving a path to rigorous review.

## When To Use

Use this when:
- A repeated user request, workflow, SOP, prompt, or decision tree should become a reusable skill.
- A team wants consistent `SKILL.md` quality across multiple agents.
- A skill will be published to a shared library such as Feishu `AI技能库`.
- An existing skill needs audit, refactor, versioning, or deprecation review.
- You need to decide whether to use a lightweight manual review or a formal validator/eval workflow.

Do not use this for one-off notes, project-specific instructions that belong in `AGENTS.md`, or tasks better solved by normal code, tests, scripts, or product changes.

## Core Rule

The pipeline creates or improves the target skill. It does not require creating a meta-skill each time. This skill itself is the reusable meta-process.

## Phase 1: Intake And Skill-Worthiness

Entry criteria:
- The user has a process, recurring need, existing prompt, SOP, or current skill to improve.

Actions:
1. Identify the target skill name, audience, platforms, and owner.
2. Ask for missing essentials only: trigger examples, ideal outputs, failure cases, boundaries, and required tools.
3. Decide whether a skill is warranted:
   - Create a skill when the behavior is reusable, judgment-heavy, cross-project, or useful to multiple agents.
   - Do not create a skill for one-off notes, simple facts, or rules that should be automated.
4. Choose the workflow depth:
   - Reduced path for tiny edits: Context + Change + Verification.
   - Standard path for ordinary skill work: Context + Source + Procedure + Harness + Verification.
   - Full path for team, high-risk, repeated, publishable, or governance work: all six layers including Iteration.
5. Capture source authority:
   - Which existing skills, SOPs, examples, policies, docs, or owner statements are authoritative?
   - Which sources are background only?
   - If sources conflict, which one wins?
6. Capture 2-4 pressure scenarios:
   - A normal request.
   - An ambiguous request.
   - A boundary or unsafe request.
   - A case where an agent would likely skip a required step.
   Use `references/pressure-scenarios.md` for reusable scenario patterns.

Exit criteria:
- There is a named target skill, workflow depth, source basis, and at least two pressure scenarios.

## Phase 2: Author The First Draft

Entry criteria:
- Phase 1 exit criteria are met.

Actions:
1. Write `SKILL.md` with required frontmatter:
   - `name`: kebab-case, stable, no special characters.
   - `description`: starts with `Use when`, describes trigger conditions only, not the workflow.
2. Apply the selected six-layer depth. For the full path, read `references/six-layer-skill-engineering.md`.
3. Cover the required layers in the draft:
   - **Context**: trigger, non-trigger, audience, platform, owner, permission and compliance boundaries.
   - **Source**: authoritative materials, source ranking, cutoff dates, and conflict rules.
   - **Prompt/Procedure**: ordered actions, tool routing, expected files, and output shape.
   - **Harness**: process guardrails, forbidden behavior, format rules, examples, scripts, or rubrics.
   - **Verification**: validator, manual review, pressure scenarios, source checks, publish checks, and acceptance owner.
   - **Iteration**: version notes, maintenance triggers, deprecation, split/merge, and eval updates.
4. Keep `SKILL.md` focused on instructions needed every time.
5. Move long domain details, examples, schemas, and checklists into `references/`.
6. Add `agents/openai.yaml` for Codex/OpenAI-facing metadata when the skill will be shared.
7. Add scripts only when deterministic execution is safer than prose.
8. When converting a human SOP into a skill, separate the human management frame from the AI instructions: owner, collaborators, deadline, acceptance criteria, and escalation path belong in source notes or references unless agents must act on them.
9. Use `references/example-conversions.md` when the author needs a concrete model for converting a prompt, SOP, or repeated behavior into a skill.

Exit criteria:
- The draft has valid frontmatter, clear trigger conditions, source basis, scoped instructions, guardrails, verification path, and resource layout.

## Phase 3: Reference Pass

Entry criteria:
- A first draft exists.

Actions:
1. Compare the draft against high-quality examples when available:
   - `external-skill-repos/superpowers/skills/writing-skills/SKILL.md`
   - `external-skill-repos/agent-skills/skills/*/SKILL.md`
   - `external-skill-repos/trailofbits-skills/plugins/*/skills/*/SKILL.md`
2. Improve structure, not voice-copying.
3. Prefer numbered phases, entry/exit criteria, routing tables, and explicit safety gates for workflow skills.
4. Keep platform-specific details isolated unless the skill is platform-specific.

Exit criteria:
- The draft follows a recognizable skill pattern and avoids long narrative prose.

## Phase 4: Quality Review

Entry criteria:
- The draft is structurally complete.

Actions:
1. Read `references/review-rubric.md`.
2. Check:
   - Trigger quality.
   - Scope and non-use cases.
   - Source authority and conflict rules.
   - Step order.
   - Failure modes.
   - Harness/verification separation.
   - Tool and permission boundaries.
   - Resource map.
   - Install/publish path.
   - Iteration and governance triggers for repeated or published skills.
3. If `skill-validator` is installed, run structural validation.
4. If no validator is available, perform the manual rubric and record that automated validation was skipped.

Exit criteria:
- Blocking issues are fixed or explicitly documented.

## Phase 5: Effect Evaluation

Entry criteria:
- The skill passes manual or structural review.

Actions:
1. Use the Phase 1 pressure scenarios as tests.
2. Evaluate whether the skill changes behavior:
   - Without the skill, what would an agent likely miss?
   - With the skill, does the agent follow the required routing, boundaries, and output shape?
3. Include at least one scenario that tests Source, Harness, or Verification when those layers are central to the skill.
4. Score the scenarios with the manual rubric in `references/pressure-scenarios.md` unless a formal eval is available.
5. If `skillgrade` or `agent-skills-eval` is available, run a formal with-skill vs without-skill check.
6. If formal eval is too heavy, run a lightweight manual eval and record residual risk.

Exit criteria:
- There is evidence that the skill improves behavior or a clear list of gaps to fix.

## Phase 6: Package And Publish

Entry criteria:
- Review and evaluation are complete enough for the intended audience.

Actions:
1. If publishing to Feishu/Lark is requested, use `sc`.
2. Publish the full skill directory, not just `SKILL.md`, when references, scripts, assets, or metadata exist.
3. Verify:
   - Page fetch works.
   - Attachment download works.
   - Index points to the intended page.
   - Hash/version record is visible.
4. If publishing is not requested, report the local skill path and verification status.

Exit criteria:
- The target skill is available to its intended users with verification evidence.

## Phase 7: Governance

Entry criteria:
- The skill has been published or adopted.

Actions:
1. Track owner, version/hash, source path, publish date, and audience.
2. Deprecate instead of silently overwriting incompatible workflows.
3. Merge duplicate skills when they share triggers and differ only in wording.
4. Split skills when a single `SKILL.md` mixes unrelated workflows.
5. Re-run review after major model, tool, API, or organization-policy changes.

Exit criteria:
- The skill has a clear maintenance path.

## Quick Decision Table

| Need | Path |
|-|-|
| Tiny low-risk edit | Reduced six-layer path plus validation |
| Fast personal skill | Phases 1-2 plus manual test |
| Team reusable skill | Phases 1-6 |
| High-risk or cross-agent skill | Phases 1-7 with validator and eval |
| Publish to Feishu | Use `sc` in Phase 6 |
| Existing skill audit | Start at Phase 4, then loop back to Phase 2 if needed |

## Toolchain Map

Read `references/toolchain-map.md` before installing or requiring any external tool.

Default rule:
- The pipeline works without external downloads.
- External tools are optional quality gates.
- Do not block ordinary authors on installing every reference repo.

## Common Mistakes

- Writing `description` as a summary instead of trigger conditions.
- Creating a skill for a one-off task.
- Applying the full six-layer frame to tiny edits.
- Writing Prompt/Procedure before Context and Source are clear.
- Treating all source materials as equally reliable.
- Mixing Harness process guardrails with Verification acceptance checks.
- Putting large reference material directly in `SKILL.md`.
- Publishing without verifying page fetch and attachment download.
- Treating GitHub stars as proof of fit.
- Skipping pressure scenarios, which makes the skill impossible to evaluate.
- Skipping Iteration for repeated or team-adopted workflows.
- Making every team member install all tooling before they can contribute.
