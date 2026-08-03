import re
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_TOPICS = {
    "hermes-profile-and-model.md": ("profile", "model", "key_env", "workspace"),
    "feishu-bot-and-permissions.md": ("websocket", "gateway", "allowlist", "App ID"),
    "lark-user-authorization.md": ("bot-only", "user-default", "device-code", "--as user"),
    "context-files-and-prompts.md": ("SOUL.md", "AGENTS.md", "20,000", "terminal.cwd"),
    "troubleshooting.md": ("401", "App ID", "PowerShell", "gateway"),
    "security-and-handoff.md": ("rotate", "600", "allowlist", "handoff"),
    "pressure-scenarios.md": ("无技能基线风险", "使用技能后的通过信号", "评分规则"),
}
TEMPLATE_PLACEHOLDERS = {
    "SOUL.md.template": {
        "{{AGENT_NAME}}",
        "{{ONE_LINE_ROLE}}",
        "{{PERMISSION_BOUNDARIES}}",
    },
    "AGENTS.md.template": {
        "{{INPUT_SOURCES}}",
        "{{OUTPUT_TARGETS}}",
        "{{PERMISSION_BOUNDARIES}}",
        "{{VERIFICATION_RULES}}",
    },
    "README.md.template": {
        "{{AGENT_NAME}}",
        "{{AUTOMATIC_CAPABILITIES}}",
        "{{ON_DEMAND_CAPABILITIES}}",
        "{{NOT_ENABLED_CAPABILITIES}}",
    },
    "PROJECT.md.template": {
        "{{PRIMARY_USERS}}",
        "{{INPUT_SOURCES}}",
        "{{OUTPUT_TARGETS}}",
        "{{AUTOMATIC_CAPABILITIES}}",
        "{{ON_DEMAND_CAPABILITIES}}",
        "{{NOT_ENABLED_CAPABILITIES}}",
    },
}
ALL_PLACEHOLDERS = {
    "{{AGENT_NAME}}",
    "{{ONE_LINE_ROLE}}",
    "{{PRIMARY_USERS}}",
    "{{INPUT_SOURCES}}",
    "{{OUTPUT_TARGETS}}",
    "{{AUTOMATIC_CAPABILITIES}}",
    "{{ON_DEMAND_CAPABILITIES}}",
    "{{NOT_ENABLED_CAPABILITIES}}",
    "{{PERMISSION_BOUNDARIES}}",
    "{{VERIFICATION_RULES}}",
}
SECRET_NAME = r"(?:[A-Z][A-Z0-9_]*_)?(?:API_KEY|APP_SECRET|PASSWORD)"
SECRET_ASSIGNMENT = re.compile(
    rf"(?im)^\s*(?:export\s+)?(?P<name>{SECRET_NAME})\s*(?:=|:)\s*(?P<value>[^#\r\n]+?)\s*$"
)
FEISHU_IDENTIFIER = re.compile(
    r"(?<![A-Za-z0-9])(?:cli|ou)_[A-Za-z0-9]{16,}(?![A-Za-z0-9])"
)
PLACEHOLDER_WORDS = ("redacted", "dummy", "changeme", "placeholder", "example", "test-only")


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", text, re.DOTALL)
    if not match:
        return {}

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip().strip("'\"")
    return fields


def is_placeholder_value(value: str) -> bool:
    normalized = value.strip().strip("'\"").strip().lower()
    return (
        not normalized
        or any(word in normalized for word in PLACEHOLDER_WORDS)
        or (normalized.startswith("<") and normalized.endswith(">"))
        or (normalized.startswith("${") and normalized.endswith("}"))
        or (normalized.startswith("{{") and normalized.endswith("}}"))
        or normalized.startswith("$")
        or re.fullmatch(r"(?:cli_|ou_)?0{8,}", normalized) is not None
    )


def find_likely_secrets(text: str) -> list[str]:
    findings = []
    for match in SECRET_ASSIGNMENT.finditer(text):
        if not is_placeholder_value(match.group("value")):
            findings.append(match.group("name"))
    for match in FEISHU_IDENTIFIER.finditer(text):
        if not is_placeholder_value(match.group(0)):
            findings.append("FEISHU_IDENTIFIER")
    return findings


class SecretScannerTests(unittest.TestCase):
    def test_flags_bare_export_yaml_and_prefixed_secrets(self) -> None:
        key_field = "API" + "_KEY"
        app_field = "APP_" + "SECRET"
        credential_field = "PASS" + "WORD"
        vendor_field = "VENDOR_" + key_field
        identifier = "cli_" + "a1b2c3d4e5f6g7h8"
        text = "\n".join(
            (
                f"{key_field}=sk-live-value-123",
                f"export {app_field}=live-app-value-456",
                f'{credential_field}: "live-password-789"',
                f"{vendor_field}: live-vendor-value-012",
                identifier,
            )
        )

        self.assertCountEqual(
            [key_field, app_field, credential_field, vendor_field, "FEISHU_IDENTIFIER"],
            find_likely_secrets(text),
        )

    def test_ignores_documented_placeholders_and_all_zero_ids(self) -> None:
        key_field = "API" + "_KEY"
        app_field = "APP_" + "SECRET"
        credential_field = "PASS" + "WORD"
        text = "\n".join(
            (
                f"{key_field}=<your-key>",
                f"export {app_field}=redacted",
                f"{credential_field}: dummy-password",
                f"SERVICE_{key_field}=changeme",
                f"SECONDARY_{key_field}=placeholder",
                f"THIRD_{key_field}=" + "${" + key_field + "}",
                "FEISHU_APP_ID=cli_" + "0" * 20,
                "ou_" + "0" * 20,
            )
        )

        self.assertEqual([], find_likely_secrets(text))


class SkillPackageTests(unittest.TestCase):
    def test_required_references_are_nonempty_and_cover_key_topics(self) -> None:
        reference_dir = PACKAGE_ROOT / "references"
        for filename, topics in REFERENCE_TOPICS.items():
            with self.subTest(filename=filename):
                path = reference_dir / filename
                self.assertTrue(path.is_file(), f"missing reference: {filename}")
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.strip(), f"empty reference: {filename}")
                for topic in topics:
                    self.assertIn(topic.casefold(), text.casefold(), f"{filename} lacks {topic}")

    def test_required_templates_are_nonempty_and_have_role_placeholders(self) -> None:
        template_dir = PACKAGE_ROOT / "assets" / "templates"
        seen_placeholders = set()
        for filename, required in TEMPLATE_PLACEHOLDERS.items():
            with self.subTest(filename=filename):
                path = template_dir / filename
                self.assertTrue(path.is_file(), f"missing template: {filename}")
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.strip(), f"empty template: {filename}")
                self.assertEqual(set(), required - set(re.findall(r"\{\{[A-Z_]+\}\}", text)))
                seen_placeholders.update(re.findall(r"\{\{[A-Z_]+\}\}", text))

        self.assertEqual(ALL_PLACEHOLDERS, seen_placeholders & ALL_PLACEHOLDERS)

    def test_skill_frontmatter_has_only_name_and_description(self) -> None:
        frontmatter = read_frontmatter(PACKAGE_ROOT / "SKILL.md")

        self.assertEqual({"name", "description"}, set(frontmatter))

    def test_skill_description_starts_with_use_when(self) -> None:
        frontmatter = read_frontmatter(PACKAGE_ROOT / "SKILL.md")

        self.assertIsInstance(frontmatter.get("description"), str)
        self.assertTrue(frontmatter["description"].startswith("Use when"))

    def test_openai_metadata_names_explicit_invocation(self) -> None:
        metadata = (PACKAGE_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn("$agentgo", metadata)

    def test_package_contains_no_todo_markers(self) -> None:
        marker = "TO" + "DO"
        offenders = []
        for path in self._package_text_files():
            if marker in path.read_text(encoding="utf-8"):
                offenders.append(path.relative_to(PACKAGE_ROOT).as_posix())

        self.assertEqual([], offenders)

    def test_package_contains_no_likely_real_secrets(self) -> None:
        offenders = []
        for path in self._package_text_files():
            if find_likely_secrets(path.read_text(encoding="utf-8")):
                offenders.append(path.relative_to(PACKAGE_ROOT).as_posix())

        self.assertEqual([], offenders)

    @staticmethod
    def _package_text_files() -> list[Path]:
        return sorted(
            path
            for path in PACKAGE_ROOT.rglob("*")
            if path.is_file()
            and path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".template"}
        )


if __name__ == "__main__":
    unittest.main()
