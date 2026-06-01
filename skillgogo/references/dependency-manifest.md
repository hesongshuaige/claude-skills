# SkillGoGo Dependency Manifest

Use this manifest when installing SkillGoGo for Claude Code, Codex, OpenClaw,
Hemes, or another agent runtime. Do not ask agents to download similarly named
skills from web search results. Prefer the approved sources below.

## Canonical Download Source

Primary source for team use:

- Feishu/Lark knowledge space: `AI技能库`
- Canonical index: `00_技能库总索引`
- Index URL: https://my.feishu.cn/wiki/SQALwOAk0i2vDvkiJKDcvyHbnJh
- SkillGoGo page URL: https://my.feishu.cn/wiki/HtHowIptNitV0DkJuOCc7uzSnEd

Download rule:

1. Open the index URL.
2. Search the exact skill id from the tables below.
3. Open the matching skill page.
4. Use that page's `Self-Install From Feishu` section to download the attachment.
5. Verify the unpacked directory contains `SKILL.md` with the same `name`.

If a dependency is missing from `AI技能库`, ask a maintainer to publish that
exact local skill with `sc` before relying on web downloads.

## Skill Dependencies

### Required For Normal Use

| Skill id | Why it is needed | Approved local source on this host |
|----------|------------------|------------------------------------|
| `skillgogo` | Orchestrates the whole skill-quality workflow | `/home/ubuntu/.codex/skills/skillgogo` |
| `using-superpowers` | Enforces "use the relevant skill first" discipline | `/home/ubuntu/.codex/skills/using-superpowers` |
| `skillgo` | Provides the main skill engineering, review, evaluation, publishing, and governance process | `/home/ubuntu/.codex/skills/skillgo` |

### Recommended For Reliable Skill Work

| Skill id | Why it is needed | Approved local source on this host |
|----------|------------------|------------------------------------|
| `skill-scout` | Searches existing local, marketplace, GitHub, and web skill sources before creating or merging | `/home/ubuntu/.codex/skills/skill-scout` |
| `writing-skills` | Gives SKILL.md authoring rules, trigger descriptions, references layout, and token discipline | `/home/ubuntu/.codex/skills/writing-skills` |
| `review-skill` | Runs structured skill review and points to validator installation/scoring workflows | `/home/ubuntu/.codex/skills/review-skill` |

### Optional For Formal Evaluation And Publishing

| Skill or tool | Why it is needed | Approved source |
|---------------|------------------|-----------------|
| `skillgrade-setup` | Sets up formal skillgrade evaluations | `/home/ubuntu/.codex/skills/skillgrade-setup` |
| `skillgrade-graders` | Authors deterministic and LLM rubric graders | `/home/ubuntu/.codex/skills/skillgrade-graders` |
| `sc` | Publishes local skills to Feishu/Lark `AI技能库` | `/home/ubuntu/.codex/skills/sc` |
| `skill-validator` CLI | Validates skill structure and content | `go install github.com/agent-ecosystem/skill-validator/cmd/skill-validator@latest` |
| `skillgrade` CLI | Runs skill behavior evaluations | `npm install -g skillgrade` |
| `lark-cli` CLI | Downloads Feishu attachments and supports `sc` publishing | `npm install -g @larksuite/cli` |

## Platform Install Locations

Install each downloaded skill directory under the runtime's skill directory.
Keep the directory name equal to the skill id.

| Runtime | Recommended install location |
|---------|------------------------------|
| Codex | `~/.codex/skills/<skill-id>` |
| Claude Code | the configured Claude skills directory, commonly `~/.claude/skills/<skill-id>` |
| OpenClaw | the configured OpenClaw local skills directory, preserving `SKILL.md` and subdirectories |
| Hemes | the configured Hemes local skills directory, preserving `SKILL.md` and subdirectories |

## Minimal Bundles

**Page-only use**: An agent can read the SkillGoGo page and follow the broad
workflow, but should report that dependency skills are not locally available.

**Minimum local bundle**:

- `skillgogo`
- `using-superpowers`
- `skillgo`

**Recommended local bundle**:

- all minimum bundle skills
- `skill-scout`
- `writing-skills`
- `review-skill`
- `skill-validator` CLI

**Publishing bundle**:

- all recommended bundle skills
- `sc`
- authenticated `lark-cli`

**Formal evaluation bundle**:

- all recommended bundle skills
- `skillgrade-setup`
- `skillgrade-graders`
- `skillgrade` CLI

## Verification Commands

After installation, run:

```bash
skill-validator check ~/.codex/skills/skillgogo
skill-validator check ~/.codex/skills/skillgo
skill-validator check ~/.codex/skills/writing-skills
```

For non-Codex runtimes, replace `~/.codex/skills` with that runtime's local
skill directory.

CLI checks:

```bash
skill-validator --version
skillgrade --help
lark-cli doctor
```

If a command is unavailable, the related workflow becomes optional or manual:

- no `skill-validator`: use manual SkillGo rubric and report that automated validation was skipped
- no `skillgrade`: use lightweight pressure scenarios
- no `lark-cli`: do not publish or download Feishu attachments from that agent
