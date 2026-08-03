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
_REQUIRED_FILES = ("profile.yaml", "config.yaml", ".env", "SOUL.md")
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
    if value[0] in "[{" or value[-1:] in "]}":
        raise ValueError("flow collections are not supported")
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


def parse_simple_yaml(path: Path | str) -> dict:
    """Parse the mapping-only YAML subset used by Hermes configuration."""
    source = Path(path).read_text(encoding="utf-8-sig")
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for line_number, raw_line in enumerate(source.splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            raise ValueError(f"line {line_number}: tabs are not valid indentation")
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        content = raw_line[indent:]
        if content.startswith("-"):
            raise ValueError(f"line {line_number}: lists are not supported")
        if ":" not in content:
            raise ValueError(f"line {line_number}: expected key: value")
        key, raw_value = content.split(":", 1)
        key = key.strip()
        if not _YAML_KEY.fullmatch(key):
            raise ValueError(f"line {line_number}: invalid mapping key")

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError(f"line {line_number}: invalid indentation")
        if indent > 0 and stack[-1][0] < 0:
            raise ValueError(f"line {line_number}: unexpected indentation")
        parent = stack[-1][1]
        if key in parent:
            raise ValueError(f"line {line_number}: duplicate key {key}")

        cleaned = _strip_yaml_comment(raw_value).strip()
        if cleaned:
            parent[key] = _parse_scalar(cleaned)
        else:
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))

    return root


def _parse_env(path: Path | str) -> dict[str, str]:
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
            values[name] = value.strip()
    return values


def parse_env_names(path: Path | str) -> set[str]:
    """Return variable names only; callers cannot accidentally expose values."""
    return set(_parse_env(path))


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


def validate_profile(profile: Path | str) -> list[Finding]:
    """Inspect a profile without changing it or contacting external services."""
    profile_path = Path(profile).expanduser()
    findings: list[Finding] = []
    if not profile_path.is_dir():
        return [Finding("ERROR", "PROFILE_MISSING", f"Profile directory does not exist: {profile_path}")]

    for name in _REQUIRED_FILES:
        if not (profile_path / name).is_file():
            findings.append(Finding("ERROR", "MISSING_FILE", f"Required profile file is missing: {name}"))
    for name in _REQUIRED_DIRECTORIES:
        if not (profile_path / name).is_dir():
            findings.append(Finding("ERROR", "MISSING_DIRECTORY", f"Required profile directory is missing: {name}"))

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
            env_values = _parse_env(env_path)
        except (OSError, UnicodeError) as error:
            findings.append(Finding("ERROR", "ENV_UNREADABLE", f"Cannot read .env: {error}"))
        if os.name != "nt":
            try:
                if env_path.stat().st_mode & 0o077:
                    findings.append(Finding("WARN", "ENV_PERMISSIONS", ".env permissions are more open than 600"))
            except OSError as error:
                findings.append(Finding("WARN", "ENV_STAT_FAILED", f"Cannot inspect .env permissions: {error}"))

    for name in _REQUIRED_FEISHU:
        if name not in env_values:
            findings.append(Finding("ERROR", "ENV_MISSING", f"Required .env variable is missing: {name}"))
    for name, allowed in _FEISHU_ENUMS.items():
        if name in env_values:
            value = env_values[name]
            if value not in allowed:
                findings.append(Finding("ERROR", "ENV_INVALID", f"Invalid {name} value: {value}"))

    if config is not None:
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
                provider_name = provider_reference.partition(":")[2] if provider_reference.startswith("custom:") else provider_reference
                providers = _get_mapping(config, "providers")
                provider = providers.get(provider_name) if providers else None
                if not isinstance(provider, dict):
                    findings.append(Finding("ERROR", "PROVIDER_UNKNOWN", f"Provider is not configured: {provider_name}"))
                else:
                    key_env = provider.get("key_env")
                    if not isinstance(key_env, str) or not key_env:
                        findings.append(Finding("ERROR", "PROVIDER_KEY_ENV_MISSING", f"providers.{provider_name}.key_env is required"))
                    elif key_env not in env_values:
                        findings.append(Finding("ERROR", "PROVIDER_KEY_MISSING", f".env is missing model key variable: {key_env}"))

        terminal = _get_mapping(config, "terminal")
        cwd_value = terminal.get("cwd") if terminal else None
        if not isinstance(cwd_value, str) or not cwd_value:
            findings.append(Finding("ERROR", "WORKSPACE_MISSING", "terminal.cwd must point to the workspace"))
        else:
            workspace = Path(cwd_value).expanduser()
            if not workspace.is_absolute():
                workspace = profile_path / workspace
            if not workspace.is_dir():
                findings.append(Finding("ERROR", "WORKSPACE_MISSING", f"terminal.cwd workspace does not exist: {workspace}"))
            else:
                for filename in _CONTEXT_FILES:
                    finding = _context_finding(workspace / filename)
                    if finding:
                        findings.append(finding)

    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Hermes agent profile without modifying it")
    parser.add_argument("profile", type=Path, help="path to the Hermes profile directory")
    try:
        arguments = parser.parse_args(argv)
        findings = validate_profile(arguments.profile)
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
