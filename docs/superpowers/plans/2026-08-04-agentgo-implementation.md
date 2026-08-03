# AgentGo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a portable `agentgo` skill that guides Claude, Codex, or Hermes through creating an isolated Hermes profile, generating its context files, connecting a dedicated Feishu bot, authorizing user resources, and verifying the full setup safely.

**Architecture:** Keep the always-loaded workflow in `SKILL.md`, route detailed operational material into focused references, copy four editable context templates from assets, and use one dependency-free Python validator for deterministic read-only checks. Treat QR scans, credentials, app scopes, and user authorization as human-confirmed gates.

**Tech Stack:** Markdown, YAML, Python 3 standard library, `unittest`, Hermes CLI, lark-cli, Git, GitHub CLI.

---

## File Map

- Create `agentgo/SKILL.md`: trigger conditions, decision gates, ordered workflow, resource routing, and acceptance criteria.
- Create `agentgo/agents/openai.yaml`: Codex/OpenAI skill metadata.
- Create `agentgo/assets/templates/SOUL.md.template`: durable identity and safety-boundary template.
- Create `agentgo/assets/templates/AGENTS.md.template`: project execution rules and verification template.
- Create `agentgo/assets/templates/README.md.template`: user-facing capability menu and example prompts.
- Create `agentgo/assets/templates/PROJECT.md.template`: purpose, data flow, state, and enablement conditions.
- Create `agentgo/references/hermes-profile-and-model.md`: profile discovery, creation, model configuration, and direct model test.
- Create `agentgo/references/feishu-bot-and-permissions.md`: app creation, bot scopes, websocket setup, and gateway lifecycle.
- Create `agentgo/references/lark-user-authorization.md`: bot/user identity split, binding, device-code authorization, and read-only checks.
- Create `agentgo/references/context-files-and-prompts.md`: SOUL/AGENTS/README/PROJECT responsibilities and generation guidance.
- Create `agentgo/references/troubleshooting.md`: verified failures, diagnosis order, and fixes.
- Create `agentgo/references/security-and-handoff.md`: secret handling, minimum permissions, and handoff checklist.
- Create `agentgo/references/pressure-scenarios.md`: baseline and forward-test prompts with pass signals.
- Create `agentgo/scripts/validate_agent_profile.py`: read-only local profile validator.
- Create `agentgo/tests/test_validate_agent_profile.py`: validator behavior tests.
- Create `agentgo/tests/test_skill_package.py`: package, frontmatter, metadata, template, and secret-scan tests.
- Modify `README.md`: add AgentGo to the repository index and installation examples.
- Existing `docs/superpowers/specs/2026-08-04-agentgo-design.md`: authoritative design; do not broaden scope without updating it first.

### Task 1: Create the branch and official skill scaffold

**Files:**
- Create: `agentgo/SKILL.md`
- Create: `agentgo/agents/openai.yaml`
- Create directories: `agentgo/scripts`, `agentgo/references`, `agentgo/assets`

- [ ] **Step 1: Confirm the repository is clean except for approved planning documents**

Run:

```powershell
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' status --short
```

Expected: only `docs/superpowers/specs/2026-08-04-agentgo-design.md` and this plan are untracked or modified.

- [ ] **Step 2: Create a focused branch from current main**

Run:

```powershell
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' switch -c agent/add-agentgo
```

Expected: `Switched to a new branch 'agent/add-agentgo'`.

- [ ] **Step 3: Initialize the skill with the required system script**

Run:

```powershell
python 'C:\Users\Admin\.codex\skills\.system\skill-creator\scripts\init_skill.py' agentgo `
  --path 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' `
  --resources scripts,references,assets `
  --interface 'display_name=AgentGo' `
  --interface 'short_description=Build isolated Hermes agents with Feishu safely' `
  --interface 'default_prompt=Use $agentgo to create and verify an isolated Hermes agent with a dedicated Feishu bot.'
```

Expected: the `agentgo` directory, `SKILL.md`, `agents/openai.yaml`, and three resource directories are created.

- [ ] **Step 4: Commit the approved design and scaffold**

```powershell
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' add docs/superpowers agentgo
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' commit -m 'chore: scaffold agentgo skill'
```

Expected: one commit containing only the two planning documents and generated scaffold.

### Task 2: Establish RED tests and baseline pressure scenarios

**Files:**
- Create: `agentgo/tests/test_validate_agent_profile.py`
- Create: `agentgo/tests/test_skill_package.py`
- Create: `agentgo/references/pressure-scenarios.md`

- [ ] **Step 1: Write validator tests before the validator exists**

Create tests that load `scripts/validate_agent_profile.py` as a subprocess and use temporary profile directories. Cover:

```python
def test_complete_profile_passes(): ...
def test_missing_required_file_fails(): ...
def test_mismatched_key_env_fails_without_printing_secret(): ...
def test_missing_workspace_fails(): ...
def test_oversized_context_file_warns(): ...
def test_invalid_feishu_policy_fails(): ...
def test_open_env_permissions_warn_on_posix(): ...
```

Use this helper shape:

```python
def run_validator(profile: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(profile)],
        text=True,
        capture_output=True,
        check=False,
    )
```

- [ ] **Step 2: Write package tests before content exists**

The package test must assert:

```python
REQUIRED_REFERENCES = {
    "hermes-profile-and-model.md",
    "feishu-bot-and-permissions.md",
    "lark-user-authorization.md",
    "context-files-and-prompts.md",
    "troubleshooting.md",
    "security-and-handoff.md",
    "pressure-scenarios.md",
}

REQUIRED_TEMPLATES = {
    "SOUL.md.template",
    "AGENTS.md.template",
    "README.md.template",
    "PROJECT.md.template",
}
```

Also assert that frontmatter contains only `name` and `description`, the description starts with `Use when`, `openai.yaml` explicitly contains `$agentgo`, no `TODO` remains, and no likely secret pattern is committed.

- [ ] **Step 3: Record six baseline scenarios**

Write the exact six prompts from the design: normal chat-only setup, user-resource setup, reused App ID request, secret pasted into chat, skipped model test, and Windows-to-Linux Chinese-file transfer. For each, record the behavior an unskilled agent is likely to miss and the required post-skill pass signals.

- [ ] **Step 4: Run the tests and verify RED**

Run:

```powershell
python -m unittest discover -s 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills\agentgo\tests' -v
```

Expected: failures for missing validator, references, templates, final frontmatter, and unfinished scaffold text.

- [ ] **Step 5: Commit only the failing tests and baseline scenarios**

```powershell
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' add agentgo/tests agentgo/references/pressure-scenarios.md
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' commit -m 'test: define agentgo acceptance cases'
```

### Task 3: Implement the read-only profile validator

**Files:**
- Create: `agentgo/scripts/validate_agent_profile.py`
- Test: `agentgo/tests/test_validate_agent_profile.py`

- [ ] **Step 1: Implement the minimal validator**

Use only the standard library. Define these stable interfaces:

```python
@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    message: str

def parse_simple_yaml(path: Path) -> dict[str, object]: ...
def parse_env_names(path: Path) -> set[str]: ...
def validate_profile(profile: Path) -> list[Finding]: ...
def main(argv: list[str] | None = None) -> int: ...
```

The YAML parser only needs the nested mappings and scalar values used by Hermes configuration. It must never return or print `.env` values; `parse_env_names` returns variable names only. Exit `0` when no `ERROR` finding exists and `1` otherwise.

- [ ] **Step 2: Run validator tests**

Run:

```powershell
python -m unittest 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills\agentgo\tests\test_validate_agent_profile.py' -v
```

Expected: all validator tests pass, with the POSIX permission case skipped on Windows.

- [ ] **Step 3: Run the validator against the real WXAgent profile without exposing values**

Run:

```powershell
python 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills\agentgo\scripts\validate_agent_profile.py' 'C:\Users\Admin\AppData\Local\hermes\profiles\wxagent'
```

Expected: a finding summary containing variable names at most, never their values. Known local differences may produce warnings, but no traceback.

- [ ] **Step 4: Commit validator and tests**

```powershell
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' add agentgo/scripts/validate_agent_profile.py agentgo/tests/test_validate_agent_profile.py
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' commit -m 'feat: validate Hermes agent profiles safely'
```

### Task 4: Add the four context templates

**Files:**
- Create: `agentgo/assets/templates/SOUL.md.template`
- Create: `agentgo/assets/templates/AGENTS.md.template`
- Create: `agentgo/assets/templates/README.md.template`
- Create: `agentgo/assets/templates/PROJECT.md.template`
- Test: `agentgo/tests/test_skill_package.py`

- [ ] **Step 1: Create focused templates with consistent placeholders**

Use only these placeholders so replacement is deterministic:

```text
{{AGENT_NAME}}
{{ONE_LINE_ROLE}}
{{PRIMARY_USERS}}
{{INPUT_SOURCES}}
{{OUTPUT_TARGETS}}
{{AUTOMATIC_CAPABILITIES}}
{{ON_DEMAND_CAPABILITIES}}
{{NOT_ENABLED_CAPABILITIES}}
{{PERMISSION_BOUNDARIES}}
{{VERIFICATION_RULES}}
```

SOUL owns identity and durable judgment; AGENTS owns project execution rules; README owns the user menu; PROJECT owns system purpose, file responsibilities, data flow, and current state. Do not duplicate full sections across files.

- [ ] **Step 2: Run package tests**

```powershell
python -m unittest 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills\agentgo\tests\test_skill_package.py' -v
```

Expected: template tests pass; reference and final SKILL tests remain failing.

- [ ] **Step 3: Commit templates**

```powershell
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' add agentgo/assets agentgo/tests/test_skill_package.py
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' commit -m 'feat: add Hermes agent context templates'
```

### Task 5: Write the operational references

**Files:**
- Create: all seven files under `agentgo/references/`

- [ ] **Step 1: Write profile and model guidance**

Include command discovery, profile creation, independent config behavior, provider/key_env consistency, direct model test, workspace cwd configuration, Linux and Windows path differences, and version-first `--help` checks.

- [ ] **Step 2: Write Feishu bot and permission guidance**

Include QR and manual app creation paths, bot capability, websocket mode, one-app-per-profile rule, allowlist/group/mention choices, gateway install/start/restart/status, outbound/DM/group tests, and scope-error console handling.

- [ ] **Step 3: Write lark user authorization guidance**

Include app binding to the correct new profile, `bot-only` versus `user-default`, the split device-code flow, opaque URL forwarding, QR generation, `--as user`, status verification, and read-before-write testing.

- [ ] **Step 4: Write context, troubleshooting, and handoff guidance**

Include the 20,000-character context limit, SOUL always-loaded behavior, AGENTS cwd-only behavior, the complete verified pitfall list, secret rotation, minimum permissions, handoff fields, and truthful capability states.

- [ ] **Step 5: Run package tests and secret scan**

```powershell
python -m unittest discover -s 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills\agentgo\tests' -v
rg -n -i '(app_secret\s*=\s*[^<{]|api[_-]?key\s*=\s*[^<{]|password\s*=\s*[^<{]|cli_[a-z0-9]{10,}|ou_[a-z0-9]{10,})' 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills\agentgo'
```

Expected: tests fail only for unfinished `SKILL.md`; the secret scan returns no matches containing real values.

- [ ] **Step 6: Commit references**

```powershell
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' add agentgo/references
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' commit -m 'docs: add AgentGo setup and troubleshooting guides'
```

### Task 6: Finish the main skill and metadata

**Files:**
- Modify: `agentgo/SKILL.md`
- Modify: `agentgo/agents/openai.yaml`
- Test: `agentgo/tests/test_skill_package.py`

- [ ] **Step 1: Replace scaffold content with the workflow**

The frontmatter must be exactly:

```yaml
---
name: agentgo
description: "Use when creating, repairing, or handing off an isolated Hermes Agent profile; connecting it to a dedicated Feishu bot; granting bot or user-level Feishu access; or generating SOUL.md, AGENTS.md, README.md, and PROJECT.md for a reusable agent deployment."
---
```

The body must route users through: preflight, requirements, profile isolation, model test, template generation, Feishu app creation, permission/auth split, gateway startup, layered verification, troubleshooting, and handoff. It must say when not to use the skill and name exactly which reference to read for each branch.

- [ ] **Step 2: Finalize OpenAI metadata**

Use quoted string values and this minimal shape:

```yaml
interface:
  display_name: "AgentGo"
  short_description: "Build isolated Hermes agents with Feishu safely"
  default_prompt: "Use $agentgo to create and verify an isolated Hermes agent with a dedicated Feishu bot."
policy:
  allow_implicit_invocation: true
```

- [ ] **Step 3: Run structural and package validation**

```powershell
python 'C:\Users\Admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py' 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills\agentgo'
python -m unittest discover -s 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills\agentgo\tests' -v
```

Expected: `Skill is valid!` and all tests pass.

- [ ] **Step 4: Commit skill workflow and metadata**

```powershell
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' add agentgo/SKILL.md agentgo/agents/openai.yaml
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' commit -m 'feat: add AgentGo deployment workflow'
```

### Task 7: Forward-test, document installation, and review the diff

**Files:**
- Modify: `README.md`
- Modify if failures require it: files under `agentgo/`

- [ ] **Step 1: Forward-test all six pressure scenarios**

For each prompt in `references/pressure-scenarios.md`, compare the proposed behavior with its pass signals. Record score and exact gap in that file. Fix the smallest skill section responsible for each gap and rerun the affected scenario.

Expected: every scenario scores 2/2, with no secret reuse, silent user-identity downgrade, skipped model test, or false full-success claim.

- [ ] **Step 2: Update the repository README**

Add AgentGo to the skill index and add installation examples that copy `agentgo` into the normal Claude, Codex, and Hermes skill directories. Keep existing README style and do not renumber unrelated entries unnecessarily.

- [ ] **Step 3: Run the complete verification suite**

```powershell
python 'C:\Users\Admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py' 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills\agentgo'
python -m unittest discover -s 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills\agentgo\tests' -v
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' diff --check main...HEAD
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' status --short
```

Expected: validator and tests pass, no whitespace errors, and only intended files are changed.

- [ ] **Step 4: Commit README and final pressure-test refinements**

```powershell
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' add README.md agentgo
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' commit -m 'docs: publish AgentGo usage and verification'
```

### Task 8: Push and open the draft pull request

**Files:**
- No new local files expected.

- [ ] **Step 1: Inspect final scope and commit history**

```powershell
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' diff --stat main...HEAD
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' log --oneline main..HEAD
```

Expected: only AgentGo, its tests, approved planning documents, and the root README are present.

- [ ] **Step 2: Push the branch**

```powershell
git -C 'C:\Users\Admin\Documents\Codex\2026-06-05\github\work\claude-skills' push -u origin agent/add-agentgo
```

Expected: remote branch created successfully.

- [ ] **Step 3: Create a draft pull request**

```powershell
gh pr create --repo hesongshuaige/claude-skills --base main --head agent/add-agentgo --draft `
  --title 'feat: add AgentGo Hermes deployment skill' `
  --body 'Adds a tested, portable skill for isolated Hermes profiles, dedicated Feishu bots, user authorization, context templates, troubleshooting, and safe handoff.'
```

Expected: GitHub returns the draft pull-request URL.

- [ ] **Step 4: Verify the remote pull request**

```powershell
gh pr view --repo hesongshuaige/claude-skills --json url,isDraft,headRefName,baseRefName,statusCheckRollup
```

Expected: `isDraft` is true, head is `agent/add-agentgo`, and base is `main`.

## Self-Review Results

- Spec coverage: all twelve design sections map to Tasks 1–8.
- Scope: one cohesive deliverable; references, templates, validator, tests, and publication all serve the same skill.
- Placeholder scan: no TBD/TODO/“implement later” instructions remain in this plan.
- Interface consistency: the validator entrypoint, template placeholder set, required reference names, and metadata values are stable across tasks.
- Safety: external publication occurs only in Task 8, after local validation; secrets are never accepted as committed content or printed by the validator.
