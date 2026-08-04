---
name: agentgo
description: "Use when creating, repairing, or handing off an isolated Hermes Agent profile; connecting it to a dedicated Feishu bot; granting bot or user-level Feishu access; or generating SOUL.md, AGENTS.md, README.md, and PROJECT.md for a reusable agent deployment."
---

# AgentGo

Use this skill to create, repair, validate, hand off, or retire an isolated Hermes profile; connect its dedicated Feishu bot; authorize user resources; or generate its four context files. Do not use it for ordinary chat, general business automation, or read-only Feishu lookups that do not change an agent deployment.

## Non-negotiable safety gates

- Never ask for or accept a secret in chat. Have the user enter model keys, App Secrets, tokens, device codes, and passwords in a secure terminal or secret store. Show variable names and presence only, never values.
- Treat every suspected exposure as a leak: stop using the credential and follow the pre-authorized incident procedure in [security-and-handoff.md](references/security-and-handoff.md). If rotation or revocation is not already authorized, pause for explicit approval.
- Give every profile a new, dedicated Feishu application and independent credentials. Never clone or reuse `.env`, App ID, App Secret, model key, or user token material.
- Keep approvals in `smart` or `manual` mode. Never use `--yolo`, disable approvals, or describe an approval-bypassing path as safe.
- Require explicit, action-specific approval before scanning a QR code, granting consent, opening an application scope, creating or binding an application, writing a user resource, changing permissions, deleting anything, or retiring a deployment.
- A fixed automatic task may continue only inside an already documented authorization whose target, scope, frequency, recipient, and identity remain unchanged. Encode that boundary in the generated `AGENTS.md`. Any change requires fresh approval.
- Never silently fall back from `user` to `bot`, or from `bot` to `user`. Report the failed identity layer and stop.

## Permission decision tree

1. If the agent only sends or receives chat, choose `bot-only`. User OAuth is unnecessary.
2. If it must access a user's Wiki, Base, Drive, or Docs, choose `user-default`, request only the exact scopes confirmed by the target method schema, complete explicit user consent, and invoke every user-resource operation with `--as user`.
3. If an API error includes `required_scope` or `console_url`, treat it as an application-scope problem. Give the exact `console_url` to the user for approval; do not substitute user login or elevate scope yourself.
4. If identity, application, profile, or authorization ownership is uncertain, stop and reconcile them before any resource call.

Read [lark-user-authorization.md](references/lark-user-authorization.md) before configuring user identity. Bot chat alone does not require that flow.

## Staged workflow

Advance only when the current exit condition is supported by evidence. Keep commands version-aware: first probe `hermes --help` and the actual installed entry point, then inspect each relevant subcommand's `--help`. Do not hard-code a virtual-environment path or assume `-p` exists.

### 1. Preflight and requirements

**Entry:** The user requests a new, repaired, handed-off, or retired deployment.

**Actions:** Read [security-and-handoff.md](references/security-and-handoff.md). Establish the requested profile name, display name, role, host, workspace, Feishu domain, users, chat policy, model/provider, resource identity, automatic tasks, success evidence, and retirement scope. Inspect existing profiles and installations without changing them. Ask one blocking question at a time. Record unapproved capabilities as not enabled.

**Exit:** Scope, success criteria, required approvals, and prohibited actions are explicit; the Hermes entry point and supported command shapes are known.

### 2. Create or repair the isolated profile

**Entry:** Profile creation or repair is approved and no naming collision is unresolved.

**Actions:** Follow [hermes-profile-and-model.md](references/hermes-profile-and-model.md). Create a new profile without cloning credentials, or make the smallest repair to the named profile. Establish a real absolute workspace and confirm the profile structure without printing secret values.

**Exit:** The correct isolated profile and workspace exist, with no credential reuse or unresolved ownership conflict.

### 3. Configure and safely test the model

**Entry:** The isolated profile exists and the user can enter credentials in a secure terminal.

**Actions:** Configure the profile-local model, provider, `key_env`, workspace, and approval mode using [hermes-profile-and-model.md](references/hermes-profile-and-model.md). Run the read-only validator first, then use the reference's human-supervised safe interaction path for the direct model test.

> **Warning:** one-shot mode bypasses approvals. Do not copy an unsafe one-shot command into this entry point, and do not use one-shot unless the narrowly isolated exception and its evidence requirements in the reference are fully satisfied.

**Exit:** The validator has no blocking model/configuration error; the expected model and provider return the expected short response without fallback, authentication error, tool side effect, or secret disclosure.

### 4. Generate the four context files

**Entry:** The profile, absolute workspace, role, capability states, authorization boundaries, and verification rules are known.

**Actions:** Read [context-files-and-prompts.md](references/context-files-and-prompts.md). Copy the four files from `assets/templates/`; replace every existing placeholder exactly once according to its template's responsibility rather than inventing duplicate fields. Put `SOUL.md` only at the profile root. Put `AGENTS.md`, `README.md`, and `PROJECT.md` only in the `terminal.cwd` workspace. Re-read all four from disk, scan for residual placeholders and secrets, confirm their locations and UTF-8 encoding, and keep each within the documented context budget. Start a fresh session to verify actual loading when the environment is available.

**Exit:** All four files are in their single correct locations, contain no placeholder or secret residue, agree on capability state, and the workspace rules load in a new session or are explicitly reported as unverified.

### 5. Create or bind the dedicated Feishu application

**Entry:** The model test passed and the user explicitly approved creating or binding a new dedicated application.

**Actions:** Read [feishu-bot-and-permissions.md](references/feishu-bot-and-permissions.md). Use its QR or manual route, keeping interactive registration alive. The user must personally approve scanning and application creation. Enable only approved minimum scopes and events, publish as required, and have the user enter credentials securely. Never bind an old application's credentials.

**Exit:** The profile has one dedicated application, the bot capability/events/scopes match the approved chat use case, and no secret appears in chat, repository, handoff, or ordinary logs.

### 6. Route application permissions and user authorization

**Entry:** The dedicated application exists and the required identity is known.

**Actions:** Apply the permission decision tree above. For chat-only deployments, retain `bot-only`. For user resources, follow [lark-user-authorization.md](references/lark-user-authorization.md): bind the current new application, inspect the exact method schema, request exact scopes, let the user consent, verify identity, and begin with an explicitly user-scoped read. Require separate approval for each write target, scope, and consequence.

**Exit:** Application scope, bot access, user consent, resource sharing, and invocation identity have each been verified separately, or the unverified layer is named without fallback.

### 7. Start the gateway

**Entry:** Model validation passed, the dedicated application is configured, and the intended users/chat policy are approved.

**Actions:** Use the lifecycle and logging instructions in [feishu-bot-and-permissions.md](references/feishu-bot-and-permissions.md). Install or run only the service mode supported by local help, under an ordinary user. Restart the correct profile after configuration changes. Inspect status and fresh logs without exposing values.

**Exit:** Status and logs identify the intended profile and show its Feishu websocket connected; otherwise stop at the gateway layer.

### 8. Perform layered acceptance

**Entry:** Generated files and configuration pass static validation, and each live test has its required authorization.

**Actions:** Test in this exact order:

1. read-only profile validator;
2. direct model response;
3. gateway status and current log;
4. outbound message;
5. allowlisted private chat;
6. group chat with the approved policy and mention behavior;
7. explicitly user-scoped read-only resource access, if enabled;
8. a narrowly scoped write test only when that exact write is authorized.

Record each layer as passed, failed, or not run. Partial success is never full success. Use [troubleshooting.md](references/troubleshooting.md) after a failure: identify the layer, change one thing, and retest that layer before continuing.

**Exit:** Every required layer has evidence, and every optional or blocked layer is accurately marked unverified or failed.

### 9. Hand off or retire

**Entry:** Acceptance has stopped at a known layer and the owner is ready to receive the result, or retirement was explicitly requested.

**Actions:** Follow [security-and-handoff.md](references/security-and-handoff.md). Produce its secret-free handoff with paths, display names, variable names, service status, per-layer evidence, not-enabled capabilities, risks, dates, and owner. For retirement, inventory profile, gateway, application, authorization, schedules, sessions, memories, and business data; obtain a separate decision for each stop, retain, export, revoke, or delete action.

**Exit:** The handoff contains no credential, token, real App ID, real user identifier, server address, or password; completed, partial, blocked, retained, revoked, and deleted states are not conflated.

## Failure, validation, and maintenance

- On any failure, read [troubleshooting.md](references/troubleshooting.md), preserve the last safe state, change only one relevant cause, and rerun the failed layer. Do not edit several layers speculatively.
- Run the validator after profile/config/context changes and before model or gateway acceptance. Re-run affected live layers after credential rotation, scope/consent changes, identity-policy changes, gateway changes, or context-file changes.
- Use [pressure-scenarios.md](references/pressure-scenarios.md) when developing, reviewing, or materially changing this skill, and before claiming a reusable deployment is robust. Fill its execution record only after the target agent actually ran the scenario in the required clean environment; static review is not a pressure-test result.
- During maintenance, re-check local help, profile/application ownership, minimum scopes, authorization boundaries, context loading, secret hygiene, and the dates/evidence in `README.md` and `PROJECT.md`. Never convert old evidence into a current-pass claim.

## Resource map

Read only the resources needed for the active stage, but always load the named safety reference before its gate.

| Resource | Read or use when |
|---|---|
| [hermes-profile-and-model.md](references/hermes-profile-and-model.md) | Discovering Hermes, creating/repairing a profile, configuring a model, or running the safe direct model test. |
| [feishu-bot-and-permissions.md](references/feishu-bot-and-permissions.md) | Creating the dedicated app, choosing bot scopes/events, managing the gateway, or running message acceptance. |
| [lark-user-authorization.md](references/lark-user-authorization.md) | Accessing user Wiki, Base, Drive, Docs, calendar, or mail; not needed for chat-only bots. |
| [context-files-and-prompts.md](references/context-files-and-prompts.md) | Generating, locating, budgeting, transferring, or verifying the four context files. |
| [troubleshooting.md](references/troubleshooting.md) | Any model, app, gateway, message, user-auth, transfer, or context-loading failure. |
| [security-and-handoff.md](references/security-and-handoff.md) | Before credentials, scope expansion, automation, handoff, incident response, deletion, or retirement. |
| [pressure-scenarios.md](references/pressure-scenarios.md) | Forward-testing or reviewing the skill; record results only after actual execution. |
| [SOUL.md.template](assets/templates/SOUL.md.template) | Generate the profile-root long-term identity and highest-level boundaries. |
| [AGENTS.md.template](assets/templates/AGENTS.md.template) | Generate workspace execution rules, authorization boundaries, recovery, and acceptance rules. |
| [README.md.template](assets/templates/README.md.template) | Generate the workspace capability menu, triggers, identities, evidence, and enablement conditions. |
| [PROJECT.md.template](assets/templates/PROJECT.md.template) | Generate workspace goals, users, data flow, file ownership, overall status, and risks. |
| [validate_agent_profile.py](scripts/validate_agent_profile.py) | Perform read-only structural/configuration/context validation; run `--help` first and pass the profile directory. |
