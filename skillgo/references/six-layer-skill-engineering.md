# Six-Layer Skill Engineering

Use this reference when creating, auditing, or upgrading a skill needs more
structure than a small edit. The frame turns vague workflows into skills that
are executable, checkable, reviewable, and reusable.

The frame is not a universal form. Use a reduced path for small, low-risk
changes. Use the full path for complex, repeated, collaborative,
quality-sensitive, or risk-sensitive skills.

## Layer Map

| Layer | Skill engineering question | Typical artifact |
|-------|----------------------------|------------------|
| Context | Why should this skill exist, who uses it, when does it trigger, and what is out of scope? | Frontmatter, When To Use, non-use cases, platform and permission boundaries |
| Source | What evidence, material, or authority defines correct behavior? | Source list, owner notes, official docs, existing skills, examples, policy, data cutoff |
| Prompt/Procedure | What should the agent do and in what order? | Phases, steps, routing tables, output templates, required files |
| Harness | What keeps execution from drifting? | Guardrails, forbidden behavior, style/format constraints, examples, rubrics, scripts |
| Verification | How is the finished skill accepted? | Validator result, manual rubric, pressure scenarios, evals, publish checks |
| Iteration | How does the skill improve after use? | Version notes, governance, split/merge/deprecate criteria, new eval cases |

## Depth Selection

| Work type | Use |
|-----------|-----|
| Typo, wording, one small rule | Context + Change + Verification |
| Frontmatter or trigger improvement | Context + Source + Verification |
| Existing skill audit or optimization | Context + Source + Procedure + Harness + Verification |
| New team skill or publishable skill | Full six layers |
| High-risk domain skill | Full six layers plus explicit source authority and reviewer |
| Human SOP converted into an agent skill | Full six layers plus management fields in source notes |

## Source Authority

Do not treat all inputs as equally reliable. Rank source material and state what
happens when sources conflict.

Common ranking:

- Official or canonical documentation.
- Approved internal policy, SOP, or owner-provided material.
- Existing local skills and project instructions.
- Public news, third-party research, or examples.
- AI-generated drafts.
- Unverified oral notes or background-only material.

For policy, investment, legal, compliance, public communication, or operational
workflows, unclear Source is a quality risk even when the prose looks polished.

## AI Skill Versus Human SOP

For AI-facing skills, emphasize:

- Role and trigger.
- Allowed materials and missing-information behavior.
- Concrete output format.
- Forbidden actions or wording.
- Self-checks and validator/eval steps.

For human/team workflows, also preserve:

- Owner and collaborators.
- Deliverables and deadline.
- Acceptance criteria and reviewer.
- Escalation path when inputs are blocked.

Do not force human delegation into prompt format. Convert it into skill
instructions only when an agent needs to perform or coordinate the work.

## Harness Versus Verification

Harness is an in-process guardrail. It prevents bad execution.

Examples:

- Keep frontmatter descriptions trigger-only.
- Do not publish externally without approval.
- Move heavy examples into `references/`.
- Do not overwrite unrelated user changes.
- Do not make claims unsupported by sources.

Verification is a post-work acceptance check. It confirms the result is ready.

Examples:

- Run `skill-validator check <skill-dir>`.
- Apply `references/review-rubric.md`.
- Test normal, ambiguous, boundary, and failure pressure scenarios.
- Confirm source-backed claims and publish checks.
- Record residual risk.

## Iteration Triggers

Update the skill when:

- Pressure scenarios expose missed behavior.
- Users repeat the same clarification or correction.
- A model, tool, API, policy, or publishing target changes.
- Two skills overlap in trigger or one skill mixes unrelated workflows.
- Review or eval results show drift.

Prefer a small targeted update over broad rewriting. Split, merge, or deprecate
only when the trigger and behavior justify it.

## Memory Aid

Clarify the context, rank the sources, define the procedure, set the harness,
verify the result, then preserve the lesson.
