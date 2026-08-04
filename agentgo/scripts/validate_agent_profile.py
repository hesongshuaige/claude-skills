#!/usr/bin/env python3
"""Read-only validation for a Hermes agent profile."""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    message: str


_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_YAML_KEY = re.compile(r"^[A-Za-z0-9_.-]+$")
_MODEL_REQUIRED_FILES = ("profile.yaml", "config.yaml", ".env")
_FULL_REQUIRED_FILES = _MODEL_REQUIRED_FILES + ("SOUL.md",)
_REQUIRED_DIRECTORIES = ("skills", "sessions", "memories")
_CONTEXT_FILES = ("AGENTS.md", "README.md", "PROJECT.md")
_REQUIRED_FEISHU = (
    "FEISHU_APP_ID",
    "FEISHU_APP_SECRET",
    "FEISHU_DOMAIN",
    "FEISHU_CONNECTION_MODE",
    "FEISHU_ALLOWED_USERS",
    "FEISHU_GROUP_POLICY",
    "FEISHU_REQUIRE_MENTION",
)
_FEISHU_ENUMS = {
    "FEISHU_DOMAIN": {"feishu", "lark"},
    "FEISHU_CONNECTION_MODE": {"websocket"},
    "FEISHU_GROUP_POLICY": {"open", "allowlist", "disabled"},
    "FEISHU_REQUIRE_MENTION": {"true", "false"},
}
# Authoritative source: the installed Hermes runtime's ``PROVIDER_REGISTRY``,
# ``resolve_provider`` alias table, and ``is_runtime_provider_routable`` special
# identities. This is a portable static fallback snapshot checked 2026-08-04;
# it intentionally avoids importing Hermes or triggering plugin/network setup.
_BUILTIN_MODEL_PROVIDERS = frozenset(
    """
    ai-gateway aigateway alibaba alibaba-cloud alibaba-coding
    alibaba-coding-plan alibaba_coding alibaba_coding_plan amazon
    amazon-bedrock anthropic arcee arcee-ai arceeai auto aws aws-bedrock
    azure-foundry bedrock claude claude-code copilot copilot-acp
    copilot-acp-agent custom dashscope deep-infra deepinfra deepinfra-ai
    deepseek fireworks fireworks-ai fw gemini github github-copilot
    github-copilot-acp github-model github-models glm gmi gmi-cloud gmicloud
    go google google-ai-studio google-gemini grok grok-oauth hf hugging-face
    huggingface huggingface-hub kilo kilo-code kilo-gateway kilocode kimi
    kimi-cn kimi-coding kimi-coding-cn kimi-for-coding llama-cpp llama.cpp
    llamacpp lm-studio lm_studio lmstudio mimo minimax minimax-china minimax-cn
    minimax-global minimax-oauth minimax-portal minimax_cn minimax_oauth moa
    moonshot moonshot-cn nous novita novita-ai novitaai nvidia nvidia-nim
    ollama ollama-cloud ollama_cloud openai-api openai-codex opencode
    opencode-go opencode-go-sub opencode-zen openrouter qwen qwen-cli
    qwen-oauth qwen-portal solar step stepfun stepfun-coding-plan tencent
    tencent-cloud tencent-tokenhub tencentmaas tokenhub upstage vercel
    vercel-ai-gateway vertex vllm x-ai x-ai-oauth x.ai xai xai-grok-oauth
    xai-oauth xiaomi xiaomi-mimo z-ai z.ai zai zen zhipu
    """.split()
)


def _strip_yaml_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote == '"':
            escaped = True
            continue
        if character in "'\"":
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
        elif character == "#" and quote is None and (
            index == 0 or value[index - 1].isspace()
        ):
            return value[:index].rstrip()
    if quote is not None:
        raise ValueError("unterminated quoted scalar")
    return value.rstrip()


def _parse_scalar(value: str) -> Any:
    value = _strip_yaml_comment(value).strip()
    if not value:
        raise ValueError("missing scalar value")
    if value[0] in "[{":
        return _parse_flow_collection(value)
    if value[-1:] in "]}":
        raise ValueError("unmatched flow collection delimiter")
    if value[0] in "'\"":
        quote = value[0]
        if len(value) < 2 or value[-1] != quote:
            raise ValueError("invalid quoted scalar")
        inner = value[1:-1]
        if quote == "'":
            return inner.replace("''", "'")
        # Preserve ordinary backslashes so quoted Windows paths stay usable.
        return inner.replace('\\"', '"').replace("\\\\", "\\")
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    return value


def _split_flow_items(value: str) -> list[str]:
    items: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote == '"':
            escaped = True
            continue
        if character in "'\"":
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
            continue
        if quote is not None:
            continue
        if character in "[{":
            depth += 1
        elif character in "]}":
            depth -= 1
            if depth < 0:
                raise ValueError("unmatched flow collection delimiter")
        elif character == "," and depth == 0:
            items.append(value[start:index].strip())
            start = index + 1
    if quote is not None or depth != 0:
        raise ValueError("unterminated flow collection")
    items.append(value[start:].strip())
    if any(not item for item in items):
        raise ValueError("empty flow collection item")
    return items


def _split_mapping_entry(
    value: str, *, allow_compact: bool = False
) -> tuple[str, str] | None:
    quote: str | None = None
    escaped = False
    depth = 0
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote == '"':
            escaped = True
            continue
        if character in "'\"":
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
            continue
        if quote is not None:
            continue
        if character in "[{":
            depth += 1
        elif character in "]}":
            depth -= 1
        elif character == ":" and depth == 0 and (
            allow_compact
            or index + 1 == len(value)
            or value[index + 1].isspace()
        ):
            return value[:index].strip(), value[index + 1 :].strip()
    return None


def _parse_flow_collection(value: str) -> Any:
    opener = value[0]
    closer = "]" if opener == "[" else "}"
    if not value.endswith(closer):
        raise ValueError("unterminated flow collection")
    inner = value[1:-1].strip()
    if not inner:
        return [] if opener == "[" else {}
    parts = _split_flow_items(inner)
    if opener == "[":
        return [_parse_scalar(part) for part in parts]
    mapping: dict[str, Any] = {}
    for part in parts:
        entry = _split_mapping_entry(part, allow_compact=True)
        if entry is None:
            raise ValueError("flow mapping entry must contain a colon")
        raw_key, raw_value = entry
        key = _parse_scalar(raw_key)
        if not isinstance(key, str) or not key or key in mapping:
            raise ValueError("invalid or duplicate flow mapping key")
        mapping[key] = _parse_scalar(raw_value)
    return mapping


def parse_simple_yaml(path: Path | str) -> dict:
    """Parse the mappings, scalars, and string lists used by Hermes config."""
    source = Path(path).read_text(encoding="utf-8-sig")
    tokens: list[tuple[int, str, int]] = []
    for line_number, raw_line in enumerate(source.splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            raise ValueError(f"line {line_number}: tabs are not valid indentation")
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        tokens.append((indent, raw_line[indent:], line_number))

    if not tokens:
        return {}
    if tokens[0][0] != 0:
        raise ValueError(f"line {tokens[0][2]}: unexpected indentation")

    def parse_block(index: int, block_indent: int) -> tuple[Any, int]:
        first_content = tokens[index][1]
        is_list = first_content == "-" or first_content.startswith("- ")
        container: Any = [] if is_list else {}

        while index < len(tokens):
            indent, content, line_number = tokens[index]
            if indent < block_indent:
                break
            if indent > block_indent:
                raise ValueError(f"line {line_number}: unexpected indentation")

            item_is_list = content == "-" or content.startswith("- ")
            if item_is_list != is_list:
                raise ValueError(f"line {line_number}: cannot mix lists and mappings")

            if is_list:
                raw_item = content[1:].strip()
                if not raw_item:
                    index += 1
                    if index >= len(tokens) or tokens[index][0] <= block_indent:
                        raise ValueError(
                            f"line {line_number}: empty list item must have nested content"
                        )
                    child_indent = tokens[index][0]
                    nested_item, index = parse_block(index, child_indent)
                    container.append(nested_item)
                    continue
                mapping_entry = _split_mapping_entry(raw_item)
                index += 1
                if mapping_entry is None:
                    container.append(_parse_scalar(raw_item))
                    if index < len(tokens) and tokens[index][0] > block_indent:
                        raise ValueError(
                            f"line {tokens[index][2]}: scalar list item cannot have children"
                        )
                    continue

                raw_key, raw_value = mapping_entry
                key = _parse_scalar(raw_key)
                if not isinstance(key, str) or not key or (
                    raw_key[0] not in "'\"" and not _YAML_KEY.fullmatch(key)
                ):
                    raise ValueError(f"line {line_number}: invalid list mapping key")
                item: dict[str, Any] = {}
                mapping_indent = block_indent + 2
                if raw_value:
                    item[key] = _parse_scalar(raw_value)
                elif index < len(tokens) and tokens[index][0] > mapping_indent:
                    child_indent = tokens[index][0]
                    item[key], index = parse_block(index, child_indent)
                else:
                    item[key] = {}
                if index < len(tokens) and tokens[index][0] > block_indent:
                    child_indent = tokens[index][0]
                    continuation, index = parse_block(index, child_indent)
                    if not isinstance(continuation, dict):
                        raise ValueError(
                            f"line {line_number}: list mapping continuation must be a mapping"
                        )
                    duplicate_keys = item.keys() & continuation.keys()
                    if duplicate_keys:
                        raise ValueError(f"line {line_number}: duplicate list mapping key")
                    item.update(continuation)
                container.append(item)
                continue

            if ":" not in content:
                raise ValueError(f"line {line_number}: expected key: value")
            key, raw_value = content.split(":", 1)
            key = key.strip()
            if not _YAML_KEY.fullmatch(key):
                raise ValueError(f"line {line_number}: invalid mapping key")
            if key in container:
                raise ValueError(f"line {line_number}: duplicate key {key}")

            cleaned = _strip_yaml_comment(raw_value).strip()
            index += 1
            if cleaned:
                container[key] = _parse_scalar(cleaned)
                if index < len(tokens) and tokens[index][0] > block_indent:
                    raise ValueError(
                        f"line {tokens[index][2]}: scalar value cannot have children"
                    )
            elif index < len(tokens) and tokens[index][0] > block_indent:
                child_indent = tokens[index][0]
                container[key], index = parse_block(index, child_indent)
            else:
                container[key] = {}

        return container, index

    parsed, final_index = parse_block(0, 0)
    if final_index != len(tokens):
        raise ValueError(f"line {tokens[final_index][2]}: invalid structure")
    if not isinstance(parsed, dict):
        raise ValueError("top-level YAML value must be a mapping")
    return parsed


def _normalize_env_value(raw_value: str) -> str:
    value = raw_value.strip()
    if not value:
        return ""
    if value[0] in "'\"":
        quote = value[0]
        escaped = False
        closing_index: int | None = None
        for index in range(1, len(value)):
            character = value[index]
            if escaped:
                escaped = False
                continue
            if quote == '"' and character == "\\":
                escaped = True
                continue
            if character == quote:
                closing_index = index
                break
        if closing_index is None:
            return ""
        suffix = value[closing_index + 1 :].strip()
        if suffix and not suffix.startswith("#"):
            return ""
        normalized = value[1:closing_index]
        if quote == '"':
            normalized = normalized.replace('\\"', '"').replace("\\\\", "\\")
        return normalized.strip()

    for index, character in enumerate(value):
        if character == "#" and (index == 0 or value[index - 1].isspace()):
            value = value[:index]
            break
    return value.strip()


def _parse_env_values(path: Path | str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if _ENV_NAME.fullmatch(name):
            values[name] = _normalize_env_value(value)
    return values


def parse_env_names(path: Path | str) -> set[str]:
    """Return variable names only; callers cannot accidentally expose values."""
    return set(_parse_env_values(path))


def _get_mapping(config: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = config.get(key)
    return value if isinstance(value, dict) else None


def _context_finding(path: Path) -> Finding | None:
    if not path.is_file():
        return Finding("ERROR", "MISSING_CONTEXT", f"Required context file is missing: {path.name}")
    try:
        length = len(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        return Finding("ERROR", "CONTEXT_UNREADABLE", f"Cannot read {path.name}: {error}")
    if length > 20_000:
        return Finding(
            "WARN",
            "CONTEXT_OVERSIZED",
            f"{path.name} is {length} characters; recommended maximum is 20000",
        )
    return None


def _is_obvious_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    if not normalized:
        return True
    if re.fullmatch(r"<[^>]+>", normalized):
        return True
    if any(marker in normalized for marker in ("placeholder", "changeme", "redacted", "your-")):
        return True
    compact = re.sub(r"[^a-z0-9]", "", normalized)
    return bool(compact) and set(compact) == {"0"}


def validate_profile(
    profile: Path | str,
    stage: str = "full",
    runtime_cwd: Path | str | None = None,
) -> list[Finding]:
    """Inspect a profile without changing it or contacting external services."""
    profile_path = Path(profile).expanduser()
    findings: list[Finding] = []
    if stage not in {"model", "full"}:
        return [Finding("ERROR", "STAGE_INVALID", "Validation stage must be model or full")]
    if not profile_path.is_dir():
        return [Finding("ERROR", "PROFILE_MISSING", f"Profile directory does not exist: {profile_path}")]

    required_files = _FULL_REQUIRED_FILES if stage == "full" else _MODEL_REQUIRED_FILES
    for name in required_files:
        if not (profile_path / name).is_file():
            findings.append(Finding("ERROR", "MISSING_FILE", f"Required profile file is missing: {name}"))
    if stage == "full":
        for name in _REQUIRED_DIRECTORIES:
            if not (profile_path / name).is_dir():
                findings.append(Finding("ERROR", "MISSING_DIRECTORY", f"Required profile directory is missing: {name}"))

    profile_yaml_path = profile_path / "profile.yaml"
    if profile_yaml_path.is_file():
        try:
            profile_data = parse_simple_yaml(profile_yaml_path)
        except (OSError, UnicodeError, ValueError) as error:
            findings.append(Finding("ERROR", "PROFILE_INVALID", f"Cannot parse profile.yaml: {error}"))
        else:
            profile_name = profile_data.get("name")
            profile_status = profile_data.get("status")
            # Legacy Hermes profiles, including deployed pre-metadata profiles,
            # contain description fields only. In that exact shape Hermes uses
            # the directory name as identity and presence as implicit active.
            legacy_identity = (
                "name" not in profile_data
                and "status" not in profile_data
                and isinstance(profile_data.get("description"), str)
                and bool(profile_data["description"].strip())
            )
            if not legacy_identity:
                if not isinstance(profile_name, str) or not profile_name.strip():
                    findings.append(Finding("ERROR", "PROFILE_NAME_MISSING", "profile.yaml name must be non-empty"))
                elif profile_name.strip() != profile_path.name:
                    findings.append(Finding("ERROR", "PROFILE_NAME_MISMATCH", f"profile.yaml name must match directory name {profile_path.name}"))
                if not isinstance(profile_status, str) or not profile_status.strip():
                    findings.append(Finding("ERROR", "PROFILE_STATUS_MISSING", "profile.yaml status must be non-empty"))
                elif profile_status.strip() != "active":
                    findings.append(Finding("WARN", "PROFILE_STATUS_INACTIVE", "profile.yaml status is not active"))

    soul = profile_path / "SOUL.md"
    if soul.is_file():
        finding = _context_finding(soul)
        if finding:
            findings.append(finding)

    config_path = profile_path / "config.yaml"
    config: dict[str, Any] | None = None
    if config_path.is_file():
        try:
            config = parse_simple_yaml(config_path)
        except (OSError, UnicodeError, ValueError) as error:
            findings.append(Finding("ERROR", "CONFIG_INVALID", f"Cannot parse config.yaml: {error}"))

    env_path = profile_path / ".env"
    env_values: dict[str, str] = {}
    if env_path.is_file():
        try:
            env_values = _parse_env_values(env_path)
        except (OSError, UnicodeError) as error:
            findings.append(Finding("ERROR", "ENV_UNREADABLE", f"Cannot read .env: {error}"))
        if stage == "full" and os.name != "nt":
            try:
                if env_path.stat().st_mode & 0o077:
                    findings.append(Finding("WARN", "ENV_PERMISSIONS", ".env permissions are more open than 600"))
            except OSError as error:
                findings.append(Finding("WARN", "ENV_STAT_FAILED", f"Cannot inspect .env permissions: {error}"))

    if stage == "full":
        for name in _REQUIRED_FEISHU:
            value = env_values.get(name, "").strip()
            if not value:
                findings.append(Finding("ERROR", "ENV_MISSING", f"Required .env variable is missing or empty: {name}"))
            elif _is_obvious_placeholder(value):
                findings.append(Finding("ERROR", "ENV_PLACEHOLDER", f"Required .env variable contains an obvious placeholder: {name}"))
        for name, allowed in _FEISHU_ENUMS.items():
            if env_values.get(name, "").strip():
                value = env_values[name]
                if value not in allowed:
                    findings.append(Finding("ERROR", "ENV_INVALID", f"Invalid value for {name}"))

    if config is not None:
        if "approvals" not in config:
            findings.append(
                Finding(
                    "WARN",
                    "APPROVALS_MODE_MISSING",
                    "approvals.mode is missing; Hermes normally defaults to smart",
                )
            )
        else:
            approvals = _get_mapping(config, "approvals")
            if approvals is None:
                findings.append(
                    Finding(
                        "ERROR",
                        "APPROVALS_MODE_INVALID",
                        "approvals must be a mapping",
                    )
                )
                approval_mode = None
            else:
                approval_mode = approvals.get("mode")
            if approvals is not None and approval_mode is None:
                findings.append(
                    Finding(
                        "WARN",
                        "APPROVALS_MODE_MISSING",
                        "approvals.mode is missing; Hermes normally defaults to smart",
                    )
                )
            elif approval_mode == "off":
                findings.append(
                    Finding(
                        "ERROR",
                        "APPROVALS_DISABLED",
                        "approvals.mode off disables command safety approval",
                    )
                )
            elif approval_mode is not None and approval_mode not in {"smart", "manual"}:
                findings.append(
                    Finding(
                        "ERROR",
                        "APPROVALS_MODE_INVALID",
                        "approvals.mode must be smart or manual",
                    )
                )

        model = _get_mapping(config, "model")
        if model is None:
            findings.append(Finding("ERROR", "MODEL_MISSING", "config.yaml must contain a model mapping"))
        else:
            default_model = model.get("default")
            provider_reference = model.get("provider")
            if not isinstance(default_model, str) or not default_model:
                findings.append(Finding("ERROR", "MODEL_DEFAULT_MISSING", "model.default is required"))
            if not isinstance(provider_reference, str) or not provider_reference:
                findings.append(Finding("ERROR", "MODEL_PROVIDER_MISSING", "model.provider is required"))
            else:
                providers = _get_mapping(config, "providers")

                def check_provider(provider_name: str, provider: Any) -> None:
                    if not isinstance(provider, dict):
                        findings.append(Finding("ERROR", "PROVIDER_UNKNOWN", f"Provider is not configured: {provider_name}"))
                        return
                    key_env = provider.get("key_env")
                    if not isinstance(key_env, str) or not key_env.strip():
                        findings.append(Finding("ERROR", "PROVIDER_KEY_ENV_MISSING", f"providers.{provider_name}.key_env is required"))
                    elif not env_values.get(key_env.strip(), "").strip():
                        findings.append(Finding("ERROR", "PROVIDER_KEY_MISSING", f".env model key variable is missing or empty: {key_env}"))
                    elif _is_obvious_placeholder(env_values[key_env.strip()]):
                        findings.append(Finding("ERROR", "PROVIDER_KEY_PLACEHOLDER", f".env model key variable contains an obvious placeholder: {key_env}"))

                if provider_reference.startswith("custom:"):
                    provider_name = provider_reference.partition(":")[2]
                    check_provider(
                        provider_name,
                        providers.get(provider_name) if providers else None,
                    )
                elif providers and provider_reference in providers:
                    check_provider(provider_reference, providers[provider_reference])
                elif provider_reference in _BUILTIN_MODEL_PROVIDERS:
                    findings.append(
                        Finding(
                            "WARN",
                            "PROVIDER_UNVERIFIED",
                            f"Built-in provider {provider_reference} has no local credential mapping; verify it with a direct model test",
                        )
                    )
                else:
                    findings.append(
                        Finding(
                            "ERROR",
                            "PROVIDER_UNKNOWN",
                            f"Provider is not recognized: {provider_reference}",
                        )
                    )

        terminal = _get_mapping(config, "terminal")
        cwd_value = terminal.get("cwd") if terminal else None

        def check_workspace_context(workspace_path: Path) -> None:
            for filename in _CONTEXT_FILES:
                finding = _context_finding(workspace_path / filename)
                if finding:
                    findings.append(finding)

        if not isinstance(cwd_value, str) or not cwd_value:
            findings.append(Finding("ERROR", "WORKSPACE_MISSING", "terminal.cwd must point to the workspace"))
        else:
            cwd_value = cwd_value.strip()
            workspace = Path(cwd_value).expanduser()
            is_windows_absolute = bool(
                re.match(r"^[A-Za-z]:[\\/]", cwd_value)
                or cwd_value.startswith("\\\\")
            )
            is_posix_absolute = cwd_value.startswith("/")
            if cwd_value in {"auto", "cwd", "."}:
                if stage == "model":
                    findings.append(
                        Finding(
                            "WARN",
                            "WORKSPACE_UNVERIFIED",
                            f"terminal.cwd uses runtime placeholder {cwd_value}; static validation cannot confirm workspace context",
                        )
                    )
                elif runtime_cwd is None:
                    findings.append(
                        Finding(
                            "ERROR",
                            "WORKSPACE_UNRESOLVED",
                            "terminal.cwd is a runtime placeholder; full validation requires --runtime-cwd",
                        )
                    )
                else:
                    runtime_workspace = Path(runtime_cwd).expanduser()
                    if not runtime_workspace.is_absolute():
                        findings.append(
                            Finding(
                                "ERROR",
                                "WORKSPACE_UNRESOLVED",
                                "--runtime-cwd must be an absolute path on this platform",
                            )
                        )
                    elif not runtime_workspace.is_dir():
                        findings.append(
                            Finding(
                                "ERROR",
                                "WORKSPACE_MISSING",
                                "--runtime-cwd directory does not exist",
                            )
                        )
                    else:
                        check_workspace_context(runtime_workspace)
            elif workspace.is_absolute():
                if not workspace.is_dir():
                    findings.append(Finding("ERROR", "WORKSPACE_MISSING", f"terminal.cwd workspace does not exist: {workspace}"))
                elif stage == "full":
                    check_workspace_context(workspace)
            elif is_windows_absolute or is_posix_absolute:
                findings.append(
                    Finding(
                        "ERROR" if stage == "full" else "WARN",
                        "WORKSPACE_UNRESOLVED" if stage == "full" else "WORKSPACE_UNVERIFIED",
                        "terminal.cwd is absolute for another platform and cannot be checked on this host",
                    )
                )
            else:
                findings.append(
                    Finding(
                        "ERROR",
                        "WORKSPACE_RELATIVE",
                        "terminal.cwd is a relative path whose runtime location cannot be validated safely",
                    )
                )

    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Hermes agent profile without modifying it")
    parser.add_argument(
        "--stage",
        choices=("model", "full"),
        default="full",
        help="model checks the pre-app model gate; full also checks Feishu and workspace readiness (default: full)",
    )
    parser.add_argument(
        "--runtime-cwd",
        type=Path,
        help="actual workspace path for full validation when terminal.cwd is auto, cwd, or .",
    )
    parser.add_argument("profile", type=Path, help="path to the Hermes profile directory")
    try:
        arguments = parser.parse_args(argv)
        findings = validate_profile(
            arguments.profile,
            stage=arguments.stage,
            runtime_cwd=arguments.runtime_cwd,
        )
    except KeyboardInterrupt:
        print("[ERROR] INTERRUPTED: validation interrupted")
        return 130
    except Exception as error:  # Last-resort CLI boundary: never expose a traceback.
        print(f"[ERROR] VALIDATION_FAILED: {error}")
        return 2

    for finding in findings:
        print(f"[{finding.level}] {finding.code}: {finding.message}")
    errors = sum(finding.level == "ERROR" for finding in findings)
    warnings = sum(finding.level == "WARN" for finding in findings)
    print(f"[SUMMARY] errors={errors} warnings={warnings}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
