# Six-Layer Skill Frame

Use this reference when SkillGoGo needs more structure than a small edit. The
frame converts vague work into something executable, checkable, reviewable, and
reusable. It is valuable, but it is not a universal form to complete for every
task.

Rule of thumb: use a reduced frame for small, low-risk edits; use the full frame
for complex, repeated, collaborative, quality-sensitive, or risk-sensitive work.

## The Six Layers

| Layer | Question it answers | Skill authoring use |
|-------|---------------------|---------------------|
| Context | Why does this exist, who uses it, when does it trigger, and what is out of scope? | Frontmatter trigger, When to Use, When NOT to Use, platform and permission boundaries |
| Source | What evidence, material, or authority should guide the work? | Existing skills, SOPs, policy, examples, codebase files, official docs, internal source material |
| Prompt/Procedure | What exactly should the agent or person do? | Ordered phases, output shape, required files, tool routing, handoff steps |
| Harness | What prevents bad execution while work is in progress? | Guardrails, forbidden behavior, format rules, examples, rubrics, scripts, validators |
| Verification | How is the finished result accepted? | `skill-validator`, review rubric, pressure scenarios, evals, source checks, publish checks |
| Iteration | How does this become better next time? | Version notes, governance, deprecation, split/merge decisions, new references or eval cases |

## Depth Selection

| Task | Minimum useful frame |
|------|----------------------|
| Fix typo or wording | Context + Change + Verification |
| Improve description/frontmatter | Context + Source + Verification |
| Add a rule to an existing skill | Context + Source + Harness + Verification |
| Audit or optimize a skill | Context + Source + Procedure + Harness + Verification |
| Create a reusable team skill | Full six layers |
| Publish or govern a skill library entry | Full six layers plus owner, version, source path, and publish verification |

## AI Skill Version

When the target is an AI-facing skill, emphasize:

- Context: trigger, non-trigger, role, user, platform, permissions.
- Source: allowed references, trusted sources, data cutoff, conflict handling.
- Prompt/Procedure: ordered actions and output format.
- Harness: style, format, compliance, tool, and safety constraints.
- Verification: self-checks, validator, scenarios, reviewer, publish checks.
- Iteration: when to update examples, references, tests, or governance.

If information is missing, the skill should say whether to ask, assume, search,
or proceed with a documented caveat.

## Human/Team Process Version

When converting a workflow for people instead of agents, do not write it like a
prompt. Add management fields:

- Why the work is needed.
- Who owns it.
- Who collaborates or supplies inputs.
- Which source materials and data definitions are authoritative.
- What deliverables are required.
- When they are due.
- What "good enough" means.
- Who accepts the work.
- When and to whom blocked work escalates.

This version is often better for SOPs, department handoffs, meeting follow-up,
publishing operations, and cross-functional workflows.

## Source Trust Rules

Separate sources by authority. For sensitive work, name which source wins when
sources conflict.

Typical levels:

- Official or canonical source.
- Internal approved material.
- Subject-matter owner statement.
- Public news or third-party research.
- AI-generated draft material.
- Unverified rumor, oral note, or background-only input.

Do not let polished output hide weak sources. If a source cannot support a fact,
mark the fact as unverified or remove it.

## Harness Versus Verification

Harness is used during execution. It prevents drift.

Examples:

- Do not promise investment returns.
- Do not publish externally without approval.
- Keep frontmatter descriptions trigger-only.
- Move long examples into `references/`.
- Preserve unrelated user changes.

Verification happens after execution. It confirms the finished artifact is
acceptable.

Examples:

- Run `skill-validator check <skill-dir>`.
- Apply the manual review rubric.
- Test normal, ambiguous, boundary, and failure pressure scenarios.
- Confirm publish page and attachment download work.
- Confirm no forbidden wording remains.

## Common Misuse

| Misuse | Correction |
|--------|------------|
| Turning the frame into mandatory paperwork | Select the lightest depth that still controls risk |
| Writing Prompt/Procedure before Context | Define trigger, audience, and boundaries first |
| Treating all sources as equal | Rank sources and state conflict rules |
| Mixing Harness and Verification | Separate process constraints from acceptance checks |
| Giving people AI-style prompts | Add owner, deadline, collaborator, acceptance, and escalation |
| Skipping Iteration | Capture reusable lessons, templates, evals, or governance updates |

## One-Line Memory Aid

Clarify the scene, confirm the source, define the output, set the guardrails,
verify the result, then preserve the lesson for next time.
