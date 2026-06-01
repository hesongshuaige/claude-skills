# Toolchain Map

## Default Distribution Model

Most users and agents only need SkillGo itself.

Optional tools are used by maintainers, reviewers, CI, or publishing agents:

| Tool or repo | Role | Required for routine use? |
|-|-|-|
| `writing-skills` | Authoring method for SKILL.md quality | Recommended, but SkillGo includes the core rules |
| `superpowers` | Source examples for TDD-style skill authoring | No |
| `agent-skills` | High-quality engineering skill examples | No |
| `trailofbits-skills` | Security-heavy workflow and boundary examples | No |
| `skills-best-practices` | Concise authoring reference | No |
| `skill-validator` | Automated structure/content review | Only for formal review or CI |
| `skillgrade` | Skill behavior tests | Only for formal evaluation |
| `agent-skills-eval` | With-skill vs without-skill evaluation | Only for formal evaluation |
| `sc` | Publish skill pages and attachments to Feishu AI技能库 | Only for Feishu publishing |

## Local Reference Paths

On this machine, downloaded references live under:

```text
/home/ubuntu/codex/external-skill-repos/
```

Useful paths:

```text
superpowers/skills/writing-skills/SKILL.md
agent-skills/skills/using-agent-skills/SKILL.md
trailofbits-skills/plugins/workflow-skill-design/skills/designing-workflow-skills/SKILL.md
skill-validator/examples/review-skill/SKILL.md
```

## Installation Policy

Do not require every team member to install every external tool.

Use this split:

- Authors: SkillGo, plus examples as needed.
- Reviewers: SkillGo plus `skill-validator`.
- Evaluators: SkillGo plus `skillgrade` or `agent-skills-eval`.
- Publishers: SkillGo plus `sc` and Lark/Feishu auth.
- CI: validator and eval tools pinned by version.

## Quality Gates By Risk

| Risk | Required evidence |
|-|-|
| Low | Manual rubric and one pressure scenario |
| Medium | Manual rubric, 2-4 pressure scenarios, parse validation |
| High | Validator, pressure scenarios, with-skill vs without-skill eval, publish verification |
