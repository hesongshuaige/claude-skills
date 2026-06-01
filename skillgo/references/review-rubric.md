# Skill Review Rubric

Use this rubric before publishing or adopting a skill.

## Blocking Checks

The skill should not publish until these pass:

1. `SKILL.md` exists.
2. Frontmatter has `name` and `description`.
3. `name` is stable kebab-case.
4. `description` starts with `Use when` and describes triggers, not workflow steps.
5. The skill states when to use it and when not to use it.
6. The workflow has ordered steps or phases when order matters.
7. External write actions, destructive operations, credentials, and paid actions have explicit boundaries.
8. Required resources are either inline or listed in a resource map.
9. Verification steps are present.
10. Source authority is clear when the skill depends on facts, policy, domain material, or existing workflows.

## Quality Checks

These are not always blocking, but improve cross-agent reliability:

| Area | Good signal |
|-|-|
| Trigger | Concrete symptoms, commands, task names, or user phrases |
| Scope | Clear non-use cases and alternatives |
| Context | Audience, platform, owner, authority, and permission boundaries are explicit when relevant |
| Source | Trusted materials, cutoff dates, and conflict rules are documented |
| Workflow | Numbered phases with entry/exit criteria |
| Harness | Guardrails, forbidden behavior, style/format constraints, scripts, or rubrics guide execution |
| Verification | Acceptance checks are separate from in-process guardrails |
| Examples | At least one normal and one edge-case scenario |
| Safety | Permission and confirmation rules are explicit |
| Progressive disclosure | Long material lives in `references/`, scripts, or assets |
| Portability | Platform-specific assumptions are named |
| Evaluation | Pressure scenarios or formal eval plan included |
| Publishing | Version/hash/source path can be tracked |
| Iteration | Repeated or published skills state when to update, split, merge, deprecate, or add evals |

## Review Output Template

```markdown
## Verdict
Pass / Pass with warnings / Blocked

## Blocking Issues
- [file/section] issue and required fix

## Warnings
- [file/section] issue and recommended fix

## Evidence
- Structural validation:
- Manual rubric:
- Pressure scenarios:
- Eval result:
- Publish verification:
```
