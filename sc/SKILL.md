---
name: sc
description: "Use when the user asks to upload, register, catalog, publish, update, audit, or share a local AI agent skill in the Feishu/Lark AI skill knowledge base, especially when other agents should read a runtime page and download the full package only when needed."
---

# SC

## Purpose

Use this skill to publish a selected local agent skill into the Feishu/Lark `AI技能库` knowledge space.

The library is both human-readable and agent-readable:

- Humans can browse what each skill does.
- Agents can read a compact runtime guide directly from Feishu.
- Agents download the attached archive only when local installation, scripts, assets, or full references are required.

Because this skill performs external writes, use the full six-layer frame:
Context, Source, Procedure, Harness, Verification, and Iteration. Do not treat
it as a simple upload command.

## Trigger

Use this skill when the user asks to:

- upload a skill to Feishu;
- register a newly created skill;
- update an existing skill page;
- catalog a useful downloaded skill;
- make a skill available to other agents through the Feishu knowledge base.

Do not use it for bulk scanning unless the user explicitly asks. The default mode is active publishing of one specified skill.

Do not use it when the user only wants a local review, package inspection, or
draft publication plan. In those cases, stop before Feishu writes and report the
local findings.

## Six-Layer Operating Model

| Layer | SC requirement |
|-------|----------------|
| Context | Confirm the user explicitly wants to publish or update a local skill in the Feishu/Lark skill library. |
| Source | Use the local skill directory as the source of truth. Read `SKILL.md`, frontmatter, resources, metadata, scripts, and tests before publishing. |
| Procedure | Resolve the skill path, run the publisher, update the skill page and index, upload the archive, and verify page plus attachment. |
| Harness | Prevent unsafe external writes, duplicate indexes, secret publication, public sharing, and broad bulk operations. |
| Verification | Fetch the page, download the attachment, report URLs, attachment status, content hash, and any failed checks. |
| Iteration | Preserve hash/version evidence and use repeated failures to update page requirements, tests, or publishing rules. |

## Required Input

Resolve one of these before publishing:

- a local skill directory path;
- a skill name that can be resolved to a local directory.

The target directory must contain `SKILL.md` with frontmatter fields:

- `name`
- `description`

Source authority:

- `SKILL.md` frontmatter is the source of truth for skill ID and description.
- The local skill directory is the source of truth for packaged files.
- `agents/openai.yaml`, `references/`, `scripts/`, `assets/`, and `tests/` are supporting material when present.
- The canonical Feishu index is `00_技能库总索引`; legacy `AI技能库总索引` is compatibility-only.
- `lark-cli` authenticated user access determines whether publishing can proceed.

## Workflow

1. Confirm the user explicitly requested publishing or updating, then confirm the skill path or resolve the skill name.
2. Inspect `SKILL.md`, `agents/openai.yaml`, `references/`, `scripts/`, `assets/`, and `tests/` when present.
3. Check for obvious secrets or credentials before packaging.
4. Run the bundled publisher script.
5. Verify the Feishu page can be fetched.
6. Verify the attachment can be downloaded.
7. Report the knowledge space ID, index URL, skill page URL, attachment status, content hash, and verification status.

If the user asks to audit or prepare publishing without explicitly asking to
publish, perform steps 1-3 only and do not run the publisher script.

## Command

After installing this skill, set `SC_SKILL_DIR` to the unpacked `sc` directory. The command works from any working directory and does not depend on this machine's paths:

```bash
SC_SKILL_DIR="${SC_SKILL_DIR:-$HOME/.codex/skills/sc}"
PYTHONPATH="$(dirname "$SC_SKILL_DIR")" python3 "$SC_SKILL_DIR/scripts/publish_skill_to_lark.py" /path/to/skill --space-name AI技能库
```

To publish this skill itself:

```bash
SC_SKILL_DIR="${SC_SKILL_DIR:-$HOME/.codex/skills/sc}"
PYTHONPATH="$(dirname "$SC_SKILL_DIR")" python3 "$SC_SKILL_DIR/scripts/publish_skill_to_lark.py" "$SC_SKILL_DIR" --space-name AI技能库
```

## Distribution Install

Unpack the archive so the directory name remains `sc`, then place it in the skill directory for the target agent:

- Codex: `~/.codex/skills/sc`
- Claude Code: use the agent's configured skills directory, commonly `~/.claude/skills/sc`
- OpenClaw and Hemes: use their configured local skills directory, preserving `sc/SKILL.md`, `sc/scripts/`, `sc/agents/`, and `sc/tests/`

Runtime requirements:

- `python3`
- `PyYAML`
- `lark-cli` authenticated with access to the target Feishu/Lark workspace

Optional local verification:

```bash
SC_SKILL_DIR="${SC_SKILL_DIR:-$HOME/.codex/skills/sc}"
PYTHONPATH="$(dirname "$SC_SKILL_DIR")" python3 -m unittest discover "$SC_SKILL_DIR/tests"
```

## Feishu Behavior

The publisher:

- finds or creates the `AI技能库` knowledge space;
- finds or creates `00_技能库总索引`;
- uses `name` from `SKILL.md` as the unique skill ID;
- creates or updates one skill page;
- uploads a `.tar.gz` archive of the full skill directory;
- fetches the page and downloads the attachment for verification.

## Index Policy

Use `00_技能库总索引` as the only active index page.

If a legacy `AI技能库总索引` page exists, treat it as an old bootstrap artifact. Do not create a second index for the same space. After confirming the canonical index contains all current skills, ask the user before deleting or archiving the legacy index.

The index and every skill page should include a plain-language section so humans can quickly understand what the knowledge base contains and what each skill does before reading the agent-facing protocol.

## Safety Boundaries

- Treat Feishu writes as external actions. Publish only when the user explicitly asks to publish or update the skill.
- If the current request is review, audit, dry run, inspection, or planning, do not publish.
- Do not delete spaces, nodes, pages, or old attachments.
- Do not make pages public.
- Do not publish secrets. If a skill appears to contain credentials, stop and ask the user.
- Prefer user identity for Wiki resources unless the user explicitly asks for bot identity.
- Do not bulk-publish, bulk-download, or bulk-scan skills unless explicitly requested with a clear scope.
- Do not modify local credentials or `lark-cli` authentication state as part of publishing.

## Agent Consumption Policy

Agents using the skill library should:

1. Read `00_技能库总索引` to find the skill.
2. Read the target skill page.
3. Use the Agent Runtime Guide first.
4. Download the attachment only when the task needs local installation, scripts, assets, or full references.

Agents should not bulk-download every skill by default.

## Bootstrap Page Requirements

When publishing a skill page, make the Feishu page useful even before local installation:

- Include a `Quick Decision` section that tells agents when page-only use is enough and when full installation is required.
- Include `Self-Install From Feishu` with the current attachment token and concrete download, extract, install, and run commands.
- Include `Page-Only Fallback` for agents that can read Feishu but cannot download or install attachments.
- Include `Current Attachment Manifest` so agents can verify what the archive contains before installing.

For script-backed skills like `sc`, page-only use is not equivalent to installation. A page-only agent can understand the protocol, but an agent needs the attachment installed locally to run the deterministic publisher.

## Failure Handling And Iteration

If publishing or verification fails:

1. Report the failed phase: source parsing, archive creation, space/index lookup, page update, attachment upload, page fetch, or attachment download.
2. Include the relevant local path, Feishu URL or token if available, and whether any external write already happened.
3. Do not retry destructive or broad operations.
4. If the failure repeats, update this skill, its tests, or the publisher script so the failure becomes a documented preflight check.

Iteration triggers:

- Feishu/Lark CLI command shape changes.
- Attachment download verification becomes unreliable.
- Index naming or library governance changes.
- A published page lacks enough page-only guidance for agents.
- A secret or unsupported file type is found during preflight.
